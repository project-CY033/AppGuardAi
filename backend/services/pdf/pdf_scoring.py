from typing import Dict, Any, List

# Configurable constants for scoring logic
BASE_SCORE = 100
PENALTY_JAVASCRIPT = 40
PENALTY_EXTERNAL_URL = 15
PENALTY_OBFUSCATION = 20
PENALTY_CORRUPTION = 65
PENALTY_ENCRYPTION = 10

class PDFScoring:
    @staticmethod
    def calculate_score(extraction_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the definitive risk score based on deterministic rules and extracted artifacts.
        """
        score = BASE_SCORE
        checks: List[Dict[str, str]] = []

        # 1. Javascript check
        has_js = extraction_data.get("has_javascript", False) or analysis_data.get("js_detected_by_peepdf", False)
        if has_js:
            score -= PENALTY_JAVASCRIPT
            checks.append({
                "title": "Embedded Script Detection",
                "status": "risk",
                "description": "Embedded JavaScript detected. Active scripting poses a severe security vulnerability."
            })
        else:
            checks.append({
                "title": "Embedded Script Detection",
                "status": "safe",
                "description": "No JavaScript or active macros found in the document tree."
            })

        # 2. Obfuscation
        if analysis_data.get("obfuscated_elements", False):
            score -= PENALTY_OBFUSCATION
            checks.append({
                "title": "Obfuscated Content",
                "status": "risk",
                "description": "Heuristics detected potentially obfuscated or concealed object streams."
            })
            
        # 3. External Links
        urls = analysis_data.get("suspicious_urls", [])
        if len(urls) > 0:
            score -= PENALTY_EXTERNAL_URL
            checks.append({
                "title": "External Links",
                "status": "warning",
                "description": f"Found embeded URLs indicating external reachability ({len(urls)} items)."
            })
        else:
            checks.append({
                "title": "External Links",
                "status": "safe",
                "description": "All embedded URLs are verified absent or safe."
            })

        # 4. Encryption
        if extraction_data.get("has_encryption", False):
            score -= PENALTY_ENCRYPTION
            checks.append({
                "title": "File Encryption",
                "status": "warning",
                "description": "File contains encrypted blocks which may conceal malicious streams."
            })

        # 5. Fallback/Corruption
        if extraction_data.get("is_corrupt", False):
            score -= PENALTY_CORRUPTION
            checks.append({
                "title": "Document Integrity",
                "status": "risk",
                "description": "Structural corruption detected. This is often an evasion technique used by malformed threats."
            })
        else:
            checks.append({
                "title": "Document Integrity",
                "status": "safe",
                "description": "Verified document structure and header signatures."
            })

        # Ensure bounds
        score = max(0, min(100, score))

        # Classification
        if score >= 80:
            status = "Safe"
        elif score >= 50:
            status = "Warning"
        else:
            status = "Risk"

        return {
            "scan_score": score,
            "overall_status": status,
            "checks": checks
        }
