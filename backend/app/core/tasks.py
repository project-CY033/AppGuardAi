"""
APK Security Scanner - Advanced Analysis Engine
Integrates OWASP MASVS, SAST, SCA, Secret Detection, Malware Scanning
Based on: BeVigil, ImmuniWeb, DerScanner, Quixxi
"""
import logging
import os
import zipfile
import hashlib
import struct
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from ..models.database import SessionLocal
from ..models.scan import ScanJob, ScanResult, ScanStatus, PermissionAnalysis, ThreatLevel
from ..models.app import App, AppTrustLevel

# Import advanced scanner
from app.core.advanced_scanner import (
    AdvancedAPKScanner,
    OWASPMASVSScanner,
    SecretDetector,
    SoftwareCompositionAnalyzer,
    MalwareScanner,
    RiskScoringEngine,
    SecurityReportGenerator,
    RiskLevel,
    ScanCategory,
    SecurityFinding,
)

logger = logging.getLogger(__name__)

# Known dangerous permissions with risk scores
DANGEROUS_PERMISSIONS = {
    "android.permission.READ_LOGS": {"risk": "critical", "score": 95, "description": "Reads system logs containing sensitive data"},
    "android.permission.SET_DEBUG_APP": {"risk": "high", "score": 85, "description": "Enables debugging, potential code injection"},
    "android.permission.INSTALL_PACKAGES": {"risk": "critical", "score": 98, "description": "Silent app installation"},
    "android.permission.READ_SMS": {"risk": "high", "score": 80, "description": "Reads SMS messages"},
    "android.permission.SEND_SMS": {"risk": "high", "score": 75, "description": "Sends SMS, premium SMS fraud risk"},
    "android.permission.READ_CONTACTS": {"risk": "medium", "score": 60, "description": "Reads contact information"},
    "android.permission.ACCESS_FINE_LOCATION": {"risk": "medium", "score": 50, "description": "Precise location access"},
    "android.permission.CAMERA": {"risk": "medium", "score": 55, "description": "Camera access"},
    "android.permission.RECORD_AUDIO": {"risk": "medium", "score": 60, "description": "Microphone access"},
    "android.permission.READ_PHONE_STATE": {"risk": "medium", "score": 45, "description": "Phone identity access"},
    "android.permission.INTERNET": {"risk": "low", "score": 10, "description": "Network access"},
    "android.permission.WRITE_EXTERNAL_STORAGE": {"risk": "low", "score": 20, "description": "External storage write"},
    "android.permission.ACCESS_NETWORK_STATE": {"risk": "low", "score": 5, "description": "Network state access"},
    "android.permission.WAKE_LOCK": {"risk": "low", "score": 10, "description": "Prevents device sleep"},
    "android.permission.RECEIVE_BOOT_COMPLETED": {"risk": "low", "score": 15, "description": "Starts on boot"},
    "android.permission.SYSTEM_ALERT_WINDOW": {"risk": "high", "score": 65, "description": "Display over other apps"},
    "android.permission.WRITE_SETTINGS": {"risk": "high", "score": 60, "description": "Modify system settings"},
    "android.permission.DEVICE_ADMIN": {"risk": "critical", "score": 90, "description": "Device administrator privileges"},
}

# Suspicious code patterns in DEX files
SUSPICIOUS_PATTERNS = [
    (b"Runtime.exec", "critical", "Command execution capability"),
    (b"ProcessBuilder", "high", "Process creation"),
    (b"DexClassLoader", "high", "Dynamic code loading"),
    (b"getDeviceId", "high", "Device ID access"),
    (b"sendTextMessage", "high", "SMS sending"),
]


