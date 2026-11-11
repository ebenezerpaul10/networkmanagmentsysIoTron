"""
NetShield-IoT: Network Latency & Bandwidth Monitor
Tracks real-time throughput and connection health across primary and secondary interfaces.
"""

import time
import socket
from typing import Tuple, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from platforms.base import AbstractPlatformAdapter
from config.settings import ROAM_PING_TARGET

class NetworkMonitor:
    """Monitors live network metrics: throughput, RTT latency, and health verdicts."""

    def __init__(self, platform_adapter: AbstractPlatformAdapter):
        self.platform = platform_adapter
        self.last_rx1 = 0
        self.last_rx2 = 0
        self.last_sample_time = time.time()
        self.latency_ms = -1.0
        self.health_verdict = "Checking..."

    def sample_throughput_mbps(self) -> Tuple[float, float, float]:
        """
        Samples rx bytes and returns: (mbps_primary, mbps_secondary, mbps_total)
        """
        now = time.time()
        dt = max(0.1, now - self.last_sample_time)
        self.last_sample_time = now

        cur_rx1, cur_rx2 = self.platform.sample_bandwidth_bytes()

        d1 = max(0, cur_rx1 - self.last_rx1) if self.last_rx1 > 0 else 0
        d2 = max(0, cur_rx2 - self.last_rx2) if self.last_rx2 > 0 else 0

        self.last_rx1 = cur_rx1
        self.last_rx2 = cur_rx2

        mbps1 = (d1 * 8) / (dt * 1_000_000.0)
        mbps2 = (d2 * 8) / (dt * 1_000_000.0)

        # Check if secondary is actually detected
        if not self.platform.is_secondary_wifi_detected():
            mbps2 = 0.0

        mbps_total = mbps1 + mbps2
        return round(mbps1, 2), round(mbps2, 2), round(mbps_total, 2)

    def measure_latency(self) -> float:
        """Measures real TCP RTT to high-availability target."""
        try:
            t0 = time.time()
            s = socket.create_connection(ROAM_PING_TARGET, timeout=2.5)
            lat = round((time.time() - t0) * 1000, 1)
            s.close()
            self.latency_ms = lat

            if lat < 45:
                self.health_verdict = "🔥 EXCELLENT (Smooth for Gaming/Calls)"
            elif lat < 110:
                self.health_verdict = "⚡ GOOD (Standard Browsing/Streaming)"
            else:
                self.health_verdict = "⚠️ CONGESTED (High Traffic Delay)"
            return lat
        except Exception:
            self.latency_ms = -1.0
            self.health_verdict = "🔴 PACKET DROP / TIMEOUT"
            return -1.0
