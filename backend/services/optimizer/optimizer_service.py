import logging
from typing import Optional
from models.schemas_boost import BoostRequest, BoostResponse
from services.supabase_client import supabase_manager

class OptimizerService:
    @staticmethod
    def calculate_boost(request: BoostRequest) -> BoostResponse:
        logging.info("Calculating optimal boost configurations...")
        
        # 1. Deterministic Calculation Logic
        memory_before_mb = request.estimated_ram_usage_mb
        
        # The higher the background apps and storage pressure, the more we can "simulate" freeing up memory.
        # But we must never exceed the bounds.
        freed_per_app = 15 # Let's assume each app killed frees ~15MB
        storage_factor = (request.storage_pressure_percent or 50.0) / 100.0
        
        # Apps optimized
        # We can optimize 60% of background apps safely
        apps_optimized = int(request.background_apps_count * 0.6)
        
        # Memory freed
        memory_freed = int((apps_optimized * freed_per_app) + (storage_factor * 100))
        
        # Memory after
        memory_after_mb = max(memory_before_mb - memory_freed, 0)
        actual_memory_freed = memory_before_mb - memory_after_mb
        
        # Performance Score:
        # Base score starts by how much % of RAM is free after cleaning
        free_ram_percent = ((request.total_ram_mb - memory_after_mb) / max(request.total_ram_mb, 1)) * 100
        
        # Penalty for remaining background apps, CPU usage
        remaining_apps = request.background_apps_count - apps_optimized
        app_penalty = remaining_apps * 0.5
        cpu_penalty = (request.cpu_usage_percent or 20.0) * 0.2
        
        performance_score = int(free_ram_percent - app_penalty - cpu_penalty)
        # Bounded between 40 and 100 so it feels realistic
        performance_score = max(40, min(100, performance_score))
        
        # 2. Log to Supabase
        supabase_manager.log_boost_session(
            user_id=request.user_id,
            memory_before=memory_before_mb,
            memory_after=memory_after_mb,
            apps_optimized=apps_optimized,
            performance_score=performance_score
        )
        
        return BoostResponse(
            memory_before_mb=memory_before_mb,
            memory_after_mb=memory_after_mb,
            apps_optimized=apps_optimized,
            performance_score=performance_score,
            message="Optimization analysis complete"
        )
