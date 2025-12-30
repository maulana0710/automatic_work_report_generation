import uuid
import json
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass
from fastapi import UploadFile, HTTPException

from app.config import settings


@dataclass
class FileMetadata:
    """Metadata for an uploaded file."""
    file_id: str
    original_name: str
    file_path: Path
    size: int
    uploaded_at: datetime


class FileManager:
    """Handles file upload, storage, and cleanup."""

    def __init__(
        self,
        upload_dir: Path = settings.upload_dir,
        max_file_size: int = settings.max_file_size,
        allowed_extensions: set = settings.allowed_extensions,
    ):
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Filename mapping for preserving original names
        self.mapping_file = self.upload_dir / "file_mapping.json"
        self.filename_mapping: Dict[str, str] = {}
        self._load_mapping()

    def _load_mapping(self):
        """Load filename mapping from JSON file."""
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.filename_mapping = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.filename_mapping = {}
        else:
            self.filename_mapping = {}

    def _save_mapping(self):
        """Save filename mapping to JSON file."""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.filename_mapping, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if can't write

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        ext = Path(file.filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}",
            )

    async def save_upload(self, file: UploadFile) -> FileMetadata:
        """Save an uploaded file with validation."""
        self._validate_file(file)

        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix.lower()
        new_filename = f"{file_id}{ext}"
        file_path = self.upload_dir / new_filename

        content = await file.read()

        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB",
            )

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Save original filename mapping
        self.filename_mapping[file_id] = file.filename
        self._save_mapping()

        return FileMetadata(
            file_id=file_id,
            original_name=file.filename,
            file_path=file_path,
            size=len(content),
            uploaded_at=datetime.now(),
        )

    async def save_multiple(self, files: List[UploadFile]) -> List[FileMetadata]:
        """Save multiple files."""
        results = []
        for file in files:
            metadata = await self.save_upload(file)
            results.append(metadata)
        return results

    def get_file_path(self, file_id: str) -> Optional[Path]:
        """Get the path to an uploaded file by ID."""
        for ext in self.allowed_extensions:
            path = self.upload_dir / f"{file_id}{ext}"
            if path.exists():
                return path
        return None

    def get_file_content(self, file_id: str) -> Optional[str]:
        """Read and return file content."""
        path = self.get_file_path(file_id)
        if path and path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def save_content(self, content: str, filename: str = "processed.md") -> FileMetadata:
        """Save string content as a new markdown file."""
        file_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower() or ".md"
        new_filename = f"{file_id}{ext}"
        file_path = self.upload_dir / new_filename

        file_path.write_text(content, encoding="utf-8")

        # Save original filename mapping
        self.filename_mapping[file_id] = filename
        self._save_mapping()

        return FileMetadata(
            file_id=file_id,
            original_name=filename,
            file_path=file_path,
            size=len(content.encode("utf-8")),
            uploaded_at=datetime.now(),
        )

    def delete_file(self, file_id: str) -> bool:
        """Delete an uploaded file."""
        path = self.get_file_path(file_id)
        if path and path.exists():
            path.unlink()

            # Remove from mapping
            if file_id in self.filename_mapping:
                del self.filename_mapping[file_id]
                self._save_mapping()

            return True
        return False

    def list_files(self) -> List[FileMetadata]:
        """List all uploaded files."""
        files = []
        for path in self.upload_dir.iterdir():
            if path.suffix.lower() in self.allowed_extensions:
                file_id = path.stem
                stat = path.stat()

                # Get original name from mapping, fallback to path.name
                original_name = self.filename_mapping.get(file_id, path.name)

                files.append(
                    FileMetadata(
                        file_id=file_id,
                        original_name=original_name,
                        file_path=path,
                        size=stat.st_size,
                        uploaded_at=datetime.fromtimestamp(stat.st_mtime),
                    )
                )
        return sorted(files, key=lambda x: x.uploaded_at, reverse=True)

    def cleanup_old_files(self, max_age_hours: int = settings.file_max_age_hours) -> int:
        """Remove files older than specified age. Returns count of deleted files."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        deleted = 0

        for path in self.upload_dir.iterdir():
            if path.suffix.lower() in self.allowed_extensions:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    path.unlink()
                    deleted += 1

        return deleted


# Singleton instance
file_manager = FileManager()
