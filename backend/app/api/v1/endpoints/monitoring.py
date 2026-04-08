from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ....models.database import get_db
from ....models.monitoring import APICall, NetworkTraffic, DeviceHealth, MonitoringAlert, APICategory
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas
class APICallResponse(BaseModel):
    id: int
    app_id: int
    api_name: str
    category: APICategory
    timestamp: datetime
    is_suspicious: bool
    risk_score: float
    parameters: dict
    
    class Config:
        from_attributes = True


class NetworkTrafficResponse(BaseModel):
    id: int
    app_id: int
    protocol: str
    destination_host: Optional[str]
    destination_port: Optional[int]
    method: Optional[str]
    timestamp: datetime
    is_suspicious: bool
    risk_score: float
    contains_pii: bool
    
    class Config:
        from_attributes = True


class DeviceHealthResponse(BaseModel):
    id: int
    device_id: str
    is_rooted: bool
    risk_score: float
    risk_factors: list
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MonitoringAlertResponse(BaseModel):
    id: int
    device_id: Optional[str]
    app_id: Optional[int]
    alert_type: str
    title: str
    severity: str
    risk_score: float
    timestamp: datetime
    acknowledged: bool
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_apps_monitored: int
    active_alerts: int
    api_calls_last_hour: int
    suspicious_api_calls: int
    network_connections: int
    suspicious_connections: int
    devices_monitored: int
    high_risk_devices: int


@router.get("/dashboard", response_model=DashboardStats)
async def get_monitoring_dashboard(db: Session = Depends(get_db)):
    """Get monitoring dashboard statistics."""
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    api_calls = db.query(APICall).filter(APICall.timestamp >= one_hour_ago).count()
    suspicious_apis = db.query(APICall).filter(
        APICall.timestamp >= one_hour_ago,
        APICall.is_suspicious == True
    ).count()
    
    network_conns = db.query(NetworkTraffic).filter(
        NetworkTraffic.timestamp >= one_hour_ago
    ).count()
    suspicious_conns = db.query(NetworkTraffic).filter(
        NetworkTraffic.timestamp >= one_hour_ago,
        NetworkTraffic.is_suspicious == True
    ).count()
    
    devices = db.query(DeviceHealth).distinct(DeviceHealth.device_id).count()
    high_risk = db.query(DeviceHealth).filter(
        DeviceHealth.risk_score >= 70
    ).distinct(DeviceHealth.device_id).count()
    
    active_alerts = db.query(MonitoringAlert).filter(
        MonitoringAlert.acknowledged == False
    ).count()
    
    unique_apps = db.query(APICall).distinct(APICall.app_id).count()
    
    return DashboardStats(
        total_apps_monitored=unique_apps,
        active_alerts=active_alerts,
        api_calls_last_hour=api_calls,
        suspicious_api_calls=suspicious_apis,
        network_connections=network_conns,
        suspicious_connections=suspicious_conns,
        devices_monitored=devices,
        high_risk_devices=high_risk
    )


