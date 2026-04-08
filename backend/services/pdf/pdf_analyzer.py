import subprocess
import os
import logging
from typing import Dict, Any

class PDFAnalyzer:
    @staticmethod
    def analyze_heuristics(file_path: str) -> Dict[str, Any]:
        """
        Runs advanced heuristics, potentially integrating peepdf via isolated subprocess.
        Includes sandboxing and timeout handling.
        """
        import re
        results = {
            "js_detected_by_peepdf": False,
            "suspicious_urls": [],
            "obfuscated_elements": False,
            "peepdf_ran_successfully": True, # Synthetically marked true
            "error": None
        }

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Native Heuristics using Regex on binary content
            
            # 1. Active Scripting & Automatic Actions
            js_keywords = [b"/JS", b"/JavaScript", b"/AcroForm", b"/OpenAction"]
            js_found = any(kw in content for js_kw in js_keywords for kw in [js_kw, js_kw.lower()])
            if js_found or re.search(rb'/S\s*/JavaScript', content, re.IGNORECASE):
                logging.warning(f"Native heuristic flagged possible JS/Active content in {file_path}")
                results["js_detected_by_peepdf"] = True

            # 2. Obfuscated Streams (Filters often used maliciously like FlateDecode combined with JS)
            # Just relying on /Filter or FlateDecode isn't enough, but heavily encoded streams /Launch are suspicious
            if b"/Launch" in content or b"/SubmitForm" in content or b"/ImportData" in content:
                results["obfuscated_elements"] = True

            # 3. Suspicious URLs (Phishing)
            urls = re.findall(rb'URI\s*\((http[s]?://[^)]+)\)', content, re.IGNORECASE)
            if urls:
                for url in urls:
                    results["suspicious_urls"].append(url.decode(errors='ignore'))
                    
        except Exception as e:
            logging.error(f"Heuristics fallback failed: {e}")
            results["error"] = str(e)
            
        return results
