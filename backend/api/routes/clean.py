import logging
from fastapi import APIRouter, HTTPException
from models.schemas_clean import CleanRequest, CleanResponse
from services.clean.clean_service import CleanService

router = APIRouter()

@router.post("/analyze", response_model=CleanResponse)
async def analyze_storage(request: CleanRequest):
    """
    Simulates deep storage analysis and heuristic breakdown.
    """
    try:
        logging.info(f"Analyzing storage for {request.installed_apps_count} installed apps...")
        response = CleanService.analyze_storage(request)
        return response
    except Exception as e:
        logging.error(f"Error analyzing storage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
