"""
NetShield-IoT: Multipath Interface & Health Manager
Discovers and monitors physical network interfaces (Wi-Fi, Ethernet, Cellular) for multipath routing.
"""

import time
import socket
from typing import List, Dict, Optional
from core.interfaces import PathMetric

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class InterfacePathManager:
    """Discovers and evaluates all available network paths on the host."""

    @staticmethod
    def get_available_interfaces() -> List[str]:
        """Returns non-loopback network interfaces."""
        if not HAS_PSUTIL:
            return ["wlan0"]
        interfaces = []
        for iface, addrs in psutil.net_if_addrs().items():
            if iface.startswith("lo"):
                continue
            # Check if has IPv4
            has_ip = any(a.family == socket.AF_INET for a in addrs)
            if has_ip:
                interfaces.append(iface)
        return interfaces

    @staticmethod
    def get_path_metrics() -> List[PathMetric]:
        """Collects IP, operational status, and byte metrics for each interface."""
        if not HAS_PSUTIL:
            return [PathMetric(interface="wlan0", is_up=True)]

        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        io_counters = psutil.net_io_counters(pernic=True)

        metrics = []
        for iface in InterfacePathManager.get_available_interfaces():
            is_up = stats[iface].isup if iface in stats else False
            ip_addr = None
            if iface in addrs:
                for a in addrs[iface]:
                    if a.family == socket.AF_INET:
                        ip_addr = a.address
                        break

            rx_b = io_counters[iface].bytes_recv if iface in io_counters else 0
            tx_b = io_counters[iface].bytes_sent if iface in io_counters else 0

            metrics.append(PathMetric(
                interface=iface,
                ip_address=ip_addr,
                is_up=is_up,
                rx_bytes=rx_b,
                tx_bytes=tx_b
            ))

        return metrics
