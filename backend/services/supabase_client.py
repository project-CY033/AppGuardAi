import httpx
import logging
from core.config import settings

class SupabaseManager:
    def __init__(self):
        self.url: str = settings.supabase_url.rstrip('/')
        self.key: str = settings.supabase_key
        # We use purely direct HTTPX REST for Supabase to bypass the python Client's strict JWT requirements.
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        logging.info(f"Supabase Client manually bound via REST format using explicit key.")

    def log_scan_session(self, user_id: str, scan_type: str, total_apps: int, threats_found: int):
        try:
            payload = {
                "user_id": user_id if user_id else None,
                "scan_type": scan_type,
                "total_apps_scanned": total_apps,
                "threats_found": threats_found
            }
            res = httpx.post(
                f"{self.url}/rest/v1/scan_sessions", 
                headers=self.headers, 
                json=payload
            )
            if res.status_code >= 400:
                logging.error(f"Supabase REST Session Error {res.status_code}: {res.text}")
            
            data = res.json()
            # If Prefer: return=representation is used, data is a list
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("id")
            return None
        except Exception as e:
            logging.error(f"Error executing HTTPX session logging: {e}")
            return None

    def log_app_security_report(self, scan_id: str, package_name: str, app_name: str, app_version: str, hash_sha256: str, security_score: int, is_malicious: bool, risk_level: str, threat_details: dict, report_pdf_url: str = None, status: str = 'completed'):
        try:
            payload = {
                "scan_id": scan_id if scan_id else None,
                "package_name": package_name,
                "app_name": app_name,
                "app_version": app_version,
                "hash_sha256": hash_sha256,
                "security_score": security_score,
                "is_malicious": is_malicious,
                "risk_level": risk_level,
                "threat_details": threat_details,
                "report_pdf_url": report_pdf_url,
                "status": status
            }
            res = httpx.post(
                f"{self.url}/rest/v1/app_security_reports", 
                headers=self.headers, 
                json=payload
            )
            if res.status_code >= 400:
                logging.error(f"Supabase REST App Result Error {res.status_code}: {res.text}")
            return res.json() if res.status_code == 201 else None
        except Exception as e:
            logging.error(f"Error executing HTTPX app result logging: {e}")
            return None

    def add_to_whitelist(self, user_id: str, package_name: str):
        try:
            payload = {
                "user_id": user_id if user_id else None,
                "package_name": package_name
            }
            res = httpx.post(
                f"{self.url}/rest/v1/user_whitelist", 
                headers=self.headers, 
                json=payload
            )
            if res.status_code >= 400:
                logging.error(f"Supabase REST Whitelist Error {res.status_code}: {res.text}")
            return res.json() if res.status_code == 201 else None
        except Exception as e:
            logging.error(f"Error executing HTTPX Whitelist logging: {e}")
            return None

    def log_pdf_report(self, file_name: str, file_path: str, file_size: str, scan_score: int, status: str, report_data: dict):
        try:
            payload = {
                "file_name": file_name,
                "file_path": file_path,
                "file_size": file_size,
                "scan_score": scan_score,
                "status": status,
                "report_data": report_data
            }
            res = httpx.post(
                f"{self.url}/rest/v1/pdf_reports", 
                headers=self.headers, 
                json=payload
            )
            if res.status_code >= 400:
                logging.error(f"Supabase REST PDF Result Error {res.status_code}: {res.text}")
            return res.json() if res.status_code == 201 else None
        except Exception as e:
            logging.error(f"Error executing HTTPX PDF result logging: {e}")
            return None

    def log_boost_session(self, user_id: str, memory_before: int, memory_after: int, apps_optimized: int, performance_score: int):
        try:
            payload = {
                "user_id": user_id if user_id else None,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "apps_optimized": apps_optimized,
                "performance_score": performance_score
            }
            res = httpx.post(
                f"{self.url}/rest/v1/boost_sessions", 
                headers=self.headers, 
                json=payload
            )
            if res.status_code >= 400:
                logging.error(f"Supabase REST Boost Session Error {res.status_code}: {res.text}")
            
            # 201 Created
            if res.status_code == 201:
                return True
            return False
        except Exception as e:
            logging.error(f"Error executing HTTPX boost session logging: {e}")
            return False

supabase_manager = SupabaseManager()
