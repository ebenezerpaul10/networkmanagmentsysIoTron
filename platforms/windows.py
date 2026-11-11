"""
NetShield-IoT: Windows Platform Implementation
Uses Windows native WLAN tools (netsh wlan) and psutil.
"""

import subprocess
import time
import socket
from typing import Tuple, List, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from platforms.base import AbstractPlatformAdapter
from core.interfaces import (
    ActiveWifiStatus,
    ApCandidate,
    ScanResult,
    Capabilities80211,
    RoamResult
)

class WindowsPlatformAdapter(AbstractPlatformAdapter):
    """Windows implementation using netsh wlan and native Windows APIs."""

    def __init__(self):
        self.p1 = "Wi-Fi"
        self.p2 = None
        self._detect_interfaces()

    def get_system_name(self) -> str:
        return "Windows"

    def _detect_interfaces(self):
        interfaces = []
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True, stderr=subprocess.DEVNULL, timeout=3.0
            )
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Name"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        interfaces.append(parts[1].strip())
        except Exception:
            pass

        self.p1 = interfaces[0] if len(interfaces) > 0 else "Wi-Fi"
        self.p2 = interfaces[1] if len(interfaces) > 1 else None

    def get_wifi_interfaces(self) -> Tuple[Optional[str], Optional[str]]:
        self._detect_interfaces()
        return self.p1, self.p2

    def is_secondary_wifi_detected(self) -> bool:
        self._detect_interfaces()
        return self.p2 is not None

    def get_active_wifi_status(self) -> ActiveWifiStatus:
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True, stderr=subprocess.DEVNULL, timeout=3.0
            )
            ssid = "Unknown"
            bssid = "None"
            channel = 0
            signal = 0
            state = "disconnected"

            for line in out.splitlines():
                line = line.strip()
                if line.startswith("State"):
                    state = line.split(":", 1)[1].strip().lower()
                elif line.startswith("SSID") and not line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1: ssid = parts[1].strip()
                elif line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1: bssid = parts[1].strip().upper()
                elif line.startswith("Channel"):
                    parts = line.split(":", 1)
                    if len(parts) > 1 and parts[1].strip().isdigit():
                        channel = int(parts[1].strip())
                elif line.startswith("Signal"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        val = parts[1].strip().replace("%", "")
                        if val.isdigit(): signal = int(val)

            is_connected = ("connected" in state and ssid != "Unknown")
            rssi = int((signal / 2) - 100)
            return ActiveWifiStatus(
                ssid=ssid if is_connected else "Disconnected",
                bssid=bssid if is_connected else "None",
                channel=channel,
                signal_pct=signal,
                rssi_dbm=rssi,
                frequency_mhz=2412 + (channel - 1) * 5 if channel > 0 else 0,
                is_connected=is_connected
            )
        except Exception:
            return ActiveWifiStatus()

    def scan_nearby_wifi_channels(self) -> ScanResult:
        ch1 = 0; ch6 = 0; ch11 = 0; total = 0
        best_bssid = "None"
        best_chan = 1
        best_sig = 0
        candidates = []

        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                text=True, stderr=subprocess.DEVNULL, timeout=4.0
            )
            cur_ssid = None
            cur_bssid = None
            cur_sig = 0

            for line in out.splitlines():
                line = line.strip()
                if line.startswith("SSID") and not line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        cur_ssid = parts[1].strip()
                elif line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        cur_bssid = parts[1].strip().upper()
                        total += 1
                elif line.startswith("Signal"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        val = parts[1].strip().replace("%", "")
                        cur_sig = int(val) if val.isdigit() else 0
                elif line.startswith("Channel"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        c_str = parts[1].strip()
                        chan = int(c_str) if c_str.isdigit() else 0
                        if chan == 1: ch1 += 1
                        elif chan == 6: ch6 += 1
                        elif chan == 11: ch11 += 1

                        if cur_bssid and cur_ssid:
                            rssi = int((cur_sig / 2) - 100)
                            candidates.append(ApCandidate(
                                bssid=cur_bssid,
                                ssid=cur_ssid,
                                channel=chan,
                                signal_pct=cur_sig,
                                rssi_dbm=rssi
                            ))

                        if cur_sig > best_sig and cur_bssid:
                            best_sig = cur_sig
                            best_chan = chan
                            best_bssid = cur_bssid
        except Exception:
            pass

        return ScanResult(
            ch1_count=ch1, ch6_count=ch6, ch11_count=ch11,
            total_aps=total, best_bssid=best_bssid,
            best_chan=best_chan, best_sig=best_sig,
            candidates=candidates
        )

    def find_candidates_for_ssid(self, target_ssid: str) -> List[ApCandidate]:
        if not target_ssid or target_ssid in ["Disconnected", "Scanning..."]:
            return []
        scan = self.scan_nearby_wifi_channels()
        matches = [c for c in scan.candidates if c.ssid == target_ssid]
        matches.sort(key=lambda x: x.signal_pct, reverse=True)
        return matches

    def detect_80211_capabilities(self, iface: Optional[str] = None) -> Capabilities80211:
        # Windows Native WLAN handles 802.11r in driver/profile if supported
        has_ft = False
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "drivers"],
                text=True, stderr=subprocess.DEVNULL, timeout=3.0
            )
            if "Fast Roaming" in out or "802.11r" in out:
                has_ft = True
        except Exception:
            pass

        return Capabilities80211(
            supports_80211r=has_ft,
            supports_80211k=False,
            supports_80211v=False,
            driver_name="Windows WLAN Native Driver",
            phy_name=self.p1,
            details="Windows Native WLAN Auto-Configuration"
        )

    def switch_wifi_bssid(
        self,
        ssid: str,
        target_bssid: str,
        use_fast_transition: bool = True
    ) -> RoamResult:
        current_status = self.get_active_wifi_status()
        prev_bssid = current_status.bssid
        t_start = time.perf_counter()

        try:
            subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6.0
            )
            time.sleep(1.5)
            new_st = self.get_active_wifi_status()
            lat = self._measure_ping()
            t_duration = round((time.perf_counter() - t_start) * 1000, 1)

            return RoamResult(
                success=True,
                method_used="netsh_connect",
                previous_bssid=prev_bssid,
                target_bssid=new_st.bssid if new_st.bssid != "None" else target_bssid,
                channel=new_st.channel,
                signal_pct=new_st.signal_pct,
                latency_ms=lat,
                interruption_duration_ms=t_duration,
                message=f"Reconnected to {ssid} on Windows"
            )
        except Exception as e:
            return RoamResult(
                success=False,
                method_used="netsh_connect",
                previous_bssid=prev_bssid,
                target_bssid=target_bssid,
                channel=current_status.channel,
                signal_pct=current_status.signal_pct,
                latency_ms=-1.0,
                message=f"Windows netsh switch error: {e}"
            )

    def sample_bandwidth_bytes(self) -> Tuple[int, int]:
        rx1, rx2 = 0, 0
        if HAS_PSUTIL:
            try:
                counters = psutil.net_io_counters(pernic=True)
                if self.p1 in counters:
                    rx1 = counters[self.p1].bytes_recv
                if self.p2 and self.p2 in counters:
                    rx2 = counters[self.p2].bytes_recv
            except Exception:
                pass
        return rx1, rx2

    def _measure_ping(self) -> float:
        try:
            t0 = time.time()
            s = socket.create_connection(("1.1.1.1", 53), timeout=2.0)
            latency = round((time.time() - t0) * 1000, 1)
            s.close()
            return latency
        except Exception:
            return -1.0
