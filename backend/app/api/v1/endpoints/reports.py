from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import json
import io

from ....models.database import get_db
from ....models.scan import ScanJob, ScanResult, ScanStatus
from ....models.app import App
from ....models.incident import Incident
from ....models.monitoring import APICall, NetworkTraffic

router = APIRouter()


@router.get("/security/summary")
async def get_security_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get security summary report."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Scan statistics
    scans_completed = db.query(ScanJob).filter(
        ScanJob.status == ScanStatus.COMPLETED,
        ScanJob.completed_at >= start_date
    ).count()
    
    scans_failed = db.query(ScanJob).filter(
        ScanJob.status == ScanStatus.FAILED,
        ScanJob.completed_at >= start_date
    ).count()
    
    # Threat statistics
    malware_detected = db.query(App).filter(App.is_malware == True).count()
    clones_detected = db.query(App).filter(App.is_clone == True).count()
    phishing_detected = db.query(App).filter(App.is_phishing == True).count()
    
    # Severity distribution
    high_findings = db.query(ScanResult).filter(
        ScanResult.severity == "high",
        ScanResult.created_at >= start_date
    ).count()
    
    medium_findings = db.query(ScanResult).filter(
        ScanResult.severity == "medium",
        ScanResult.created_at >= start_date
    ).count()
    
    low_findings = db.query(ScanResult).filter(
        ScanResult.severity == "low",
        ScanResult.created_at >= start_date
    ).count()
    
    # Incident statistics
    incidents_created = db.query(Incident).filter(
        Incident.created_at >= start_date
    ).count()
    
    incidents_resolved = db.query(Incident).filter(
        Incident.closed_at >= start_date
    ).count()
    
    # Trend data (daily)
    daily_scans = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.query(ScanJob).filter(
            ScanJob.completed_at >= day_start,
            ScanJob.completed_at < day_end
        ).count()
        daily_scans.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})
    
    return {
        "period_days": days,
        "scan_statistics": {
            "completed": scans_completed,
            "failed": scans_failed,
            "success_rate": scans_completed / (scans_completed + scans_failed) * 100 if (scans_completed + scans_failed) > 0 else 0
        },
        "threat_statistics": {
            "malware_detected": malware_detected,
            "clones_detected": clones_detected,
            "phishing_detected": phishing_detected,
            "total_threats": malware_detected + clones_detected + phishing_detected
        },
        "findings": {
            "high": high_findings,
            "medium": medium_findings,
            "low": low_findings,
            "total": high_findings + medium_findings + low_findings
        },
        "incident_statistics": {
            "created": incidents_created,
            "resolved": incidents_resolved,
            "open": incidents_created - incidents_resolved
        },
        "trends": {
            "daily_scans": daily_scans
        }
    }


@router.get("/app/{app_id}")
async def get_app_report(app_id: int, db: Session = Depends(get_db)):
    """Get comprehensive app analysis report."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Get latest scan
    latest_scan = db.query(ScanJob).filter(
        ScanJob.app_id == app_id,
        ScanJob.status == ScanStatus.COMPLETED
    ).order_by(ScanJob.completed_at.desc()).first()
    
    findings = []
    if latest_scan:
        findings = db.query(ScanResult).filter(
            ScanResult.scan_job_id == latest_scan.id
        ).all()
    
    # Get permissions
    from ....models.scan import PermissionAnalysis
    perms = db.query(PermissionAnalysis).filter(
        PermissionAnalysis.app_id == app_id
    ).order_by(PermissionAnalysis.created_at.desc()).first()
    
    # Get incidents
    incidents = db.query(Incident).filter(
        Incident.app_id == app_id
    ).order_by(Incident.created_at.desc()).all()
    
    return {
        "app": {
            "id": app.id,
            "package_name": app.package_name,
            "app_name": app.app_name,
            "version": app.version_name,
            "developer": app.developer_name,
            "trust_level": app.trust_level.value if app.trust_level else None,
            "risk_score": app.overall_risk_score,
            "is_malware": app.is_malware,
            "is_clone": app.is_clone,
            "is_phishing": app.is_phishing
        },
        "latest_scan": {
            "id": latest_scan.id if latest_scan else None,
            "completed_at": latest_scan.completed_at if latest_scan else None,
            "risk_score": latest_scan.risk_score if latest_scan else None,
            "threat_level": latest_scan.threat_level.value if latest_scan and latest_scan.threat_level else None
        } if latest_scan else None,
        "findings_summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.severity.value == "critical"),
            "high": sum(1 for f in findings if f.severity.value == "high"),
            "medium": sum(1 for f in findings if f.severity.value == "medium"),
            "low": sum(1 for f in findings if f.severity.value == "low")
        },
        "permissions": {
            "total": len(perms.declared_permissions) if perms else 0,
            "dangerous": len(perms.dangerous_permissions) if perms else 0,
            "hidden": len(perms.hidden_permissions) if perms else 0,
            "risk_score": perms.permission_risk_score if perms else 0
        } if perms else None,
        "incidents": [
            {
                "id": i.incident_id,
                "title": i.title,
                "severity": i.severity.value,
                "status": i.status.value,
                "created_at": i.created_at
            }
            for i in incidents
        ]
    }


@router.get("/compliance/gdpr")
async def get_gdpr_compliance_report(db: Session = Depends(get_db)):
    """Generate GDPR compliance report."""
    from ....models.scan import PermissionAnalysis
    
    apps_with_location = db.query(App).join(PermissionAnalysis).filter(
        PermissionAnalysis.requested_permissions.contains("ACCESS_FINE_LOCATION")
    ).count()
    
    apps_with_contacts = db.query(App).join(PermissionAnalysis).filter(
        PermissionAnalysis.requested_permissions.contains("READ_CONTACTS")
    ).count()
    
    apps_with_calendar = db.query(App).join(PermissionAnalysis).filter(
        PermissionAnalysis.requested_permissions.contains("READ_CALENDAR")
    ).count()
    
    apps_with_sms = db.query(App).join(PermissionAnalysis).filter(
        PermissionAnalysis.requested_permissions.contains("READ_SMS")
    ).count()
    
    return {
        "report_type": "gdpr_compliance",
        "generated_at": datetime.utcnow().isoformat(),
        "data_access_analysis": {
            "location_data": apps_with_location,
            "contact_data": apps_with_contacts,
            "calendar_data": apps_with_calendar,
            "sms_data": apps_with_sms
        },
        "recommendations": [
            "Review apps requesting location data for legitimate purpose",
            "Ensure data minimization for contact access",
            "Check retention policies for sensitive data"
        ]
    }


@router.get("/export/{format}")
async def export_report(
    format: str,
    report_type: str = "summary",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Export report in specified format (json, csv)."""
    summary = await get_security_summary(days=days, db=db)
    
    if format == "json":
        return Response(
            content=json.dumps(summary, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=security_report.json"}
        )
    elif format == "csv":
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Scans Completed", summary["scan_statistics"]["completed"]])
        writer.writerow(["Malware Detected", summary["threat_statistics"]["malware_detected"]])
        writer.writerow(["Clones Detected", summary["threat_statistics"]["clones_detected"]])
        writer.writerow(["Incidents Open", summary["incident_statistics"]["open"]])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=security_report.csv"}
        )
    
    raise HTTPException(status_code=400, detail="Unsupported format")
