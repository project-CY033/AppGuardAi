from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ....models.database import get_db
from ....models.incident import Incident, IncidentTimeline, Playbook, SLAPolicy, IncidentStatus, IncidentSeverity, IncidentCategory
from pydantic import BaseModel

router = APIRouter()


class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    risk_score: float
    app_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncidentDetailResponse(IncidentResponse):
    description: Optional[str]
    threat_type: Optional[str]
    malware_family: Optional[str]
    iocs: list
    mitre_techniques: list
    evidence: dict
    assigned_to: Optional[str]
    resolution_summary: Optional[str]
    
    class Config:
        from_attributes = True


class IncidentStats(BaseModel):
    total: int
    open: int
    in_progress: int
    closed: int
    by_severity: dict
    by_category: dict
    avg_resolution_time: Optional[float]
    sla_breached: int


@router.get("/stats", response_model=IncidentStats)
async def get_incident_stats(db: Session = Depends(get_db)):
    """Get incident statistics."""
    total = db.query(Incident).count()
    open_count = db.query(Incident).filter(Incident.status == IncidentStatus.NEW).count()
    in_progress = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.INVESTIGATING, IncidentStatus.CONFIRMED])
    ).count()
    closed = db.query(Incident).filter(Incident.status == IncidentStatus.CLOSED).count()
    
    # By severity
    by_severity = {}
    for sev in IncidentSeverity:
        count = db.query(Incident).filter(Incident.severity == sev).count()
        by_severity[sev.value] = count
    
    # By category
    by_category = {}
    incidents = db.query(Incident).all()
    for inc in incidents:
        cat = inc.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    
    # Avg resolution time
    resolved = db.query(Incident).filter(
        Incident.resolution_time_minutes.isnot(None)
    ).all()
    avg_time = None
    if resolved:
        avg_time = sum(i.resolution_time_minutes for i in resolved) / len(resolved)
    
    sla_breached = db.query(Incident).filter(Incident.sla_breached == True).count()
    
    return IncidentStats(
        total=total,
        open=open_count,
        in_progress=in_progress,
        closed=closed,
        by_severity=by_severity,
        by_category=by_category,
        avg_resolution_time=avg_time,
        sla_breached=sla_breached
    )


@router.get("/")
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    category: Optional[IncidentCategory] = None,
    assigned_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List incidents with filtering."""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if category:
        query = query.filter(Incident.category == category)
    if assigned_to:
        query = query.filter(Incident.assigned_to == assigned_to)
    
    total = query.count()
    items = query.order_by(Incident.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [IncidentResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get incident details."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentDetailResponse.from_orm(incident)


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    """Get incident timeline."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    timeline = db.query(IncidentTimeline).filter(
        IncidentTimeline.incident_id == incident.id
    ).order_by(IncidentTimeline.created_at.asc()).all()
    
    return [
        {
            "id": t.id,
            "event_type": t.event_type,
            "title": t.title,
            "description": t.description,
            "actor_type": t.actor_type,
            "actor_name": t.actor_name,
            "event_data": t.event_data,
            "created_at": t.created_at
        }
        for t in timeline
    ]


@router.post("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    new_status: IncidentStatus,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update incident status."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    old_status = incident.status
    incident.status = new_status
    
    # Add timeline event
    timeline_event = IncidentTimeline(
        incident_id=incident.id,
        event_type="status_change",
        title=f"Status changed from {old_status} to {new_status}",
        description=notes,
        previous_value=old_status.value,
        new_value=new_status.value
    )
    db.add(timeline_event)
    
    if new_status == IncidentStatus.CLOSED:
        incident.closed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Incident status updated", "new_status": new_status}


@router.post("/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    assigned_to: str,
    db: Session = Depends(get_db)
):
    """Assign incident to analyst."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.assigned_to = assigned_to
    
    timeline_event = IncidentTimeline(
        incident_id=incident.id,
        event_type="assignment",
        title=f"Assigned to {assigned_to}",
        actor_type="user"
    )
    db.add(timeline_event)
    db.commit()
    
    return {"message": "Incident assigned", "assigned_to": assigned_to}


@router.post("/{incident_id}/comment")
async def add_incident_comment(
    incident_id: str,
    comment: str,
    db: Session = Depends(get_db)
):
    """Add comment to incident."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    timeline_event = IncidentTimeline(
        incident_id=incident.id,
        event_type="comment",
        title="Comment added",
        description=comment
    )
    db.add(timeline_event)
    db.commit()
    
    return {"message": "Comment added"}


@router.get("/playbooks/list")
async def list_playbooks(active_only: bool = True, db: Session = Depends(get_db)):
    """List available playbooks."""
    query = db.query(Playbook)
    if active_only:
        query = query.filter(Playbook.is_active == True)
    
    playbooks = query.all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "trigger_category": p.trigger_category,
            "trigger_severity": p.trigger_severity,
            "automated_steps": p.automated_steps,
            "execution_count": p.execution_count,
            "success_rate": p.success_rate
        }
        for p in playbooks
    ]


@router.get("/sla/policies")
async def get_sla_policies(db: Session = Depends(get_db)):
    """Get SLA policies."""
    policies = db.query(SLAPolicy).filter(SLAPolicy.is_active == True).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "severity": p.severity,
            "category": p.category,
            "response_time": p.response_time,
            "resolution_time": p.resolution_time
        }
        for p in policies
    ]
