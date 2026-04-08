import logging
from fastapi import APIRouter, HTTPException
from models.schemas_boost import BoostRequest, BoostResponse
from services.optimizer.optimizer_service import OptimizerService

router = APIRouter()

@router.post("", response_model=BoostResponse)
async def boost_device(request: BoostRequest):
    """
    Calculates optimal device boost settings deterministically
    and logs the session to Supabase.
    """
    try:
        logging.info(f"Boost request received for {request.background_apps_count} background apps.")
        response = OptimizerService.calculate_boost(request)
        return response
    except Exception as e:
        logging.error(f"Error executing boost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
