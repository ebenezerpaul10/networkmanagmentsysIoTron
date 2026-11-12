"""
NetShield-IoT: HTTP API Server
Hosts the REST endpoints and web dashboard.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class DashboardApiHandler(BaseHTTPRequestHandler):
    dispatcher = None

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if not self.dispatcher:
            self.send_response(500)
            self.end_headers()
            return

        status, ctype, body = self.dispatcher.handle_get(self.path)
        self.send_response(status)
        self.send_header("Content-type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if not self.dispatcher:
            self.send_response(500)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        status, ctype, resp_body = self.dispatcher.handle_post(self.path, body)
        self.send_response(status)
        self.send_header("Content-type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp_body)

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging in terminal
        return

def create_api_server(host: str, port: int, dispatcher) -> HTTPServer:
    DashboardApiHandler.dispatcher = dispatcher
    server = HTTPServer((host, port), DashboardApiHandler)
    return server
