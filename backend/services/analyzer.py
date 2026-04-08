import asyncio
import logging
from typing import List

from models.schemas import AppInfoPayload, AppRiskResult
from services.analysis.static_analyzer import StaticAnalyzer
from services.analysis.behavioral_simulator import BehavioralSimulator
from services.analysis.scoring_engine import ScoringEngine
from services.analysis.virustotal import vt_client

class AsyncAnalyzer:
    def __init__(self):
        self.static_analyzer = StaticAnalyzer()
        self.behavioral_simulator = BehavioralSimulator()
        self.scoring_engine = ScoringEngine()
        self._cache = {} 

    async def _analyze_single_app(self, app: AppInfoPayload) -> AppRiskResult:
        if app.package_name in self._cache:
            return self._cache[app.package_name]

        vt_found = False
        vt_data = {}
        risk_level = "Safe"
        is_malicious = False
        threat_details = {}

        # 1. Check Virustotal if hash exists
        if app.hash_sha256:
            vt_found, vt_data = await vt_client.check_hash(app.hash_sha256)
        
        static_points = 0
        behavioral_points = 0
        total_flags = []

        if vt_found and "malicious" in vt_data:
            # We bypass heavy fallback if VT is highly confident
            malicious_hits = vt_data.get("malicious", 0)
            if malicious_hits > 0:
                is_malicious = True
                static_points += (malicious_hits * 10)
                total_flags.append(f"VirusTotal detected {malicious_hits} vendor flags.")
                threat_details["virustotal"] = f"Malicious hits: {malicious_hits} / {vt_data.get('total', 0)}"
        else:
            # Fallback static / behavioral
            static_points, static_flags = await self.static_analyzer.run_analysis(
                is_system_app=app.is_system_app,
                app_name=app.app_name, 
                package_name=app.package_name
            )
            behavioral_points, behavioral_flags = await self.behavioral_simulator.simulate_dynamic_execution(
                is_system_app=app.is_system_app, 
                package_name=app.package_name
            )
            total_flags = static_flags + behavioral_flags

        final_score, _ = self.scoring_engine.calculate_final_score(static_points, behavioral_points)

        # Apply MobSF severity map levels (final_score is penalty: 0 is safe, 100 is high risk)
        if final_score >= 70:
            risk_level = "High"
            is_malicious = True
        elif final_score >= 30:
            risk_level = "Medium"
        elif final_score >= 10:
            risk_level = "Low"
        else:
            risk_level = "Safe"

        # The UI visual progress bar expects 100 to be perfectly safe
        display_score = 100 - final_score

        if total_flags and not threat_details:
            threat_details["heuristics"] = total_flags

        result = AppRiskResult(
            app_name=app.app_name,
            package_name=app.package_name,
            is_safe=not is_malicious,
            is_malicious=is_malicious,
            risk_score=display_score,
            risk_level=risk_level,
            flags=total_flags,
            threat_details=threat_details
        )
        
        self._cache[app.package_name] = result
        return result

    async def analyze_batch(self, apps: List[AppInfoPayload]) -> List[AppRiskResult]:
        logging.info(f"Kicking off async batch analysis for {len(apps)} apps.")
        
        # Limit concurrency to prevent overloading DB or hitting external API rate limits too hard
        semaphore = asyncio.Semaphore(10) 
        
        async def sem_analyze(app):
            async with semaphore:
                return await self._analyze_single_app(app)

        tasks = [sem_analyze(app) for app in apps]
        return await asyncio.gather(*tasks)
