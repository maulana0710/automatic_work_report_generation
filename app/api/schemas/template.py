from typing import List
from pydantic import BaseModel


class TemplateInfoResponse(BaseModel):
    """Response model for template info."""
    name: str
    display_name: str
    is_custom: bool


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    templates: List[TemplateInfoResponse]


class StyleListResponse(BaseModel):
    """Response model for listing CSS styles."""
    styles: List[str]
