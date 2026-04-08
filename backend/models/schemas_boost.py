from pydantic import BaseModel
from typing import Optional

class BoostRequest(BaseModel):
    user_id: Optional[str] = None
    estimated_ram_usage_mb: int
    total_ram_mb: int
    background_apps_count: int
    storage_pressure_percent: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

class BoostResponse(BaseModel):
    memory_before_mb: int
    memory_after_mb: int
    apps_optimized: int
    performance_score: int
    message: str