@router.get("/api-calls")
async def get_api_calls(
    app_id: Optional[int] = None,
    device_id: Optional[str] = None,
    category: Optional[APICategory] = None,
    suspicious_only: bool = False,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get API call logs with filtering."""
    query = db.query(APICall)
    
    if app_id:
        query = query.filter(APICall.app_id == app_id)
    if device_id:
        query = query.filter(APICall.device_id == device_id)
    if category:
        query = query.filter(APICall.category == category)
    if suspicious_only:
        query = query.filter(APICall.is_suspicious == True)
    if start_time:
        query = query.filter(APICall.timestamp >= start_time)
    if end_time:
        query = query.filter(APICall.timestamp <= end_time)
    
    total = query.count()
    items = query.order_by(APICall.timestamp.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [APICallResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/api-calls/stats")
async def get_api_call_stats(
    app_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get API call statistics."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(APICall).filter(APICall.timestamp >= start_time)
    if app_id:
        query = query.filter(APICall.app_id == app_id)
    
    calls = query.all()
    
    # Aggregate by category
    by_category = {}
    for call in calls:
        cat = call.category.value
        if cat not in by_category:
            by_category[cat] = {"total": 0, "suspicious": 0}
        by_category[cat]["total"] += 1
        if call.is_suspicious:
            by_category[cat]["suspicious"] += 1
    
    # Top APIs
    api_counts = {}
    for call in calls:
        if call.api_name not in api_counts:
            api_counts[call.api_name] = 0
        api_counts[call.api_name] += 1
    
    top_apis = sorted(api_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        "total_calls": len(calls),
        "suspicious_calls": sum(1 for c in calls if c.is_suspicious),
        "by_category": by_category,
        "top_apis": [{"api": api, "count": count} for api, count in top_apis],
        "hours": hours
    }


@router.get("/network-traffic")
async def get_network_traffic(
    app_id: Optional[int] = None,
    device_id: Optional[str] = None,
    suspicious_only: bool = False,
    pii_only: bool = False,
    protocol: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get network traffic logs with filtering."""
    query = db.query(NetworkTraffic)
    
    if app_id:
        query = query.filter(NetworkTraffic.app_id == app_id)
    if suspicious_only:
        query = query.filter(NetworkTraffic.is_suspicious == True)
    if pii_only:
        query = query.filter(NetworkTraffic.contains_pii == True)
    if protocol:
        query = query.filter(NetworkTraffic.protocol == protocol)
    
    total = query.count()
    items = query.order_by(NetworkTraffic.timestamp.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [NetworkTrafficResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/network-traffic/analysis")
async def get_network_analysis(
    app_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get network traffic analysis."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(NetworkTraffic).filter(NetworkTraffic.timestamp >= start_time)
    if app_id:
        query = query.filter(NetworkTraffic.app_id == app_id)
    
    traffic = query.all()
    
    # Aggregate stats
    by_protocol = {}
    by_host = {}
    by_country = {}
    total_bytes = 0
    
    for t in traffic:
        # By protocol
        proto = t.protocol.value if t.protocol else "unknown"
        if proto not in by_protocol:
            by_protocol[proto] = {"count": 0, "bytes": 0}
        by_protocol[proto]["count"] += 1
        by_protocol[proto]["bytes"] += (t.request_size or 0) + (t.response_size or 0)
        
        # By host
        if t.destination_host:
            if t.destination_host not in by_host:
                by_host[t.destination_host] = 0
            by_host[t.destination_host] += 1
        
        # By country
        if t.destination_country:
            if t.destination_country not in by_country:
                by_country[t.destination_country] = 0
            by_country[t.destination_country] += 1
        
        total_bytes += (t.request_size or 0) + (t.response_size or 0)
    
    return {
        "total_requests": len(traffic),
        "total_bytes": total_bytes,
        "suspicious_count": sum(1 for t in traffic if t.is_suspicious),
        "pii_count": sum(1 for t in traffic if t.contains_pii),
        "by_protocol": by_protocol,
        "top_hosts": dict(sorted(by_host.items(), key=lambda x: x[1], reverse=True)[:20]),
        "by_country": by_country,
        "hours": hours
    }


@router.get("/device-health")
async def get_device_health(
    device_id: Optional[str] = None,
    high_risk_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get device health status."""
    query = db.query(DeviceHealth)
    
    if device_id:
        query = query.filter(DeviceHealth.device_id == device_id)
    if high_risk_only:
        query = query.filter(DeviceHealth.risk_score >= 70)
    
    total = query.count()
    items = query.order_by(DeviceHealth.timestamp.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [DeviceHealthResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/alerts")
async def get_alerts(
    device_id: Optional[str] = None,
    app_id: Optional[int] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get monitoring alerts."""
    query = db.query(MonitoringAlert)
    
    if device_id:
        query = query.filter(MonitoringAlert.device_id == device_id)
    if app_id:
        query = query.filter(MonitoringAlert.app_id == app_id)
    if severity:
        query = query.filter(MonitoringAlert.severity == severity)
    if acknowledged is not None:
        query = query.filter(MonitoringAlert.acknowledged == acknowledged)
    
    total = query.count()
    items = query.order_by(MonitoringAlert.timestamp.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [MonitoringAlertResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge a monitoring alert."""
    alert = db.query(MonitoringAlert).filter(MonitoringAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert acknowledged"}
