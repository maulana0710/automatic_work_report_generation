import re
import markdown
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from datetime import datetime


class CombineMode(str, Enum):
    """How to combine multiple markdown files."""
    SEQUENTIAL = "sequential"  # Files concatenated with separator
    SECTIONED = "sectioned"    # Each file becomes a section with header
    CHAPTERED = "chaptered"    # Each file gets page break


@dataclass
class ParsedMarkdown:
    """Result of parsing markdown content."""
    html: str
    toc: str
    meta: Dict[str, Any]


class MarkdownParser:
    """Converts Markdown to HTML with extensions."""

    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "toc",
                "meta",
                "nl2br",
                "sane_lists",
                "attr_list",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "linenums": False,
                    "guess_lang": True,
                },
                "toc": {
                    "permalink": False,
                    "toc_depth": 3,
                },
            },
        )

    def parse(self, md_content: str) -> ParsedMarkdown:
        """Convert markdown to HTML with metadata."""
        self.md.reset()
        html = self.md.convert(md_content)
        toc = getattr(self.md, "toc", "")
        meta = getattr(self.md, "Meta", {})

        return ParsedMarkdown(html=html, toc=toc, meta=meta)

    def parse_file(self, file_path: Path) -> ParsedMarkdown:
        """Parse a markdown file."""
        content = file_path.read_text(encoding="utf-8")
        return self.parse(content)

    def combine_contents(
        self,
        contents: List[str],
        filenames: Optional[List[str]] = None,
        mode: CombineMode = CombineMode.SEQUENTIAL,
    ) -> str:
        """Combine multiple markdown contents into one."""
        if not contents:
            return ""

        if mode == CombineMode.SEQUENTIAL:
            return "\n\n---\n\n".join(contents)

        elif mode == CombineMode.SECTIONED:
            parts = []
            for i, content in enumerate(contents):
                if filenames and i < len(filenames):
                    name = Path(filenames[i]).stem.replace("_", " ").replace("-", " ").title()
                    parts.append(f"## {name}\n\n{content}")
                else:
                    parts.append(content)
            return "\n\n---\n\n".join(parts)

        elif mode == CombineMode.CHAPTERED:
            parts = []
            for i, content in enumerate(contents):
                if filenames and i < len(filenames):
                    name = Path(filenames[i]).stem.replace("_", " ").replace("-", " ").title()
                    parts.append(f'<div class="chapter">\n\n## {name}\n\n{content}\n\n</div>')
                else:
                    parts.append(f'<div class="chapter">\n\n{content}\n\n</div>')
            return "\n\n".join(parts)

        return "\n\n".join(contents)

    def combine_files(
        self,
        file_paths: List[Path],
        mode: CombineMode = CombineMode.SEQUENTIAL,
    ) -> str:
        """Combine multiple markdown files into one string."""
        contents = []
        filenames = []

        for path in file_paths:
            if path.exists():
                contents.append(path.read_text(encoding="utf-8"))
                filenames.append(path.name)

        return self.combine_contents(contents, filenames, mode)


    # Indonesian month names mapping
    MONTH_MAP = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
        'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
        # English fallback
        'january': 1, 'february': 2, 'march': 3, 'may': 5,
        'june': 6, 'july': 7, 'august': 8, 'october': 10, 'december': 12,
    }

    def _parse_date_from_header(self, header: str) -> Optional[datetime]:
        """
        Parse date from a header like "## 22 Desember 2025" or "## 24 Desember 2025".
        Returns datetime object or None if not a date header.
        """
        # Pattern: ## DD Month YYYY or # DD Month YYYY
        pattern = r'#+ (\d{1,2})\s+(\w+)\s+(\d{4})'
        match = re.search(pattern, header, re.IGNORECASE)

        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3))

            month = self.MONTH_MAP.get(month_name)
            if month:
                try:
                    return datetime(year, month, day)
                except ValueError:
                    return None
        return None

    def _extract_sections_by_date(self, content: str) -> Tuple[List[str], List[Tuple[Optional[datetime], str, str]]]:
        """
        Extract sections from markdown based on date headers.
        Returns list of (date, header_line, section_content) tuples.
        """
        lines = content.split('\n')
        sections = []
        current_header = None
        current_date = None
        current_lines = []
        header_before_dates = []
        found_first_date = False

        for line in lines:
            # Check if this is a date header (## or # followed by date)
            if re.match(r'^#{1,2}\s+\d{1,2}\s+\w+\s+\d{4}', line):
                # Save previous section if exists
                if current_header is not None:
                    sections.append((current_date, current_header, '\n'.join(current_lines)))

                found_first_date = True
                current_header = line
                current_date = self._parse_date_from_header(line)
                current_lines = []
            elif not found_first_date:
                # Content before any date header (like title, summary)
                header_before_dates.append(line)
            else:
                current_lines.append(line)

        # Don't forget the last section
        if current_header is not None:
            sections.append((current_date, current_header, '\n'.join(current_lines)))

        return header_before_dates, sections

    def sort_by_date(self, content: str) -> str:
        """
        Sort markdown content chronologically by date headers.
        Dates are sorted from oldest to newest (e.g., 22 Dec → 23 Dec → 24 Dec).
        """
        header_before_dates, sections = self._extract_sections_by_date(content)

        # If no date sections found, return original content
        if not sections:
            return content

        # Sort sections by date (oldest first, None dates at the end)
        sorted_sections = sorted(
            sections,
            key=lambda x: (x[0] is None, x[0] if x[0] else datetime.max)
        )

        # Rebuild the markdown
        result_parts = []

        # Add header content (title, summary, etc.) first
        if header_before_dates:
            result_parts.append('\n'.join(header_before_dates))

        # Add sorted date sections
        for date, header, section_content in sorted_sections:
            result_parts.append(header)
            if section_content.strip():
                result_parts.append(section_content)

        return '\n'.join(result_parts)


# Singleton instance
markdown_parser = MarkdownParser()
