"""Seed the database with sample data for demonstration."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.database import SessionLocal, init_db
from app.models.app import App, AppCategory, AppPlatform, AppTrustLevel
from app.models.threat import ThreatIndicator, IndicatorType, ThreatType, MalwareFamily, PhishingSignature
from app.models.scan import ScanJob, ScanResult, ScanStatus, ThreatLevel, PermissionAnalysis, ScanType
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.monitoring import APICall, NetworkTraffic, DeviceHealth, MonitoringAlert, APICategory, TrafficProtocol
from datetime import datetime, timedelta
import random
import uuid


def seed_database():
    """Seed database with sample data."""
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.query(MonitoringAlert).delete()
        # db.query(APICall).delete()
        # db.query(NetworkTraffic).delete()
        # db.query(DeviceHealth).delete()
        # db.query(Incident).delete()
        # db.query(ThreatIndicator).delete()
        # db.query(ScanResult).delete()
        # db.query(ScanJob).delete()
        # db.query(PermissionAnalysis).delete()
        # db.query(App).delete()
        # db.commit()
        
        # Check if data already exists
        if db.query(App).count() > 0:
            print("Database already has data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create sample apps
        apps_data = [
            {"package_name": "com.whatsapp", "app_name": "WhatsApp Messenger", "trust_level": AppTrustLevel.TRUSTED, "category": AppCategory.COMMUNICATION, "overall_risk_score": 12.5},
            {"package_name": "com.facebook.katana", "app_name": "Facebook", "trust_level": AppTrustLevel.TRUSTED, "category": AppCategory.SOCIAL, "overall_risk_score": 18.3},
            {"package_name": "com.instagram.android", "app_name": "Instagram", "trust_level": AppTrustLevel.TRUSTED, "category": AppCategory.SOCIAL, "overall_risk_score": 15.2},
            {"package_name": "com.spotify.music", "app_name": "Spotify", "trust_level": AppTrustLevel.TRUSTED, "category": AppCategory.MUSIC, "overall_risk_score": 10.5},
            {"package_name": "com.fake.whatsapp", "app_name": "WhatsApp Plus", "trust_level": AppTrustLevel.MALICIOUS, "category": AppCategory.COMMUNICATION, "overall_risk_score": 89.5, "is_malware": True, "is_clone": True},
            {"package_name": "com.malicious.banking", "app_name": "Banking Secure", "trust_level": AppTrustLevel.MALICIOUS, "category": AppCategory.FINANCE, "overall_risk_score": 95.2, "is_malware": True, "is_phishing": True},
            {"package_name": "com.suspicious.cleaner", "app_name": "Super Cleaner Pro", "trust_level": AppTrustLevel.SUSPICIOUS, "category": AppCategory.UTILITY, "overall_risk_score": 62.3, "has_hidden_permissions": True},
            {"package_name": "com.clone.instagram", "app_name": "InstaPro", "trust_level": AppTrustLevel.SUSPICIOUS, "category": AppCategory.SOCIAL, "overall_risk_score": 71.5, "is_clone": True},
            {"package_name": "com.tiktok.android", "app_name": "TikTok", "trust_level": AppTrustLevel.TRUSTED, "category": AppCategory.ENTERTAINMENT, "overall_risk_score": 22.1},
            {"package_name": "com.malware.spyware", "app_name": "Flashlight Pro", "trust_level": AppTrustLevel.MALICIOUS, "category": AppCategory.UTILITY, "overall_risk_score": 92.8, "is_malware": True},
        ]
        
        apps = []
        for data in apps_data:
            app = App(
                package_name=data["package_name"],
                app_name=data["app_name"],
                platform=AppPlatform.ANDROID,
                category=data["category"],
                trust_level=data["trust_level"],
                overall_risk_score=data["overall_risk_score"],
                is_clone=data.get("is_clone", False),
                is_malware=data.get("is_malware", False),
                is_phishing=data.get("is_phishing", False),
                has_hidden_permissions=data.get("has_hidden_permissions", False),
                developer_name="Sample Developer",
                version_name=f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
                min_sdk_version=random.choice([21, 23, 26, 28]),
                target_sdk_version=random.choice([30, 31, 33, 34]),
                app_size=random.randint(5000000, 150000000)
            )
            db.add(app)
            apps.append(app)
        
        db.commit()
        print(f"Created {len(apps)} sample apps")
        
        # Create threat indicators
        threats_data = [
            {"type": IndicatorType.HASH, "value": "a1b2c3d4e5f6789012345678901234567890abcd", "threat_type": ThreatType.MALWARE, "severity": "critical", "family": "SpyAgent"},
            {"type": IndicatorType.DOMAIN, "value": "malicious-c2-server.com", "threat_type": ThreatType.MALWARE, "severity": "critical", "family": "BankBot"},
            {"type": IndicatorType.DOMAIN, "value": "phishing-bank.com", "threat_type": ThreatType.PHISHING, "severity": "high"},
            {"type": IndicatorType.IP, "value": "185.220.101.45", "threat_type": ThreatType.TROJAN, "severity": "high"},
            {"type": IndicatorType.PACKAGE_NAME, "value": "com.fake.whatsapp", "threat_type": ThreatType.CLONE_APP, "severity": "medium"},
            {"type": IndicatorType.HASH, "value": "deadbeef1234567890abcdef1234567890abcdef", "threat_type": ThreatType.RANSOMWARE, "severity": "critical"},
            {"type": IndicatorType.URL, "value": "https://fake-login.com/steal", "threat_type": ThreatType.PHISHING, "severity": "high"},
            {"type": IndicatorType.DOMAIN, "value": "crypto-miner-pool.xyz", "threat_type": ThreatType.CRYPTOMINER, "severity": "medium"},
        ]
        
        for data in threats_data:
            indicator = ThreatIndicator(
                indicator_type=data["type"],
                indicator_value=data["value"],
                threat_type=data["threat_type"],
                severity=data["severity"],
                malware_family=data.get("family"),
                source="internal",
                confidence=random.uniform(0.7, 0.99),
                first_seen=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                last_seen=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            db.add(indicator)
        
        db.commit()
        print(f"Created {len(threats_data)} threat indicators")
        
        # Create malware families
        families_data = [
            {"name": "SpyAgent", "category": "spyware", "description": "Advanced spyware targeting banking credentials", "sample_count": 1250},
            {"name": "BankBot", "category": "trojan", "description": "Banking trojan with overlay attacks", "sample_count": 890},
            {"name": "Anubis", "category": "trojan", "description": "Mobile banking trojan with RAT capabilities", "sample_count": 650},
            {"name": "Cerberus", "category": "trojan", "description": "Android banking trojan with keylogging", "sample_count": 420},
        ]
        
        for data in families_data:
            family = MalwareFamily(
                name=data["name"],
                category=data["category"],
                description=data["description"],
                sample_count=data["sample_count"],
                is_active=True,
                first_seen=datetime.utcnow() - timedelta(days=random.randint(90, 365)),
                last_seen=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            db.add(family)
        
        db.commit()
        print(f"Created {len(families_data)} malware families")
        
        # Create phishing signatures
        phishing_data = [
            {"name": "Bank of America Phish", "target_brand": "Bank of America", "confidence": 0.95},
            {"name": "PayPal Login Phish", "target_brand": "PayPal", "confidence": 0.92},
            {"name": "Amazon Phish", "target_brand": "Amazon", "confidence": 0.89},
            {"name": "Google Phish", "target_brand": "Google", "confidence": 0.94},
        ]
        
        for data in phishing_data:
            sig = PhishingSignature(
                name=data["name"],
                target_brand=data["target_brand"],
                confidence=data["confidence"],
                is_active=True
            )
            db.add(sig)
        
        db.commit()
        print(f"Created {len(phishing_data)} phishing signatures")
        
        # Create incidents
        incidents_data = [
            {"title": "Malware detected: SpyAgent variant", "category": IncidentCategory.MALWARE_DETECTED, "severity": IncidentSeverity.CRITICAL, "status": IncidentStatus.NEW},
            {"title": "Clone app detected: WhatsApp fake", "category": IncidentCategory.CLONE_APP, "severity": IncidentSeverity.HIGH, "status": IncidentStatus.INVESTIGATING},
            {"title": "Phishing attempt blocked", "category": IncidentCategory.PHISHING, "severity": IncidentSeverity.MEDIUM, "status": IncidentStatus.CONFIRMED},
            {"title": "Suspicious network activity", "category": IncidentCategory.UNUSUAL_NETWORK_ACTIVITY, "severity": IncidentSeverity.MEDIUM, "status": IncidentStatus.INVESTIGATING},
            {"title": "Data exfiltration attempt blocked", "category": IncidentCategory.DATA_EXFILTRATION, "severity": IncidentSeverity.HIGH, "status": IncidentStatus.NEW},
            {"title": "Hidden permissions detected", "category": IncidentCategory.SUSPICIOUS_PERMISSION, "severity": IncidentSeverity.LOW, "status": IncidentStatus.CLOSED},
        ]
        
        for data in incidents_data:
            incident = Incident(
                incident_id=str(uuid.uuid4()),
                title=data["title"],
                category=data["category"],
                severity=data["severity"],
                status=data["status"],
                risk_score=random.uniform(30, 95),
                app_id=random.choice(apps).id if apps else None
            )
            db.add(incident)
        
        db.commit()
        print(f"Created {len(incidents_data)} incidents")
        
        # Create API calls
        api_categories = list(APICategory)
        api_names = [
            "Runtime.exec", "LocationManager.getLastKnownLocation", 
            "TelephonyManager.getDeviceId", "ContentResolver.query",
            "HttpURLConnection.connect", "Socket.connect",
            "FileInputStream.read", "Camera.open",
            "AudioRecord.startRecording", "AccessibilityService.onAccessibilityEvent"
        ]
        
        for i in range(50):
            api_call = APICall(
                app_id=random.choice(apps).id if apps else 1,
                api_name=random.choice(api_names),
                category=random.choice(api_categories),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                is_suspicious=random.random() < 0.15,
                risk_score=random.uniform(0, 100),
                parameters={}
            )
            db.add(api_call)
        
        db.commit()
        print("Created 50 API calls")
        
        # Create network traffic
        protocols = list(TrafficProtocol)
        hosts = ["google.com", "facebook.com", "api.example.com", "analytics.google.com", "cdn.example.com"]
        
        for i in range(50):
            traffic = NetworkTraffic(
                app_id=random.choice(apps).id if apps else 1,
                protocol=random.choice(protocols),
                destination_host=random.choice(hosts),
                destination_port=random.choice([80, 443, 8080, 8443]),
                method=random.choice(["GET", "POST", "PUT", "DELETE"]),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                request_size=random.randint(100, 10000),
                response_size=random.randint(100, 50000),
                is_suspicious=random.random() < 0.1,
                contains_pii=random.random() < 0.05,
                risk_score=random.uniform(0, 100),
                destination_country=random.choice(["US", "DE", "CN", "RU", "UK"])
            )
            db.add(traffic)
        
        db.commit()
        print("Created 50 network traffic records")
        
        # Create device health records
        device_health = DeviceHealth(
            device_id="demo-device-001",
            device_model="Samsung Galaxy S23",
            device_manufacturer="Samsung",
            android_version="14",
            security_patch_level="2026-03-01",
            is_rooted=False,
            encryption_enabled=True,
            battery_level=random.uniform(20, 100),
            cpu_usage=random.uniform(10, 60),
            memory_usage=random.uniform(30, 80),
            storage_usage=random.uniform(20, 70),
            risk_score=random.uniform(10, 30),
            timestamp=datetime.utcnow()
        )
        db.add(device_health)
        db.commit()
        print("Created device health record")
        
        # Create monitoring alerts
        alerts_data = [
            {"title": "High-risk app installation blocked", "alert_type": "installation_block", "severity": "high"},
            {"title": "Suspicious API call detected", "alert_type": "api_monitor", "severity": "medium"},
            {"title": "Data exfiltration attempt blocked", "alert_type": "network_monitor", "severity": "critical"},
            {"title": "Hidden permission requested", "alert_type": "permission_monitor", "severity": "medium"},
        ]
        
        for data in alerts_data:
            alert = MonitoringAlert(
                device_id="demo-device-001",
                alert_type=data["alert_type"],
                title=data["title"],
                severity=data["severity"],
                risk_score=random.uniform(50, 95),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                acknowledged=False
            )
            db.add(alert)
        
        db.commit()
        print(f"Created {len(alerts_data)} monitoring alerts")
        
        print("\n=== Database seeded successfully! ===")
        print(f"Total apps: {db.query(App).count()}")
        print(f"Total threats: {db.query(ThreatIndicator).count()}")
        print(f"Total incidents: {db.query(Incident).count()}")
        print(f"Total API calls: {db.query(APICall).count()}")
        print(f"Total network records: {db.query(NetworkTraffic).count()}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
