"""
NetShield-IoT: Unified Wi-Fi Scanner Coordinator
Bridges ESP32 Hardware Radar (Mode 2) with Native OS Scanning (Mode 1 Fallback).
"""

import time
import logging
from typing import Optional, Dict, Any, TYPE_CHECKING
from core.interfaces import ScanResult
if TYPE_CHECKING:
    from platforms.base import AbstractPlatformAdapter
from hardware.esp32 import Esp32RadarClient

logger = logging.getLogger(__name__)

class UnifiedWifiScanner:
    """Coordinates hardware and software Wi-Fi scanning modes."""

    def __init__(self, platform_adapter: AbstractPlatformAdapter, esp32_client: Esp32RadarClient):
        self.platform = platform_adapter
        self.esp32 = esp32_client
        self.last_scan_result = ScanResult()
        self.last_scan_time = 0.0

    def get_radar_source_name(self) -> str:
        if self.esp32.is_connected:
            return f"ESP32 Hardware Antenna ({self.esp32.port})"
        return f"{self.platform.get_system_name()} Wi-Fi (Software Fallback)"

    def scan(self) -> ScanResult:
        """
        Retrieves the latest spectrum scan.
        Prefers ESP32 hardware telemetry if connected and fresh (< 5s).
        Falls back to platform adapter software scan otherwise.
        """
        now = time.time()

        # Check if ESP32 telemetry is active
        if self.esp32.is_connected and (now - self.esp32.last_packet_time < 5.0):
            return self.last_scan_result

        # Fallback to OS-native scan
        scan = self.platform.scan_nearby_wifi_channels()
        self.last_scan_result = scan
        self.last_scan_time = now
        return scan

    def update_from_esp32_packet(self, data: Dict[str, Any]):
        """Updates internal scan state from an incoming ESP32 JSON packet."""
        c1 = data.get("ch1_count", 0)
        c6 = data.get("ch6_count", 0)
        c11 = data.get("ch11_count", 0)
        total = data.get("total_aps", c1 + c6 + c11)

        self.last_scan_result.ch1_count = c1
        self.last_scan_result.ch6_count = c6
        self.last_scan_result.ch11_count = c11
        self.last_scan_result.total_aps = total
        self.last_scan_time = time.time()
