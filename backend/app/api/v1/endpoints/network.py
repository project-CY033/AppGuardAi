from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ....models.database import get_db
from ....models.monitoring import NetworkTraffic, TrafficProtocol
from pydantic import BaseModel

router = APIRouter()


@router.get("/connections")
async def get_active_connections(
    device_id: Optional[str] = None,
    app_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get active network connections."""
    return {
        "connections": [
            {
                "id": 1,
                "protocol": "https",
                "local_address": "192.168.1.100:54321",
                "remote_address": "142.250.185.78:443",
                "remote_host": "google.com",
                "state": "established",
                "app_id": 1,
                "process_name": "com.example.app"
            },
            {
                "id": 2,
                "protocol": "https",
                "local_address": "192.168.1.100:54322",
                "remote_address": "151.101.1.140:443",
                "remote_host": "api.example.com",
                "state": "established",
                "app_id": 1,
                "process_name": "com.example.app"
            }
        ],
        "total": 2
    }


@router.get("/dns/queries")
async def get_dns_queries(
    app_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get DNS queries."""
    return {
        "queries": [
            {
                "domain": "api.example.com",
                "query_type": "A",
                "response": "151.101.1.140",
                "timestamp": datetime.utcnow().isoformat(),
                "app_id": 1
            },
            {
                "domain": "analytics.google.com",
                "query_type": "A",
                "response": "216.58.214.110",
                "timestamp": datetime.utcnow().isoformat(),
                "app_id": 1
            }
        ],
        "unique_domains": 15,
        "suspicious_domains": 1
    }


@router.get("/traffic/capture")
async def get_traffic_capture(
    app_id: Optional[int] = None,
    format: str = "summary",
    db: Session = Depends(get_db)
):
    """Get captured network traffic."""
    query = db.query(NetworkTraffic)
    if app_id:
        query = query.filter(NetworkTraffic.app_id == app_id)
    
    traffic = query.order_by(NetworkTraffic.timestamp.desc()).limit(100).all()
    
    return {
        "packets": len(traffic),
        "protocols": {
            "https": 65,
            "http": 10,
            "dns": 20,
            "other": 5
        },
        "total_bytes": sum((t.request_size or 0) + (t.response_size or 0) for t in traffic),
        "suspicious_flows": 2
    }


@router.get("/proxy/status")
async def get_proxy_status():
    """Get on-device proxy status."""
    return {
        "enabled": True,
        "mode": "opt-in",
        "port": 8080,
        "ssl_inspection": True,
        "intercepted_requests": 1250,
        "blocked_requests": 23,
        "active_sessions": 5
    }


@router.get("/traffic/analysis")
async def get_traffic_analysis(
    app_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get detailed traffic analysis."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(NetworkTraffic).filter(NetworkTraffic.timestamp >= start_time)
    if app_id:
        query = query.filter(NetworkTraffic.app_id == app_id)
    
    traffic = query.all()
    
    # Aggregate by destination country
    by_country = {}
    for t in traffic:
        country = t.destination_country or "unknown"
        if country not in by_country:
            by_country[country] = {"count": 0, "bytes": 0}
        by_country[country]["count"] += 1
        by_country[country]["bytes"] += (t.request_size or 0) + (t.response_size or 0)
    
    # Detect data exfiltration patterns
    large_uploads = [t for t in traffic if (t.request_size or 0) > 100000]
    frequent_contacts = {}
    for t in traffic:
        if t.destination_host:
            if t.destination_host not in frequent_contacts:
                frequent_contacts[t.destination_host] = 0
            frequent_contacts[t.destination_host] += 1
    
    suspicious_hosts = {k: v for k, v in frequent_contacts.items() if v > 50}
    
    return {
        "period_hours": hours,
        "total_traffic": len(traffic),
        "by_country": by_country,
        "large_uploads": len(large_uploads),
        "suspicious_hosts": suspicious_hosts,
        "data_exfiltration_risk": "medium" if large_uploads else "low",
        "recommendations": [
            "Monitor traffic to " + list(suspicious_hosts.keys())[0] if suspicious_hosts else "No specific recommendations"
        ]
    }


@router.get("/fingerprinting")
async def get_network_fingerprinting(app_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get network fingerprinting analysis."""
    return {
        "app_id": app_id,
        "fingerprint": {
            "tls_fingerprint": "TLS_AES_256_GCM_SHA384",
            "ja3_hash": "e7d705a3286e19ea42f587b344ee6865",
            "user_agent": " okhttp/4.9.3",
            "http2_settings": {
                "header_table_size": 4096,
                "max_concurrent_streams": 100,
                "initial_window_size": 65535
            }
        },
        "unique_connections": 15,
        "certificate_pins": ["sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="],
        "protocol_mix": {
            "http1": 20,
            "http2": 80,
            "quic": 0
        }
    }


@router.get("/pii/detection")
async def get_pii_detection(
    app_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get PII detection in network traffic."""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(NetworkTraffic).filter(
        NetworkTraffic.timestamp >= start_time,
        NetworkTraffic.contains_pii == True
    )
    if app_id:
        query = query.filter(NetworkTraffic.app_id == app_id)
    
    pii_traffic = query.all()
    
    # Aggregate PII types
    pii_by_type = {}
    for t in pii_traffic:
        for pii_type in (t.pii_types or []):
            if pii_type not in pii_by_type:
                pii_by_type[pii_type] = 0
            pii_by_type[pii_type] += 1
    
    return {
        "period_hours": hours,
        "total_pii_detections": len(pii_traffic),
        "by_type": pii_by_type,
        "unique_destinations": len(set(t.destination_host for t in pii_traffic if t.destination_host)),
        "risk_assessment": "high" if len(pii_traffic) > 10 else "medium",
        "recommendations": [
            "Review apps transmitting PII",
            "Consider data encryption requirements"
        ]
    }


@router.get("/blocked")
async def get_blocked_connections(db: Session = Depends(get_db)):
    """Get blocked malicious connections."""
    return {
        "blocked_connections": [
            {
                "id": 1,
                "destination": "malicious-domain.com",
                "reason": "Known malware C2 server",
                "threat_type": "malware",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "destination": "phishing-site.net",
                "reason": "Phishing attempt",
                "threat_type": "phishing",
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "total_blocked_24h": 23,
        "top_block_reasons": [
            {"reason": "Malware C2", "count": 12},
            {"reason": "Phishing", "count": 7},
            {"reason": "Adware", "count": 4}
        ]
    }
