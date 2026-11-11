"""
Unit Tests: Platform Abstraction Layer
Verifies platform adapter contract, Linux frequency conversions, and 802.11 capabilities.
"""

import unittest
from platforms import get_platform_adapter
from platforms.linux import LinuxPlatformAdapter
from platforms.base import AbstractPlatformAdapter
from core.interfaces import Capabilities80211

class TestPlatforms(unittest.TestCase):
    def test_factory_returns_adapter(self):
        adapter = get_platform_adapter()
        self.assertIsInstance(adapter, AbstractPlatformAdapter)
        self.assertIn(adapter.get_system_name(), ["Linux", "Windows", "Darwin"])

    def test_linux_frequency_conversion(self):
        adapter = LinuxPlatformAdapter()
        # 2.4 GHz band
        self.assertEqual(adapter._freq_to_channel(2412), 1)
        self.assertEqual(adapter._freq_to_channel(2437), 6)
        self.assertEqual(adapter._freq_to_channel(2462), 11)
        self.assertEqual(adapter._freq_to_channel(2484), 14)
        # 5 GHz band
        self.assertEqual(adapter._freq_to_channel(5180), 36)
        self.assertEqual(adapter._freq_to_channel(5240), 48)

    def test_capabilities_detection_structure(self):
        adapter = LinuxPlatformAdapter()
        caps = adapter.detect_80211_capabilities()
        self.assertIsInstance(caps, Capabilities80211)
        self.assertIsInstance(caps.supports_80211r, bool)
        self.assertIsInstance(caps.supports_80211k, bool)
        self.assertIsInstance(caps.supports_80211v, bool)

    def test_bandwidth_counter_structure(self):
        adapter = get_platform_adapter()
        rx1, rx2 = adapter.sample_bandwidth_bytes()
        self.assertIsInstance(rx1, int)
        self.assertIsInstance(rx2, int)

if __name__ == "__main__":
    unittest.main()
