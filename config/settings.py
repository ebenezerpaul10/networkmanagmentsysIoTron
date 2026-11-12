"""
NetShield-IoT: Centralized Configuration & System Settings
"""

import os
import socket

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DASHBOARD_DIR = os.path.join(BASE_DIR, "web_dashboard")
HTML_FILE_PATH = os.path.join(WEB_DASHBOARD_DIR, "index.html")

# System & API Server Settings
WEB_HOST = "0.0.0.0"
WEB_PORT = 8080
DEFAULT_BAUD = 115200

# ---------------------------------------------------------------------------
# Intelligent Wi-Fi Roaming & Decision Settings
# ---------------------------------------------------------------------------
# Minimum signal improvement required to consider a roam (avoids oscillation)
ROAM_HYSTERESIS_DBM = 10         # e.g., candidate must be >= 10 dBm stronger
ROAM_HYSTERESIS_PCT = 15         # e.g., candidate must have >= 15% higher signal
ROAM_STICKY_THRESHOLD_DBM = -72  # RSSI below which client is considered "sticky"
ROAM_STICKY_THRESHOLD_PCT = 45   # Signal % below which roaming search activates
ROAM_COOLDOWN_SEC = 45           # Minimum seconds between automatic roaming decisions
ROAM_VERIFY_TIMEOUT_SEC = 4.0    # Post-roam association verification timeout
ROAM_PING_TARGET = ("1.1.1.1", 53)
ROAM_HTTP_TARGET = "https://www.google.com"

# ---------------------------------------------------------------------------
# DNS Sinkhole Settings
# ---------------------------------------------------------------------------
DNS_BIND_ADDR = "127.0.0.1"      # Bind to loopback to prevent open resolver abuse
DNS_STANDARD_PORT = 53           # RFC-compliant standard DNS port
DNS_FALLBACK_PORT = 5354         # Fallback if port 53 cannot be bound (NEVER 5353 mDNS)
DNS_UPSTREAM_PRIMARY = ("1.1.1.1", 53)
DNS_UPSTREAM_SECONDARY = ("8.8.8.8", 53)
DNS_QUERY_TIMEOUT = 2.0

DEFAULT_BLOCKED_DOMAINS = [
    "doubleclick.net", "googleadservices.com", "adservice.google.com",
    "telemetry.microsoft.com", "analytics.google.com", "facebook.com/tr",
    "scorecardresearch.com", "adnxs.com", "taboola.com", "outbrain.com",
    "adroll.com", "criteo.com", "popads.net", "tracking", "telemetry"
]

DEFAULT_ALLOWED_DOMAINS = [
    "cloudflare.com", "google.com", "github.com", "apple.com", "microsoft.com"
]

# ---------------------------------------------------------------------------
# Multipath & MPTCP Settings
# ---------------------------------------------------------------------------
MPTCP_PROT_NUMBER = getattr(socket, "IPPROTO_MPTCP", 262)
MPTCP_TEST_HOST = "multipath-tcp.org"
MPTCP_TEST_PORT = 80
DISPATCH_PROXY_PORT = 1080

# ---------------------------------------------------------------------------
# Hardware / ESP32 Serial Settings
# ---------------------------------------------------------------------------
ESP32_KEYWORDS = [
    "cp210", "ch340", "ch341", "ch9102", "ftdi", "uart",
    "usb serial", "espressif", "esp32", "usb to uart"
]
