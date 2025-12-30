from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class CombineModeEnum(str, Enum):
    """How to combine multiple markdown files."""
    sequential = "sequential"
    sectioned = "sectioned"
    chaptered = "chaptered"


class ReportVariablesRequest(BaseModel):
    """Request model for report variables."""
    week_number: Optional[int] = None
    author_name: str = ""
    author_email: str = ""
    department: str = ""
    report_title: str = "Weekly Work Report"
    show_toc: bool = True
    next_week_plan: str = ""  # Rencana kerja minggu depan


class GenerateReportRequest(BaseModel):
    """Request model for generating a report."""
    file_ids: List[str]
    image_ids: List[str] = []  # Optional list of image IDs to include
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
    template_name: str = "default_report.html"
    css_files: List[str] = ["default.css"]
    variables: ReportVariablesRequest = ReportVariablesRequest()
    combine_mode: CombineModeEnum = CombineModeEnum.sequential
