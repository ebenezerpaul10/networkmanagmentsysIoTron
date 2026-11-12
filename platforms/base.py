"""
NetShield-IoT: Abstract Base Platform Adapter
Defines the standard cross-platform contract for wireless network operations.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from core.interfaces import (
    ActiveWifiStatus,
    ApCandidate,
    ScanResult,
    Capabilities80211,
    RoamResult
)

class AbstractPlatformAdapter(ABC):
    """Abstract interface for OS-level Wi-Fi, hardware, and network management."""

    @abstractmethod
    def get_system_name(self) -> str:
        """Returns the canonical OS identifier ('Linux', 'Windows', 'Darwin')."""
        pass

    @abstractmethod
    def get_wifi_interfaces(self) -> Tuple[Optional[str], Optional[str]]:
        """Returns (primary_wifi_interface, secondary_wifi_interface)."""
        pass

    @abstractmethod
    def is_secondary_wifi_detected(self) -> bool:
        """Returns True if a second Wi-Fi dongle or tethered interface is active."""
        pass

    @abstractmethod
    def get_active_wifi_status(self) -> ActiveWifiStatus:
        """Returns the active Wi-Fi SSID, BSSID, channel, signal, and connection state."""
        pass

    @abstractmethod
    def scan_nearby_wifi_channels(self) -> ScanResult:
        """Performs out-of-band or native scan of nearby 2.4GHz APs."""
        pass

    @abstractmethod
    def find_candidates_for_ssid(self, target_ssid: str) -> List[ApCandidate]:
        """Returns all visible BSSID candidates for the given SSID, sorted by quality."""
        pass

    @abstractmethod
    def detect_80211_capabilities(self, iface: Optional[str] = None) -> Capabilities80211:
        """Queries wireless driver and subsystem for 802.11r/k/v capabilities."""
        pass

    @abstractmethod
    def switch_wifi_bssid(
        self,
        ssid: str,
        target_bssid: str,
        use_fast_transition: bool = True
    ) -> RoamResult:
        """
        Executes a BSSID transition.
        Attempts seamless fast transition if supported, falling back gracefully to profile update.
        """
        pass

    @abstractmethod
    def sample_bandwidth_bytes(self) -> Tuple[int, int]:
        """Returns raw (rx_bytes_primary, rx_bytes_secondary) counters."""
        pass
