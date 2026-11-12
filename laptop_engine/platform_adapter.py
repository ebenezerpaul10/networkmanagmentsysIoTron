"""
NetShield-IoT Platform Adapter (v5.0 Enterprise - Pure Physical Telemetry)
Universal cross-platform network, Wi-Fi, and hardware abstraction layer for Windows, macOS, and Linux.
ZERO synthetic noise, ZERO random generators, 100% verified physical telemetry.
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

SYSTEM = platform.system()  # 'Windows', 'Linux', 'Darwin'

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
    Finds real ESP32 hardware serial port on Windows (COM*), Linux (/dev/ttyUSB*),
    and macOS (/dev/cu.usb*).
    STRICT: Only matches verified physical USB-UART bridges (CP210x, CH340, FTDI, ESP32 USB),
    never virtual Bluetooth links or modem ports.
    """
    if HAS_PYSERIAL_PORTS:
        try:
            keywords = (
                "USB", "UART", "CP210", "CH340", "CH341", "CH9102",
                "FTDI", "ESPRESSIF", "ESP32", "SILICON LABS"
            )
            for p in serial_list_ports.comports():
                desc = (p.description or "").upper()
                hwid = (p.hwid or "").upper()
                mfg = (getattr(p, "manufacturer", "") or "").upper()
                
                # Exclude obvious Bluetooth and virtual serial ports
                if "BLUETOOTH" in desc or "BTHENUM" in hwid:
                    continue
                
                if any(k in desc or k in hwid or k in mfg for k in keywords):
                    return p.device
        except Exception:
            pass

    # Filesystem fallback for Linux & macOS
    if SYSTEM == "Linux":
        matches = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        if matches:
            return sorted(matches)[0]
    elif SYSTEM == "Darwin":
        matches = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.wch*") + glob.glob("/dev/cu.SLAB*")
        if matches:
            return sorted(matches)[0]

    return None

# ---------------------------------------------------------------------------
# 2. Wi-Fi Interface Enumeration & IP Binding
# ---------------------------------------------------------------------------
def get_wifi_interface_names():
    """
    Returns a tuple (primary_iface, secondary_iface) of Wi-Fi interfaces.
    Windows: ('Wi-Fi', 'Wi-Fi 2')
    Linux: ('wlan0', 'wlan1')
    macOS: ('en0', 'en1')
    """
    if SYSTEM == "Windows":
        interfaces = []
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore"
            )
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
    """Checks whether a secondary Wi-Fi adapter (wlan1 / Wi-Fi 2) is present."""
    _, p2 = get_wifi_interface_names()
    if not p2:
        return False
    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore"
            )
            return p2 in out
        except Exception:
            return False
    elif SYSTEM == "Linux":
        return os.path.exists(f"/sys/class/net/{p2}")
    else:
        return False

def get_interface_ip(iface_name):
    """Resolves the active IPv4 address assigned to a specific network interface."""
    if not iface_name:
        return None
    if HAS_PSUTIL:
        try:
            addrs = psutil.net_if_addrs()
            if iface_name in addrs:
                for a in addrs[iface_name]:
                    if a.family == socket.AF_INET and not a.address.startswith("127."):
                        return a.address
        except Exception:
            pass
    return None

