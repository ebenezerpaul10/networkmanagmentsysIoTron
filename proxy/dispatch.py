"""
NetShield-IoT: Application-Level Multi-Interface Socket Dispatcher
Preserves existing dispatch-proxy compatibility while clearly distinguishing
application round-robin socket binding from genuine transport-layer MPTCP.
"""

import shutil
import subprocess
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class DispatchProxyBridge:
    """
    Manages the application-layer dispatch-proxy service for multi-interface traffic distribution.
    Note: Distributes individual application TCP sockets across interfaces; does not aggregate a single TCP flow.
    """

    def __init__(self, port: int = 1080):
        self.port = port
        self._process: Optional[subprocess.Popen] = None

    @staticmethod
    def is_installed() -> bool:
        return shutil.which("dispatch") is not None

    def start(self, interfaces: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.is_installed():
            return {
                "success": False,
                "message": "dispatch-proxy is not installed (install via 'npm install -g dispatch-proxy')"
            }

        if self._process and self._process.poll() is None:
            return {"success": True, "message": f"Dispatch proxy already running on port {self.port}"}

        cmd = ["dispatch", "start", "--port", str(self.port)]
        if interfaces:
            for iface in interfaces:
                cmd.extend(["--interface", iface])

        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {
                "success": True,
                "port": self.port,
                "type": "Application-Level SOCKS5 Multi-Interface Dispatcher",
                "message": f"Started dispatch-proxy on port {self.port}"
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to launch dispatch: {e}"}

    def stop(self):
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2.0)
            except Exception:
                try: self._process.kill()
                except Exception: pass
            self._process = None

    def get_status(self) -> Dict[str, Any]:
        running = (self._process is not None and self._process.poll() is None)
        return {
            "installed": self.is_installed(),
            "running": running,
            "port": self.port,
            "technology": "Application-Layer Round-Robin SOCKS Proxy (Not MPTCP)"
        }
