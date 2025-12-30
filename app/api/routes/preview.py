from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from io import BytesIO

from app.core.markdown_parser import CombineMode
from app.core.template_engine import ReportVariables
from app.services.report_service import report_service
from app.api.schemas.report import PreviewRequest

router = APIRouter(prefix="/preview", tags=["preview"])


@router.post("/html", response_class=HTMLResponse)
async def preview_html(request: PreviewRequest):
    """Get HTML preview of the report."""
    try:
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

        html = report_service.generate_preview_html(
            file_ids=request.file_ids,
            image_ids=request.image_ids,
            template_name=request.template_name,
            variables=variables,
            combine_mode=combine_mode,
        )

        return HTMLResponse(content=html)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


@router.post("/pdf")
async def preview_pdf(request: PreviewRequest):
    """Get PDF preview (in-browser viewing)."""
    try:
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

        pdf_bytes = report_service.generate_preview_pdf(
            file_ids=request.file_ids,
            image_ids=request.image_ids,
            template_name=request.template_name,
            css_files=request.css_files,
            variables=variables,
            combine_mode=combine_mode,
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=preview.pdf"},
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF preview: {str(e)}")
