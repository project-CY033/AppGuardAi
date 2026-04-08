"""
Advanced APK Security Scanner
Features based on: BeVigil, ImmuniWeb, DerScanner, Quixxi
Implements: OWASP MASVS, SAST, SCA, Secret Detection, Malware Scanning,
            Certificate Analysis, Network Security, Crypto Analysis
"""

import os
import re
import json
import hashlib
import zipfile
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import struct

# Import additional analyzers
from app.core.certificate_analyzer import (
    CertificateAnalyzer,
    NetworkSecurityAnalyzer,
    CryptoAnalyzer,
    DataStorageAnalyzer,
    AdvancedComplianceReporter,
)


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanCategory(Enum):
    OWASP_MASVS = "OWASP MASVS"
    SAST = "Static Analysis"
    SCA = "Software Composition"
    SECRETS = "Secret Detection"
    MALWARE = "Malware Detection"
    CERTIFICATE = "Certificate Analysis"
    PERMISSION = "Permission Analysis"
    NETWORK = "Network Security"
    CRYPTO = "Cryptography"
    STORAGE = "Data Storage"
    CODE_QUALITY = "Code Quality"


@dataclass
class SecurityFinding:
    category: ScanCategory
    title: str
    description: str
    risk_level: RiskLevel
    evidence: str = ""
    file_path: str = ""
    line_number: int = 0
    owasp_id: str = ""
    cwe_id: str = ""
    recommendation: str = ""
    confidence: int = 80  # 0-100


@dataclass
class ScanResult:
    scan_id: str
    package_name: str
    app_name: str
    version: str
    risk_score: int  # 0-100
    risk_level: str
    findings: List[SecurityFinding] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    compliance: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# OWASP MASVS V1: Architecture, Design and Threat Modeling
# ============================================================================

