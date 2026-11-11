"""
NetShield-IoT: macOS Platform Implementation
Uses macOS native CoreWLAN / airport binary and networksetup tools.
"""

import os
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

AIRPORT_BIN = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

class MacOSPlatformAdapter(AbstractPlatformAdapter):
    """macOS implementation using Apple CoreWLAN airport utility and networksetup."""

    def __init__(self):
        self.p1 = "en0"
        self.p2 = None

    def get_system_name(self) -> str:
        return "Darwin"

    def get_wifi_interfaces(self) -> Tuple[Optional[str], Optional[str]]:
        return self.p1, self.p2

    def is_secondary_wifi_detected(self) -> bool:
        return False

    def get_active_wifi_status(self) -> ActiveWifiStatus:
        if not os.path.exists(AIRPORT_BIN):
            return ActiveWifiStatus()

        try:
            out = subprocess.check_output(
                [AIRPORT_BIN, "-I"],
                text=True, stderr=subprocess.DEVNULL, timeout=2.5
            )
            ssid = "Unknown"
            bssid = "None"
            channel = 0
            rssi = -100

            for line in out.splitlines():
                line = line.strip()
                if line.startswith("SSID:"):
                    ssid = line.split(":", 1)[1].strip()
                elif line.startswith("BSSID:"):
                    bssid = line.split(":", 1)[1].strip().upper()
                elif line.startswith("channel:"):
                    ch_str = line.split(":", 1)[1].strip().split(",")[0]
                    if ch_str.isdigit(): channel = int(ch_str)
                elif line.startswith("agrCtlRSSI:"):
                    r_str = line.split(":", 1)[1].strip()
                    if r_str.lstrip("-").isdigit(): rssi = int(r_str)

            signal = min(100, max(0, int((rssi + 100) * 2)))
            is_connected = (ssid != "Unknown" and bssid != "None")
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

        if not os.path.exists(AIRPORT_BIN):
            return ScanResult()

        try:
            out = subprocess.check_output(
                [AIRPORT_BIN, "-s"],
                text=True, stderr=subprocess.DEVNULL, timeout=4.0
            )
            for line in out.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    total += 1
                    ssid = parts[0]
                    bssid = parts[1].upper()
                    rssi = int(parts[2]) if parts[2].lstrip("-").isdigit() else -100
                    sig = min(100, max(0, int((rssi + 100) * 2)))
                    chan = 0
                    for p in parts[3:]:
                        if p.isdigit():
                            chan = int(p)
                            break

                    if chan == 1: ch1 += 1
                    elif chan == 6: ch6 += 1
                    elif chan == 11: ch11 += 1

                    candidates.append(ApCandidate(
                        bssid=bssid,
                        ssid=ssid,
                        channel=chan,
                        signal_pct=sig,
                        rssi_dbm=rssi
                    ))

                    if sig > best_sig:
                        best_sig = sig
                        best_chan = chan
                        best_bssid = bssid
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
        return Capabilities80211(
            supports_80211r=True,  # macOS Apple Silicon and Intel CoreWLAN natively support 802.11r/k/v
            supports_80211k=True,
            supports_80211v=True,
            driver_name="Apple CoreWLAN / AirPort",
            phy_name=self.p1,
            details="macOS Native 802.11k/v/r CoreWLAN Fast Roaming"
        )

    def switch_wifi_bssid(
        self,
        ssid: str,
        target_bssid: str,
        use_fast_transition: bool = True
    ) -> RoamResult:
        current_status = self.get_active_wifi_status()
        t_start = time.perf_counter()

        try:
            subprocess.run(
                ["networksetup", "-setairportnetwork", self.p1, ssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6.0
            )
            time.sleep(1.5)
            new_st = self.get_active_wifi_status()
            lat = self._measure_ping()
            t_duration = round((time.perf_counter() - t_start) * 1000, 1)

            return RoamResult(
                success=True,
                method_used="macos_networksetup",
                previous_bssid=current_status.bssid,
                target_bssid=new_st.bssid if new_st.bssid != "None" else target_bssid,
                channel=new_st.channel,
                signal_pct=new_st.signal_pct,
                latency_ms=lat,
                interruption_duration_ms=t_duration,
                message=f"Reassociated on macOS ({ssid})"
            )
        except Exception as e:
            return RoamResult(
                success=False,
                method_used="macos_networksetup",
                previous_bssid=current_status.bssid,
                target_bssid=target_bssid,
                channel=current_status.channel,
                signal_pct=current_status.signal_pct,
                latency_ms=-1.0,
                message=f"macOS roam error: {e}"
            )

    def sample_bandwidth_bytes(self) -> Tuple[int, int]:
        rx1, rx2 = 0, 0
        if HAS_PSUTIL:
            try:
                counters = psutil.net_io_counters(pernic=True)
                if self.p1 in counters:
                    rx1 = counters[self.p1].bytes_recv
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
