from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.file_manager import file_manager
from app.core.image_manager import image_manager
from app.api.routes import upload, templates, reports, preview, images, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name}...")
    yield
    # Shutdown
    print("Cleaning up old files...")
    deleted_files = file_manager.cleanup_old_files()
    deleted_images = image_manager.cleanup_old_images()
    print(f"Deleted {deleted_files} old file(s) and {deleted_images} old image(s)")


app = FastAPI(
    title=settings.app_name,
    description="Generate PDF reports from Markdown files",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.mount("/uploads/images", StaticFiles(directory=settings.images_dir), name="images")

# Include API routers
app.include_router(upload.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(preview.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse(settings.base_dir / "frontend" / "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