class OWASPMASVSScanner:
    """OWASP MASVS compliance scanner"""
    
    MASVS_CONTROLS = {
        "V1.1": "The app correctly requests and uses permissions",
        "V1.2": "The app does not expose sensitive data via IPC",
        "V1.3": "The app does not export sensitive components via IPC",
        "V1.4": "The app does not leak personal data to third parties",
        "V2.1": "The app uses industry-standard cryptography",
        "V2.2": "The app does not use hardcoded cryptographic keys",
        "V2.3": "The app uses secure random number generation",
        "V3.1": "The app stores sensitive data in secure storage",
        "V3.2": "The app does not store sensitive data in external storage",
        "V3.3": "The app does not store sensitive data in logs",
        "V4.1": "The app validates all user input",
        "V4.2": "The app does not execute code from untrusted sources",
        "V4.3": "The app uses WebViews securely",
        "V5.1": "The app uses certificate pinning for sensitive connections",
        "V5.2": "The app uses HTTPS for all network communications",
        "V5.3": "The app authenticates all network connections",
        "V6.1": "The app prevents memory leaks of sensitive data",
        "V6.2": "The app uses anti-tampering mechanisms",
        "V6.3": "The app has anti-debugging protections",
        "V7.1": "The app uses the least privileged permissions",
        "V7.2": "The app does not expose IPC components to other apps",
        "V7.3": "The app does not expose WebView to untrusted content",
    }

    def __init__(self, apk_path: str, extracted_dir: str):
        self.apk_path = apk_path
        self.extracted_dir = extracted_dir
        self.findings: List[SecurityFinding] = []

    def scan(self) -> List[SecurityFinding]:
        """Run all MASVS checks"""
        self._check_permissions()
        self._check_crypto()
        self._check_storage()
        self._check_network_security()
        self._check_webviews()
        self._check_ipc_export()
        self._check_logging()
        return self.findings

    def _check_permissions(self):
        """V1.1: Check permission usage"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        dangerous_permissions = {
            "SEND_SMS": "Allows sending SMS messages",
            "RECEIVE_SMS": "Allows receiving SMS messages",
            "READ_SMS": "Allows reading SMS messages",
            "CAMERA": "Allows camera access",
            "RECORD_AUDIO": "Allows microphone access",
            "ACCESS_FINE_LOCATION": "Allows precise location access",
            "ACCESS_COARSE_LOCATION": "Allows coarse location access",
            "READ_CONTACTS": "Allows reading contacts",
            "WRITE_CONTACTS": "Allows writing contacts",
            "READ_PHONE_STATE": "Allows reading phone state",
            "CALL_PHONE": "Allows making phone calls",
            "READ_EXTERNAL_STORAGE": "Allows reading external storage",
            "WRITE_EXTERNAL_STORAGE": "Allows writing external storage",
        }
        
        for perm, desc in dangerous_permissions.items():
            if perm in content:
                self.findings.append(SecurityFinding(
                    category=ScanCategory.PERMISSION,
                    title=f"Dangerous Permission: {perm}",
                    description=f"{desc}. Verify this permission is necessary.",
                    risk_level=RiskLevel.MEDIUM,
                    owasp_id="V1.1",
                    cwe_id="CWE-250",
                    recommendation="Use the principle of least privilege. Request permissions only when needed."
                ))

    def _check_crypto(self):
        """V2.2: Check for hardcoded cryptographic keys"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt', '.xml', '.properties')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for hardcoded keys
                        key_patterns = [
                            (r'(?:key|secret|password|token)\s*[=:]\s*["\'][A-Za-z0-9+/=]{16,}["\']', "Hardcoded secret"),
                            (r'(?:AES|DES|RSA|CBC|ECB)\s*[=:]\s*["\'][^"\']+["\']', "Hardcoded algorithm configuration"),
                            (r'0x[0-9A-Fa-f]{16,}', "Possible hardcoded key in hex"),
                        ]
                        
                        for pattern, desc in key_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                self.findings.append(SecurityFinding(
                                    category=ScanCategory.CRYPTO,
                                    title=f"Hardcoded Cryptographic Material: {desc}",
                                    description="Found hardcoded cryptographic keys or configuration.",
                                    risk_level=RiskLevel.HIGH,
                                    file_path=filepath,
                                    owasp_id="V2.2",
                                    cwe_id="CWE-798",
                                    recommendation="Store cryptographic keys in Android Keystore, not in code."
                                ))
                    except Exception:
                        pass

    def _check_storage(self):
        """V3.1-V3.3: Check for insecure data storage"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for insecure storage patterns
                        insecure_patterns = [
                            (r'getExternalStorageDirectory', "External storage usage"),
                            (r'openFileOutput.*MODE_WORLD_READABLE', "World-readable file"),
                            (r'getSharedPreferences.*MODE_WORLD_READABLE', "World-readable preferences"),
                            (r'Log\.\w+\(.*(?:password|token|key|secret|credit)', "Sensitive data in logs"),
                        ]
                        
                        for pattern, desc in insecure_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                risk = RiskLevel.HIGH if "World" in desc or "password" in desc.lower() else RiskLevel.MEDIUM
                                self.findings.append(SecurityFinding(
                                    category=ScanCategory.STORAGE,
                                    title=f"Insecure Storage: {desc}",
                                    description=f"Potential insecure data storage detected.",
                                    risk_level=risk,
                                    file_path=filepath,
                                    owasp_id="V3.1" if "World" in desc else "V3.3",
                                    cwe_id="CWE-200",
                                    recommendation="Use internal storage or encrypted SharedPreferences for sensitive data."
                                ))
                    except Exception:
                        pass

    def _check_network_security(self):
        """V5.1-V5.3: Check network security configuration"""
        nsc_path = os.path.join(self.extracted_dir, "res", "xml", "network_security_config.xml")
        
        if not os.path.exists(nsc_path):
            self.findings.append(SecurityFinding(
                category=ScanCategory.NETWORK,
                title="No Network Security Configuration",
                description="App does not define network security configuration.",
                risk_level=RiskLevel.MEDIUM,
                owasp_id="V5.1",
                cwe_id="CWE-319",
                recommendation="Add network_security_config.xml with certificate pinning."
            ))
        
        # Check for cleartext traffic
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if 'usesCleartextTraffic="true"' in content:
                self.findings.append(SecurityFinding(
                    category=ScanCategory.NETWORK,
                    title="Cleartext Traffic Enabled",
                    description="App allows unencrypted HTTP traffic.",
                    risk_level=RiskLevel.HIGH,
                    owasp_id="V5.2",
                    cwe_id="CWE-319",
                    recommendation="Disable cleartext traffic and use HTTPS only."
                ))

    def _check_webviews(self):
        """V4.3: Check WebView security"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if 'setJavaScriptEnabled(true)' in content:
                            self.findings.append(SecurityFinding(
                                category=ScanCategory.SAST,
                                title="JavaScript Enabled in WebView",
                                description="JavaScript is enabled in WebView, which may increase attack surface.",
                                risk_level=RiskLevel.MEDIUM,
                                file_path=filepath,
                                owasp_id="V4.3",
                                cwe_id="CWE-79",
                                recommendation="Only enable JavaScript if absolutely necessary and validate all inputs."
                            ))
                        
                        if 'addJavascriptInterface' in content:
                            self.findings.append(SecurityFinding(
                                category=ScanCategory.SAST,
                                title="JavaScript Interface in WebView",
                                description="JavaScript interface allows JS to access native code.",
                                risk_level=RiskLevel.HIGH,
                                file_path=filepath,
                                owasp_id="V4.3",
                                cwe_id="CWE-749",
                                recommendation="Be careful with JavaScript interfaces on Android < 4.2."
                            ))
                    except Exception:
                        pass

    def _check_ipc_export(self):
        """V1.2-V1.3: Check exported components"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        exported_patterns = [
            (r'<activity[^>]*android:exported="true"', "Exported Activity"),
            (r'<service[^>]*android:exported="true"', "Exported Service"),
            (r'<receiver[^>]*android:exported="true"', "Exported Receiver"),
            (r'<provider[^>]*android:exported="true"', "Exported Provider"),
        ]
        
        for pattern, comp_type in exported_patterns:
            if re.search(pattern, content):
                self.findings.append(SecurityFinding(
                    category=ScanCategory.SAST,
                    title=f"{comp_type} Without Permission",
                    description=f"Found {comp_type.lower()} with exported=true. Ensure proper permissions.",
                    risk_level=RiskLevel.MEDIUM,
                    owasp_id="V1.3",
                    cwe_id="CWE-200",
                    recommendation="Add android:permission attribute to protect exported components."
                ))

    def _check_logging(self):
        """V3.3: Check for sensitive data logging"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for sensitive logging
                        sensitive_terms = ['password', 'token', 'secret', 'credit_card', 'ssn', 'ap
                        i_key']
                        for term in sensitive_terms:
                            if re.search(rf'Log\.\w+\(.*{term}', content, re.IGNORECASE):
                                self.findings.append(SecurityFinding(
                                    category=ScanCategory.STORAGE,
                                    title=f"Sensitive Data Logging: {term}",
                                    description=f"App may log sensitive data ({term}).",
                                    risk_level=RiskLevel.MEDIUM,
                                    file_path=filepath,
                                    owasp_id="V3.3",
                                    cwe_id="CWE-532",
                                    recommendation="Remove all logging of sensitive information in production."
                                ))
                    except Exception:
                        pass


# ============================================================================
# Secret Detection Scanner (Based on BeVigil)
# ============================================================================

class SecretDetector:
    """Detect hardcoded secrets, API keys, and credentials"""
    
    SECRET_PATTERNS = [
        # API Keys
        (r'(?i)(api[_-]?key|apikey)["\s:=]+["\']([a-zA-Z0-9_\-]{16,})["\']', "API Key", RiskLevel.HIGH),
        (r'(?i)sk_live_[a-zA-Z0-9]{24,}', "Stripe Live Secret Key", RiskLevel.CRITICAL),
        (r'(?i)sk_test_[a-zA-Z0-9]{24,}', "Stripe Test Secret Key", RiskLevel.HIGH),
        (r'(?i)AKIA[0-9A-Z]{16}', "AWS Access Key", RiskLevel.CRITICAL),
        (r'(?i)(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])', "Possible AWS Secret Key", RiskLevel.CRITICAL),
        
        # Passwords
        (r'(?i)(password|passwd|pwd)["\s:=]+["\']([^"\']{4,})["\']', "Hardcoded Password", RiskLevel.CRITICAL),
        (r'(?i)basic\s+[a-zA-Z0-9+/=]{10,}', "Basic Auth Header", RiskLevel.HIGH),
        
        # Tokens
        (r'(?i)(token|auth|bearer|jwt)["\s:=]+["\']([a-zA-Z0-9_\-\.]{20,})["\']', "Authentication Token", RiskLevel.HIGH),
        (r'(?i)ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token", RiskLevel.CRITICAL),
        (r'(?i)glpat-[a-zA-Z0-9\-]{20}', "GitLab Personal Access Token", RiskLevel.CRITICAL),
        
        # Private Keys
        (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private Key", RiskLevel.CRITICAL),
        (r'-----BEGIN ENCRYPTED PRIVATE KEY-----', "Encrypted Private Key", RiskLevel.HIGH),
        
        # Database
        (r'(?i)(mongodb|mysql|postgres|redis)://[^\s\'"]+', "Database Connection String", RiskLevel.CRITICAL),
        
        # Firebase
        (r'(?i)AIza[0-9A-Za-z\-_]{35}', "Firebase API Key", RiskLevel.HIGH),
        
        # Slack
        (r'(?i)xox[bpors]-[0-9]{10,13}-[a-zA-Z0-9]{24,34}', "Slack Token", RiskLevel.CRITICAL),
        
        # Google OAuth
        (r'(?i)[0-9]+-[a-zA-Z0-9_]{32}\.apps\.googleusercontent\.com', "Google OAuth Client ID", RiskLevel.MEDIUM),
    ]

    def __init__(self, extracted_dir: str):
        self.extracted_dir = extracted_dir
        self.findings: List[SecurityFinding] = []

    def scan(self) -> List[SecurityFinding]:
        """Scan all files for secrets"""
        skip_dirs = {'META-INF', 'kotlin', 'okhttp', 'android', 'google', 'com/google', 'org/apache'}
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ttf', '.otf', '.woff', '.so', '.dex'}
        
        for root, dirs, files in os.walk(self.extracted_dir):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in skip_extensions):
                    continue
                    
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern, secret_type, risk_level in self.SECRET_PATTERNS:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            self.findings.append(SecurityFinding(
                                category=ScanCategory.SECRETS,
                                title=f"{secret_type} Found",
                                description=f"Detected {secret_type} in source code.",
                                risk_level=risk_level,
                                file_path=filepath,
                                line_number=line_num,
                                cwe_id="CWE-798",
                                recommendation="Move secrets to environment variables or secure key management."
                            ))
                except Exception:
                    pass
        
        return self.findings


# ============================================================================
# Software Composition Analysis (SCA) - Based on DerScanner
# ============================================================================

class SoftwareCompositionAnalyzer:
    """Analyze third-party libraries for known vulnerabilities"""
    
    # Known vulnerable libraries database (simplified)
    VULNERABLE_LIBS = {
        "okhttp3": {"versions": ["3.12.0", "3.12.1"], "cve": "CVE-2023-0833", "severity": "high"},
        "gson": {"versions": ["2.8.5"], "cve": "CVE-2022-25647", "severity": "high"},
        "jackson-databind": {"versions": ["2.9.8", "2.9.9"], "cve": "CVE-2019-14540", "severity": "critical"},
        "retrofit": {"versions": ["2.4.0"], "cve": "CVE-2018-1000850", "severity": "medium"},
        "glide": {"versions": ["4.8.0"], "cve": "CVE-2020-15258", "severity": "medium"},
        "picasso": {"versions": ["2.71828"], "cve": "KNOWN-VULN", "severity": "medium"},
        "butterknife": {"versions": ["8.8.1"], "cve": "CVE-2019-10164", "severity": "low"},
        "dagger": {"versions": ["2.15"], "cve": "CVE-2018-1000845", "severity": "low"},
        "exoplayer": {"versions": ["2.9.0", "2.9.1", "2.9.2"], "cve": "CVE-2020-13396", "severity": "high"},
        "leakcanary": {"versions": ["1.6.1"], "cve": "KNOWN-VULN", "severity": "info"},
    }
    
    # Suspicious URLs in code
    SUSPICIOUS_PATTERNS = [
        (r'http://[^\s"\'<>]+', "HTTP URL (unencrypted)"),
        (r'ftp://[^\s"\'<>]+', "FTP URL (insecure protocol)"),
    ]

    def __init__(self, extracted_dir: str):
        self.extracted_dir = extracted_dir
        self.findings: List[SecurityFinding] = []
        self.libraries: List[Dict[str, Any]] = []

    def scan(self) -> List[SecurityFinding]:
        """Run SCA analysis"""
        self._detect_libraries()
        self._check_vulnerable_libraries()
        self._scan_suspicious_urls()
        self._check_obfuscated_code()
        return self.findings

    def _detect_libraries(self):
        """Detect libraries from various sources"""
        # Check build.gradle
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file == "build.gradle" or file == "build.gradle.kts":
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Parse dependencies
                        dep_patterns = [
                            r'(?:implementation|api|compile)\s+["\']([^"\']+)["\']',
                            r'(?:implementation|api|compile)\s+\(.*["\']([^"\']+)["\']',
                        ]
                        
                        for pattern in dep_patterns:
                            for match in re.finditer(pattern, content):
                                dep = match.group(1)
                                self.libraries.append({"name": dep, "source": "gradle"})
                    except Exception:
                        pass
        
        # Check for library signatures in smali
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith('.smali'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Detect library packages
                        lib_indicators = [
                            'Lcom/squareup/okhttp3/',  # OkHttp
                            'Lcom/google/gson/',       # Gson
                            'Lcom/fasterxml/jackson/', # Jackson
                            'Lretrofit2/',             # Retrofit
                            'Lcom/bumptech/glide/',    # Glide
                            'Lcom/squareup/picasso/',  # Picasso
                            'Lcom/google/firebase/',   # Firebase
                            'Lcom/facebook/',          # Facebook SDK
                        ]
                        
                        for indicator in lib_indicators:
                            if indicator in content:
                                lib_name = indicator.split('/')[-2]
                                if lib_name not in [l['name'] for l in self.libraries]:
                                    self.libraries.append({"name": lib_name, "source": "smali"})
                    except Exception:
                        pass

    def _check_vulnerable_libraries(self):
        """Check libraries against vulnerability database"""
        for lib in self.libraries:
            lib_name = lib['name'].lower()
            for vuln_lib, vuln_info in self.VULNERABLE_LIBS.items():
                if vuln_lib.lower() in lib_name:
                    self.findings.append(SecurityFinding(
                        category=ScanCategory.SCA,
                        title=f"Potentially Vulnerable Library: {vuln_lib}",
                        description=f"Library {vuln_lib} may have known vulnerabilities ({vuln_info.get('cve', 'N/A')}).",
                        risk_level=RiskLevel.HIGH if vuln_info['severity'] == 'high' else RiskLevel.MEDIUM,
                        cwe_id="CWE-1104",
                        recommendation=f"Update to the latest version of {vuln_lib}."
                    ))

    def _scan_suspicious_urls(self):
        """Scan for suspicious URLs"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith(('.java', '.kt', '.xml', '.smali')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for pattern, desc in self.SUSPICIOUS_PATTERNS:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                url = match.group(0)
                                # Skip common Android URLs
                                if any(skip in url for skip in ['android.com', 'googleapis.com', 'schemas.android.com']):
                                    continue
                                
                                self.findings.append(SecurityFinding(
                                    category=ScanCategory.NETWORK,
                                    title=f"Suspicious URL: {desc}",
                                    description=f"Found {desc}: {url[:100]}",
                                    risk_level=RiskLevel.LOW if "HTTP" in desc else RiskLevel.MEDIUM,
                                    file_path=filepath,
                                    recommendation="Use HTTPS instead of HTTP for all network communications."
                                ))
                    except Exception:
                        pass

    def _check_obfuscated_code(self):
        """Check for code obfuscation (could indicate malicious intent)"""
        smali_dir = os.path.join(self.extracted_dir, "smali")
        if not os.path.exists(smali_dir):
            return
        
        obfuscated_classes = 0
        total_classes = 0
        
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    total_classes += 1
                    # Check for single-letter class names (obfuscation)
                    if len(file.replace('.smali', '')) <= 2:
                        obfuscated_classes += 1
        
        if total_classes > 0:
            obfuscation_ratio = obfuscated_classes / total_classes
            if obfuscation_ratio > 0.5:
                self.findings.append(SecurityFinding(
                    category=ScanCategory.CODE_QUALITY,
                    title="Code Heavily Obfuscated",
                    description=f"{obfuscation_ratio:.1%} of classes appear obfuscated.",
                    risk_level=RiskLevel.MEDIUM,
                    recommendation="Obfuscation may indicate malicious code. Review carefully."
                ))


# ============================================================================
# Malware Detection Scanner
# ============================================================================

class MalwareScanner:
    """Detect potential malware indicators"""
    
    # Dangerous permission combinations
    DANGEROUS_COMBOS = [
        (["SEND_SMS", "READ_SMS", "RECEIVE_SMS"], "SMS Stealer/Spammer"),
        (["CAMERA", "RECORD_AUDIO", "ACCESS_FINE_LOCATION"], "Spyware"),
        (["READ_CONTACTS", "READ_SMS", "READ_PHONE_STATE"], "Data Stealer"),
        (["INTERNET", "SEND_SMS", "READ_SMS"], "Premium SMS Fraud"),
        (["INTERNET", "READ_CONTACTS", "SEND_SMS"], "Contact Stealer"),
        (["INTERNET", "RECORD_AUDIO", "CAMERA"], "Surveillance"),
    ]
    
    # Known malware signatures (simplified patterns)
    MALWARE_SIGNATURES = [
        (r'Landroid/content/Context;->getInstalledPackages', "Enumeration of installed packages"),
        (r'Landroid/telephony/SmsManager;->sendTextMessage', "SMS sending capability"),
        (r'Landroid/app/DeviceAdminReceiver', "Device admin privileges"),
        (r'Landroid/content/Intent;->ACTION_DELETE', "App uninstall capability"),
        (r'Landroid/provider/Settings;->ACTION_MANAGE_OVERLAY_PERMISSION', "Overlay permission (for clickjacking)"),
        (r'Landroid/accessibilityservice/AccessibilityService', "Accessibility service (keylogger potential)"),
        (r'Landroid/app/UsageStatsManager', "App usage monitoring"),
        (r'Landroid/app/admin/DevicePolicyManager', "Device policy management"),
    ]

    def __init__(self, extracted_dir: str, permissions: List[str]):
        self.extracted_dir = extracted_dir
        self.permissions = permissions
        self.findings: List[SecurityFinding] = []

    def scan(self) -> List[SecurityFinding]:
        """Run malware detection"""
        self._check_dangerous_permission_combos()
        self._scan_malware_signatures()
        self._check_suspicious_intents()
        self._check_dynamic_code_loading()
        self._check_suspicious_permissions()
        return self.findings

    def _check_dangerous_permission_combos(self):
        """Check for dangerous permission combinations"""
        for combo, threat in self.DANGEROUS_COMBOS:
            if all(p in self.permissions for p in combo):
                self.findings.append(SecurityFinding(
                    category=ScanCategory.MALWARE,
                    title=f"Suspicious Permission Combination: {threat}",
                    description=f"App requests permissions commonly used by {threat.lower()}: {', '.join(combo)}",
                    risk_level=RiskLevel.HIGH,
                    cwe_id="CWE-250",
                    recommendation=f"Verify if {threat.lower()} functionality is necessary."
                ))

    def _scan_malware_signatures(self):
        """Scan for malware signatures"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith('.smali'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for pattern, desc in self.MALWARE_SIGNATURES:
                            if re.search(pattern, content):
                                self.findings.append(SecurityFinding(
                                    category=ScanCategory.MALWARE,
                                    title=f"Malware Indicator: {desc}",
                                    description=f"Found code pattern associated with malicious behavior.",
                                    risk_level=RiskLevel.HIGH,
                                    file_path=filepath,
                                    cwe_id="CWE-506",
                                    recommendation="Review the functionality carefully for malicious intent."
                                ))
                    except Exception:
                        pass

    def _check_suspicious_intents(self):
        """Check for suspicious intent filters"""
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        suspicious_actions = [
            "android.intent.action.BOOT_COMPLETED",
            "android.intent.action.PHONE_STATE",
            "android.intent.action.NEW_OUTGOING_CALL",
            "android.intent.action.SEND_MULTIPLE",
            "android.app.action.DEVICE_ADMIN_ENABLED",
        ]
        
        for action in suspicious_actions:
            if action in content:
                self.findings.append(SecurityFinding(
                    category=ScanCategory.MALWARE,
                    title=f"Suspicious Intent Action: {action}",
                    description="This intent action is commonly used by malware.",
                    risk_level=RiskLevel.MEDIUM,
                    cwe_id="CWE-912",
                    recommendation="Verify this functionality is required for legitimate purposes."
                ))

    def _check_dynamic_code_loading(self):
        """Check for dynamic code loading (DEX loading)"""
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith('.smali'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if 'DexClassLoader' in content or 'PathClassLoader' in content:
                            self.findings.append(SecurityFinding(
                                category=ScanCategory.MALWARE,
                                title="Dynamic Code Loading Detected",
                                description="App uses DexClassLoader which may load malicious code at runtime.",
                                risk_level=RiskLevel.HIGH,
                                file_path=filepath,
                                cwe_id="CWE-95",
                                recommendation="Dynamic code loading should be avoided or heavily scrutinized."
                            ))
                    except Exception:
                        pass

    def _check_suspicious_permissions(self):
        """Check for highly suspicious permissions"""
        suspicious = {
            "SYSTEM_ALERT_WINDOW": ("Overlay attacks", RiskLevel.HIGH),
            "RECEIVE_BOOT_COMPLETED": ("Auto-start on boot", RiskLevel.MEDIUM),
            "WRITE_SETTINGS": ("Modify system settings", RiskLevel.HIGH),
            "REQUEST_INSTALL_PACKAGES": ("Install other apps", RiskLevel.HIGH),
            "READ_CALL_LOG": ("Read call history", RiskLevel.HIGH),
            "WRITE_CALL_LOG": ("Modify call history", RiskLevel.CRITICAL),
        }
        
        for perm, (desc, risk) in suspicious.items():
            if perm in self.permissions:
                self.findings.append(SecurityFinding(
                    category=ScanCategory.PERMISSION,
                    title=f"Suspicious Permission: {perm}",
                    description=f"{desc}. Commonly abused by malware.",
                    risk_level=risk,
                    cwe_id="CWE-250",
                    recommendation="Ensure this permission is absolutely necessary."
                ))


# ============================================================================
# Risk Scoring Engine (Based on BeVigil)
# ============================================================================

class RiskScoringEngine:
    """Calculate comprehensive risk score"""
    
    RISK_WEIGHTS = {
        ScanCategory.MALWARE: 25,
        ScanCategory.SECRETS: 20,
        ScanCategory.OWASP_MASVS: 15,
        ScanCategory.SAST: 10,
        ScanCategory.SCA: 10,
        ScanCategory.PERMISSION: 10,
        ScanCategory.NETWORK: 5,
        ScanCategory.CRYPTO: 5,
    }

    def calculate_risk_score(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Calculate overall risk score from findings"""
        
        risk_scores = {level: 0 for level in RiskLevel}
        category_scores = {cat: 0 for cat in ScanCategory}
        
        # Count findings by severity
        for finding in findings:
            risk_scores[finding.risk_level] += 1
            category_scores[finding.category] += 1
        
        # Calculate weighted score
        total_score = 0
        max_score = 100
        
        # Deductions based on findings
        deductions = {
            RiskLevel.CRITICAL: 30,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 5,
            RiskLevel.LOW: 2,
            RiskLevel.INFO: 0,
        }
        
        for level, count in risk_scores.items():
            total_score += deductions[level] * count
        
        # Cap at 100
        risk_score = min(100, total_score)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        elif risk_score >= 10:
            risk_level = "low"
        else:
            risk_level = "safe"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_findings": len(findings),
            "critical_count": risk_scores[RiskLevel.CRITICAL],
            "high_count": risk_scores[RiskLevel.HIGH],
            "medium_count": risk_scores[RiskLevel.MEDIUM],
            "low_count": risk_scores[RiskLevel.LOW],
            "info_count": risk_scores[RiskLevel.INFO],
            "category_breakdown": {cat.value: count for cat, count in category_scores.items() if count > 0},
        }


# ============================================================================
# Comprehensive Report Generator
# ============================================================================

class SecurityReportGenerator:
    """Generate comprehensive security reports"""
    
    def generate_report(self, scan_result: ScanResult) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        return {
            "scan_id": scan_result.scan_id,
            "app_info": {
                "package_name": scan_result.package_name,
                "app_name": scan_result.app_name,
                "version": scan_result.version,
            },
            "risk_assessment": {
                "score": scan_result.risk_score,
                "level": scan_result.risk_level,
                "summary": self._get_risk_summary(scan_result.risk_level),
            },
            "findings_summary": {
                "total": len(scan_result.findings),
                "critical": sum(1 for f in scan_result.findings if f.risk_level == RiskLevel.CRITICAL),
                "high": sum(1 for f in scan_result.findings if f.risk_level == RiskLevel.HIGH),
                "medium": sum(1 for f in scan_result.findings if f.risk_level == RiskLevel.MEDIUM),
                "low": sum(1 for f in scan_result.findings if f.risk_level == RiskLevel.LOW),
                "info": sum(1 for f in scan_result.findings if f.risk_level == RiskLevel.INFO),
            },
            "compliance": {
                "owasp_masvs": self._check_masvs_compliance(scan_result.findings),
            },
            "categories": self._group_by_category(scan_result.findings),
            "recommendations": self._generate_recommendations(scan_result.findings),
            "detailed_findings": [self._finding_to_dict(f) for f in scan_result.findings],
        }
    
    def _get_risk_summary(self, risk_level: str) -> str:
        summaries = {
            "critical": "This app has critical security vulnerabilities that pose immediate risk.",
            "high": "This app has significant security issues that should be addressed.",
            "medium": "This app has some security concerns that should be reviewed.",
            "low": "This app has minor security issues.",
            "safe": "This app passed all security checks.",
        }
        return summaries.get(risk_level, "Unable to determine risk level.")
    
    def _check_masvs_compliance(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Check OWASP MASVS compliance status"""
        masvs_ids = set()
        failed_controls = []
        
        for finding in findings:
            if finding.owasp_id:
                masvs_ids.add(finding.owasp_id)
                failed_controls.append({
                    "control": finding.owasp_id,
                    "title": OWASPMASVSScanner.MASVS_CONTROLS.get(finding.owasp_id, finding.title),
                    "status": "FAIL",
                })
        
        total_controls = len(OWASPMASVSScanner.MASVS_CONTROLS)
        passed = total_controls - len(masvs_ids)
        
        return {
            "compliance_score": f"{passed}/{total_controls}",
            "compliance_percentage": round((passed / total_controls) * 100, 1),
            "failed_controls": failed_controls[:20],  # Limit to 20
        }
    
    def _group_by_category(self, findings: List[SecurityFinding]) -> Dict[str, List]:
        """Group findings by category"""
        categories = {}
        for finding in findings:
            cat = finding.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(self._finding_to_dict(finding))
        return categories
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Get unique recommendations from critical/high findings
        for finding in sorted(findings, key=lambda f: list(RiskLevel).index(f.risk_level)):
            if finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                if finding.recommendation and finding.recommendation not in recommendations:
                    recommendations.append(finding.recommendation)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _finding_to_dict(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "category": finding.category.value,
            "title": finding.title,
            "description": finding.description,
            "risk_level": finding.risk_level.value,
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "owasp_id": finding.owasp_id,
            "cwe_id": finding.cwe_id,
            "recommendation": finding.recommendation,
            "confidence": finding.confidence,
        }


# ============================================================================
# Main Advanced Scanner
# ============================================================================

class AdvancedAPKScanner:
    """Main scanner that orchestrates all security scans"""
    
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.extracted_dir = apk_path.replace('.apk', '_extracted')
        self.scan_id = hashlib.md5(f"{apk_path}{os.path.getmtime(apk_path)}".encode()).hexdigest()[:12]
        
    def extract_apk(self):
        """Extract APK contents"""
        os.makedirs(self.extracted_dir, exist_ok=True)
        
        with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
            zip_ref.extractall(self.extracted_dir)
    
    def get_apk_info(self) -> Dict[str, str]:
        """Extract APK metadata"""
        info = {
            "package_name": "unknown",
            "app_name": "Unknown App",
            "version": "1.0",
        }
        
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract package name
            pkg_match = re.search(r'package="([^"]+)"', content)
            if pkg_match:
                info["package_name"] = pkg_match.group(1)
            
            # Extract version
            version_match = re.search(r'android:versionName="([^"]+)"', content)
            if version_match:
                info["version"] = version_match.group(1)
        
        return info
    
    def get_permissions(self) -> List[str]:
        """Extract permissions from manifest"""
        permissions = []
        manifest_path = os.path.join(self.extracted_dir, "AndroidManifest.xml")
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            perm_matches = re.findall(r'android:permission="([^"]+)"', content)
            for perm in perm_matches:
                # Extract just the permission name
                perm_name = perm.split('.')[-1]
                permissions.append(perm_name)
        
        return permissions
    
    def scan(self) -> Dict[str, Any]:
        """Execute comprehensive security scan"""
        
        # Extract APK
        self.extract_apk()
        
        # Get APK info
        apk_info = self.get_apk_info()
        permissions = self.get_permissions()
        
        # Run all scanners
        all_findings = []
        
        # OWASP MASVS Scanner
        masvs_scanner = OWASPMASVSScanner(self.apk_path, self.extracted_dir)
        all_findings.extend(masvs_scanner.scan())
        
        # Secret Detector
        secret_detector = SecretDetector(self.extracted_dir)
        all_findings.extend(secret_detector.scan())
        
        # SCA Scanner
        sca_scanner = SoftwareCompositionAnalyzer(self.extracted_dir)
        all_findings.extend(sca_scanner.scan())
        
        # Malware Scanner
        malware_scanner = MalwareScanner(self.extracted_dir, permissions)
        all_findings.extend(malware_scanner.scan())
        
        # Certificate Analyzer
        cert_analyzer = CertificateAnalyzer(self.apk_path)
        cert_results = cert_analyzer.analyze()
        all_findings.extend([{
            "category": ScanCategory.CERTIFICATE,
            "title": f["title"],
            "description": f["description"],
            "risk_level": RiskLevel.MEDIUM if f["severity"] == "medium" else RiskLevel.LOW,
        } for f in cert_results.get("findings", [])])
        
        # Network Security Analyzer
        network_analyzer = NetworkSecurityAnalyzer(self.extracted_dir)
        network_results = network_analyzer.analyze()
        all_findings.extend([{
            "category": ScanCategory.NETWORK,
            "title": f["title"],
            "description": f["description"],
            "risk_level": RiskLevel.HIGH if f["severity"] == "high" else RiskLevel.MEDIUM,
        } for f in network_results.get("findings", [])])
        
        # Crypto Analyzer
        crypto_analyzer = CryptoAnalyzer(self.extracted_dir)
        crypto_results = crypto_analyzer.analyze()
        all_findings.extend([{
            "category": ScanCategory.CRYPTO,
            "title": f["title"],
            "description": f["description"],
            "risk_level": RiskLevel.HIGH if f["severity"] == "high" else RiskLevel.MEDIUM,
        } for f in crypto_results.get("findings", [])])
        
        # Data Storage Analyzer
        storage_analyzer = DataStorageAnalyzer(self.extracted_dir)
        storage_results = storage_analyzer.analyze()
        all_findings.extend([{
            "category": ScanCategory.STORAGE,
            "title": f["title"],
            "description": f["description"],
            "risk_level": RiskLevel.HIGH if f["severity"] == "high" else RiskLevel.MEDIUM,
        } for f in storage_results.get("findings", [])])
        
        # Convert dict findings to SecurityFinding objects
        normalized_findings = []
        for f in all_findings:
            if isinstance(f, dict):
                normalized_findings.append(SecurityFinding(
                    category=f.get("category", ScanCategory.SAST),
                    title=f.get("title", ""),
                    description=f.get("description", ""),
                    risk_level=f.get("risk_level", RiskLevel.LOW),
                    file_path=f.get("file_path", ""),
                ))
            else:
                normalized_findings.append(f)
        
        # Calculate risk score
        scoring_engine = RiskScoringEngine()
        risk_assessment = scoring_engine.calculate_risk_score(normalized_findings)
        
        # Generate compliance report
        compliance_reporter = AdvancedComplianceReporter()
        compliance = compliance_reporter.generate_compliance_report([
            {"title": f.title, "description": f.description, "severity": f.risk_level.value}
            for f in normalized_findings
        ])
        
        # Create scan result
        scan_result = ScanResult(
            scan_id=self.scan_id,
            package_name=apk_info["package_name"],
            app_name=apk_info["app_name"],
            version=apk_info["version"],
            risk_score=risk_assessment["risk_score"],
            risk_level=risk_assessment["risk_level"],
            findings=normalized_findings,
            statistics={
                "permissions_count": len(permissions),
                "permissions": permissions,
                "libraries_count": len(sca_scanner.libraries),
                "libraries": sca_scanner.libraries[:20],
            },
            compliance=risk_assessment,
        )
        
        # Generate report
        report_generator = SecurityReportGenerator()
        report = report_generator.generate_report(scan_result)
        
        # Add statistics and additional analysis
        report["statistics"] = scan_result.statistics
        report["certificate_analysis"] = cert_results
        report["network_analysis"] = network_results
        report["crypto_analysis"] = crypto_results
        report["storage_analysis"] = storage_results
        report["compliance_report"] = compliance
        
        return report