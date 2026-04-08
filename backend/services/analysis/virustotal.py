import os
import httpx
import logging
from typing import Dict, Any, Tuple
import asyncio
from typing import Optional

# Simple memory cache to prevent rate limit hits across app lifespan
_vt_cache = {}

class VirusTotalClient:
    def __init__(self):
        self.api_key = os.getenv('VT_API_KEY')
        self.base_url = "https://www.virustotal.com/api/v3/files/"
        if not self.api_key:
            logging.info("VIRUSTOTAL_API_KEY locally missing. Will fallback to Native Static Analysis only.")

    async def check_hash(self, hash_sha256: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Queries VT for a given SHA256 hash.
        Returns a tuple: (success, data_dict)
        """
        if not hash_sha256 or not self.api_key:
            return False, {}
            
        if hash_sha256 in _vt_cache:
            logging.debug(f"VT Cache Hit for {hash_sha256}")
            return True, _vt_cache[hash_sha256]
            
        headers = {
            "x-apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}{hash_sha256}", headers=headers, timeout=5.0)
                
                if res.status_code == 200:
                    data = res.json().get('data', {})
                    attrs = data.get('attributes', {})
                    stats = attrs.get('last_analysis_stats', {})
                    
                    results = {
                        "malicious": stats.get('malicious', 0),
                        "suspicious": stats.get('suspicious', 0),
                        "undetected": stats.get('undetected', 0),
                        "total": sum(stats.values()) if stats else 0,
                        "meaningful_name": attrs.get('meaningful_name', 'Unknown')
                    }
                    _vt_cache[hash_sha256] = results
                    return True, results
                elif res.status_code == 404:
                    return True, {"not_found": True}
                elif res.status_code == 429:
                    logging.warning("VirusTotal API Rate Limit hit! Falling back to static.")
                    return False, {"error": "rate_limited"}
                else:
                    logging.warning(f"VirusTotal API warning: {res.status_code} - {res.text}")
                    return False, {"error": f"status {res.status_code}"}
        except httpx.RequestError as e:
            logging.warning(f"VirusTotal Network Error: {e}")
            return False, {"error": str(e)}

vt_client = VirusTotalClient()
