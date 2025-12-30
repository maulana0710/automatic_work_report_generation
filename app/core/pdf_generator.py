from pathlib import Path
from typing import List, Optional
from io import BytesIO
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.config import settings


class PDFGenerator:
    """Generates PDF from HTML using WeasyPrint."""

    def __init__(self, css_dir: Path = settings.static_dir / "css" / "pdf"):
        self.css_dir = css_dir
        self.css_dir.mkdir(parents=True, exist_ok=True)
        self.font_config = FontConfiguration()

    def _load_stylesheets(self, css_files: List[str]) -> List[CSS]:
        """Load CSS files as WeasyPrint stylesheets."""
        stylesheets = []

        for css_file in css_files:
            css_path = self.css_dir / css_file
            if css_path.exists():
                stylesheets.append(
                    CSS(filename=str(css_path), font_config=self.font_config)
                )

        return stylesheets

    def generate(
        self,
        html_content: str,
        output_path: Path,
        css_files: Optional[List[str]] = None,
        base_url: Optional[str] = None,
    ) -> Path:
        """Generate PDF from HTML and save to file."""
        if css_files is None:
            css_files = ["default.css"]

        stylesheets = self._load_stylesheets(css_files)

        html = HTML(string=html_content, base_url=base_url)
        html.write_pdf(
            output_path,
            stylesheets=stylesheets,
            font_config=self.font_config,
        )

        return output_path

    def generate_bytes(
        self,
        html_content: str,
        css_files: Optional[List[str]] = None,
        base_url: Optional[str] = None,
    ) -> bytes:
        """Generate PDF from HTML and return as bytes."""
        if css_files is None:
            css_files = ["default.css"]

        stylesheets = self._load_stylesheets(css_files)

        html = HTML(string=html_content, base_url=base_url)
        pdf_buffer = BytesIO()
        html.write_pdf(
            pdf_buffer,
            stylesheets=stylesheets,
            font_config=self.font_config,
        )

        return pdf_buffer.getvalue()

    def list_styles(self) -> List[str]:
        """List available CSS style files."""
        styles = []
        for path in self.css_dir.glob("*.css"):
            styles.append(path.name)
        return sorted(styles)


# Singleton instance
pdf_generator = PDFGenerator()
