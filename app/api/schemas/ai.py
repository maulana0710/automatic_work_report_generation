"""Schemas for AI processing endpoints."""

from pydantic import BaseModel
from typing import Optional


class AIProcessRequest(BaseModel):
    """Request model for AI processing."""
    file_id: str


class AIProcessResponse(BaseModel):
    """Response model for AI processing."""
    processed_content: str
    original_file_id: str
    new_file_id: str
    new_filename: str


class AIStatusResponse(BaseModel):
    """Response model for AI status check."""
    configured: bool
    model: Optional[str] = None
