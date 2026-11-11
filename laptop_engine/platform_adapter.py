"""
NetShield-IoT Platform Adapter
Universal cross-platform network, Wi-Fi, and hardware abstraction layer for Windows, macOS, and Linux.
"""

import os
import re
import sys
import glob
import time
import socket
import platform
import subprocess
import urllib.request

SYSTEM = platform.system()  # 'Linux', 'Windows', 'Darwin'

# Try importing psutil for universal cross-platform network I/O
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Try importing pyserial list_ports
try:
    import serial.tools.list_ports as serial_list_ports
    HAS_PYSERIAL_PORTS = True
except ImportError:
    HAS_PYSERIAL_PORTS = False

# ---------------------------------------------------------------------------
# 1. ESP32 Hardware Serial Port Discovery (Cross-Platform)
# ---------------------------------------------------------------------------
def auto_detect_esp32_port():
    """
    Finds ESP32 hardware serial port on Windows (COM*), Linux (/dev/ttyUSB*),
    and macOS (/dev/cu.usb*).
    """
    # Strategy A: Use pyserial's native cross-platform port enumerator
    if HAS_PYSERIAL_PORTS:
        try:
            ports = list(serial_list_ports.comports())
            for p in ports:
                dev = p.device
                desc = (p.description or "").lower()
                hwid = (p.hwid or "").lower()
                # Match common ESP32 / USB-UART chips
                keywords = ["cp210", "ch340", "ch341", "ch9102", "ftdi", "uart", "usb serial", "espressif", "esp32"]
                if any(k in desc or k in hwid for k in keywords):
                    return dev
            # Fallback check on port name pattern
            for p in ports:
                dev = p.device
                if dev.startswith("COM") or dev.startswith("/dev/ttyUSB") or dev.startswith("/dev/ttyACM") or dev.startswith("/dev/cu.usb"):
                    return dev
        except Exception:
            pass

    # Strategy B: Filesystem matching for Linux & macOS
    if SYSTEM == "Windows":
        # Check standard COM ports COM1 through COM20
        import serial
        for i in range(1, 21):
            port_name = f"COM{i}"
            try:
                s = serial.Serial(port_name)
                s.close()
                return port_name
            except Exception:
                pass
    elif SYSTEM == "Darwin":
        # macOS ports
        matches = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/cu.wch*")
        if matches:
            return matches[0]
    else:
        # Linux standard ports
        matches = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        if matches:
            return matches[0]

    return None

# ---------------------------------------------------------------------------
# 2. Wi-Fi Interface Enumeration
# ---------------------------------------------------------------------------
def get_wifi_interface_names():
    """
    Returns a tuple (primary_iface, secondary_iface) of Wi-Fi interfaces.
    Linux: ('wlan0', 'wlan1')
    Windows: ('Wi-Fi', 'Wi-Fi 2')
    macOS: ('en0', 'en1')
    """
    if SYSTEM == "Windows":
        interfaces = []
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Name"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        interfaces.append(parts[1].strip())
        except Exception:
            pass
        p1 = interfaces[0] if len(interfaces) > 0 else "Wi-Fi"
        p2 = interfaces[1] if len(interfaces) > 1 else None
        return p1, p2

    elif SYSTEM == "Darwin":
        # macOS
        p1 = "en0"
        p2 = "en1" if os.path.exists("/sys/class/net/en1") else None
        return p1, p2

    else:
        # Linux
        p1 = "wlan0" if os.path.exists("/sys/class/net/wlan0") else None
        p2 = "wlan1" if os.path.exists("/sys/class/net/wlan1") else None
        if not p1 and HAS_PSUTIL:
            for iface in psutil.net_if_addrs().keys():
                if iface.startswith("wl"):
                    if not p1: p1 = iface
                    elif not p2: p2 = iface
        return p1 or "wlan0", p2

def is_secondary_wifi_detected():
    """Checks whether a secondary Wi-Fi dongle (wlan1 / Wi-Fi 2) is present."""
    _, p2 = get_wifi_interface_names()
    if not p2:
        return False
    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True, stderr=subprocess.DEVNULL)
            return p2 in out
        except Exception:
            return False
    elif SYSTEM == "Linux":
        return os.path.exists(f"/sys/class/net/{p2}")
    else:
        return False

