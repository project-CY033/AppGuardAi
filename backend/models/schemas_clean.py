from pydantic import BaseModel
from typing import List, Optional

class CleanItem(BaseModel):
    id: str
    category: str
    description: str
    size_bytes: int
    is_safe_to_clean: bool

class CleanRequest(BaseModel):
    total_space_bytes: int
    used_space_bytes: int
    installed_apps_count: int

class CleanResponse(BaseModel):
    total_cleanable_bytes: int
    categories: List[CleanItem]
    storage_health_score: int
