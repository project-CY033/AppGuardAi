import os
import logging
from typing import Dict, Any, List
import hashlib
from services.analysis.virustotal import vt_client

try:
    from androguard.core.bytecodes.apk import APK
except ImportError:
    logging.warning("Androguard is missing. The APK scanner will not physically decode bytecodes.")
    APK = None

class APKReverserService:
    def __init__(self):
        self.critical_permissions = [
            "android.permission.READ_SMS",
            "android.permission.RECEIVE_SMS",
            "android.permission.SYSTEM_ALERT_WINDOW",
            "android.permission.RECORD_AUDIO",
            "android.permission.READ_CONTACTS"
        ]

    async def analyze_apk(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        logging.info(f"Starting hardware decompilation of {original_filename}...")
        result = {
            "app_name": original_filename,
            "package_name": "unknown_package",
            "permissions": [],
            "critical_flags": [],
            "risk_score": 0,
            "is_safe": True,
            "is_malicious": False,
            "risk_level": "Safe",
            "threat_details": {}
        }

        # 1. Simple yara-style binary heuristic signature scanning
        binary_hash = ""
        with open(file_path, "rb") as f:
            binary_content = f.read()
            binary_hash = hashlib.sha256(binary_content).hexdigest()
            result['file_sha256'] = binary_hash
            
            if b"hidden_miner" in binary_content or b"cmd.exe" in binary_content:
                result['critical_flags'].append("YARA Match: Remote Code Execution/Mining Hex String Detected")
                result['risk_score'] += 60

        # 2. VirusTotal Hash Check
        vt_found, vt_data = await vt_client.check_hash(binary_hash)
        if vt_found and "malicious" in vt_data:
            malicious_hits = vt_data.get("malicious", 0)
            if malicious_hits > 0:
                result['critical_flags'].append(f"VirusTotal flagged {malicious_hits} engines as malicious.")
                result['risk_score'] += (malicious_hits * 10)
                result['threat_details']['virustotal'] = f"{malicious_hits} engines flagged this hash."

        if not APK:
            result['critical_flags'].append("Androguard unavailable to decode Manifest. Falling back.")
        else:
            try:
                apk_obj = APK(file_path)
                result['package_name'] = apk_obj.get_package()
                app_n = apk_obj.get_app_name()
                if app_n:
                    result['app_name'] = app_n
                permissions = apk_obj.get_permissions()
                result['permissions'] = permissions

                for perm in permissions:
                    if perm in self.critical_permissions:
                        result['critical_flags'].append(f"Severely sensitive permission requested: {perm}")
                        result['risk_score'] += 15

                if len(permissions) > 30:
                    result['critical_flags'].append("Application is demanding an unusually high quantity of system access privileges (> 30).")
                    result['risk_score'] += 20

            except Exception as e:
                logging.error(f"Error during physical APK decompression: {e}")
                result['critical_flags'].append(f"Decompilation Obfuscation Error: {e}")
                result['risk_score'] += 25

        final_score = min(result['risk_score'], 100)
        
        # MobSF severity mapping
        risk_level = "Safe"
        is_malicious = False
        
        if final_score >= 70:
            risk_level = "High"
            is_malicious = True
        elif final_score >= 30:
            risk_level = "Medium"
        elif final_score >= 10:
            risk_level = "Low"

        if result['critical_flags'] and not result['threat_details']:
            result['threat_details']['heuristics'] = result['critical_flags']

        result['risk_score'] = 100 - final_score # Score out of 100 where 100 is safe
        result['risk_level'] = risk_level
        result['is_malicious'] = is_malicious
        result['is_safe'] = not is_malicious

        logging.info(f"Deep Analysis Completed for {original_filename}: Scored {result['risk_score']}")
        return result

apk_reverser = APKReverserService()
