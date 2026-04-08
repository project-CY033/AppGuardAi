from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import asyncio

from ....models.database import get_db
from ....models.scan import ScanJob, ScanResult, ScanStatus, ScanType, ThreatLevel
from ....models.app import App
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic schemas
class ScanRequest(BaseModel):
    app_id: int
    scan_type: ScanType = ScanType.FULL
    priority: int = 5
    enabled_analyzers: Optional[List[str]] = None


class ScanResponse(BaseModel):
    id: str
    app_id: int
    scan_type: ScanType
    status: ScanStatus
    progress: float
    threat_level: Optional[ThreatLevel]
    risk_score: Optional[float]
    findings_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    
    class Config:
        from_attributes = True


class ScanResultResponse(BaseModel):
    id: int
    category: str
    subcategory: Optional[str]
    title: str
    description: Optional[str]
    severity: ThreatLevel
    confidence: float
    detection_method: str
    remediation: Optional[str]
    
    class Config:
        from_attributes = True


class ScanStatusResponse(BaseModel):
    scan: ScanResponse
    results: List[ScanResultResponse]
    summary: dict


class ScanQueueResponse(BaseModel):
    items: List[ScanResponse]
    total: int
    running: int
    queued: int


@router.post("/start", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new scan for an application."""
    # Verify app exists
    app = db.query(App).filter(App.id == request.app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Create scan job
    scan_job = ScanJob(
        id=str(uuid.uuid4()),
        app_id=request.app_id,
        scan_type=request.scan_type,
        status=ScanStatus.QUEUED,
        priority=request.priority,
        enabled_analyzers=request.enabled_analyzers or [],
        queued_at=datetime.utcnow()
    )
    db.add(scan_job)
    db.commit()
    db.refresh(scan_job)
    
    # Start scan in background
    from ....core.tasks import run_scan_task
    asyncio.create_task(run_scan_task(scan_job.id))
    
    return ScanResponse.from_orm(scan_job)


@router.get("/status/{scan_id}", response_model=ScanStatusResponse)
async def get_scan_status(scan_id: str, db: Session = Depends(get_db)):
    """Get the current status of a scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    results = db.query(ScanResult).filter(
        ScanResult.scan_job_id == scan_id
    ).all()
    
    # Generate summary
    summary = {
        "critical": sum(1 for r in results if r.severity == ThreatLevel.CRITICAL),
        "high": sum(1 for r in results if r.severity == ThreatLevel.HIGH),
        "medium": sum(1 for r in results if r.severity == ThreatLevel.MEDIUM),
        "low": sum(1 for r in results if r.severity == ThreatLevel.LOW),
        "categories": {}
    }
    
    for result in results:
        if result.category not in summary["categories"]:
            summary["categories"][result.category] = 0
        summary["categories"][result.category] += 1
    
    return ScanStatusResponse(
        scan=ScanResponse.from_orm(scan),
        results=[ScanResultResponse.from_orm(r) for r in results],
        summary=summary
    )


@router.get("/results/{scan_id}")
async def get_scan_results(
    scan_id: str,
    severity: Optional[ThreatLevel] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get detailed results of a scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    query = db.query(ScanResult).filter(ScanResult.scan_job_id == scan_id)
    
    if severity:
        query = query.filter(ScanResult.severity == severity)
    if category:
        query = query.filter(ScanResult.category == category)
    
    results = query.order_by(ScanResult.severity.desc()).all()
    
    return {
        "scan_id": scan_id,
        "total_results": len(results),
        "results": [
            {
                "id": r.id,
                "category": r.category,
                "subcategory": r.subcategory,
                "title": r.title,
                "description": r.description,
                "severity": r.severity,
                "confidence": r.confidence,
                "detection_method": r.detection_method,
                "file_path": r.file_path,
                "line_number": r.line_number,
                "evidence": r.evidence,
                "remediation": r.remediation,
                "references": r.references,
                "cve_ids": r.cve_ids,
                "feature_importance": r.feature_importance
            }
            for r in results
        ]
    }


@router.get("/queue", response_model=ScanQueueResponse)
async def get_scan_queue(db: Session = Depends(get_db)):
    """Get the current scan queue status."""
    running = db.query(ScanJob).filter(
        ScanJob.status == ScanStatus.RUNNING
    ).count()
    
    queued = db.query(ScanJob).filter(
        ScanJob.status == ScanStatus.QUEUED
    ).count()
    
    recent = db.query(ScanJob).order_by(
        ScanJob.created_at.desc()
    ).limit(50).all()
    
    return ScanQueueResponse(
        items=[ScanResponse.from_orm(s) for s in recent],
        total=len(recent),
        running=running,
        queued=queued
    )


@router.post("/{scan_id}/cancel")
async def cancel_scan(scan_id: str, db: Session = Depends(get_db)):
    """Cancel a running or queued scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Scan already {scan.status}")
    
    scan.status = ScanStatus.CANCELLED
    scan.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Scan cancelled successfully"}


@router.post("/quick/{app_id}")
async def quick_scan(
    app_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run a quick scan (permission check + signature verification)."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    scan_job = ScanJob(
        id=str(uuid.uuid4()),
        app_id=app_id,
        scan_type=ScanType.QUICK,
        status=ScanStatus.QUEUED,
        priority=1,
        enabled_analyzers=["permission", "signature", "hash"]
    )
    db.add(scan_job)
    db.commit()
    
    from ....core.tasks import run_scan_task
    asyncio.create_task(run_scan_task(scan_job.id))
    
    return {"scan_id": scan_job.id, "status": "queued"}


@router.post("/clone-check/{app_id}")
async def clone_check(
    app_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run clone detection analysis."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    scan_job = ScanJob(
        id=str(uuid.uuid4()),
        app_id=app_id,
        scan_type=ScanType.CLONE,
        status=ScanStatus.QUEUED,
        priority=2,
        enabled_analyzers=["clone", "icon", "code_similarity"]
    )
    db.add(scan_job)
    db.commit()
    
    from ....core.tasks import run_scan_task
    asyncio.create_task(run_scan_task(scan_job.id))
    
    return {"scan_id": scan_job.id, "status": "queued"}


@router.post("/advanced/{app_id}")
async def advanced_scan(
    app_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run comprehensive advanced security scan.
    
    Includes:
    - OWASP MASVS compliance checking
    - Static Application Security Testing (SAST)
    - Software Composition Analysis (SCA)
    - Secret/credential detection
    - Malware pattern detection
    - Certificate analysis
    """
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    scan_job = ScanJob(
        id=str(uuid.uuid4()),
        app_id=app_id,
        scan_type=ScanType.FULL,
        status=ScanStatus.QUEUED,
        priority=1,
        enabled_analyzers=[
            "owasp_masvs",
            "sast", 
            "sca",
            "secrets",
            "malware",
            "certificate",
            "permissions",
            "network",
            "crypto",
        ]
    )
    db.add(scan_job)
    db.commit()
    
    from ....core.tasks import run_scan_task
    asyncio.create_task(run_scan_task(scan_job.id))
    
    return {
        "scan_id": scan_job.id,
        "status": "queued",
        "analyzers": scan_job.enabled_analyzers,
        "message": "Advanced security scan started with OWASP MASVS, SAST, SCA, and malware detection"
    }


@router.get("/compliance/{scan_id}")
async def get_compliance_report(
    scan_id: str,
    db: Session = Depends(get_db)
):
    """Get OWASP MASVS compliance report for a scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    results = db.query(ScanResult).filter(
        ScanResult.scan_job_id == scan_id
    ).all()
    
    # Filter for OWASP findings
    masvs_controls = {}
    for result in results:
        if hasattr(result, 'references') and result.references:
            if 'OWASP' in str(result.references):
                masvs_controls[result.title] = {
                    "status": "FAIL",
                    "severity": result.severity,
                    "description": result.description,
                    "remediation": result.remediation,
                }
    
    passed = 21 - len(masvs_controls)  # Total MASVS controls
    
    return {
        "scan_id": scan_id,
        "compliance_score": f"{passed}/21",
        "compliance_percentage": round((passed / 21) * 100, 1),
        "failed_controls": masvs_controls,
        "summary": "Good" if passed >= 17 else "Fair" if passed >= 14 else "Poor"
    }


@router.get("/secrets/{scan_id}")
async def get_secrets_report(
    scan_id: str,
    db: Session = Depends(get_db)
):
    """Get secret detection report for a scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    results = db.query(ScanResult).filter(
        ScanResult.scan_job_id == scan_id,
        ScanResult.category == "secrets"
    ).all()
    
    return {
        "scan_id": scan_id,
        "total_secrets": len(results),
        "secrets": [
            {
                "title": r.title,
                "description": r.description,
                "severity": r.severity,
                "file_path": r.file_path,
                "line_number": r.line_number,
                "remediation": r.remediation,
            }
            for r in results
        ]
    }


@router.get("/malware-indicators/{scan_id}")
async def get_malware_indicators(
    scan_id: str,
    db: Session = Depends(get_db)
):
    """Get malware detection indicators for a scan."""
    scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    results = db.query(ScanResult).filter(
        ScanResult.scan_job_id == scan_id,
        ScanResult.category == "malware"
    ).all()
    
    return {
        "scan_id": scan_id,
        "total_indicators": len(results),
        "is_suspicious": len(results) > 3,
        "indicators": [
            {
                "title": r.title,
                "description": r.description,
                "severity": r.severity,
                "detection_method": r.detection_method,
            }
            for r in results
        ]
    }
