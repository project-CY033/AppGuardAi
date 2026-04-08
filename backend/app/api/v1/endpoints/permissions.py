from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ....models.database import get_db
from ....models.scan import PermissionAnalysis
from ....models.app import App
from pydantic import BaseModel

router = APIRouter()


class PermissionInfo(BaseModel):
    permission: str
    risk_level: str
    description: str
    category: str


# Android permission risk classification
PERMISSION_RISK_DB = {
    "android.permission.READ_CALENDAR": {
        "risk_level": "medium",
        "description": "Allows read access to calendar events",
        "category": "privacy"
    },
    "android.permission.CAMERA": {
        "risk_level": "high",
        "description": "Allows access to camera device",
        "category": "privacy"
    },
    "android.permission.READ_CONTACTS": {
        "risk_level": "high",
        "description": "Allows read access to contacts",
        "category": "privacy"
    },
    "android.permission.ACCESS_FINE_LOCATION": {
        "risk_level": "high",
        "description": "Allows access to precise location",
        "category": "privacy"
    },
    "android.permission.ACCESS_COARSE_LOCATION": {
        "risk_level": "medium",
        "description": "Allows access to approximate location",
        "category": "privacy"
    },
    "android.permission.RECORD_AUDIO": {
        "risk_level": "high",
        "description": "Allows recording audio",
        "category": "privacy"
    },
    "android.permission.READ_PHONE_STATE": {
        "risk_level": "high",
        "description": "Allows read access to phone state",
        "category": "privacy"
    },
    "android.permission.READ_SMS": {
        "risk_level": "high",
        "description": "Allows read access to SMS messages",
        "category": "privacy"
    },
    "android.permission.SEND_SMS": {
        "risk_level": "high",
        "description": "Allows sending SMS messages",
        "category": "privacy"
    },
    "android.permission.READ_EXTERNAL_STORAGE": {
        "risk_level": "medium",
        "description": "Allows read access to external storage",
        "category": "storage"
    },
    "android.permission.WRITE_EXTERNAL_STORAGE": {
        "risk_level": "medium",
        "description": "Allows write access to external storage",
        "category": "storage"
    },
    "android.permission.INTERNET": {
        "risk_level": "low",
        "description": "Allows network access",
        "category": "network"
    },
    "android.permission.ACCESS_NETWORK_STATE": {
        "risk_level": "low",
        "description": "Allows access to network state",
        "category": "network"
    },
    "android.permission.BLUETOOTH": {
        "risk_level": "medium",
        "description": "Allows Bluetooth access",
        "category": "connectivity"
    },
    "android.permission.READ_LOGS": {
        "risk_level": "critical",
        "description": "Allows reading system logs (requires system signature)",
        "category": "system"
    },
    "android.permission.SET_DEBUG_APP": {
        "risk_level": "critical",
        "description": "Allows setting debug app (requires system signature)",
        "category": "system"
    },
    "android.permission.INSTALL_PACKAGES": {
        "risk_level": "critical",
        "description": "Allows installing packages (requires system signature)",
        "category": "system"
    },
    "android.permission.DEVICE_POWER": {
        "risk_level": "high",
        "description": "Allows control of device power state",
        "category": "system"
    },
    "android.permission.SYSTEM_ALERT_WINDOW": {
        "risk_level": "high",
        "description": "Allows creating overlay windows (draw over apps)",
        "category": "system"
    },
    "android.permission.WRITE_SETTINGS": {
        "risk_level": "high",
        "description": "Allows modifying system settings",
        "category": "system"
    },
    "android.permission.BIND_ACCESSIBILITY_SERVICE": {
        "risk_level": "critical",
        "description": "Allows binding to accessibility service",
        "category": "system"
    },
    "android.permission.BIND_DEVICE_ADMIN": {
        "risk_level": "critical",
        "description": "Allows binding to device admin",
        "category": "system"
    }
}


