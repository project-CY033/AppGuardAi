"""
Certificate and Signing Analysis Module
Based on DerScanner MAST and ImmuniWeb
"""

import os
import re
import zipfile
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CertificateInfo:
    """Certificate information"""
    is_signed: bool = False
    signer_name: str = ""
    validity_start: str = ""
    validity_end: str = ""
    algorithm: str = ""
    is_self_signed: bool = False
    is_debug_build: bool = False
    md5_fingerprint: str = ""
    sha1_fingerprint: str = ""
    sha256_fingerprint: str = ""


@dataclass
class SignatureInfo:
    """APK signature information"""
    signature_version: int = 0
    signature_files: List[str] = None
    certificate_chain_valid: bool = True
    timestamp_token: Optional[str] = None


class CertificateAnalyzer:
    """Analyze APK certificates and signing"""
    
    # Known debug signatures
    DEBUG_SIGNATURES = [
        "CN=Android Debug",
        "CN=Android, OU=Android, O=Google, L=Mountain View",
        "CN=Debug",
    ]
    
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.findings: List[Dict] = []
        
    def analyze(self) -> Dict[str, Any]:
        """Run certificate analysis"""
        cert_info = self._extract_certificate_info()
        sig_info = self._analyze_signature()
        self._check_certificate_security(cert_info, sig_info)
        self._check_v1_v2_signing()
        
        return {
            "certificate": cert_info.__dict__,
            "signature": {
                "version": sig_info.signature_version,
                "files": sig_info.signature_files or [],
                "chain_valid": sig_info.certificate_chain_valid,
            },
            "findings": self.findings,
        }
    
    def _extract_certificate_info(self) -> CertificateInfo:
        """Extract certificate information from APK"""
        info = CertificateInfo()
        
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                meta_inf_files = [f for f in zf.namelist() if f.startswith('META-INF/')]
                
                if meta_inf_files:
                    info.is_signed = True
                    info.signature_files = meta_inf_files
                    
                    # Check for .RSA, .DSA, .EC files
                    for f in meta_inf_files:
                        if f.endswith('.RSA'):
                            info.algorithm = "RSA"
                        elif f.endswith('.DSA'):
                            info.algorithm = "DSA"
                        elif f.endswith('.EC'):
                            info.algorithm = "EC"
                            
        except Exception as e:
            self.findings.append({
                "type": "error",
                "title": "Certificate Reading Error",
                "description": f"Could not read certificate: {str(e)}",
                "severity": "medium",
            })
        
        return info
    
    def _analyze_signature(self) -> SignatureInfo:
        """Analyze APK signature"""
        info = SignatureInfo()
        
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                # Check for v2/v3 signature (META-INF/*.SF files)
                sf_files = [f for f in zf.namelist() if f.endswith('.SF') and 'META-INF' in f]
                
                if sf_files:
                    info.signature_version = 1
                    
                    # Check for APK Signature Scheme v2/v3
                    # These are stored in the APK as magic bytes
                    with open(self.apk_path, 'rb') as f:
                        content = f.read()
                        # APK Signature Scheme v2 magic
                        if b'APK Sig Block 42' in content:
                            info.signature_version = 2
                        # APK Signature Scheme v3 magic (similar to v2)
                        if b'APK Sig Block 43' in content:
                            info.signature_version = 3
                            
        except Exception as e:
            pass
        
        return info
    
    def _check_certificate_security(self, cert_info: CertificateInfo, sig_info: SignatureInfo):
        """Check certificate security issues"""
        
        # Check if debug build
        for debug_sig in self.DEBUG_SIGNATURES:
            if debug_sig in cert_info.signer_name:
                cert_info.is_debug_build = True
                self.findings.append({
                    "type": "warning",
                    "title": "Debug Build Detected",
                    "description": "APK is signed with a debug certificate.",
                    "severity": "medium",
                    "recommendation": "Use release build for production.",
                })
                break
        
        # Check signature version
        if sig_info.signature_version < 2:
            self.findings.append({
                "type": "warning",
                "title": "Old Signature Scheme",
                "description": f"APK uses v{sig_info.signature_version} signature. Consider upgrading to v2+.",
                "severity": "low",
                "recommendation": "Enable APK Signature Scheme v2 or v3 for better security.",
            })
        
        # Check if self-signed
        if cert_info.is_self_signed:
            self.findings.append({
                "type": "warning",
                "title": "Self-Signed Certificate",
                "description": "APK uses self-signed certificate, not from a trusted CA.",
                "severity": "medium",
                "recommendation": "Use certificates from trusted Certificate Authorities.",
            })
    
    def _check_v1_v2_signing(self):
        """Check JAR and APK signature schemes"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                # Check for MANIFEST.MF
                if 'META-INF/MANIFEST.MF' not in zf.namelist():
                    self.findings.append({
                        "type": "warning",
                        "title": "Missing MANIFEST.MF",
                        "description": "No MANIFEST.MF found in APK.",
                        "severity": "low",
                    })
                    
        except Exception:
            pass


class NetworkSecurityAnalyzer:
    """Analyze network security configuration"""
    
    def __init__(self, extracted_dir: str):
        self.extracted_dir = extracted_dir
        self.findings: List[Dict] = []
        
    def analyze(self) -> Dict[str, Any]:
        """Run network security analysis"""
        nsc_config = self._parse_network_security_config()
        self._check_cleartext_traffic()
        self._check_certificate_pinning()
        self._check_domain_config()
        
        return {
            "network_config": nsc_config,
            "findings": self.findings,
        }
    
    def _parse_network_security_config(self) -> Dict[str, Any]:
        """Parse network_security_config.xml"""
        nsc_path = os.path.join(self.extracted_dir, "res", "xml", "network_security_config.xml")
        
        if not os.path.exists(nsc_path):
            self.findings.append({
                "type": "warning",
                "title": "No Network Security Config",
                "description": "App does not define network_security_config.xml.",
                "severity": "medium",
                "recommendation": "Create network_security_config.xml to configure network security.",
            })
            return {"exists": False}
        
        try:
            with open(nsc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = {
                "exists": True,
                "has_cleartext_traffic": 'cleartextTrafficPermitted="true"' in content,
                "has_pin_set": '<pin-set' in content,
                "has_trust_anchors": '<trust-anchors' in content,
            }
            
            return config
        except Exception:
            return {"exists": True, "parse_error": True}
    
    def _check_cleartext_traffic(self):
        """Check for cleartext traffic configuration"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if 'usesCleartextTraffic="true"' in content:
                self.findings.append({
                    "type": "warning",
                    "title": "Cleartext Traffic Enabled",
                    "description": "App allows unencrypted HTTP connections.",
                    "severity": "high",
                    "recommendation": "Set usesCleartextTraffic=\"false\" and use HTTPS only.",
                })
    
    def _check_certificate_pinning(self):
        """Check for certificate pinning"""
        nsc_path = os.path.join(self.extracted_dir, "res", "xml", "network_security_config.xml")
        
        if os.path.exists(nsc_path):
            with open(nsc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '<pin-set' not in content:
                self.findings.append({
                    "type": "info",
                    "title": "No Certificate Pinning",
                    "description": "Certificate pinning is not configured.",
                    "severity": "low",
                    "recommendation": "Consider implementing certificate pinning for sensitive connections.",
                })
    
    def _check_domain_config(self):
        """Check domain configuration"""
        # Look for domain configurations in code
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for hardcoded URLs
                        urls = re.findall(r'https?://[^\s"\'<>]+', content)
                        for url in urls:
                            if 'localhost' in url or '192.168.' in url or '10.0.' in url:
                                self.findings.append({
                                    "type": "warning",
                                    "title": "Hardcoded Local URL",
                                    "description": f"Found hardcoded local URL: {url}",
                                    "severity": "medium",
                                    "recommendation": "Use configuration instead of hardcoded URLs.",
                                })
                    except Exception:
                        pass


class CryptoAnalyzer:
    """Analyze cryptographic implementations"""
    
    WEAK_ALGORITHMS = {
        "DES": "Data Encryption Standard - deprecated",
        "3DES": "Triple DES - deprecated",
        "RC4": "RC4 stream cipher - insecure",
        "MD5": "MD5 hashing - collision vulnerabilities",
        "SHA1": "SHA-1 hashing - collision vulnerabilities",
    }
    
    STRONG_ALGORITHMS = ["AES", "SHA-256", "SHA-512", "RSA-2048", "ECDSA", "ChaCha20"]
    
    def __init__(self, extracted_dir: str):
        self.extracted_dir = extracted_dir
        self.findings: List[Dict] = []
        
    def analyze(self) -> Dict[str, Any]:
        """Run cryptographic analysis"""
        weak_algos = self._check_weak_algorithms()
        self._check_secure_random()
        self._check_key_storage()
        
        return {
            "weak_algorithms_found": weak_algos,
            "findings": self.findings,
        }
    
    def _check_weak_algorithms(self) -> List[str]:
        """Check for weak cryptographic algorithms"""
        found_weak = []
        
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt', '.smali')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for algo, desc in self.WEAK_ALGORITHMS.items():
                            if algo in content:
                                found_weak.append(algo)
                                self.findings.append({
                                    "type": "warning",
                                    "title": f"Weak Algorithm: {algo}",
                                    "description": desc,
                                    "severity": "high",
                                    "file": filepath,
                                    "recommendation": f"Replace {algo} with AES or ChaCha20.",
                                })
                    except Exception:
                        pass
        
        return list(set(found_weak))
    
    def _check_secure_random(self):
        """Check for insecure random number generation"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for insecure Random usage
                        if 'java.util.Random' in content and 'SecureRandom' not in content:
                            self.findings.append({
                                "type": "warning",
                                "title": "Insecure Random Number Generator",
                                "description": "Using java.util.Random for security purposes.",
                                "severity": "high",
                                "file": filepath,
                                "recommendation": "Use SecureRandom for cryptographic purposes.",
                            })
                    except Exception:
                        pass
    
    def _check_key_storage(self):
        """Check for insecure key storage"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for insecure key storage patterns
                        if 'SharedPreferences' in content and ('key' in content.lower() or 'secret' in content.lower()):
                            self.findings.append({
                                "type": "warning",
                                "title": "Key Stored in SharedPreferences",
                                "description": "Cryptographic keys may be stored in SharedPreferences.",
                                "severity": "high",
                                "file": filepath,
                                "recommendation": "Use Android Keystore for key storage.",
                            })
                    except Exception:
                        pass


class DataStorageAnalyzer:
    """Analyze data storage security"""
    
    def __init__(self, extracted_dir: str):
        self.extracted_dir = extracted_dir
        self.findings: List[Dict] = []
        
    def analyze(self) -> Dict[str, Any]:
        """Run data storage analysis"""
        self._check_external_storage()
        self._check_logging()
        self._check_backup_config()
        self._check_content_providers()
        
        return {
            "findings": self.findings,
        }
    
    def _check_external_storage(self):
        """Check for external storage usage"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        insecure_patterns = [
                            ('getExternalStorageDirectory', 'Uses deprecated external storage'),
                            ('getExternalFilesDir', 'Uses external files directory'),
                            ('MODE_WORLD_READABLE', 'World-readable file mode'),
                            ('MODE_WORLD_WRITEABLE', 'World-writable file mode'),
                        ]
                        
                        for pattern, desc in insecure_patterns:
                            if pattern in content:
                                self.findings.append({
                                    "type": "warning",
                                    "title": f"External Storage: {pattern}",
                                    "description": desc,
                                    "severity": "high" if "WORLD" in pattern else "medium",
                                    "file": filepath,
                                    "recommendation": "Use internal storage or encrypted external storage.",
                                })
                    except Exception:
                        pass
    
    def _check_logging(self):
        """Check for sensitive data logging"""
        sensitive_terms = ['password', 'token', 'secret', 'credit', 'ssn', 'api_key', 'auth']
        
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                            for term in sensitive_terms:
                                log_pattern = rf'Log\.\w+\(.*{term}'
                                if re.search(log_pattern, content, re.IGNORECASE):
                                    self.findings.append({
                                        "type": "warning",
                                        "title": f"Sensitive Data Logged: {term}",
                                        "description": "App may log sensitive information.",
                                        "severity": "high",
                                        "file": filepath,
                                        "recommendation": "Remove logging of sensitive data.",
                                    })
                    except Exception:
                        pass
    
    def _check_backup_config(self):
        """Check Android backup configuration"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if 'android:allowBackup="true"' in content:
                self.findings.append({
                    "type": "info",
                    "title": "Backup Enabled",
                    "description": "App allows backup, sensitive data may be exposed.",
                    "severity": "low",
                    "recommendation": "Consider setting allowBackup=\"false\" for sensitive apps.",
                })
    
    def _check_content_providers(self):
        """Check exported content providers"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find exported providers
            providers = re.findall(r'<provider[^>]*exported="true"[^>]*>', content)
            
            for provider in providers:
                if 'permission' not in provider.lower():
                    self.findings.append({
                        "type": "warning",
                        "title": "Exported Provider Without Permission",
                        "description": "Content provider exported without permission protection.",
                        "severity": "high",
                        "recommendation": "Add permission to exported content provider.",
                    })


class AdvancedComplianceReporter:
    """Generate compliance reports for various standards"""
    
    STANDARDS = {
        "OWASP_MASVS_L1": "OWASP MASVS Level 1 - Baseline",
        "OWASP_MASVS_L2": "OWASP MASVS Level 2 - Defense in Depth",
        "OWASP_MASVS_R": "OWASP MASVS - Reverse Engineering",
        "PCI_DSS": "Payment Card Industry Data Security Standard",
        "HIPAA": "Health Insurance Portability and Accountability Act",
        "GDPR": "General Data Protection Regulation",
        "SOC2": "Service Organization Control 2",
    }
    
    def generate_compliance_report(self, all_findings: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "standards": {},
        }
        
        # OWASP MASVS L1 compliance
        masvs_l1 = self._check_masvs_l1(all_findings)
        report["standards"]["OWASP_MASVS_L1"] = masvs_l1
        
        # GDPR compliance (data privacy)
        gdpr = self._check_gdpr_compliance(all_findings)
        report["standards"]["GDPR"] = gdpr
        
        # General security score
        report["overall_score"] = self._calculate_security_score(all_findings)
        report["grade"] = self._get_grade(report["overall_score"])
        
        return report
    
    def _check_masvs_l1(self, findings: List[Dict]) -> Dict[str, Any]:
        """Check OWASP MASVS Level 1 compliance"""
        controls = {
            "V1.1": {"name": "App permissions", "passed": True},
            "V2.1": {"name": "Cryptography", "passed": True},
            "V3.1": {"name": "Data storage", "passed": True},
            "V4.1": {"name": "Input validation", "passed": True},
            "V5.1": {"name": "Network security", "passed": True},
        }
        
        # Check findings against controls
        for finding in findings:
            title = finding.get("title", "").lower()
            
            if "permission" in title:
                controls["V1.1"]["passed"] = False
            if "algorithm" in title or "crypto" in title:
                controls["V2.1"]["passed"] = False
            if "storage" in title or "external" in title:
                controls["V3.1"]["passed"] = False
            if "network" in title or "cleartext" in title:
                controls["V5.1"]["passed"] = False
        
        passed = sum(1 for c in controls.values() if c["passed"])
        total = len(controls)
        
        return {
            "compliant": passed >= 4,
            "score": f"{passed}/{total}",
            "percentage": round((passed / total) * 100, 1),
            "controls": controls,
        }
    
    def _check_gdpr_compliance(self, findings: List[Dict]) -> Dict[str, Any]:
        """Check GDPR compliance indicators"""
        issues = []
        
        for finding in findings:
            title = finding.get("title", "").lower()
            desc = finding.get("description", "").lower()
            
            if "permission" in title and "dangerous" in desc:
                issues.append("Excessive permissions may collect personal data")
            if "contact" in title or "location" in title:
                issues.append("Access to personal data requires consent")
            if "network" in title or "http" in title:
                issues.append("Data transmission must be encrypted")
        
        return {
            "compliant": len(issues) == 0,
            "issues": list(set(issues))[:10],
            "recommendation": "Ensure proper consent flows for data collection.",
        }
    
    def _calculate_security_score(self, findings: List[Dict]) -> int:
        """Calculate overall security score"""
        score = 100
        
        for finding in findings:
            severity = finding.get("severity", "low")
            if severity == "critical":
                score -= 20
            elif severity == "high":
                score -= 10
            elif severity == "medium":
                score -= 5
            elif severity == "low":
                score -= 2
        
        return max(0, score)
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"