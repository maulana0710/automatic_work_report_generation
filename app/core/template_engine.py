from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings


@dataclass
class ImageInfo:
    """Information about an image in the report."""
    image_id: str
    title: str
    url: str
    file_path: str  # Absolute path for PDF generation


@dataclass
class ReportVariables:
    """Variables available in report templates."""
    week_number: int = field(default_factory=lambda: date.today().isocalendar()[1])
    week_start_date: str = ""
    week_end_date: str = ""
    author_name: str = ""
    author_email: str = ""
    department: str = ""
    report_title: str = "Weekly Work Report"
    generation_date: str = field(default_factory=lambda: date.today().strftime("%B %d, %Y"))
    content: str = ""
    toc: str = ""
    show_toc: bool = True
    images: List[ImageInfo] = field(default_factory=list)  # List of images to include
    next_week_plan: str = ""  # Rencana kerja minggu depan

    def __post_init__(self):
        if not self.week_start_date or not self.week_end_date:
            self._calculate_week_dates()

    def _calculate_week_dates(self):
        """Calculate week start and end dates from week number."""
        today = date.today()
        year = today.year

        try:
            week_start = date.fromisocalendar(year, self.week_number, 1)
        except ValueError:
            week_start = date.fromisocalendar(year - 1, self.week_number, 1)

        week_end = week_start + timedelta(days=4)  # Friday

        self.week_start_date = week_start.strftime("%B %d, %Y")
        self.week_end_date = week_end.strftime("%B %d, %Y")


@dataclass
class TemplateInfo:
    """Information about a template."""
    name: str
    display_name: str
    path: Path
    is_custom: bool = False


class TemplateEngine:
    """Handles Jinja2 template rendering for reports."""

    def __init__(self, template_dir: Path = settings.templates_dir):
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_report(
        self,
        template_name: str,
        content: str,
        toc: str = "",
        variables: Optional[ReportVariables] = None,
    ) -> str:
        """Render HTML from template with variables."""
        if variables is None:
            variables = ReportVariables()

        variables.content = content
        variables.toc = toc

        template = self.env.get_template(template_name)

        return template.render(
            week_number=variables.week_number,
            week_start_date=variables.week_start_date,
            week_end_date=variables.week_end_date,
            author_name=variables.author_name,
            author_email=variables.author_email,
            department=variables.department,
            report_title=variables.report_title,
            generation_date=variables.generation_date,
            content=variables.content,
            toc=variables.toc,
            show_toc=variables.show_toc,
            images=variables.images,
            next_week_plan=variables.next_week_plan,
        )

    def list_templates(self) -> List[TemplateInfo]:
        """List available templates."""
        templates = []

        for path in self.template_dir.glob("*.html"):
            if path.name.startswith("_"):
                continue

            display_name = path.stem.replace("_", " ").replace("-", " ").title()

            templates.append(
                TemplateInfo(
                    name=path.name,
                    display_name=display_name,
                    path=path,
                    is_custom=path.parent.name == "custom",
                )
            )

        return sorted(templates, key=lambda x: x.display_name)

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists."""
        return (self.template_dir / template_name).exists()


# Singleton instance
template_engine = TemplateEngine()