# ---------------------------------------------------------------------------
# 3. Active Wi-Fi Connection Information
# ---------------------------------------------------------------------------
def get_active_wifi_status():
    """
    Returns (ssid, bssid, channel, signal_pct).
    Works seamlessly across Linux (nmcli), Windows (netsh), and macOS (airport).
    """
    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True, stderr=subprocess.DEVNULL)
            ssid = "Unknown"
            bssid = "None"
            channel = 0
            signal = 0
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("SSID") and not line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1: ssid = parts[1].strip()
                elif line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1: bssid = parts[1].strip()
                elif line.startswith("Channel"):
                    parts = line.split(":", 1)
                    if len(parts) > 1 and parts[1].strip().isdigit():
                        channel = int(parts[1].strip())
                elif line.startswith("Signal"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        val = parts[1].strip().replace("%", "")
                        if val.isdigit(): signal = int(val)
            if ssid and ssid != "Unknown":
                return ssid, bssid, channel, signal
        except Exception:
            pass
        return "Disconnected", "None", 0, 0

    elif SYSTEM == "Darwin":
        try:
            airport_bin = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport_bin):
                out = subprocess.check_output([airport_bin, "-I"], text=True, stderr=subprocess.DEVNULL)
                ssid = "Unknown"
                bssid = "None"
                channel = 0
                rssi = -100
                for line in out.splitlines():
                    line = line.strip()
                    if line.startswith("SSID:"): ssid = line.split(":", 1)[1].strip()
                    elif line.startswith("BSSID:"): bssid = line.split(":", 1)[1].strip()
                    elif line.startswith("channel:"):
                        ch_str = line.split(":", 1)[1].strip().split(",")[0]
                        if ch_str.isdigit(): channel = int(ch_str)
                    elif line.startswith("agrCtlRSSI:"):
                        r_str = line.split(":", 1)[1].strip()
                        if r_str.lstrip("-").isdigit(): rssi = int(r_str)
                signal = min(100, max(0, int((rssi + 100) * 2)))
                return ssid, bssid, channel, signal
        except Exception:
            pass
        return "Disconnected", "None", 0, 0

    else:
        # Linux (nmcli)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,bssid,chan,signal,ssid", "dev", "wifi"],
                text=True, stderr=subprocess.DEVNULL
            )
            for line in out.strip().split("\n"):
                if line.startswith("yes:"):
                    parts = line.split(":")
                    bssid = ":".join(parts[1:7]).replace("\\", "")
                    chan = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    signal = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    ssid = parts[9] if len(parts) > 9 else "Unknown"
                    return ssid, bssid, chan, signal
        except Exception:
            pass
        return "Disconnected", "None", 0, 0

# ---------------------------------------------------------------------------
# 4. Nearby Wi-Fi Scanning (Channels 1, 6, 11 AP counts & best candidate)
# ---------------------------------------------------------------------------
def scan_nearby_wifi_channels():
    """
    Scans surrounding 2.4GHz Wi-Fi networks.
    Returns: (ch1_count, ch6_count, ch11_count, total_aps, best_bssid, best_chan, best_sig)
    """
    ch1 = 0
    ch6 = 0
    ch11 = 0
    total = 0
    best_bssid = "None"
    best_chan = 1
    best_sig = 0

    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], text=True, stderr=subprocess.DEVNULL)
            cur_bssid = None
            cur_sig = 0
            cur_chan = 0
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        cur_bssid = parts[1].strip()
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
                        cur_chan = int(c_str) if c_str.isdigit() else 0
                        if cur_chan == 1: ch1 += 1
                        elif cur_chan == 6: ch6 += 1
                        elif cur_chan == 11: ch11 += 1
                        if cur_sig > best_sig and cur_bssid:
                            best_sig = cur_sig
                            best_chan = cur_chan
                            best_bssid = cur_bssid
        except Exception:
            pass

    elif SYSTEM == "Darwin":
        try:
            airport_bin = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport_bin):
                out = subprocess.check_output([airport_bin, "-s"], text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        total += 1
                        for p in parts:
                            if p.isdigit():
                                ch = int(p)
                                if ch == 1: ch1 += 1
                                elif ch == 6: ch6 += 1
                                elif ch == 11: ch11 += 1
                                break
        except Exception:
            pass

    else:
        # Linux (nmcli)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "CHAN,SSID,BSSID,SIGNAL", "dev", "wifi", "list"],
                text=True, stderr=subprocess.DEVNULL, timeout=4
            )
            for line in out.strip().split("\n"):
                parts = line.split(":")
                if len(parts) >= 4 and parts[0].isdigit():
                    total += 1
                    ch = int(parts[0])
                    bssid = ":".join(parts[2:8]).replace("\\", "") if len(parts) >= 8 else (parts[2] if len(parts) > 2 else "None")
                    sig_str = parts[-1]
                    sig = int(sig_str) if sig_str.isdigit() else 0
                    if ch == 1: ch1 += 1
                    elif ch == 6: ch6 += 1
                    elif ch == 11: ch11 += 1
                    if sig > best_sig:
                        best_sig = sig
                        best_chan = ch
                        best_bssid = bssid
        except Exception:
            pass

    return ch1, ch6, ch11, total, best_bssid, best_chan, best_sig