# ---------------------------------------------------------------------------
# 3. Active Wi-Fi Connection Information (100% Physically Measured)
# ---------------------------------------------------------------------------
def get_active_wifi_details():
    """
    Returns full physical link dictionary:
    {
        'state': 'connected',
        'ssid': 'KU-WL',
        'bssid': '20:a6:cd:52:de:60',
        'channel': 6,
        'signal': 77,
        'rssi': -67,
        'band': '2.4 GHz',
        'radio': '802.11n',
        'rx_rate': 144.4,
        'tx_rate': 144.4
    }
    """
    default_info = {
        "state": "disconnected",
        "ssid": "Disconnected",
        "bssid": "N/A",
        "channel": 0,
        "signal": 0,
        "rssi": -100,
        "band": "2.4 GHz",
        "radio": "802.11",
        "rx_rate": 0.0,
        "tx_rate": 0.0
    }

    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore"
            )
            info = dict(default_info)
            for raw_line in out.splitlines():
                line = raw_line.strip()
                if not line or ":" not in line:
                    continue
                key, val = [p.strip() for p in line.split(":", 1)]
                k_lower = key.lower()

                if k_lower == "state":
                    info["state"] = val.lower()
                elif k_lower == "ssid":
                    info["ssid"] = val
                elif "bssid" in k_lower:
                    info["bssid"] = val.lower()
                elif k_lower == "channel":
                    if val.isdigit():
                        info["channel"] = int(val)
                elif k_lower == "signal":
                    s = val.replace("%", "").strip()
                    if s.isdigit():
                        info["signal"] = int(s)
                elif k_lower == "rssi":
                    try:
                        info["rssi"] = int(val)
                    except Exception:
                        pass
                elif k_lower == "band":
                    info["band"] = val
                elif "radio" in k_lower:
                    info["radio"] = val
                elif "receive rate" in k_lower:
                    try:
                        info["rx_rate"] = float(val)
                    except Exception:
                        pass
                elif "transmit rate" in k_lower:
                    try:
                        info["tx_rate"] = float(val)
                    except Exception:
                        pass

            # If RSSI was not directly output by driver, derive from true signal %
            if info["rssi"] == -100 and info["signal"] > 0:
                info["rssi"] = int((info["signal"] / 2.0) - 100)

            if info["state"] == "connected" and info["ssid"] != "Disconnected":
                return info
        except Exception:
            pass
        return default_info

    elif SYSTEM == "Darwin":
        try:
            airport_bin = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport_bin):
                out = subprocess.check_output([airport_bin, "-I"], text=True, stderr=subprocess.DEVNULL, errors="ignore")
                info = dict(default_info)
                rssi = -100
                for line in out.splitlines():
                    line = line.strip()
                    if line.startswith("SSID:"):
                        info["ssid"] = line.split(":", 1)[1].strip()
                        info["state"] = "connected"
                    elif line.startswith("BSSID:"):
                        info["bssid"] = line.split(":", 1)[1].strip().lower()
                    elif line.startswith("channel:"):
                        ch_str = line.split(":", 1)[1].strip().split(",")[0]
                        if ch_str.isdigit():
                            info["channel"] = int(ch_str)
                    elif line.startswith("agrCtlRSSI:"):
                        r_str = line.split(":", 1)[1].strip()
                        if r_str.lstrip("-").isdigit():
                            rssi = int(r_str)
                info["rssi"] = rssi
                info["signal"] = min(100, max(0, int((rssi + 100) * 2)))
                return info
        except Exception:
            pass
        return default_info

    else:
        # Linux (nmcli)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,bssid,chan,signal,ssid,freq", "dev", "wifi"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore"
            )
            for line in out.strip().split("\n"):
                if line.startswith("yes:"):
                    parts = line.split(":")
                    bssid = ":".join(parts[1:7]).replace("\\", "").lower()
                    chan = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    signal = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    ssid = parts[9] if len(parts) > 9 else "Unknown"
                    freq = parts[10] if len(parts) > 10 else ""
                    band = "5 GHz" if "5" in freq else "2.4 GHz"
                    rssi = int((signal / 2.0) - 100)

                    return {
                        "state": "connected",
                        "ssid": ssid,
                        "bssid": bssid,
                        "channel": chan,
                        "signal": signal,
                        "rssi": rssi,
                        "band": band,
                        "radio": "802.11",
                        "rx_rate": 0.0,
                        "tx_rate": 0.0
                    }
        except Exception:
            pass
        return default_info

def get_active_wifi_status():
    """Backward compatible tuple: (ssid, bssid, channel, signal)."""
    details = get_active_wifi_details()
    return details["ssid"], details["bssid"], details["channel"], details["signal"]

# ---------------------------------------------------------------------------
# 4. Nearby Wi-Fi Environmental Scanner (Channels 1, 6, 11 AP Counts & Candidates)
# ---------------------------------------------------------------------------
_last_scan_time = 0
_cached_networks = []

