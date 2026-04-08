from pydantic import BaseModel
from typing import List, Optional

class AppInfoPayload(BaseModel):
    app_name: str
    package_name: str
    version_name: Optional[str] = None
    hash_sha256: Optional[str] = None
    is_system_app: bool = False

class ScanRequest(BaseModel):
    apps: List[AppInfoPayload]

class AppRiskResult(BaseModel):
    app_name: str
    package_name: str
    is_safe: bool
    is_malicious: bool
    risk_score: int
    risk_level: str
    flags: List[str]
    threat_details: dict

class ScanResponse(BaseModel):
    total_scanned: int
    safe_apps_count: int
    risky_apps_count: int
    overall_security_score: int
    risky_apps: List[AppRiskResult]
