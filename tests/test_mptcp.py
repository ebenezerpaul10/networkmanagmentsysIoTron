"""
Unit Tests: Multipath TCP (MPTCP) & Interface Path Manager
Verifies kernel capability detection, native MPTCP socket creation, and path discovery.
"""

import unittest
import socket
from proxy.mptcp import MptcpManager
from proxy.path_manager import InterfacePathManager
from proxy.dispatch import DispatchProxyBridge
from core.interfaces import MptcpStatus

class TestMptcpSubsystem(unittest.TestCase):
    def test_mptcp_kernel_detection(self):
        st = MptcpManager.detect_kernel_support()
        self.assertIsInstance(st, MptcpStatus)
        self.assertIsInstance(st.kernel_supported, bool)
        self.assertIsInstance(st.enabled, bool)
        self.assertIsInstance(st.available_schedulers, list)
        self.assertIsInstance(st.available_path_managers, list)

    def test_mptcp_socket_factory(self):
        sock, is_mptcp, desc = MptcpManager.create_mptcp_socket()
        self.assertIsNotNone(sock)
        self.assertIsInstance(is_mptcp, bool)
        self.assertIsInstance(desc, str)
        sock.close()

    def test_interface_path_discovery(self):
        ifaces = InterfacePathManager.get_available_interfaces()
        self.assertIsInstance(ifaces, list)
        # Should not contain loopback
        for iface in ifaces:
            self.assertFalse(iface.startswith("lo"))

        metrics = InterfacePathManager.get_path_metrics()
        self.assertIsInstance(metrics, list)
        for m in metrics:
            self.assertIsNotNone(m.interface)

    def test_dispatch_proxy_bridge_status(self):
        bridge = DispatchProxyBridge(port=1080)
        st = bridge.get_status()
        self.assertEqual(st["port"], 1080)
        self.assertIn("technology", st)
        # Must clearly identify application-layer proxy nature
        self.assertIn("Not MPTCP", st["technology"])

if __name__ == "__main__":
    unittest.main()
