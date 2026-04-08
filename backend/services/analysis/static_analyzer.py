from typing import List, Tuple
import logging
from services.analysis.threat_intelligence import threat_intel

class StaticAnalyzer:
    def __init__(self):
        # We preserve some standard static overrides for unmatched packages
        self.malicious_keywords = ["hack", "crack", "mod", "cheat", "freecoins", "fake", "clone"]

    async def run_analysis(self, is_system_app: bool, app_name: str, package_name: str) -> Tuple[int, List[str]]:
        """
        Runs non-blocking check against the Threat Intelligence DB and Static properties.
        Returns a tuple: (risk_points_generated, list_of_flags)
        """
        flags = []
        risk_points = 0
        app_name_lower = app_name.lower()
        pack_name_lower = package_name.lower()

        # 1. Real Threat Intelligence DB Query (Replaces Simulated Math logic)
        intel_result = await threat_intel.lookup_package(pack_name_lower)
        
        # Exact Known Malware Match from DB
        if intel_result['is_threat'] is True:
            logging.critical(f"THREAT DB MATCH: {package_name} flagged immediately.")
            return intel_result['risk_score'], intel_result['flags']
            
        # Official App Verification Match from DB
        if intel_result['is_threat'] is False:
            logging.debug(f"THREAT DB CLEARED: {package_name} is perfectly safe.")
            return 0, intel_result['flags']

        # 2. System App Override 
        if is_system_app:
            return 0, ["System Core Application (Trusted)"]

        # 3. Unidentified / 3rd Party Apps: Rule-based Heuristics Fallback
        for word in self.malicious_keywords:
            if word in app_name_lower or word in pack_name_lower:
                flags.append(f"Suspicious naming pattern detected: '{word}'")
                risk_points += 40

        segments = pack_name_lower.split(".")
        if len(segments) < 2:
            flags.append("Non-standard package namespace structure.")
            risk_points += 20

        logging.debug(f"Static Analysis complete for {package_name} - Generated {risk_points} risk points.")
        return risk_points, flags
