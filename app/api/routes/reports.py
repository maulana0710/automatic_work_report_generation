from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.markdown_parser import CombineMode
from app.core.template_engine import ReportVariables
from app.services.report_service import report_service
from app.api.schemas.report import (
    GenerateReportRequest,
    GeneratedReportResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=GeneratedReportResponse)
async def generate_report(request: GenerateReportRequest):
    """Generate a PDF report from uploaded markdown files."""
    try:
        # Convert request to domain objects
        variables = ReportVariables(
            author_name=request.variables.author_name,
            author_email=request.variables.author_email,
            department=request.variables.department,
            report_title=request.variables.report_title,
            show_toc=request.variables.show_toc,
            next_week_plan=request.variables.next_week_plan,
        )

        # Set date range if provided
        if request.variables.start_date and request.variables.end_date:
            variables.set_date_range(
                request.variables.start_date,
                request.variables.end_date
            )

        combine_mode = CombineMode(request.combine_mode.value)

        report = report_service.generate_report(
            file_ids=request.file_ids,
            image_ids=request.image_ids,
            template_name=request.template_name,
            css_files=request.css_files,
            variables=variables,
            combine_mode=combine_mode,
        )

        return GeneratedReportResponse(
            report_id=report.report_id,
            filename=report.filename,
            size=report.size,
            generated_at=report.generated_at,
            download_url=f"/api/reports/{report.report_id}/download",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Download a generated PDF report."""
    path = report_service.get_report_path(report_id)

    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=path.name,
    )


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a generated report."""
    success = report_service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}


@router.get("")
async def list_reports():
    """List all generated reports."""
    reports = report_service.list_reports()
    return {
        "reports": [
            {
                "report_id": r.report_id,
                "filename": r.filename,
                "size": r.size,
                "generated_at": r.generated_at,
                "download_url": f"/api/reports/{r.report_id}/download",
            }
            for r in reports
        ],
        "total": len(reports),
    }
