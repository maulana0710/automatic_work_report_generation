from datetime import datetime
from typing import List
from pydantic import BaseModel


class FileMetadataResponse(BaseModel):
    """Response model for file metadata."""
    file_id: str
    original_name: str
    size: int
    uploaded_at: datetime


class UploadResponse(BaseModel):
    """Response model for file upload."""
    files: List[FileMetadataResponse]
    message: str


class FileListResponse(BaseModel):
    """Response model for listing files."""
    files: List[FileMetadataResponse]
    total: int
