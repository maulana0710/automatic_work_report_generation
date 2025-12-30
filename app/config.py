from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Weekly Report Generator"
    debug: bool = False

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    images_dir: Path = base_dir / "uploads" / "images"
    output_dir: Path = base_dir / "output"
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"

    # File upload - Markdown
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".md", ".markdown"}

    # File upload - Images
    max_image_size: int = 5 * 1024 * 1024  # 5MB per image
    allowed_image_extensions: set = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

    # Cleanup
    file_max_age_hours: int = 24

    # Google Gemini AI
    gemini_api_key: str = "AIzaSyBlQ9isVooNQ9edxlofnYVvpl29pbT8bKw"
    gemini_model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure directories exist
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.images_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