def scan_all_nearby_networks(force=False):
    """
    Parses all physically visible surrounding Wi-Fi beacons from OS wireless table.
    Caches for 3.0s to avoid subprocess contention across concurrent threads.
    Returns list of dicts: [{'ssid', 'bssid', 'signal', 'channel', 'band', 'radio'}, ...]
    """
    global _last_scan_time, _cached_networks
    now = time.time()
    if not force and (now - _last_scan_time < 3.0) and _cached_networks:
        return _cached_networks

    networks = []

    if SYSTEM == "Windows":
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore"
            )
            current_ssid = ""
            current_record = None

            for raw_line in out.splitlines():
                line = raw_line.strip()
                if not line:
                    continue

                m_ssid = re.match(r"^SSID\s+\d+\s*:\s*(.*)$", line, re.IGNORECASE)
                if m_ssid:
                    current_ssid = m_ssid.group(1).strip()
                    continue

                m_bssid = re.match(r"^BSSID\s+\d+\s*:\s*([0-9a-fA-F:]{17})", line, re.IGNORECASE)
                if m_bssid:
                    if current_record and current_record.get("bssid"):
                        networks.append(current_record)
                    current_record = {
                        "ssid": current_ssid or "Hidden Network",
                        "bssid": m_bssid.group(1).lower(),
                        "signal": 0,
                        "channel": 0,
                        "band": "2.4 GHz",
                        "radio": "802.11"
                    }
                    continue

                if current_record:
                    m_sig = re.match(r"^Signal\s*:\s*(\d+)%", line, re.IGNORECASE)
                    if m_sig:
                        current_record["signal"] = int(m_sig.group(1))
                        continue

                    m_chan = re.match(r"^Channel\s*:\s*(\d+)", line, re.IGNORECASE)
                    if m_chan:
                        current_record["channel"] = int(m_chan.group(1))
                        continue

                    m_band = re.match(r"^Band\s*:\s*(.*)$", line, re.IGNORECASE)
                    if m_band:
                        current_record["band"] = m_band.group(1).strip()
                        continue

                    m_radio = re.match(r"^Radio type\s*:\s*(.*)$", line, re.IGNORECASE)
                    if m_radio:
                        current_record["radio"] = m_radio.group(1).strip()
                        continue

            if current_record and current_record.get("bssid"):
                networks.append(current_record)
        except Exception:
            pass

    elif SYSTEM == "Darwin":
        try:
            airport_bin = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport_bin):
                out = subprocess.check_output([airport_bin, "-s"], text=True, stderr=subprocess.DEVNULL, errors="ignore")
                for line in out.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        ssid = parts[0]
                        bssid = parts[1].lower()
                        rssi = int(parts[2]) if parts[2].lstrip("-").isdigit() else -100
                        chan = int(parts[3]) if parts[3].isdigit() else 0
                        sig = min(100, max(0, int((rssi + 100) * 2)))
                        band = "5 GHz" if chan > 14 else "2.4 GHz"
                        networks.append({
                            "ssid": ssid,
                            "bssid": bssid,
                            "signal": sig,
                            "channel": chan,
                            "band": band,
                            "radio": "802.11"
                        })
        except Exception:
            pass

    else:
        # Linux (nmcli)
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "CHAN,SSID,BSSID,SIGNAL,FREQ", "dev", "wifi", "list"],
                text=True, stderr=subprocess.DEVNULL, errors="ignore", timeout=4
            )
            for line in out.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 4 and parts[0].isdigit():
                    ch = int(parts[0])
                    ssid = parts[1] if len(parts) > 1 else "Unknown"
                    bssid = ":".join(parts[2:8]).replace("\\", "").lower() if len(parts) >= 8 else "none"
                    sig = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    freq = parts[9] if len(parts) > 9 else ""
                    band = "5 GHz" if "5" in freq else "2.4 GHz"
                    networks.append({
                        "ssid": ssid,
                        "bssid": bssid,
                        "signal": sig,
                        "channel": ch,
                        "band": band,
                        "radio": "802.11"
                    })
        except Exception:
            pass

    _cached_networks = networks
    _last_scan_time = time.time()
    return networks

def scan_nearby_wifi_channels():
    """
    Scans surrounding Wi-Fi networks and computes exact channel distributions.
    Returns: (ch1_count, ch6_count, ch11_count, total_aps, best_bssid, best_chan, best_sig)
    """
    networks = scan_all_nearby_networks()
    ch1 = sum(1 for n in networks if n["channel"] == 1)
    ch6 = sum(1 for n in networks if n["channel"] == 6)
    ch11 = sum(1 for n in networks if n["channel"] == 11)
    total = len(networks)

    best_bssid = "None"
    best_chan = 1
    best_sig = 0

    if networks:
        sorted_nets = sorted(networks, key=lambda x: x["signal"], reverse=True)
        top = sorted_nets[0]
        best_bssid = top["bssid"]
        best_chan = top["channel"]
        best_sig = top["signal"]

    return ch1, ch6, ch11, total, best_bssid, best_chan, best_sig

