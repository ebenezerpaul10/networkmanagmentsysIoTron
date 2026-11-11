"""
NetShield-IoT: Core Data Interfaces & Transfer Objects
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ActiveWifiStatus:
    ssid: str = "Disconnected"
    bssid: str = "None"
    channel: int = 0
    signal_pct: int = 0
    rssi_dbm: int = -100
    frequency_mhz: int = 0
    is_connected: bool = False

@dataclass
class ApCandidate:
    bssid: str
    ssid: str
    channel: int
    frequency_mhz: int = 2412
    signal_pct: int = 0
    rssi_dbm: int = -100
    supports_80211r: bool = False
    supports_80211k: bool = False
    supports_80211v: bool = False
    security_flags: str = ""

@dataclass
class ScanResult:
    ch1_count: int = 0
    ch6_count: int = 0
    ch11_count: int = 0
    total_aps: int = 0
    best_bssid: str = "None"
    best_chan: int = 1
    best_sig: int = 0
    candidates: List[ApCandidate] = field(default_factory=list)

@dataclass
class Capabilities80211:
    supports_80211r: bool = False  # Fast BSS Transition (FT)
    supports_80211k: bool = False  # Radio Resource Management (RRM)
    supports_80211v: bool = False  # BSS Transition Management (BTM)
    driver_name: str = "Unknown"
    phy_name: str = "Unknown"
    details: str = ""

@dataclass
class RoamResult:
    success: bool
    method_used: str  # "wpa_cli_ft", "wpa_cli_roam", "nmcli_switch", "unsupported"
    previous_bssid: str
    target_bssid: str
    channel: int
    signal_pct: int
    latency_ms: float
    interruption_duration_ms: float = 0.0
    rollback_triggered: bool = False
    message: str = ""

@dataclass
class MptcpStatus:
    kernel_supported: bool = False
    enabled: bool = False
    pm_type: int = 0
    available_schedulers: List[str] = field(default_factory=list)
    available_path_managers: List[str] = field(default_factory=list)
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    active_subflows: int = 0

@dataclass
class PathMetric:
    interface: str
    ip_address: Optional[str] = None
    is_up: bool = False
    latency_ms: float = -1.0
    throughput_mbps: float = 0.0
    rx_bytes: int = 0
    tx_bytes: int = 0
