import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
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

    def _load_images(self, image_ids: List[str]) -> List[ImageInfo]:
        """Load image information for the given image IDs."""
        images = []
        for image_id in image_ids:
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
                            file_path=str(path.absolute()),
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
    ) -> GeneratedReport:
        """
        Generate a PDF report from uploaded markdown files.

        Pipeline: MD files -> Combine -> Parse -> Template -> PDF
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

        # 2. Load images
        variables.images = self._load_images(image_ids)

        # 3. Combine markdown files
        combined_md = markdown_parser.combine_files(file_paths, combine_mode)

        # 3.5 Auto-sort by date (chronological order: oldest → newest)
        combined_md = markdown_parser.sort_by_date(combined_md)

        # 4. Parse to HTML
        parsed = markdown_parser.parse(combined_md)

        # 5. Render template with variables
        html_content = template_engine.render_report(
            template_name=template_name,
            content=parsed.html,
            toc=parsed.toc,
            variables=variables,
        )

        # 6. Generate PDF
        report_id = str(uuid.uuid4())
        safe_title = "".join(
            c if c.isalnum() or c in "- _" else "_"
            for c in variables.report_title
        )
        filename = f"{safe_title}_{report_id[:8]}.pdf"
        output_path = self.output_dir / filename

        # Use base_url for resolving images
        base_url = str(settings.base_dir.absolute())

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
    ) -> str:
        """Generate HTML preview without creating PDF."""
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

        # Load images
        variables.images = self._load_images(image_ids)

        # Combine and parse markdown
        combined_md = markdown_parser.combine_files(file_paths, combine_mode)

        # Auto-sort by date (chronological order: oldest → newest)
        combined_md = markdown_parser.sort_by_date(combined_md)

        parsed = markdown_parser.parse(combined_md)

        # Render template
        return template_engine.render_report(
            template_name=template_name,
            content=parsed.html,
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
    ) -> bytes:
        """Generate PDF preview as bytes without saving to file."""
        if css_files is None:
            css_files = ["default.css"]

        if image_ids is None:
            image_ids = []

        html_content = self.generate_preview_html(
            file_ids=file_ids,
            image_ids=image_ids,
            template_name=template_name,
            variables=variables,
            combine_mode=combine_mode,
        )

        # Use base_url for resolving images
        base_url = str(settings.base_dir.absolute())

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
