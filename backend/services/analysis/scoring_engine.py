from typing import Tuple

class ScoringEngine:
    def calculate_final_score(self, static_points: int, behavioral_points: int) -> Tuple[int, bool]:
        """
        Combines deterministic points strictly using the 70/30 formula.
        Returns: (normalized_risk_score, is_safe_boolean)
        """
        # Fixed deterministic weights
        weighted_total = (static_points * 0.70) + (behavioral_points * 0.30)
        
        # Round gracefully and cap tightly at 100 maximum
        final_risk_score = min(int(round(weighted_total)), 100)
        
        # Classification thresholds
        # 0 - 20: SAFE
        # 21 - 50: MODERATE
        # 51 - 100: HIGH RISK
        
        # The boolean `is_safe` controls the master UI layout (Green vs Red/Warnings)
        is_safe = final_risk_score <= 20
        
        return final_risk_score, is_safe
