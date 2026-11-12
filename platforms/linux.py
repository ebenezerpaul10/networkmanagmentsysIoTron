"""
NetShield-IoT: Linux Platform Implementation
Integrates wpa_cli (seamless 802.11 in-driver roam), NetworkManager, and iw diagnostics.
"""

import os
import re
import time
import socket
import subprocess
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

class LinuxPlatformAdapter(AbstractPlatformAdapter):
    """Linux implementation leveraging wpa_cli, nmcli, iw, and psutil."""

    def __init__(self):
        self.primary_iface = None
        self.secondary_iface = None
        self._refresh_interfaces()

    def get_system_name(self) -> str:
        return "Linux"

    def _refresh_interfaces(self):
        p1 = "wlan0" if os.path.exists("/sys/class/net/wlan0") else None
        p2 = "wlan1" if os.path.exists("/sys/class/net/wlan1") else None

        if not p1 and HAS_PSUTIL:
            for iface in psutil.net_if_addrs().keys():
                if iface.startswith("wl"):
                    if not p1:
                        p1 = iface
                    elif not p2:
                        p2 = iface

        self.primary_iface = p1 or "wlan0"
        self.secondary_iface = p2

    def get_wifi_interfaces(self) -> Tuple[Optional[str], Optional[str]]:
        self._refresh_interfaces()
        return self.primary_iface, self.secondary_iface

    def is_secondary_wifi_detected(self) -> bool:
        self._refresh_interfaces()
        if not self.secondary_iface:
            return False
        return os.path.exists(f"/sys/class/net/{self.secondary_iface}")

    def get_active_wifi_status(self) -> ActiveWifiStatus:
        """
        Retrieves active Wi-Fi status.
        Strategy A: wpa_cli status (fast, lightweight, direct supplicant query).
        Strategy B: nmcli active connection query.
        """
        # Strategy A: wpa_cli
        try:
            out = subprocess.check_output(
                ["wpa_cli", "status"],
                text=True, stderr=subprocess.DEVNULL, timeout=2.0
            )
            data = {}
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()

            state = data.get("wpa_state", "")
            if state in ["COMPLETED", "AUTHENTICATED"]:
                bssid = data.get("bssid", "None").upper()
                ssid = data.get("ssid", "Unknown")
                freq = int(data.get("freq", 0))
                chan = self._freq_to_channel(freq)

                # Query RSSI via wpa_cli bss if available
                rssi = self._get_rssi_for_bssid(bssid)
                sig_pct = min(100, max(0, int((rssi + 100) * 2))) if rssi != -100 else 60

                return ActiveWifiStatus(
                    ssid=ssid,
                    bssid=bssid,
                    channel=chan,
                    signal_pct=sig_pct,
                    rssi_dbm=rssi,
                    frequency_mhz=freq,
                    is_connected=True
                )
        except Exception:
            pass

        # Strategy B: nmcli fallback
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,bssid,chan,signal,ssid,freq", "dev", "wifi"],
                text=True, stderr=subprocess.DEVNULL, timeout=2.5
            )
            for line in out.strip().split("\n"):
                if line.startswith("yes:"):
                    parts = line.split(":")
                    bssid = ":".join(parts[1:7]).replace("\\", "").upper()
                    chan = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    signal = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    ssid = parts[9] if len(parts) > 9 else "Unknown"
                    freq = int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else (2412 + (chan - 1) * 5)
                    rssi = int((signal / 2) - 100)
                    return ActiveWifiStatus(
                        ssid=ssid,
                        bssid=bssid,
                        channel=chan,
                        signal_pct=signal,
                        rssi_dbm=rssi,
                        frequency_mhz=freq,
                        is_connected=True
                    )
        except Exception:
            pass

        return ActiveWifiStatus()

    def _get_rssi_for_bssid(self, bssid: str) -> int:
        try:
            out = subprocess.check_output(
                ["wpa_cli", "bss", bssid],
                text=True, stderr=subprocess.DEVNULL, timeout=1.5
            )
            for line in out.splitlines():
                if line.startswith("level="):
                    val = line.split("=")[1].strip()
                    return int(val)
        except Exception:
            pass
        return -100

    def _freq_to_channel(self, freq: int) -> int:
        if freq == 2484:
            return 14
        if 2412 <= freq <= 2472:
            return (freq - 2412) // 5 + 1
        if 5180 <= freq <= 5825:
            return (freq - 5000) // 5
        return 0

    def scan_nearby_wifi_channels(self) -> ScanResult:
        ch1 = 0; ch6 = 0; ch11 = 0; total = 0
        best_bssid = "None"
        best_chan = 1
        best_sig = 0
        candidate_list: List[ApCandidate] = []

        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "CHAN,SSID,BSSID,SIGNAL,FREQ,SECURITY", "dev", "wifi", "list"],
                text=True, stderr=subprocess.DEVNULL, timeout=4.0
            )
            for line in out.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 8 and parts[0].isdigit():
                    total += 1
                    ch = int(parts[0])
                    ssid = parts[1]
                    bssid = ":".join(parts[2:8]).replace("\\", "").upper()
                    sig_str = parts[8] if len(parts) > 8 else "0"
                    sig = int(sig_str) if sig_str.isdigit() else 0
                    freq_str = parts[9] if len(parts) > 9 else "2412"
                    freq = int(freq_str) if freq_str.isdigit() else 2412
                    sec = parts[10] if len(parts) > 10 else ""

                    if ch == 1: ch1 += 1
                    elif ch == 6: ch6 += 1
                    elif ch == 11: ch11 += 1

                    rssi = int((sig / 2) - 100)
                    # Check for Fast Transition or RRM flags in security string or wpa_cli
                    supports_ft = "FT" in sec or "802.11r" in sec.lower()

                    cand = ApCandidate(
                        bssid=bssid,
                        ssid=ssid,
                        channel=ch,
                        frequency_mhz=freq,
                        signal_pct=sig,
                        rssi_dbm=rssi,
                        supports_80211r=supports_ft,
                        security_flags=sec
                    )
                    candidate_list.append(cand)

                    if sig > best_sig:
                        best_sig = sig
                        best_chan = ch
                        best_bssid = bssid
        except Exception:
            pass

        return ScanResult(
            ch1_count=ch1,
            ch6_count=ch6,
            ch11_count=ch11,
            total_aps=total,
            best_bssid=best_bssid,
            best_chan=best_chan,
            best_sig=best_sig,
            candidates=candidate_list
        )

    def find_candidates_for_ssid(self, target_ssid: str) -> List[ApCandidate]:
        if not target_ssid or target_ssid in ["Disconnected", "Scanning...", "Unknown"]:
            return []

        scan = self.scan_nearby_wifi_channels()
        matches = [c for c in scan.candidates if c.ssid == target_ssid]
        matches.sort(key=lambda x: x.signal_pct, reverse=True)
        return matches

    def detect_80211_capabilities(self, iface: Optional[str] = None) -> Capabilities80211:
        """
        Directly checks Linux wireless subsystem (nl80211 / iw phy) for
        IEEE 802.11r (FT), 802.11k (RRM), and 802.11v (BTM).
        """
        target_iface = iface or self.primary_iface or "wlan0"
        has_rrm = False
        has_ft = False
        has_btm = False
        details = []

        # 1. Inspect iw phy capabilities
        try:
            out = subprocess.check_output(
                ["iw", "phy"],
                text=True, stderr=subprocess.DEVNULL, timeout=2.5
            )
            if "* [ RRM ]" in out or "RRM" in out:
                has_rrm = True
                details.append("802.11k Radio Resource Management (RRM) supported by kernel/phy")
            if "FT" in out or "FILS_STA" in out:
                has_ft = True
                details.append("Fast Link Transition (FT/FILS) support in phy")
        except Exception:
            pass

        # 2. Inspect wpa_supplicant driver capabilities
        try:
            wpa_out = subprocess.check_output(
                ["wpa_cli", "status"],
                text=True, stderr=subprocess.DEVNULL, timeout=1.5
            )
            cur_bssid = None
            for line in wpa_out.splitlines():
                if line.startswith("bssid="):
                    cur_bssid = line.split("=")[1].strip()

            if cur_bssid:
                bss_info = subprocess.check_output(
                    ["wpa_cli", "bss", cur_bssid],
                    text=True, stderr=subprocess.DEVNULL, timeout=1.5
                )
                if "FT-" in bss_info or "[FT]" in bss_info:
                    has_ft = True
                    details.append(f"Connected AP {cur_bssid} advertises 802.11r Fast Transition")
                if "RRM" in bss_info or "0b050" in bss_info:  # RRM Information Element tag
                    has_rrm = True
                if "BTM" in bss_info:
                    has_btm = True
        except Exception:
            pass

        detail_str = "; ".join(details) if details else "Standard 802.11 infrastructure roaming"
        return Capabilities80211(
            supports_80211r=has_ft,
            supports_80211k=has_rrm,
            supports_80211v=has_btm,
            driver_name="nl80211 / mac80211",
            phy_name=target_iface,
            details=detail_str
        )

    def switch_wifi_bssid(
        self,
        ssid: str,
        target_bssid: str,
        use_fast_transition: bool = True
    ) -> RoamResult:
        """
        Executes an AP transition.
        Primary Path: wpa_cli roam <target_bssid> (keeps TCP connections intact).
        Secondary Path: nmcli profile modification with rollback protection.
        """
        current_status = self.get_active_wifi_status()
        prev_bssid = current_status.bssid

        if not target_bssid or prev_bssid.upper() == target_bssid.upper():
            return RoamResult(
                success=False,
                method_used="noop",
                previous_bssid=prev_bssid,
                target_bssid=target_bssid,
                channel=current_status.channel,
                signal_pct=current_status.signal_pct,
                latency_ms=0.0,
                message="Already connected to target BSSID"
            )

        t_start = time.perf_counter()

        # Strategy 1: wpa_cli roam (fastest, keeps TCP sockets alive)
        if use_fast_transition:
            try:
                res = subprocess.run(
                    ["wpa_cli", "roam", target_bssid],
                    capture_output=True, text=True, timeout=3.0
                )
                if res.returncode == 0 and "OK" in res.stdout:
                    # Give supplicant up to 2.5s to complete in-driver transition
                    for _ in range(5):
                        time.sleep(0.5)
                        new_st = self.get_active_wifi_status()
                        if new_st.bssid.upper() == target_bssid.upper():
                            t_interruption = round((time.perf_counter() - t_start) * 1000, 1)
                            lat = self._measure_ping()
                            return RoamResult(
                                success=True,
                                method_used="wpa_cli_fast_roam",
                                previous_bssid=prev_bssid,
                                target_bssid=target_bssid,
                                channel=new_st.channel,
                                signal_pct=new_st.signal_pct,
                                latency_ms=lat,
                                interruption_duration_ms=t_interruption,
                                message=f"Seamlessly roamed via wpa_cli ({t_interruption}ms handoff)"
                            )
            except Exception:
                pass

        # Strategy 2: NetworkManager profile lock with rollback protection
        try:
            subprocess.check_call(
                ["nmcli", "connection", "modify", ssid, "802-11-wireless.bssid", target_bssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4.0
            )
            subprocess.check_call(
                ["nmcli", "connection", "up", ssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8.0
            )

            time.sleep(1.0)
            new_st = self.get_active_wifi_status()
            lat = self._measure_ping()
            t_interruption = round((time.perf_counter() - t_start) * 1000, 1)

            # Verification: Did we successfully associate and receive IP connectivity?
            if new_st.is_connected and lat > 0:
                return RoamResult(
                    success=True,
                    method_used="nmcli_locked_profile",
                    previous_bssid=prev_bssid,
                    target_bssid=new_st.bssid,
                    channel=new_st.channel,
                    signal_pct=new_st.signal_pct,
                    latency_ms=lat,
                    interruption_duration_ms=t_interruption,
                    message=f"Locked to AP {target_bssid} via NetworkManager"
                )
            else:
                raise RuntimeError("Post-roam connectivity verification failed")

        except Exception as e:
            # ROLLBACK to automatic roam profile
            try:
                subprocess.call(
                    ["nmcli", "connection", "modify", ssid, "802-11-wireless.bssid", ""],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3.0
                )
                subprocess.call(
                    ["nmcli", "connection", "up", ssid],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5.0
                )
            except Exception:
                pass

            reverted_st = self.get_active_wifi_status()
            return RoamResult(
                success=False,
                method_used="nmcli_rollback",
                previous_bssid=prev_bssid,
                target_bssid=target_bssid,
                channel=reverted_st.channel,
                signal_pct=reverted_st.signal_pct,
                latency_ms=self._measure_ping(),
                rollback_triggered=True,
                message=f"Roam to {target_bssid} failed ({e}). Connection safely restored to auto-profile."
            )

    def sample_bandwidth_bytes(self) -> Tuple[int, int]:
        rx1, rx2 = 0, 0
        if HAS_PSUTIL:
            try:
                counters = psutil.net_io_counters(pernic=True)
                p1, p2 = self.get_wifi_interfaces()
                if p1 and p1 in counters:
                    rx1 = counters[p1].bytes_recv
                if p2 and p2 in counters:
                    rx2 = counters[p2].bytes_recv
                return rx1, rx2
            except Exception:
                pass

        p1, p2 = self.get_wifi_interfaces()
        try:
            if p1 and os.path.exists(f"/sys/class/net/{p1}/statistics/rx_bytes"):
                with open(f"/sys/class/net/{p1}/statistics/rx_bytes") as f:
                    rx1 = int(f.read().strip())
            if p2 and os.path.exists(f"/sys/class/net/{p2}/statistics/rx_bytes"):
                with open(f"/sys/class/net/{p2}/statistics/rx_bytes") as f:
                    rx2 = int(f.read().strip())
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
