import re
import uuid
import html as html_lib
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass

from app.config import settings
from app.core.file_manager import file_manager
from app.core.image_manager import image_manager
from app.core.markdown_parser import markdown_parser, CombineMode
from app.core.template_engine import template_engine, ReportVariables, ImageInfo
from app.core.pdf_generator import pdf_generator


@dataclass
class GeneratedReport:
    """Information about a generated report."""
    report_id: str
    filename: str
    file_path: Path
    size: int
    generated_at: datetime


class ReportService:
    """Orchestrates the full report generation pipeline."""

    def __init__(self):
        self.output_dir = settings.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    _IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    _SRC_RE = re.compile(r'src\s*=\s*"([^"]*)"', re.IGNORECASE)
    _ALT_RE = re.compile(r'alt\s*=\s*"([^"]*)"', re.IGNORECASE)

    def _process_inline_images(
        self,
        html: str,
        for_pdf: bool,
        with_caption: bool,
    ) -> Tuple[str, Set[str]]:
        """
        Rewrite inline <img> tags in parsed markdown HTML so they point at
        uploaded images (matched by sanitized filename). Returns the processed
        HTML and the set of matched image IDs (so they can be skipped in the
        "Lampiran Gambar" section).

        - for_pdf=True   -> src becomes an absolute filesystem path (WeasyPrint).
        - for_pdf=False  -> src becomes a /uploads/images/<name> URL (browser preview).
        - with_caption   -> wrap matched images in <figure> with the alt as caption.
        - Unmatched images become a visible "[Gambar tidak ditemukan: ...]" marker.
        """
        matched_ids: Set[str] = set()

        def replace(match: "re.Match") -> str:
            tag = match.group(0)
            src_m = self._SRC_RE.search(tag)
            if not src_m:
                return tag
            src = src_m.group(1)

            alt_m = self._ALT_RE.search(tag)
            alt = alt_m.group(1) if alt_m else ""

            path = image_manager.resolve_by_filename(src)
            if path is None:
                basename = Path(src).name
                return (
                    f'<p class="img-missing">[Gambar tidak ditemukan: '
                    f'{html_lib.escape(basename)}]</p>'
                )

            matched_ids.add(path.stem)
            # PDF: file:// URI (cross-platform, valid on Windows C:\ paths too).
            # Preview: served URL via the /uploads/images static mount.
            new_src = path.absolute().as_uri() if for_pdf else f"/uploads/images/{path.name}"
            new_img = f'<img src="{html_lib.escape(new_src)}" alt="{html_lib.escape(alt)}">'

            if with_caption and alt:
                return (
                    f'<figure class="inline-figure">{new_img}'
                    f"<figcaption>{html_lib.escape(alt)}</figcaption></figure>"
                )
            return new_img

        return self._IMG_TAG_RE.sub(replace, html), matched_ids

    def _load_images(
        self, image_ids: List[str], exclude_ids: Optional[Set[str]] = None
    ) -> List[ImageInfo]:
        """Load image info for the given IDs, skipping any already shown inline."""
        exclude_ids = exclude_ids or set()
        images = []
        for image_id in image_ids:
            if image_id in exclude_ids:
                continue
            path = image_manager.get_image_path(image_id)
            if path and path.exists():
                # Get metadata from image_manager's list
                all_images = image_manager.list_images()
                for img in all_images:
                    if img.image_id == image_id:
                        images.append(ImageInfo(
                            image_id=img.image_id,
                            title=img.title,
                            url=image_manager.get_image_url(image_id),
                            file_path=path.absolute().as_uri(),
                        ))
                        break
        return images

    def generate_report(
        self,
        file_ids: List[str],
        image_ids: Optional[List[str]] = None,
        template_name: str = "default_report.html",
        css_files: Optional[List[str]] = None,
        variables: Optional[ReportVariables] = None,
        combine_mode: CombineMode = CombineMode.SEQUENTIAL,
        sort_dates: bool = True,
        with_caption: bool = False,
    ) -> GeneratedReport:
        """
        Generate a PDF report from uploaded markdown files.

        Pipeline: MD files -> Combine -> Parse -> Inline images -> Template -> PDF
        """
        if css_files is None:
            css_files = ["default.css"]

        if image_ids is None:
            image_ids = []

        if variables is None:
            variables = ReportVariables()

        # 1. Get file paths from IDs
        file_paths = []
        for file_id in file_ids:
            path = file_manager.get_file_path(file_id)
            if path and path.exists():
                file_paths.append(path)

        if not file_paths:
            raise ValueError("No valid files found for the provided file IDs")

        # 2. Combine markdown files
        combined_md = markdown_parser.combine_files(file_paths, combine_mode)

        # 2.5 Auto-sort by date (chronological order: oldest → newest)
        if sort_dates:
            combined_md = markdown_parser.sort_by_date(combined_md)

        # 3. Parse to HTML
        parsed = markdown_parser.parse(combined_md)

        # 3.5 Resolve inline images; exclude matched ones from the gallery section
        content_html, matched_ids = self._process_inline_images(
            parsed.html, for_pdf=True, with_caption=with_caption
        )
        variables.images = self._load_images(image_ids, exclude_ids=matched_ids)

        # 4. Render template with variables
        html_content = template_engine.render_report(
            template_name=template_name,
            content=content_html,
            toc=parsed.toc,
            variables=variables,
        )

        # 5. Generate PDF
        report_id = str(uuid.uuid4())
        safe_title = "".join(
            c if c.isalnum() or c in "- _" else "_"
            for c in variables.report_title
        )
        filename = f"{safe_title}_{report_id[:8]}.pdf"
        output_path = self.output_dir / filename

        # Use base_url for resolving images (file:// URI works on all OSes)
        base_url = settings.base_dir.absolute().as_uri() + "/"

        pdf_generator.generate(
            html_content=html_content,
            output_path=output_path,
            css_files=css_files,
            base_url=base_url,
        )

        return GeneratedReport(
            report_id=report_id,
            filename=filename,
            file_path=output_path,
            size=output_path.stat().st_size,
            generated_at=datetime.now(),
        )

    def generate_preview_html(
        self,
        file_ids: List[str],
        image_ids: Optional[List[str]] = None,
        template_name: str = "default_report.html",
        variables: Optional[ReportVariables] = None,
        combine_mode: CombineMode = CombineMode.SEQUENTIAL,
        sort_dates: bool = True,
        with_caption: bool = False,
        for_pdf: bool = False,
    ) -> str:
        """Generate HTML preview without creating PDF.

        for_pdf=False rewrites inline images to /uploads/images URLs (browser),
        for_pdf=True rewrites them to absolute paths (WeasyPrint).
        """
        if image_ids is None:
            image_ids = []

        if variables is None:
            variables = ReportVariables()

        # Get file paths
        file_paths = []
        for file_id in file_ids:
            path = file_manager.get_file_path(file_id)
            if path and path.exists():
                file_paths.append(path)

        if not file_paths:
            raise ValueError("No valid files found")

        # Combine and parse markdown
        combined_md = markdown_parser.combine_files(file_paths, combine_mode)

        # Auto-sort by date (chronological order: oldest → newest)
        if sort_dates:
            combined_md = markdown_parser.sort_by_date(combined_md)

        parsed = markdown_parser.parse(combined_md)

        # Resolve inline images; exclude matched ones from the gallery section
        content_html, matched_ids = self._process_inline_images(
            parsed.html, for_pdf=for_pdf, with_caption=with_caption
        )
        variables.images = self._load_images(image_ids, exclude_ids=matched_ids)

        # Render template
        return template_engine.render_report(
            template_name=template_name,
            content=content_html,
            toc=parsed.toc,
            variables=variables,
        )

    def generate_preview_pdf(
        self,
        file_ids: List[str],
        image_ids: Optional[List[str]] = None,
        template_name: str = "default_report.html",
        css_files: Optional[List[str]] = None,
        variables: Optional[ReportVariables] = None,
        combine_mode: CombineMode = CombineMode.SEQUENTIAL,
        sort_dates: bool = True,
        with_caption: bool = False,
    ) -> bytes:
        """Generate PDF preview as bytes without saving to file."""
        if css_files is None:
            css_files = ["default.css"]

        if image_ids is None:
            image_ids = []

        # PDF needs absolute image paths, so for_pdf=True
        html_content = self.generate_preview_html(
            file_ids=file_ids,
            image_ids=image_ids,
            template_name=template_name,
            variables=variables,
            combine_mode=combine_mode,
            sort_dates=sort_dates,
            with_caption=with_caption,
            for_pdf=True,
        )

        # Use base_url for resolving images (file:// URI works on all OSes)
        base_url = settings.base_dir.absolute().as_uri() + "/"

        return pdf_generator.generate_bytes(
            html_content=html_content,
            css_files=css_files,
            base_url=base_url,
        )

    def get_report_path(self, report_id: str) -> Optional[Path]:
        """Get the path to a generated report."""
        for path in self.output_dir.iterdir():
            if report_id[:8] in path.name:
                return path
        return None

    def delete_report(self, report_id: str) -> bool:
        """Delete a generated report."""
        path = self.get_report_path(report_id)
        if path and path.exists():
            path.unlink()
            return True
        return False

    def list_reports(self) -> List[GeneratedReport]:
        """List all generated reports."""
        reports = []
        for path in self.output_dir.glob("*.pdf"):
            stat = path.stat()
            report_id = path.stem.split("_")[-1] if "_" in path.stem else path.stem
            reports.append(
                GeneratedReport(
                    report_id=report_id,
                    filename=path.name,
                    file_path=path,
                    size=stat.st_size,
                    generated_at=datetime.fromtimestamp(stat.st_mtime),
                )
            )
        return sorted(reports, key=lambda x: x.generated_at, reverse=True)


# Singleton instance
report_service = ReportService()