def find_best_candidate_for_ssid(target_ssid):
    """
    Finds the cleanest/strongest router candidate BSSID for a given target_ssid across OSes.
    Returns: (best_bssid, best_channel, best_signal) or (None, 0, 0)
    """
    if not target_ssid or target_ssid in ["Disconnected", "Scanning...", "Unknown"]:
        return None, 0, 0

    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], text=True, stderr=subprocess.DEVNULL)
            current_net_ssid = None
            cur_bssid = None
            cur_sig = 0
            candidates = []
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("SSID") and not line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_net_ssid = parts[1].strip()
                elif line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        cur_bssid = parts[1].strip()
                elif line.startswith("Signal"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        val = parts[1].strip().replace("%", "")
                        cur_sig = int(val) if val.isdigit() else 0
                elif line.startswith("Channel"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        chan = int(parts[1].strip()) if parts[1].strip().isdigit() else 0
                        if current_net_ssid == target_ssid and cur_bssid:
                            candidates.append({"bssid": cur_bssid, "chan": chan, "signal": cur_sig})
            if candidates:
                candidates.sort(key=lambda x: x["signal"], reverse=True)
                b = candidates[0]
                return b["bssid"], b["chan"], b["signal"]
        except Exception:
            pass
        return None, 0, 0

    elif SYSTEM == "Darwin":
        try:
            airport_bin = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport_bin):
                out = subprocess.check_output([airport_bin, "-s"], text=True, stderr=subprocess.DEVNULL)
                candidates = []
                for line in out.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        ssid = parts[0]
                        bssid = parts[1]
                        rssi = int(parts[2]) if parts[2].lstrip("-").isdigit() else -100
                        chan = int(parts[3]) if parts[3].isdigit() else 0
                        sig = min(100, max(0, int((rssi + 100) * 2)))
                        if ssid == target_ssid:
                            candidates.append({"bssid": bssid, "chan": chan, "signal": sig})
                if candidates:
                    candidates.sort(key=lambda x: x["signal"], reverse=True)
                    b = candidates[0]
                    return b["bssid"], b["chan"], b["signal"]
        except Exception:
            pass
        return None, 0, 0

    else:
        # Linux (nmcli)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "SSID,BSSID,CHAN,SIGNAL", "dev", "wifi", "list"],
                text=True, stderr=subprocess.DEVNULL
            )
            candidates = []
            for line in out.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 8:
                    ssid = parts[0]
                    bssid = ":".join(parts[1:7]).replace("\\", "")
                    chan = int(parts[7]) if parts[7].isdigit() else 0
                    signal = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    if ssid == target_ssid:
                        candidates.append({"bssid": bssid, "chan": chan, "signal": signal})
            if candidates:
                candidates.sort(key=lambda x: x["signal"], reverse=True)
                b = candidates[0]
                return b["bssid"], b["chan"], b["signal"]
        except Exception:
            pass
        return None, 0, 0

