from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.file_manager import file_manager
from app.api.schemas.upload import (
    FileMetadataResponse,
    UploadResponse,
    FileListResponse,
)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload one or more markdown files."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded = await file_manager.save_multiple(files)

    return UploadResponse(
        files=[
            FileMetadataResponse(
                file_id=f.file_id,
                original_name=f.original_name,
                size=f.size,
                uploaded_at=f.uploaded_at,
            )
            for f in uploaded
        ],
        message=f"Successfully uploaded {len(uploaded)} file(s)",
    )


@router.get("", response_model=FileListResponse)
async def list_files():
    """List all uploaded files."""
    files = file_manager.list_files()
    return FileListResponse(
        files=[
            FileMetadataResponse(
                file_id=f.file_id,
                original_name=f.original_name,
                size=f.size,
                uploaded_at=f.uploaded_at,
            )
            for f in files
        ],
        total=len(files),
    )


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file."""
    success = file_manager.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}


@router.get("/{file_id}/content")
async def get_file_content(file_id: str):
    """Get the content of an uploaded file."""
    content = file_manager.get_file_content(file_id)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"file_id": file_id, "content": content}
