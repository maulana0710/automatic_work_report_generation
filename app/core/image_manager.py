import uuid
import aiofiles
import re
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from fastapi import UploadFile, HTTPException

from app.config import settings


@dataclass
class ImageMetadata:
    """Metadata for an uploaded image."""
    image_id: str
    original_name: str
    title: str  # Extracted from filename
    file_path: Path
    size: int
    uploaded_at: datetime


class ImageManager:
    """Handles image upload, storage, and management."""

    def __init__(
        self,
        images_dir: Path = settings.images_dir,
        max_image_size: int = settings.max_image_size,
        allowed_extensions: set = settings.allowed_image_extensions,
    ):
        self.images_dir = images_dir
        self.max_image_size = max_image_size
        self.allowed_extensions = allowed_extensions
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _extract_title_from_filename(self, filename: str) -> str:
        """
        Extract a readable title from filename.
        Example: 'screenshot_login_page.png' -> 'Screenshot Login Page'
        Example: '01-dashboard-view.jpg' -> 'Dashboard View'
        """
        # Get filename without extension
        name = Path(filename).stem

        # Remove leading numbers and special chars
        name = re.sub(r'^[\d\-_\.]+', '', name)

        # Replace underscores and hyphens with spaces
        name = re.sub(r'[-_]+', ' ', name)

        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()

        # Title case
        if name:
            return name.title()
        else:
            # Fallback to original filename without extension
            return Path(filename).stem.title()

    def _sanitize_stem(self, stem: str) -> str:
        """
        Sanitize a filename stem the same way uploaded files are stored on disk:
        keep alphanumerics/underscores/hyphens, collapse repeats, strip edges.
        Example: '1. Tampilan Tracking' -> '1_Tampilan_Tracking'
        """
        safe = re.sub(r'[^\w\-]', '_', stem)
        safe = re.sub(r'_+', '_', safe).strip('_')
        return safe or 'image'

    def resolve_by_filename(self, src: str) -> Optional[Path]:
        """
        Resolve a markdown image reference (e.g. 'img/juni/foo%20bar.png') to an
        uploaded file on disk, matching by the sanitized basename used at upload time.
        Returns the Path or None if no matching upload exists.
        """
        # Take the basename and URL-decode (handle %20 etc.)
        basename = Path(urllib.parse.unquote(src)).name
        if not basename:
            return None

        ext = Path(basename).suffix.lower()
        if ext not in self.allowed_extensions:
            return None

        sanitized = self._sanitize_stem(Path(basename).stem)

        # Exact match first
        exact = self.images_dir / f"{sanitized}{ext}"
        if exact.exists():
            return exact

        # Fallback: name collided on upload and got a '_<uuid>' suffix
        for path in self.images_dir.iterdir():
            if path.suffix.lower() == ext and path.stem.startswith(f"{sanitized}_"):
                return path

        return None

    def _validate_image(self, file: UploadFile) -> None:
        """Validate image type."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        ext = Path(file.filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Image type not allowed. Allowed: {', '.join(self.allowed_extensions)}",
            )

    async def save_image(self, file: UploadFile) -> ImageMetadata:
        """Save an uploaded image with validation."""
        self._validate_image(file)

        ext = Path(file.filename).suffix.lower()

        # Sanitize original filename: keep alphanumerics, hyphens, underscores
        safe_stem = self._sanitize_stem(Path(file.filename).stem)

        # Handle filename conflicts by appending short uuid suffix
        new_filename = f"{safe_stem}{ext}"
        file_path = self.images_dir / new_filename
        if file_path.exists():
            short_id = str(uuid.uuid4())[:8]
            new_filename = f"{safe_stem}_{short_id}{ext}"
            file_path = self.images_dir / new_filename

        image_id = Path(new_filename).stem

        content = await file.read()

        if len(content) > self.max_image_size:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Maximum size: {self.max_image_size / (1024*1024):.1f}MB",
            )

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        title = self._extract_title_from_filename(file.filename)

        return ImageMetadata(
            image_id=image_id,
            original_name=file.filename,
            title=title,
            file_path=file_path,
            size=len(content),
            uploaded_at=datetime.now(),
        )

    async def save_multiple(self, files: List[UploadFile]) -> List[ImageMetadata]:
        """Save multiple images."""
        results = []
        for file in files:
            metadata = await self.save_image(file)
            results.append(metadata)
        return results

    def get_image_path(self, image_id: str) -> Optional[Path]:
        """Get the path to an uploaded image by ID."""
        for ext in self.allowed_extensions:
            path = self.images_dir / f"{image_id}{ext}"
            if path.exists():
                return path
        return None

    def get_image_url(self, image_id: str) -> Optional[str]:
        """Get the URL path for an image."""
        path = self.get_image_path(image_id)
        if path:
            return f"/uploads/images/{path.name}"
        return None

    def delete_image(self, image_id: str) -> bool:
        """Delete an uploaded image."""
        path = self.get_image_path(image_id)
        if path and path.exists():
            path.unlink()
            return True
        return False

    def list_images(self) -> List[ImageMetadata]:
        """List all uploaded images."""
        images = []
        for path in self.images_dir.iterdir():
            if path.suffix.lower() in self.allowed_extensions:
                image_id = path.stem
                stat = path.stat()
                title = self._extract_title_from_filename(path.name)
                images.append(
                    ImageMetadata(
                        image_id=image_id,
                        original_name=path.name,
                        title=title,
                        file_path=path,
                        size=stat.st_size,
                        uploaded_at=datetime.fromtimestamp(stat.st_mtime),
                    )
                )
        return sorted(images, key=lambda x: x.uploaded_at, reverse=True)

    def cleanup_old_images(self, max_age_hours: int = settings.file_max_age_hours) -> int:
        """Remove images older than specified age. Returns count of deleted files."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        deleted = 0

        for path in self.images_dir.iterdir():
            if path.suffix.lower() in self.allowed_extensions:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    path.unlink()
                    deleted += 1

        return deleted


# Singleton instance
image_manager = ImageManager()