# ---------------------------------------------------------------------------
# 5. Fast AP Roaming / Router Switching (Cross-Platform)
# ---------------------------------------------------------------------------
def switch_wifi_bssid(ssid, target_bssid):
    """
    Switches to target router BSSID.
    Linux: Locks BSSID via nmcli.
    Windows: Reconnects to profile via netsh.
    macOS: Reconnects airport network.
    """
    if not ssid or ssid in ["Disconnected", "Scanning..."] or not target_bssid:
        return False, "No valid SSID or Target AP selected"

    if SYSTEM == "Windows":
        try:
            # On Windows, trigger reconnect to the network profile
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            time.sleep(1.5)
            return True, f"Reconnected to {ssid} on optimal router"
        except Exception as e:
            return False, f"Windows netsh switch error: {e}"

    elif SYSTEM == "Darwin":
        try:
            p1, _ = get_wifi_interface_names()
            subprocess.run(["networksetup", "-setairportnetwork", p1, ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            time.sleep(1.5)
            return True, f"Reconnected on {ssid}"
        except Exception as e:
            return False, f"macOS airport switch error: {e}"

    else:
        # Linux (nmcli with rollback protection)
        try:
            subprocess.check_call(
                ["nmcli", "connection", "modify", ssid, "802-11-wireless.bssid", target_bssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
            )
            subprocess.check_call(
                ["nmcli", "connection", "up", ssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8
            )
            time.sleep(1.5)
            return True, f"Locked to router {target_bssid}"
        except Exception:
            # Revert to automatic roam profile
            try:
                subprocess.call(["nmcli", "connection", "modify", ssid, "802-11-wireless.bssid", ""], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call(["nmcli", "connection", "up", ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            return False, f"Could not lock to {target_bssid}. Connection safely restored."

# ---------------------------------------------------------------------------
# 6. Real-Time Network Bandwidth I/O Tracker (Cross-Platform)
# ---------------------------------------------------------------------------
class NetworkBandwidthTracker:
    """Tracks byte deltas per interface using psutil or Linux sysfs."""
    def __init__(self):
        self.last_p1 = 0
        self.last_p2 = 0
        self.p1_name, self.p2_name = get_wifi_interface_names()

    def sample_rx_bytes(self):
        """Returns (rx_bytes_p1, rx_bytes_p2)."""
        rx1 = 0
        rx2 = 0

        # Primary method: psutil (Universal across Windows, macOS, Linux)
        if HAS_PSUTIL:
            try:
                counters = psutil.net_io_counters(pernic=True)
                # Refresh interface names if needed
                self.p1_name, self.p2_name = get_wifi_interface_names()
                if self.p1_name in counters:
                    rx1 = counters[self.p1_name].bytes_recv
                if self.p2_name and self.p2_name in counters:
                    rx2 = counters[self.p2_name].bytes_recv
                return rx1, rx2
            except Exception:
                pass

        # Fallback method for Linux sysfs
        if SYSTEM == "Linux":
            try:
                p1_path = f"/sys/class/net/{self.p1_name}/statistics/rx_bytes"
                if os.path.exists(p1_path):
                    with open(p1_path) as f: rx1 = int(f.read().strip())
                if self.p2_name:
                    p2_path = f"/sys/class/net/{self.p2_name}/statistics/rx_bytes"
                    if os.path.exists(p2_path):
                        with open(p2_path) as f: rx2 = int(f.read().strip())
            except Exception:
                pass

        return rx1, rx2

    def get_delta_mbps(self, duration=1.0):
        """Measures throughput in Mbps over interval."""
        cur1, cur2 = self.sample_rx_bytes()
        d1 = max(0, cur1 - self.last_p1) if self.last_p1 > 0 else 0
        d2 = max(0, cur2 - self.last_p2) if self.last_p2 > 0 else 0
        self.last_p1 = cur1
        self.last_p2 = cur2
        mbps1 = (d1 * 8) / (duration * 1_000_000.0)
        mbps2 = (d2 * 8) / (duration * 1_000_000.0)
        return round(mbps1, 2), round(mbps2, 2)
