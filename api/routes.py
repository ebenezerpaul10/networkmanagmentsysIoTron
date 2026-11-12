"""
NetShield-IoT: REST API Route Handlers & Dispatcher
"""

import json
from typing import Dict, Any, Callable, Tuple
from config.settings import HTML_FILE_PATH

class ApiRouteDispatcher:
    """Dispatches API requests to engine handlers."""

    def __init__(self, engine_context: Any):
        self.ctx = engine_context

    def handle_get(self, path: str) -> Tuple[int, str, bytes]:
        """
        Dispatches GET requests.
        Returns: (http_status, content_type, response_body_bytes)
        """
        if path in ["/", "/index.html"]:
            try:
                with open(HTML_FILE_PATH, "rb") as f:
                    return 200, "text/html", f.read()
            except Exception as e:
                return 500, "text/plain", f"Error loading dashboard: {e}".encode()

        elif path == "/api/stats":
            data = self.ctx.get_system_stats()
            return 200, "application/json", json.dumps(data).encode()

        elif path == "/api/capabilities":
            data = self.ctx.get_system_capabilities()
            return 200, "application/json", json.dumps(data).encode()

        elif path == "/api/dns/stats":
            data = self.ctx.dns_server.get_metrics()
            return 200, "application/json", json.dumps(data).encode()

        elif path == "/api/mptcp/status":
            data = self.ctx.get_mptcp_status()
            return 200, "application/json", json.dumps(data).encode()

        # Serve static assets from web_dashboard (e.g. /assets/...)
        clean_path = path.split("?")[0].lstrip("/\\")
        web_dir = os.path.dirname(HTML_FILE_PATH)
        file_target = os.path.normpath(os.path.join(web_dir, clean_path))
        try:
            if os.path.commonpath([web_dir]) == os.path.commonpath([web_dir, file_target]) and os.path.isfile(file_target):
                import mimetypes
                ctype, _ = mimetypes.guess_type(file_target)
                with open(file_target, "rb") as f:
                    return 200, ctype or "application/octet-stream", f.read()
        except Exception:
            pass

        return 404, "application/json", json.dumps({"error": "Not Found"}).encode()

    def handle_post(self, path: str, body: bytes = b"") -> Tuple[int, str, bytes]:
        """
        Dispatches POST requests.
        Returns: (http_status, content_type, response_body_bytes)
        """
        if path == "/api/switch_ap":
            result = self.ctx.trigger_manual_roam()
            return 200, "application/json", json.dumps(result).encode()

        elif path == "/api/toggle_auto_roam":
            enabled = self.ctx.toggle_auto_roam()
            return 200, "application/json", json.dumps({"auto_roam_enabled": enabled}).encode()

        elif path == "/api/capture_baseline":
            baseline = self.ctx.capture_baseline()
            return 200, "application/json", json.dumps({"success": True, "baseline": baseline}).encode()

        elif path == "/api/run_benchmark":
            results = self.ctx.run_bandwidth_benchmark()
            return 200, "application/json", json.dumps(results).encode()

        return 404, "application/json", json.dumps({"error": "Endpoint Not Found"}).encode()
