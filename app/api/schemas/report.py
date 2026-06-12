from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class CombineModeEnum(str, Enum):
    """How to combine multiple markdown files."""
    sequential = "sequential"
    sectioned = "sectioned"
    chaptered = "chaptered"


class ReportModeEnum(str, Enum):
    """Report layout mode."""
    weekly = "weekly"   # Weekly work report: date auto-sort, TOC, attachments
    update = "update"   # App update report: minimal layout, inline captioned images


# Each mode maps to its template, stylesheet and rendering behaviour.
MODE_PRESETS = {
    ReportModeEnum.weekly: {
        "template_name": "default_report.html",
        "css_files": ["default.css"],
        "sort_dates": True,
        "with_caption": False,
    },
    ReportModeEnum.update: {
        "template_name": "update_report.html",
        "css_files": ["update.css"],
        "sort_dates": False,
        "with_caption": True,
    },
}


class ReportVariablesRequest(BaseModel):
    """Request model for report variables."""
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    author_name: str = ""
    author_email: str = ""
    department: str = ""
    report_title: str = "Laporan Logbook Mingguan"
    show_toc: bool = True
    next_week_plan: str = ""  # Rencana kerja minggu depan


class GenerateReportRequest(BaseModel):
    """Request model for generating a report."""
    file_ids: List[str]
    image_ids: List[str] = []  # Optional list of image IDs to include
    report_mode: ReportModeEnum = ReportModeEnum.weekly
    template_name: str = "default_report.html"
    css_files: List[str] = ["default.css"]
    variables: ReportVariablesRequest = ReportVariablesRequest()
    combine_mode: CombineModeEnum = CombineModeEnum.sequential


class GeneratedReportResponse(BaseModel):
    """Response model for a generated report."""
    report_id: str
    filename: str
    size: int
    generated_at: datetime
    download_url: str


class PreviewRequest(BaseModel):
    """Request model for preview."""
    file_ids: List[str]
    image_ids: List[str] = []  # Optional list of image IDs to include
    report_mode: ReportModeEnum = ReportModeEnum.weekly
    template_name: str = "default_report.html"
    css_files: List[str] = ["default.css"]
    variables: ReportVariablesRequest = ReportVariablesRequest()
    combine_mode: CombineModeEnum = CombineModeEnum.sequential
