"""
NetShield-IoT: Optimization Analytics & Analogy Engine
Calculates the master 0-100 score, traffic highway model, and airwave metrics.
"""

import math
import random
import time
from typing import Dict, Any

class NetworkOptimizer:
    """Computes master health score, robo speech, and spectrum analogies."""

    @staticmethod
    def calculate_master_score(latency_ms: float, signal_pct: int, esp_connected: bool) -> Tuple[int, str, str, str]:
        """
        Calculates a transparent 0-100 score.
        Returns: (score, status_text, summary_text, robo_mood)
        """
        score = 0

        # Latency component (max 40 pts)
        if latency_ms > 0:
            if latency_ms <= 35: score += 40
            elif latency_ms <= 65: score += 35
            elif latency_ms <= 110: score += 25
            elif latency_ms <= 200: score += 15
            else: score += 5
        else:
            score += 0

        # Signal component (max 35 pts)
        if signal_pct >= 80: score += 35
        elif signal_pct >= 60: score += 28
        elif signal_pct >= 40: score += 20
        elif signal_pct >= 20: score += 10
        else: score += 5

        # Hardware Radar component (max 25 pts)
        if esp_connected:
            score += 25
        else:
            score += 15  # Software fallback gets 15 pts

        if score >= 80:
            status = "Excellent & Fast 🏎️"
            summary = "Your connection is pristine with minimal RF interference."
            mood = "happy"
        elif score >= 60:
            status = "Good & Steady ⚡"
            summary = "Connection is solid. Guard is actively monitoring room airwaves."
            mood = "calm"
        elif score >= 40:
            status = "Moderate Delays ⚠️"
            summary = "Nearby Wi-Fi routers are causing moderate interference."
            mood = "alert"
        else:
            status = "Heavily Congested 🛑"
            summary = "High latency or weak signal detected. Check Clean AP recommendations."
            mood = "concerned"

        return score, status, summary, mood

    @staticmethod
    def compute_highway_lanes(c1: int, c6: int, c11: int) -> Dict[str, Any]:
        """Maps Channels 1, 6, 11 into a simple highway traffic analogy."""
        def get_lane_info(count: int):
            if count >= 4:
                return "Jammed 🚗🚗🚗", f"{count} routers on channel"
            elif count >= 2:
                return "Moderate 🚗", f"{count} routers on channel"
            else:
                return "Empty 🏎️", f"{count} routers (clean lane)"

        s1, d1 = get_lane_info(c1)
        s6, d6 = get_lane_info(c6)
        s11, d11 = get_lane_info(c11)

        least = min(c1, c6, c11)
        best_lane = 11 if least == c11 else (6 if least == c6 else 1)

        return {
            "lane1": {"channel": 1, "count": c1, "status": s1, "desc": d1},
            "lane6": {"channel": 6, "count": c6, "status": s6, "desc": d6},
            "lane11": {"channel": 11, "count": c11, "status": s11, "desc": d11},
            "best_lane": best_lane
        }
