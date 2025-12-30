import markdown
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum


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


# Singleton instance
markdown_parser = MarkdownParser()