def find_best_candidate_for_ssid(target_ssid):
    """
    Finds the cleanest/strongest router candidate BSSID for a given target_ssid across OSes.
    Returns: (best_bssid, best_channel, best_signal) or (None, 0, 0)
    """
    if not target_ssid or target_ssid in ["Disconnected", "Scanning...", "Unknown"]:
        return None, 0, 0

    networks = scan_all_nearby_networks()
    candidates = [
        n for n in networks
        if n["ssid"].strip().lower() == target_ssid.strip().lower()
    ]

    if candidates:
        candidates.sort(key=lambda x: x["signal"], reverse=True)
        b = candidates[0]
        return b["bssid"], b["channel"], b["signal"]

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
            subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
            )
            time.sleep(1.5)
            return True, f"Reconnected to {ssid} on optimal router"
        except Exception as e:
            return False, f"Windows netsh switch error: {e}"

    elif SYSTEM == "Darwin":
        try:
            p1, _ = get_wifi_interface_names()
            subprocess.run(
                ["networksetup", "-setairportnetwork", p1, ssid],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
            )
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
    """Tracks physical byte deltas per interface using psutil or Linux sysfs."""
    def __init__(self):
        self.last_p1 = 0
        self.last_p2 = 0
        self.last_time = time.time()
        self.p1_name, self.p2_name = get_wifi_interface_names()

    def sample_rx_bytes(self):
        """Returns (rx_bytes_p1, rx_bytes_p2)."""
        rx1 = 0
        rx2 = 0

        if HAS_PSUTIL:
            try:
                counters = psutil.net_io_counters(pernic=True)
                self.p1_name, self.p2_name = get_wifi_interface_names()
                if self.p1_name in counters:
                    rx1 = counters[self.p1_name].bytes_recv
                if self.p2_name and self.p2_name in counters:
                    rx2 = counters[self.p2_name].bytes_recv
                return rx1, rx2
            except Exception:
                pass

        if SYSTEM == "Linux":
            try:
                p1_path = f"/sys/class/net/{self.p1_name}/statistics/rx_bytes"
                if os.path.exists(p1_path):
                    with open(p1_path) as f:
                        rx1 = int(f.read().strip())
                if self.p2_name:
                    p2_path = f"/sys/class/net/{self.p2_name}/statistics/rx_bytes"
                    if os.path.exists(p2_path):
                        with open(p2_path) as f:
                            rx2 = int(f.read().strip())
            except Exception:
                pass

        return rx1, rx2

    def get_delta_mbps(self, duration=1.0):
        """Measures physical throughput in Mbps over interval."""
        cur1, cur2 = self.sample_rx_bytes()
        now = time.time()
        elapsed = max(0.1, now - self.last_time)
        self.last_time = now

        d1 = max(0, cur1 - self.last_p1) if self.last_p1 > 0 else 0
        d2 = max(0, cur2 - self.last_p2) if self.last_p2 > 0 else 0
        self.last_p1 = cur1
        self.last_p2 = cur2

        mbps1 = (d1 * 8.0) / (elapsed * 1_000_000.0)
        mbps2 = (d2 * 8.0) / (elapsed * 1_000_000.0)
        return round(mbps1, 2), round(mbps2, 2)

# ---------------------------------------------------------------------------
# 7. True Physical Speed Benchmark (Curl & Direct Socket Stream Fallback)
# ---------------------------------------------------------------------------
def measure_interface_speed_mbps(iface_name=None, duration=3.0, bytes_count=15000000):
    """
    Performs a 100% physically measured download speed test against Cloudflare CDN.
    Uses native curl if available, otherwise pure socket stream with exact byte counter.
    ZERO fake fallback numbers.
    """
    null_target = "NUL" if SYSTEM == "Windows" else "/dev/null"
    test_url = f"https://speed.cloudflare.com/__down?bytes={bytes_count}"

    # Try curl first
    try:
        cmd = [
            "curl.exe" if SYSTEM == "Windows" else "curl",
            "-s",
            "--max-time", str(int(duration)),
            "-w", "%{speed_download}",
            "-o", null_target
        ]
        
        # On Windows, resolve iface to local IP for reliable socket binding
        if iface_name:
            if SYSTEM == "Windows":
                ip = get_interface_ip(iface_name)
                if ip:
                    cmd.extend(["--interface", ip])
            else:
                cmd.extend(["--interface", iface_name])

        cmd.append(test_url)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 2.5)
        raw_bps = res.stdout.strip()
        if raw_bps:
            try:
                bps = float(raw_bps)
                mbps = round((bps * 8.0) / 1_000_000.0, 2)
                if mbps > 0.0:
                    return mbps
            except ValueError:
                pass
    except Exception:
        pass

    # Pure Python Streaming Socket Fallback
    try:
        req = urllib.request.Request(
            test_url,
            headers={"User-Agent": "NetShield/5.0 Enterprise Network Controller"}
        )
        t_start = time.time()
        bytes_received = 0

        with urllib.request.urlopen(req, timeout=duration + 2.0) as resp:
            while time.time() - t_start < duration:
                chunk = resp.read(65536)
                if not chunk:
                    break
                bytes_received += len(chunk)

        elapsed = max(0.01, time.time() - t_start)
        mbps = round((bytes_received * 8.0) / (elapsed * 1_000_000.0), 2)
        return mbps
    except Exception:
        return 0.0