@router.get("/analyze/{app_id}")
async def analyze_app_permissions(app_id: int, db: Session = Depends(get_db)):
    """Get detailed permission analysis for an app."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    analysis = db.query(PermissionAnalysis).filter(
        PermissionAnalysis.app_id == app_id
    ).order_by(PermissionAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No permission analysis available")
    
    # Enrich permissions with risk info
    enriched_permissions = []
    for perm in analysis.requested_permissions:
        info = PERMISSION_RISK_DB.get(perm, {
            "risk_level": "unknown",
            "description": "Custom or unknown permission",
            "category": "custom"
        })
        enriched_permissions.append({
            "permission": perm,
            **info
        })
    
    # Sort by risk
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}
    enriched_permissions.sort(key=lambda x: risk_order.get(x["risk_level"], 5))
    
    return {
        "app_id": app_id,
        "app_name": app.app_name,
        "risk_score": analysis.permission_risk_score,
        "total_permissions": len(analysis.requested_permissions),
        "dangerous_count": len(analysis.dangerous_permissions),
        "hidden_count": len(analysis.hidden_permissions),
        "permissions": enriched_permissions,
        "hidden_permissions": analysis.hidden_permissions,
        "dynamic_permissions": analysis.dynamic_permissions,
        "anomalies": analysis.permission_anomalies,
        "excess_permissions": analysis.excess_permissions,
        "z_scores": analysis.permission_z_scores
    }


@router.get("/baseline/{category}")
async def get_category_baseline(category: str, db: Session = Depends(get_db)):
    """Get permission baseline for an app category."""
    from ....models.app import AppCategory
    
    try:
        cat_enum = AppCategory(category)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    apps = db.query(App).filter(App.category == cat_enum).limit(100).all()
    
    # Aggregate permissions
    permission_counts = {}
    for app in apps:
        analysis = db.query(PermissionAnalysis).filter(
            PermissionAnalysis.app_id == app.id
        ).first()
        if analysis:
            for perm in analysis.requested_permissions:
                if perm not in permission_counts:
                    permission_counts[perm] = 0
                permission_counts[perm] += 1
    
    # Calculate percentages
    total_apps = len(apps)
    baseline = {
        perm: {
            "count": count,
            "percentage": (count / total_apps * 100) if total_apps > 0 else 0
        }
        for perm, count in permission_counts.items()
    }
    
    # Sort by percentage
    baseline = dict(sorted(baseline.items(), key=lambda x: x[1]["percentage"], reverse=True))
    
    return {
        "category": category,
        "sample_size": total_apps,
        "baseline": baseline
    }


@router.get("/risk-database")
async def get_permission_risk_database():
    """Get the full permission risk database."""
    return {
        "permissions": [
            {
                "permission": perm,
                **info
            }
            for perm, info in PERMISSION_RISK_DB.items()
        ],
        "total": len(PERMISSION_RISK_DB)
    }


@router.get("/dangerous")
async def get_dangerous_permissions():
    """Get list of dangerous permissions."""
    dangerous = {
        perm: info
        for perm, info in PERMISSION_RISK_DB.items()
        if info["risk_level"] in ["high", "critical"]
    }
    
    return {
        "permissions": [
            {"permission": perm, **info}
            for perm, info in dangerous.items()
        ],
        "total": len(dangerous)
    }


@router.get("/hidden-detection")
async def get_hidden_permission_info():
    """Get information about hidden/stealth permission detection."""
    return {
        "description": "Hidden permissions are permissions that apps may access without explicitly declaring them",
        "detection_methods": [
            {
                "name": "Dynamic Permission Detection",
                "description": "Detects permissions requested at runtime using requestPermissions()"
            },
            {
                "name": "Reflection Analysis",
                "description": "Identifies permissions accessed via Java reflection API"
            },
            {
                "name": "Native Code Analysis",
                "description": "Analyzes native libraries for permission access"
            },
            {
                "name": "DEX Loader Detection",
                "description": "Detects dynamically loaded code that may request permissions"
            }
        ],
        "common_hidden_permissions": [
            "android.permission.READ_LOGS",
            "android.permission.SET_DEBUG_APP",
            "android.permission.INSTALL_PACKAGES",
            "android.permission.WRITE_SECURE_SETTINGS"
        ]
    }


@router.get("/similar-apps/{app_id}")
async def get_similar_app_permissions(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Compare permissions with similar apps."""
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    current_analysis = db.query(PermissionAnalysis).filter(
        PermissionAnalysis.app_id == app_id
    ).first()
    
    if not current_analysis:
        raise HTTPException(status_code=404, detail="No permission analysis available")
    
    # Get apps in same category
    similar_apps = db.query(App).filter(
        App.category == app.category,
        App.id != app_id
    ).limit(20).all()
    
    comparisons = []
    for similar_app in similar_apps:
        similar_analysis = db.query(PermissionAnalysis).filter(
            PermissionAnalysis.app_id == similar_app.id
        ).first()
        
        if similar_analysis:
            current_perms = set(current_analysis.requested_permissions)
            similar_perms = set(similar_analysis.requested_permissions)
            
            common = current_perms & similar_perms
            extra = current_perms - similar_perms
            missing = similar_perms - current_perms
            
            similarity = len(common) / len(current_perms | similar_perms) if (current_perms | similar_perms) else 0
            
            comparisons.append({
                "app_id": similar_app.id,
                "app_name": similar_app.app_name,
                "similarity": similarity,
                "common_permissions": len(common),
                "extra_permissions": list(extra),
                "missing_permissions": list(missing)
            })
    
    comparisons.sort(key=lambda x: x["similarity"], reverse=True)
    
    return {
        "app_id": app_id,
        "app_name": app.app_name,
        "category": app.category.value,
        "comparisons": comparisons[:10]
    }
