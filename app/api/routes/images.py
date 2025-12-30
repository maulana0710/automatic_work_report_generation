from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core.image_manager import image_manager

router = APIRouter(prefix="/images", tags=["images"])


@router.post("")
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload one or more images. Title is extracted from filename."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded = await image_manager.save_multiple(files)

    return {
        "images": [
            {
                "image_id": img.image_id,
                "original_name": img.original_name,
                "title": img.title,
                "size": img.size,
                "url": image_manager.get_image_url(img.image_id),
                "uploaded_at": img.uploaded_at,
            }
            for img in uploaded
        ],
        "message": f"Successfully uploaded {len(uploaded)} image(s)",
    }


@router.get("")
async def list_images():
    """List all uploaded images."""
    images = image_manager.list_images()
    return {
        "images": [
            {
                "image_id": img.image_id,
                "original_name": img.original_name,
                "title": img.title,
                "size": img.size,
                "url": image_manager.get_image_url(img.image_id),
                "uploaded_at": img.uploaded_at,
            }
            for img in images
        ],
        "total": len(images),
    }


@router.get("/{image_id}")
async def get_image(image_id: str):
    """Get image file."""
    path = image_manager.get_image_path(image_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(path)


@router.delete("/{image_id}")
async def delete_image(image_id: str):
    """Delete an uploaded image."""
    success = image_manager.delete_image(image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
