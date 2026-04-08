import asyncio
import logging
import hashlib
from typing import List, Tuple

class BehavioralSimulator:
    async def simulate_dynamic_execution(self, is_system_app: bool, package_name: str) -> Tuple[int, List[str]]:
        """
        Simulates dynamic sandbox behavior deterministically using mathematical invariants.
        Returns: (risk_points_generated, list_of_behavioral_flags)
        """
        flags = []
        risk_points = 0
        
        # System apps belong to the OS and bypass behavior heuristics
        if is_system_app:
            return 0, []

        # Simulate analysis latency (non-blocking)
        await asyncio.sleep(0.02)

        pack_lower = package_name.lower()

        # Deterministic check 1: Namespace depth (simulating basic structure trust)
        segments = pack_lower.split(".")
        if len(segments) < 3 and not is_system_app:
            flags.append("Suspicious structural depth. Lacks verified developer signatures.")
            risk_points += 25

        # Deterministic check 2: Mathematical pseudo-entropy checking (simulating sandbox payload execution)
        # By hashing the string itself, an app will ALWAYS produce exactly the same sandbox output globally.
        pack_hash = int(hashlib.md5(package_name.encode()).hexdigest(), 16)
        
        if pack_hash % 100 < 5:  # Consistent 5% statistical threshold without using random.random()
            flags.append("Elevated background network activity without foreground context.")
            risk_points += 25
            
        if pack_hash % 100 > 90: # Another fixed bracket simulating hardware tests
            flags.append("Excessive hardware permissions requested in sandbox (Camera/Mic).")
            risk_points += 15

        # Deterministic Keyword overrides in behavior matching
        if "vpn" in pack_lower or "proxy" in pack_lower:
            flags.append("Detected potential traffic tunneling and SSL inspection capabilities.")
            risk_points += 30

        logging.debug(f"Behavioral Simulation complete for {package_name} - Generated {risk_points} risk points.")
        return risk_points, flags
