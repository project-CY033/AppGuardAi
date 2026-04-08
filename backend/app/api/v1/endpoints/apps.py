from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import hashlib
import os

from ....models.database import get_db
from ....models.app import App, AppVersion, AppCategory, AppPlatform, AppTrustLevel
from ....models.scan import ScanJob, ScanType, ScanStatus
from ....config import settings
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic schemas
class AppResponse(BaseModel):
    id: int
    package_name: str
    app_name: str
    version_name: Optional[str]
    platform: AppPlatform
    category: AppCategory
    trust_level: AppTrustLevel
    overall_risk_score: float
    is_clone: bool
    is_phishing: bool
    is_malware: bool
    developer_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppDetailResponse(AppResponse):
    description: Optional[str]
    store_url: Optional[str]
    icon_url: Optional[str]
    min_sdk_version: Optional[int]
    target_sdk_version: Optional[int]
    has_hidden_permissions: bool
    has_dynamic_code_loading: bool
    has_native_code: bool
    certificate_fingerprint: Optional[str]
    
    class Config:
        from_attributes = True


class AppListResponse(BaseModel):
    items: List[AppResponse]
    total: int
    page: int
    page_size: int


class AppUploadResponse(BaseModel):
    app_id: int
    scan_job_id: str
    message: str


class AppFilter(BaseModel):
    platform: Optional[AppPlatform] = None
    category: Optional[AppCategory] = None
    trust_level: Optional[AppTrustLevel] = None
    search: Optional[str] = None
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    is_malware: Optional[bool] = None
    is_clone: Optional[bool] = None
    is_phishing: Optional[bool] = None


@router.get("/", response_model=AppListResponse)
async def list_apps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[AppPlatform] = None,
    category: Optional[AppCategory] = None,
    trust_level: Optional[AppTrustLevel] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all applications with filtering and pagination."""
    query = db.query(App)
    
    if platform:
        query = query.filter(App.platform == platform)
    if category:
        query = query.filter(App.category == category)
    if trust_level:
        query = query.filter(App.trust_level == trust_level)
    if search:
        query = query.filter(
            (App.app_name.ilike(f"%{search}%")) | 
            (App.package_name.ilike(f"%{search}%"))
        )
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return AppListResponse(
        items=[AppResponse.from_orm(app) for app in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{app_id}", response_model=AppDetailResponse)
async def get_app(app_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific application."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return AppDetailResponse.from_orm(app)


@router.post("/upload", response_model=AppUploadResponse)
async def upload_app(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Upload an app/APK for analysis."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"File type {ext} not allowed")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Read file content
        logger.info(f"Reading file: {file.filename}")
        content = await file.read()
        file_size = len(content)
        logger.info(f"File size: {file_size} bytes, limit: {settings.MAX_UPLOAD_SIZE} bytes")
        
        # Check file size with a much larger limit (500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if file_size > max_size:
            raise HTTPException(400, f"File too large. Maximum size is 500MB, got {file_size / (1024*1024):.1f}MB")
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved to: {filepath}")
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Create app record
        app = App(
            package_name=f"pending_{file_id}",
            app_name=file.filename,
            platform=AppPlatform.ANDROID if ext in [".apk", ".xapk", ".aab"] else AppPlatform.WINDOWS,
            app_size=file_size
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        
        # Create scan job
        scan_job = ScanJob(
            id=str(uuid.uuid4()),
            app_id=app.id,
            scan_type=ScanType.FULL,
            status=ScanStatus.QUEUED,
            config={"filepath": filepath, "file_hash": file_hash}
        )
        db.add(scan_job)
        db.commit()
        
        logger.info(f"Created app {app.id} and scan job {scan_job.id}")
        
        # Trigger async scan using background tasks
        from ....core.tasks import run_scan_task
        background_tasks.add_task(run_scan_task, scan_job.id)
        
        return AppUploadResponse(
            app_id=app.id,
            scan_job_id=scan_job.id,
            message="App uploaded successfully. Scan queued."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.get("/{app_id}/permissions")
async def get_app_permissions(app_id: int, db: Session = Depends(get_db)):
    """Get detailed permission analysis for an app."""
    from ....models.scan import PermissionAnalysis
    
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    perm = db.query(PermissionAnalysis).filter(
        PermissionAnalysis.app_id == app_id
    ).order_by(PermissionAnalysis.created_at.desc()).first()
    
    if not perm:
        raise HTTPException(status_code=404, detail="No permission analysis found")
    
    return {
        "app_id": app_id,
        "declared_permissions": perm.declared_permissions,
        "requested_permissions": perm.requested_permissions,
        "hidden_permissions": perm.hidden_permissions,
        "dangerous_permissions": perm.dangerous_permissions,
        "permission_risk_score": perm.permission_risk_score,
        "permission_anomalies": perm.permission_anomalies,
        "excess_permissions": perm.excess_permissions,
        "permission_z_scores": perm.permission_z_scores
    }


@router.get("/{app_id}/scans")
async def get_app_scans(app_id: int, db: Session = Depends(get_db)):
    """Get scan history for an app."""
    scans = db.query(ScanJob).filter(
        ScanJob.app_id == app_id
    ).order_by(ScanJob.created_at.desc()).all()
    
    return [
        {
            "id": s.id,
            "scan_type": s.scan_type,
            "status": s.status,
            "threat_level": s.threat_level,
            "risk_score": s.risk_score,
            "created_at": s.created_at,
            "completed_at": s.completed_at
        }
        for s in scans
    ]


@router.get("/{app_id}/similar")
async def get_similar_apps(
    app_id: int,
    threshold: float = Query(0.7, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Find similar apps (clone detection results)."""
    from ....models.scan import CloneDetection
    
    clones = db.query(CloneDetection).filter(
        (CloneDetection.app_id == app_id) | (CloneDetection.original_app_id == app_id),
        CloneDetection.overall_similarity >= threshold
    ).all()
    
    results = []
    for clone in clones:
        other_id = clone.original_app_id if clone.app_id == app_id else clone.app_id
        other_app = db.query(App).filter(App.id == other_id).first()
        if other_app:
            results.append({
                "app": AppResponse.from_orm(other_app),
                "similarity": clone.overall_similarity,
                "code_similarity": clone.code_similarity,
                "icon_similarity": clone.icon_similarity,
                "clone_type": clone.clone_type,
                "confidence": clone.confidence
            })
    
    return results


@router.delete("/{app_id}")
async def delete_app(app_id: int, db: Session = Depends(get_db)):
    """Delete an app and all related data."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db.delete(app)
    db.commit()
    
    return {"message": "App deleted successfully"}
