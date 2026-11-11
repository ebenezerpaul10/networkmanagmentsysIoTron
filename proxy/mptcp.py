"""
NetShield-IoT: True Multipath TCP (MPTCP) Transport Subsystem
Detects Linux kernel MPTCP capabilities, manages endpoints, and creates native MPTCP sockets.
"""

import os
import socket
import subprocess
import logging
from typing import Optional, List, Dict, Any, Tuple
from core.interfaces import MptcpStatus
from config.settings import MPTCP_PROT_NUMBER, MPTCP_TEST_HOST, MPTCP_TEST_PORT

logger = logging.getLogger(__name__)

class MptcpManager:
    """
    Manages true Multipath TCP (RFC 8684) kernel capabilities and sockets.
    Note: MPTCP requires kernel support, compatible remote servers, and endpoints.
    """

    @staticmethod
    def detect_kernel_support() -> MptcpStatus:
        """
        Inspects Linux kernel sysctl, socket constants, and iproute2 mptcp configuration.
        """
        enabled = False
        kernel_supported = False
        schedulers = []
        path_managers = []
        endpoints = []
        pm_type = 0

        # 1. Check socket protocol support
        try:
            proto = getattr(socket, "IPPROTO_MPTCP", 262)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
            s.close()
            kernel_supported = True
        except Exception:
            kernel_supported = False

        # 2. Check /proc/sys/net/mptcp/enabled
        try:
            if os.path.exists("/proc/sys/net/mptcp/enabled"):
                with open("/proc/sys/net/mptcp/enabled") as f:
                    val = f.read().strip()
                    enabled = (val == "1")
                    kernel_supported = True
        except Exception:
            pass

        # 3. Read available path managers & schedulers
        try:
            if os.path.exists("/proc/sys/net/mptcp/available_path_managers"):
                with open("/proc/sys/net/mptcp/available_path_managers") as f:
                    path_managers = f.read().strip().split()
            if os.path.exists("/proc/sys/net/mptcp/available_schedulers"):
                with open("/proc/sys/net/mptcp/available_schedulers") as f:
                    schedulers = f.read().strip().split()
            if os.path.exists("/proc/sys/net/mptcp/pm_type"):
                with open("/proc/sys/net/mptcp/pm_type") as f:
                    pm_type = int(f.read().strip() or "0")
        except Exception:
            pass

        # 4. Read configured endpoints via 'ip mptcp endpoint show'
        try:
            out = subprocess.check_output(
                ["ip", "mptcp", "endpoint", "show"],
                text=True, stderr=subprocess.DEVNULL, timeout=2.0
            )
            for line in out.splitlines():
                line = line.strip()
                if line:
                    endpoints.append({"raw": line})
        except Exception:
            pass

        return MptcpStatus(
            kernel_supported=kernel_supported,
            enabled=enabled,
            pm_type=pm_type,
            available_schedulers=schedulers,
            available_path_managers=path_managers,
            endpoints=endpoints,
            active_subflows=len(endpoints)
        )

    @staticmethod
    def create_mptcp_socket() -> Tuple[Optional[socket.socket], bool, str]:
        """
        Creates an MPTCP-capable socket if supported by kernel,
        otherwise falls back to standard TCP socket.
        Returns: (socket_instance, is_mptcp, protocol_description)
        """
        proto = getattr(socket, "IPPROTO_MPTCP", 262)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
            return sock, True, "Native Multipath TCP (RFC 8684)"
        except Exception as e:
            # Graceful fallback to standard TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            return sock, False, f"Standard TCP Fallback (MPTCP unavailable: {e})"

    @staticmethod
    def test_mptcp_connection(host: str = MPTCP_TEST_HOST, port: int = MPTCP_TEST_PORT) -> Dict[str, Any]:
        """
        Tests whether an end-to-end MPTCP connection can be established.
        """
        sock, is_mptcp, desc = MptcpManager.create_mptcp_socket()
        if not is_mptcp or not sock:
            return {
                "success": False,
                "is_mptcp": False,
                "error": "MPTCP protocol not available on local host"
            }

        try:
            sock.settimeout(4.0)
            sock.connect((host, port))
            # Send HTTP request
            sock.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
            resp = sock.recv(512).decode("utf-8", errors="ignore")
            sock.close()
            return {
                "success": True,
                "is_mptcp": True,
                "server": f"{host}:{port}",
                "description": desc,
                "status_line": resp.splitlines()[0] if resp else "Connected"
            }
        except Exception as e:
            try: sock.close()
            except Exception: pass
            return {
                "success": False,
                "is_mptcp": True,
                "error": f"Connection to MPTCP server failed: {e}"
            }