class APKAnalyzer:
    """Analyzes APK files for security threats using advanced scanner."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        self.file_hash = None
        self.permissions = []
        self.findings = []
        self.advanced_scanner = AdvancedAPKScanner(filepath)
        
    def calculate_hash(self) -> str:
        sha256 = hashlib.sha256()
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        self.file_hash = sha256.hexdigest()
        return self.file_hash
    
    def validate_apk(self) -> bool:
        """Validate that file is a proper APK."""
        if not os.path.exists(self.filepath):
            self.findings.append({"category": "file", "title": "File Not Found", "description": "The uploaded file could not be found", "severity": "critical", "score": 100})
            return False
        
        if self.file_size == 0:
            self.findings.append({"category": "file", "title": "Empty File", "description": "The uploaded file is empty (0 bytes)", "severity": "critical", "score": 100})
            return False
        
        if self.file_size < 1000:
            self.findings.append({"category": "file", "title": "File Too Small", "description": f"File size ({self.file_size} bytes) is too small for a valid APK", "severity": "high", "score": 80})
            return False
        
        if not zipfile.is_zipfile(self.filepath):
            self.findings.append({"category": "file", "title": "Invalid APK Format", "description": "File is not a valid ZIP/APK archive", "severity": "critical", "score": 100})
            return False
        
        with zipfile.ZipFile(self.filepath, 'r') as zf:
            names = zf.namelist()
            if 'AndroidManifest.xml' not in names:
                self.findings.append({"category": "manifest", "title": "Missing AndroidManifest.xml", "description": "APK does not contain required manifest", "severity": "high", "score": 70})
            if not any(n.endswith('.dex') for n in names):
                self.findings.append({"category": "code", "title": "No DEX Files", "description": "APK does not contain compiled code", "severity": "medium", "score": 50})
        
        return True
    
    def analyze(self) -> Dict[str, Any]:
        """Run full APK analysis with advanced security scanning."""
        self.calculate_hash()
        
        if not self.validate_apk():
            return {"valid": False, "risk_score": 100, "threat_level": "critical", "findings": self.findings, "file_size": self.file_size, "file_hash": self.file_hash}
        
        try:
            # Run advanced security scan
            logger.info(f"Running advanced security scan on {self.filepath}")
            report = self.advanced_scanner.scan()
            
            # Convert advanced findings to legacy format
            for finding in report.get("detailed_findings", []):
                severity_map = {
                    "critical": "critical",
                    "high": "high", 
                    "medium": "medium",
                    "low": "low",
                    "info": "info"
                }
                score_map = {
                    "critical": 95,
                    "high": 75,
                    "medium": 50,
                    "low": 25,
                    "info": 10
                }
                
                risk_level = finding.get("risk_level", "medium")
                self.findings.append({
                    "category": finding.get("category", "general"),
                    "title": finding.get("title", ""),
                    "description": finding.get("description", ""),
                    "severity": severity_map.get(risk_level, "medium"),
                    "score": score_map.get(risk_level, 50),
                    "file_path": finding.get("file_path", ""),
                    "line_number": finding.get("line_number", 0),
                    "owasp_id": finding.get("owasp_id", ""),
                    "cwe_id": finding.get("cwe_id", ""),
                    "recommendation": finding.get("recommendation", ""),
                })
            
            # Get permissions from statistics
            self.permissions = report.get("statistics", {}).get("permissions", [])
            
            # Get risk score from report
            risk_assessment = report.get("risk_assessment", {})
            risk_score = risk_assessment.get("risk_score", 50)
            threat_level = risk_assessment.get("risk_level", "medium")
            
            # Add compliance info to findings
            compliance = report.get("compliance", {})
            if compliance:
                masvs = compliance.get("owasp_masvs", {})
                self.findings.append({
                    "category": "compliance",
                    "title": f"OWASP MASVS Compliance: {masvs.get('compliance_percentage', 0)}%",
                    "description": f"Passed {masvs.get('compliance_score', '0/0')} MASVS controls",
                    "severity": "info" if masvs.get("compliance_percentage", 0) > 80 else "medium",
                    "score": max(0, 100 - masvs.get("compliance_percentage", 0)),
                })
            
            return {
                "valid": True,
                "risk_score": risk_score,
                "threat_level": threat_level,
                "findings": self.findings,
                "permissions": self.permissions,
                "file_size": self.file_size,
                "file_hash": self.file_hash,
                "app_info": report.get("app_info", {}),
                "compliance": compliance,
                "recommendations": report.get("recommendations", []),
                "statistics": report.get("statistics", {}),
            }
            
        except Exception as e:
            logger.error(f"Advanced scan failed, falling back to basic: {e}")
            # Fallback to basic scanning if advanced fails
            return self._basic_analyze()
    
    def _basic_analyze(self) -> Dict[str, Any]:
        """Fallback basic analysis if advanced scanner fails."""
        # Extract permissions
        try:
            with zipfile.ZipFile(self.filepath, 'r') as zf:
                if 'AndroidManifest.xml' in zf.namelist():
                    manifest_data = zf.read('AndroidManifest.xml')
                    matches = re.findall(rb'android\.permission\.[A-Z_]+', manifest_data)
                    if matches:
                        self.permissions = list(set([m.decode('utf-8', errors='ignore') if isinstance(m, bytes) else m for m in matches]))
        except Exception as e:
            logger.error(f"Permission extraction error: {e}")
        
        # Score permissions
        for perm in self.permissions:
            if perm in DANGEROUS_PERMISSIONS:
                info = DANGEROUS_PERMISSIONS[perm]
                self.findings.append({"category": "permission", "title": f"Dangerous: {perm.replace('android.permission.', '')}", "description": info["description"], "severity": info["risk"], "score": info["score"]})
        
        # Calculate risk score
        if self.findings:
            max_score = max(f["score"] for f in self.findings)
            avg_score = sum(f["score"] for f in self.findings) / len(self.findings)
            risk_score = (max_score * 0.6) + (avg_score * 0.4)
        else:
            risk_score = 5
        
        # Determine threat level
        if risk_score >= 80: threat_level = "critical"
        elif risk_score >= 60: threat_level = "high"
        elif risk_score >= 40: threat_level = "medium"
        elif risk_score >= 20: threat_level = "low"
        else: threat_level = "safe"
        
        return {"valid": True, "risk_score": round(risk_score, 1), "threat_level": threat_level, "findings": self.findings, "permissions": self.permissions, "file_size": self.file_size, "file_hash": self.file_hash}


async def run_scan_task(scan_id: str):
    """Run a complete scan for an app."""
    db = SessionLocal()
    scan = None
    
    try:
        logger.info(f"Starting scan task for {scan_id}")
        
        scan = db.query(ScanJob).filter(ScanJob.id == scan_id).first()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return
        
        app = db.query(App).filter(App.id == scan.app_id).first()
        if not app:
            logger.error(f"App {scan.app_id} not found")
            return
        
        filepath = scan.config.get("filepath") if scan.config else None
        logger.info(f"Scan {scan_id} - filepath: {filepath}")
        
        # Update scan status
        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        scan.current_stage = "analysis"
        scan.progress = 50
        db.commit()
        
        results = []
        
        if filepath and os.path.exists(filepath):
            logger.info(f"Scan {scan_id} - running analyzer")
            analyzer = APKAnalyzer(filepath)
            analysis = analyzer.analyze()
            logger.info(f"Scan {scan_id} - analysis complete: risk={analysis.get('risk_score')}")
            
            # Create findings
            severity_map = {"critical": ThreatLevel.CRITICAL, "high": ThreatLevel.HIGH, "medium": ThreatLevel.MEDIUM, "low": ThreatLevel.LOW, "safe": ThreatLevel.SAFE}
            
            for finding in analysis.get("findings", []):
                result = ScanResult(
                    scan_job_id=scan_id,
                    app_id=app.id,
                    category=finding.get("category", "general"),
                    title=finding.get("title", "Finding"),
                    description=finding.get("description", ""),
                    severity=severity_map.get(finding.get("severity", "low"), ThreatLevel.LOW),
                    confidence=0.9,
                    detection_method="static_analysis"
                )
                db.add(result)
                results.append(result)
            
            # Create permission analysis
            perm_analysis = PermissionAnalysis(
                app_id=app.id,
                scan_job_id=scan_id,
                declared_permissions=analysis.get("permissions", []),
                requested_permissions=analysis.get("permissions", []),
                dangerous_permissions=[p for p in analysis.get("permissions", []) if p in DANGEROUS_PERMISSIONS],
                hidden_permissions=[],
                permission_risk_score=min(100, len([p for p in analysis.get("permissions", []) if p in DANGEROUS_PERMISSIONS]) * 15),
                category="app"
            )
            db.add(perm_analysis)
            
            # Update scan
            risk_score = analysis.get("risk_score", 50)
            threat_level_str = analysis.get("threat_level", "medium")
            
            scan.current_stage = "completed"
            scan.progress = 100
            scan.status = ScanStatus.COMPLETED
            scan.completed_at = datetime.utcnow()
            scan.duration_seconds = (scan.completed_at - scan.started_at).total_seconds()
            scan.risk_score = risk_score
            scan.threat_level = severity_map.get(threat_level_str, ThreatLevel.MEDIUM)
            scan.findings_count = len(results)
            scan.critical_findings = sum(1 for r in results if r.severity == ThreatLevel.CRITICAL)
            scan.high_findings = sum(1 for r in results if r.severity == ThreatLevel.HIGH)
            scan.medium_findings = sum(1 for r in results if r.severity == ThreatLevel.MEDIUM)
            scan.low_findings = sum(1 for r in results if r.severity == ThreatLevel.LOW)
            
            # Update app
            app.overall_risk_score = risk_score
            if risk_score >= 80:
                app.is_malware = True
                app.trust_level = AppTrustLevel.MALICIOUS
            elif risk_score >= 50:
                app.trust_level = AppTrustLevel.SUSPICIOUS
            else:
                app.trust_level = AppTrustLevel.TRUSTED
            
        else:
            logger.warning(f"Scan {scan_id} - no filepath or file not found")
            result = ScanResult(
                scan_job_id=scan_id,
                app_id=app.id,
                category="error",
                title="File Not Available",
                description="APK file not found for analysis",
                severity=ThreatLevel.HIGH,
                confidence=1.0,
                detection_method="system"
            )
            db.add(result)
            results.append(result)
            
            scan.current_stage = "completed"
            scan.progress = 100
            scan.status = ScanStatus.COMPLETED
            scan.risk_score = 50
            scan.threat_level = ThreatLevel.MEDIUM
            scan.findings_count = 1
            scan.completed_at = datetime.utcnow()
            scan.duration_seconds = (scan.completed_at - scan.started_at).total_seconds()
        
        db.commit()
        logger.info(f"Scan {scan_id} COMPLETED with {len(results)} findings, risk={scan.risk_score}")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} FAILED: {e}", exc_info=True)
        if scan:
            try:
                scan.status = ScanStatus.FAILED
                scan.error_message = str(e)
                scan.completed_at = datetime.utcnow()
                db.commit()
            except:
                pass
    finally:
        db.close()
