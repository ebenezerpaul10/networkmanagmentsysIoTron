"""
Integration Tests: Full Engine Lifecycle & REST API Endpoints
Verifies that all modular subsystems communicate and serve valid JSON payloads.
"""

import unittest
import json
import os
import sys

# Ensure root dir is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from laptop_engine.netshield import NetShieldEngine

class TestNetShieldIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = NetShieldEngine(bind_http=False)

    def test_stats_api_schema(self):
        code, ctype, body = self.engine.api_dispatcher.handle_get("/api/stats")
        self.assertEqual(code, 200)
        self.assertEqual(ctype, "application/json")
        data = json.loads(body.decode())

        # Essential UI keys
        required_keys = [
            "current_ssid", "current_bssid", "current_channel", "current_signal",
            "radar_source", "esp_connected", "health_score", "score_status",
            "highway", "spectrum_history", "before_metrics", "after_metrics",
            "download_speed_str"
        ]
        for k in required_keys:
            self.assertIn(k, data, f"Missing key in /api/stats: {k}")

    def test_capabilities_api(self):
        code, ctype, body = self.engine.api_dispatcher.handle_get("/api/capabilities")
        self.assertEqual(code, 200)
        data = json.loads(body.decode())
        self.assertIn("80211", data)
        self.assertIn("mptcp", data)
        self.assertIn("dns", data)

    def test_mptcp_status_api(self):
        code, ctype, body = self.engine.api_dispatcher.handle_get("/api/mptcp/status")
        self.assertEqual(code, 200)
        data = json.loads(body.decode())
        self.assertIn("kernel_supported", data)
        self.assertIn("paths", data)

    def test_dns_stats_api(self):
        code, ctype, body = self.engine.api_dispatcher.handle_get("/api/dns/stats")
        self.assertEqual(code, 200)
        data = json.loads(body.decode())
        self.assertIn("total_queries", data)
        self.assertIn("blocked_queries", data)

    def test_capture_baseline_post(self):
        code, ctype, body = self.engine.api_dispatcher.handle_post("/api/capture_baseline")
        self.assertEqual(code, 200)
        data = json.loads(body.decode())
        self.assertTrue(data.get("success"))
        self.assertIn("baseline", data)

    def test_index_html_served(self):
        code, ctype, body = self.engine.api_dispatcher.handle_get("/index.html")
        self.assertEqual(code, 200)
        self.assertEqual(ctype, "text/html")
        self.assertIn(b"NetShield", body)

if __name__ == "__main__":
    unittest.main()
