"""AI processing routes using Google Gemini."""

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.core.file_manager import file_manager
from app.services.gemini_service import gemini_service
from app.api.schemas.ai import AIProcessRequest, AIProcessResponse, AIStatusResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AIStatusResponse)
async def ai_status():
    """Check if AI (Gemini) is configured and available."""
    return AIStatusResponse(
        configured=gemini_service.is_configured(),
        model=settings.gemini_model if gemini_service.is_configured() else None,
    )


@router.post("/process", response_model=AIProcessResponse)
async def process_with_ai(request: AIProcessRequest):
    """
    Process a git log file with Google Gemini AI.

    Takes the uploaded file, sends it to Gemini for processing,
    and saves the result as a new markdown file.
    """
    if not gemini_service.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Gemini API is not configured. Please add GEMINI_API_KEY to your .env file.",
        )

    # Check if file exists
    original_content = file_manager.get_file_content(request.file_id)
    if not original_content:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Process with Gemini
        processed_content = gemini_service.process_gitlog(request.file_id)

        # Save processed content as new file
        new_file = file_manager.save_content(
            content=processed_content,
            filename="Processed_Work_Report.md",
        )

        # Delete original file to prevent duplicate content
        file_manager.delete_file(request.file_id)

        return AIProcessResponse(
            processed_content=processed_content,
            original_file_id=request.file_id,
            new_file_id=new_file.file_id,
            new_filename=new_file.original_name,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}",
        )
