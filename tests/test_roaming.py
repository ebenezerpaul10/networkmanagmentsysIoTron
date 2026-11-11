"""
Unit Tests: Intelligent Wi-Fi Roaming Decision Engine
Verifies hysteresis, sticky client handling, anti-oscillation cooldowns, and rollback.
"""

import unittest
import time
from core.interfaces import ActiveWifiStatus, ApCandidate, RoamResult, Capabilities80211
from core.roaming import IntelligentRoamingEngine
from platforms.base import AbstractPlatformAdapter

class MockPlatformAdapter(AbstractPlatformAdapter):
    def __init__(self, switch_success=True):
        self.switch_success = switch_success
        self.switched_bssid = None

    def get_system_name(self) -> str: return "MockOS"
    def get_wifi_interfaces(self): return "wlan0", None
    def is_secondary_wifi_detected(self) -> bool: return False
    def get_active_wifi_status(self):
        return ActiveWifiStatus(
            ssid="Campus-WiFi",
            bssid=self.switched_bssid or "AA:BB:CC:DD:EE:01",
            channel=6,
            signal_pct=40,
            rssi_dbm=-75,
            is_connected=True
        )
    def scan_nearby_wifi_channels(self): pass
    def find_candidates_for_ssid(self, target_ssid: str): return []
    def detect_80211_capabilities(self, iface=None):
        return Capabilities80211(supports_80211r=True, supports_80211k=True, driver_name="MockDriver")
    def switch_wifi_bssid(self, ssid, target_bssid, use_fast_transition=True):
        if self.switch_success:
            self.switched_bssid = target_bssid
            return RoamResult(
                success=True, method_used="wpa_cli_ft",
                previous_bssid="AA:BB:CC:DD:EE:01", target_bssid=target_bssid,
                channel=1, signal_pct=85, latency_ms=25.0, message="Roam OK"
            )
        else:
            return RoamResult(
                success=False, method_used="nmcli_rollback",
                previous_bssid="AA:BB:CC:DD:EE:01", target_bssid=target_bssid,
                channel=6, signal_pct=40, latency_ms=-1.0, rollback_triggered=True,
                message="Roam failed, safely reverted"
            )
    def sample_bandwidth_bytes(self): return 1000, 0

class TestIntelligentRoaming(unittest.TestCase):
    def setUp(self):
        self.mock_adapter = MockPlatformAdapter()
        self.roam_engine = IntelligentRoamingEngine(self.mock_adapter)

    def test_sticky_client_and_hysteresis_rejection(self):
        """Candidate with minor gain (< 15%) should be rejected to avoid flapping."""
        current = ActiveWifiStatus(
            ssid="Campus-WiFi", bssid="AA:BB:CC:DD:EE:01", channel=6,
            signal_pct=60, rssi_dbm=-65, is_connected=True
        )
        # Minor gain candidate (63% vs 60%)
        candidate = ApCandidate(
            bssid="AA:BB:CC:DD:EE:02", ssid="Campus-WiFi", channel=1,
            signal_pct=63, rssi_dbm=-63
        )
        should_roam, selected, reason = self.roam_engine.evaluate_roam_candidate(current, [candidate])
        self.assertFalse(should_roam)
        self.assertIsNone(selected)
        self.assertIn("hysteresis", reason.lower())

    def test_roam_acceptance_when_hysteresis_exceeded(self):
        """Candidate with substantial gain (> 15%) should be accepted."""
        current = ActiveWifiStatus(
            ssid="Campus-WiFi", bssid="AA:BB:CC:DD:EE:01", channel=6,
            signal_pct=40, rssi_dbm=-78, is_connected=True
        )
        # Strong AP on Channel 11 (82% vs 40%)
        candidate = ApCandidate(
            bssid="AA:BB:CC:DD:EE:02", ssid="Campus-WiFi", channel=11,
            frequency_mhz=5200, signal_pct=82, rssi_dbm=-55, supports_80211r=True
        )
        should_roam, selected, reason = self.roam_engine.evaluate_roam_candidate(current, [candidate])
        self.assertTrue(should_roam)
        self.assertEqual(selected.bssid, "AA:BB:CC:DD:EE:02")

    def test_ssid_mismatch_rejection(self):
        """Candidates from a different SSID must never be roamed to."""
        current = ActiveWifiStatus(
            ssid="Campus-WiFi", bssid="AA:BB:CC:DD:EE:01", channel=6,
            signal_pct=30, rssi_dbm=-82, is_connected=True
        )
        rogue_candidate = ApCandidate(
            bssid="AA:BB:CC:DD:EE:03", ssid="Other-Network", channel=1,
            signal_pct=95, rssi_dbm=-45
        )
        should_roam, selected, reason = self.roam_engine.evaluate_roam_candidate(current, [rogue_candidate])
        self.assertFalse(should_roam)

    def test_anti_oscillation_cooldown(self):
        """Engine must enforce cooldown between roams to avoid ping-ponging."""
        current = ActiveWifiStatus(
            ssid="Campus-WiFi", bssid="AA:BB:CC:DD:EE:01", channel=6,
            signal_pct=40, rssi_dbm=-78, is_connected=True
        )
        candidate = ApCandidate(
            bssid="AA:BB:CC:DD:EE:02", ssid="Campus-WiFi", channel=1,
            signal_pct=85, rssi_dbm=-50
        )
        # First roam decision
        self.roam_engine.last_roam_time = time.time()  # simulated recent roam
        should_roam, selected, reason = self.roam_engine.evaluate_roam_candidate(current, [candidate])
        self.assertFalse(should_roam)
        self.assertIn("cooldown active", reason.lower())

    def test_rollback_on_failed_roam(self):
        """If AP switch fails, rollback behavior must be logged and triggered."""
        fail_adapter = MockPlatformAdapter(switch_success=False)
        engine = IntelligentRoamingEngine(fail_adapter)
        current = ActiveWifiStatus(ssid="Campus-WiFi", bssid="AA:BB:CC:DD:EE:01", channel=6, signal_pct=40, is_connected=True)
        candidate = ApCandidate(bssid="AA:BB:CC:DD:EE:02", ssid="Campus-WiFi", channel=1, signal_pct=80)

        result = engine.execute_safe_roam(candidate, current)
        self.assertFalse(result.success)
        self.assertTrue(result.rollback_triggered)

if __name__ == "__main__":
    unittest.main()
