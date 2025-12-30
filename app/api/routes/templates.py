from fastapi import APIRouter

from app.core.template_engine import template_engine
from app.core.pdf_generator import pdf_generator
from app.api.schemas.template import (
    TemplateInfoResponse,
    TemplateListResponse,
    StyleListResponse,
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=TemplateListResponse)
async def list_templates():
    """List available report templates."""
    templates = template_engine.list_templates()
    return TemplateListResponse(
        templates=[
            TemplateInfoResponse(
                name=t.name,
                display_name=t.display_name,
                is_custom=t.is_custom,
            )
            for t in templates
        ]
    )


@router.get("/styles", response_model=StyleListResponse)
async def list_styles():
    """List available CSS styles for PDF."""
    styles = pdf_generator.list_styles()
    return StyleListResponse(styles=styles)
