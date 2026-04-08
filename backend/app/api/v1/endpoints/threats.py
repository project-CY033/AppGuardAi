from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ....models.database import get_db
from ....models.threat import ThreatIndicator, MalwareFamily, PhishingSignature, IndicatorType, ThreatType
from pydantic import BaseModel

router = APIRouter()


class ThreatIndicatorResponse(BaseModel):
    id: int
    indicator_type: IndicatorType
    indicator_value: str
    threat_type: ThreatType
    malware_family: Optional[str]
    severity: str
    confidence: float
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True


class ThreatStats(BaseModel):
    total_indicators: int
    active_families: int
    phishing_signatures: int
    indicators_by_type: dict
    indicators_by_threat: dict
    recent_indicators_24h: int


@router.get("/stats", response_model=ThreatStats)
async def get_threat_stats(db: Session = Depends(get_db)):
    """Get threat intelligence statistics."""
    total = db.query(ThreatIndicator).count()
    families = db.query(MalwareFamily).filter(MalwareFamily.is_active == True).count()
    phishing = db.query(PhishingSignature).filter(PhishingSignature.is_active == True).count()
    
    # Get counts by type
    by_type = {}
    indicators = db.query(ThreatIndicator).all()
    for ind in indicators:
        t = ind.indicator_type.value
        by_type[t] = by_type.get(t, 0) + 1
    
    by_threat = {}
    for ind in indicators:
        t = ind.threat_type.value
        by_threat[t] = by_threat.get(t, 0) + 1
    
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent = db.query(ThreatIndicator).filter(
        ThreatIndicator.first_seen >= yesterday
    ).count()
    
    return ThreatStats(
        total_indicators=total,
        active_families=families,
        phishing_signatures=phishing,
        indicators_by_type=by_type,
        indicators_by_threat=by_threat,
        recent_indicators_24h=recent
    )


@router.get("/indicators")
async def list_indicators(
    indicator_type: Optional[IndicatorType] = None,
    threat_type: Optional[ThreatType] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List threat indicators with filtering."""
    query = db.query(ThreatIndicator)
    
    if indicator_type:
        query = query.filter(ThreatIndicator.indicator_type == indicator_type)
    if threat_type:
        query = query.filter(ThreatIndicator.threat_type == threat_type)
    if severity:
        query = query.filter(ThreatIndicator.severity == severity)
    if search:
        query = query.filter(ThreatIndicator.indicator_value.ilike(f"%{search}%"))
    
    total = query.count()
    items = query.order_by(ThreatIndicator.last_seen.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "items": [ThreatIndicatorResponse.from_orm(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/indicators/check")
async def check_indicator(
    value: str,
    db: Session = Depends(get_db)
):
    """Check if a value is a known threat indicator."""
    indicator = db.query(ThreatIndicator).filter(
        ThreatIndicator.indicator_value == value
    ).first()
    
    if indicator:
        return {
            "found": True,
            "indicator": ThreatIndicatorResponse.from_orm(indicator),
            "is_threat": True
        }
    
    return {"found": False, "is_threat": False}


@router.get("/malware-families")
async def list_malware_families(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List known malware families."""
    query = db.query(MalwareFamily)
    if active_only:
        query = query.filter(MalwareFamily.is_active == True)
    
    families = query.order_by(MalwareFamily.sample_count.desc()).all()
    
    return [
        {
            "id": f.id,
            "name": f.name,
            "aliases": f.aliases,
            "category": f.category,
            "description": f.description,
            "tactics": f.tactics,
            "techniques": f.techniques,
            "sample_count": f.sample_count,
            "is_active": f.is_active,
            "first_seen": f.first_seen,
            "last_seen": f.last_seen
        }
        for f in families
    ]


@router.get("/malware-families/{family_id}")
async def get_malware_family(family_id: int, db: Session = Depends(get_db)):
    """Get detailed malware family information."""
    family = db.query(MalwareFamily).filter(MalwareFamily.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Malware family not found")
    
    return {
        "id": family.id,
        "name": family.name,
        "aliases": family.aliases,
        "category": family.category,
        "description": family.description,
        "tactics": family.tactics,
        "techniques": family.techniques,
        "indicators": family.indicators,
        "yara_rules": family.yara_rules,
        "signature_patterns": family.signature_patterns,
        "behavioral_signatures": family.behavioral_signatures,
        "sample_count": family.sample_count,
        "first_seen": family.first_seen,
        "last_seen": family.last_seen
    }


@router.get("/phishing-signatures")
async def list_phishing_signatures(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List phishing detection signatures."""
    query = db.query(PhishingSignature)
    if active_only:
        query = query.filter(PhishingSignature.is_active == True)
    
    signatures = query.all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "target_brand": s.target_brand,
            "url_patterns": s.url_patterns,
            "brand_keywords": s.brand_keywords,
            "confidence": s.confidence
        }
        for s in signatures
    ]


@router.post("/indicators")
async def add_indicator(
    indicator_type: IndicatorType,
    indicator_value: str,
    threat_type: ThreatType,
    severity: str = "medium",
    confidence: float = 0.5,
    malware_family: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Add a new threat indicator."""
    indicator = ThreatIndicator(
        indicator_type=indicator_type,
        indicator_value=indicator_value,
        threat_type=threat_type,
        severity=severity,
        confidence=confidence,
        malware_family=malware_family,
        description=description,
        source="internal",
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    
    return ThreatIndicatorResponse.from_orm(indicator)


@router.get("/intel-sources")
async def get_intel_sources(db: Session = Depends(get_db)):
    """Get configured threat intelligence sources."""
    from ....models.threat import ThreatIntelligenceFeed
    
    feeds = db.query(ThreatIntelligenceFeed).all()
    
    return [
        {
            "id": f.id,
            "name": f.name,
            "source": f.source,
            "feed_type": f.feed_type,
            "is_active": f.is_active,
            "is_healthy": f.is_healthy,
            "last_updated": f.last_updated,
            "indicators_count": f.indicators_count
        }
        for f in feeds
    ]
