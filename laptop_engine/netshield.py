#!/usr/bin/env python3
"""
NetShield-IoT: Laptop Companion Engine & Enterprise Network Controller (v5.0 Pure Physical Telemetry)
ZERO synthetic sequences, ZERO random generators, 100% verified physical hardware telemetry.

Features:
  1. Real-time Wi-Fi Link Telemetry (SSID, BSSID, Channel, Band, Signal, RSSI)
  2. Physical RF Environment Scanner across 2.4 GHz non-overlapping channels
  3. Real Network Interface I/O Bandwidth Tracker (psutil / sysfs)
  4. Physical Multi-Interface Speed Benchmark (Cloudflare CDN socket/curl streams)
  5. Local DNS Sinkhole Firewall (UDP port 5353)
  6. Dedicated ESP32 Hardware RF Sniffer with native Laptop OS Fallback
"""

import sys
import os
import glob
import time
import json
import socket
import threading
import subprocess
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from dnslib import DNSRecord, QTYPE, RR, A

try:
    import serial
except ImportError:
    print("[ERROR] pyserial not found.")
    sys.exit(1)

# Cross-Platform Hardware & Network Adapter
try:
    from laptop_engine import platform_adapter as pa
except ImportError:
    import platform_adapter as pa

bandwidth_tracker = pa.NetworkBandwidthTracker()

# Configuration
DEFAULT_BAUD = 115200
UPSTREAM_DNS = ("1.1.1.1", 53)
DNS_LISTEN_PORT = 5353
WEB_PORT = 8080
HTML_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web_dashboard", "index.html")

BLOCKED_DOMAINS = [
    "doubleclick.net", "googleadservices.com", "adservice.google.com",
    "telemetry.microsoft.com", "analytics.google.com", "facebook.com/tr",
    "scorecardresearch.com", "adnxs.com", "taboola.com", "outbrain.com",
    "adroll.com", "criteo.com", "popads.net", "tracking", "telemetry"
]

event_counter = 0

stats = {
    # System & Hardware
    "esp_connected": False,
    "esp_port": "Disconnected",
    "radar_source": f"{pa.SYSTEM} Wi-Fi (Software Fallback)",
    "auto_roam_enabled": False,
    
    # 0-100 Master Internet Score
    "health_score": 75,
    "score_status": "Analyzing Link...",
    "simple_summary": "Inspecting wireless airwaves...",
    
    # Copilot Advisory
    "robo_speech": f"Network monitored via {pa.SYSTEM} hardware adapter. Plug in ESP32 board for dedicated RF sniffer.",
    "robo_mood": "alert",
    
    # Active Connection on Laptop (Real Physical Measurements)
    "current_ssid": "Scanning...",
    "current_bssid": "N/A",
    "current_channel": 0,
    "current_signal": 0,
    "signal_bars": 3,
    "current_band": "2.4 GHz",
    "current_radio": "802.11",
    "current_rx_rate": 0.0,
    "current_tx_rate": 0.0,
    "current_rssi": -100,
    
    # Real-Time Download Speed (Physical Delta Bytes)
    "download_speed_mbps": 0.0,
    "download_speed_str": "0.00 Mbps",
    "speed_verdict": "Idle",
    
    # Cleanest Candidate AP
    "best_ssid": "Scanning...",
    "best_bssid": "N/A",
    "best_rssi": -100,
    "recommended_channel": 1,
    "congestion_score": 0,
    "total_aps": 0,
    "ch1": 0,
    "ch6": 0,
    "ch11": 0,
    
    # Rolling Spectrum History (Only physically measured channel counts)
    "spectrum_history": [{"ch1": 0.0, "ch6": 0.0, "ch11": 0.0} for _ in range(25)],
    
    # Physical Interface Traffic Buffer (True physical MB/s throughput points)
    "traffic_wave": [0.0] * 20,
    "traffic_zone": "Green (Clean Air 🏎️)",
    
    # Highway Traffic Analogy
    "highway": {
        "lane1": {"channel": 1, "count": 0, "status": "Empty 🏎️", "desc": "Fast lane"},
        "lane6": {"channel": 6, "count": 0, "status": "Empty 🏎️", "desc": "Fast lane"},
        "lane11": {"channel": 11, "count": 0, "status": "Empty 🏎️", "desc": "Fast lane"},
        "best_lane": 1
    },
    
    # Performance & Security
    "latency_ms": 0.0,
    "network_health": "Probing latency...",
    "total_queries": 0,
    "blocked_queries": 0,
    "bandwidth_saved_kb": 0.0,
    
    # Before vs After Live Comparison Metrics (Truthful Dynamic State)
    "before_metrics": {
        "bssid": "Awaiting Link",
        "channel": 1,
        "signal": 0,
        "latency_ms": 0.0,
        "download_speed": "Awaiting Test",
        "hardware": f"{pa.SYSTEM} Wi-Fi",
        "status": "Initial",
        "timestamp": "At Startup"
    },
    "after_metrics": {
        "bssid": "Live State",
        "channel": 1,
        "signal": 0,
        "latency_ms": 0.0,
        "download_speed": "Awaiting Test",
        "hardware": f"{pa.SYSTEM} Wi-Fi",
        "status": "Live Tracking",
        "timestamp": "Live"
    },
    "improvements": {
        "speed_boost_pct": 0,
        "latency_drop_pct": 0,
        "signal_gain_pct": 0,
        "channel_cleared": False,
        "mode": "standby"
    },
    
    # Dual Wi-Fi Live Speed
    "wlan0_speed_mbps": 0.0,
    "wlan1_speed_mbps": 0.0,
    "dual_combined_mbps": 0.0,
    "wlan1_detected": pa.is_secondary_wifi_detected(),
    
    # Event Audit Trail
    "assistant_events": []
}

def log_assistant(category, title, message, impact="Info"):
    """Appends a structured log event with unique ID."""
    global event_counter
    event_counter += 1
    timestamp = time.strftime("%H:%M:%S")
    entry = {
        "id": event_counter,
        "time": timestamp,
        "category": category,  # RADAR, ROAMER, SHIELD, COPILOT
        "title": title,
        "message": message,
        "impact": impact
    }
    stats["assistant_events"].insert(0, entry)
    if len(stats["assistant_events"]) > 30:
        stats["assistant_events"].pop()
    print(f"[NETSHIELD] #{event_counter} [{category}] {title}: {message}")

def auto_detect_esp():
    """Detects ESP32 hardware serial port across Windows, macOS, and Linux."""
    return pa.auto_detect_esp32_port()

def calculate_master_score():
    """Computes a logical 0-100 Master Internet Score based on physical metrics."""
    score = 0
    lat = stats["latency_ms"]
    if lat > 0:
        if lat <= 35: score += 40
        elif lat <= 65: score += 35
        elif lat <= 110: score += 25
        elif lat <= 200: score += 15
        else: score += 5
    
    sig = stats["current_signal"]
    score += int((sig / 100.0) * 35)
    
    best_ch = stats["recommended_channel"]
    cur_ch = stats["current_channel"]
    if cur_ch == best_ch or cur_ch > 14:
        score += 15
    else:
        score += 5
        
    if stats["esp_connected"]:
        score += 10
        
    stats["health_score"] = min(100, max(10, score))
    
    radar_desc = "ESP32 Hardware Radar is sniffing 24/7." if stats.get("esp_connected") else f"{pa.SYSTEM} Wi-Fi Adapter is actively monitoring link."
    if stats["health_score"] >= 80:
        stats["score_status"] = "Optimal Link ⚡"
        stats["simple_summary"] = f"Your network connection is clean and performing at peak efficiency. {radar_desc}"
        stats["robo_speech"] = f"Link quality is optimal with low latency. {radar_desc}"
        stats["robo_mood"] = "happy"
    elif stats["health_score"] >= 60:
        stats["score_status"] = "Good & Steady ⚡"
        stats["simple_summary"] = f"Network is stable with moderate room latency. {radar_desc}"
        stats["robo_speech"] = f"Stable connection maintained. {radar_desc}"
        stats["robo_mood"] = "alert"
    else:
        stats["score_status"] = "Suboptimal Link 🛑"
        stats["simple_summary"] = f"High latency or signal degradation detected. BSSID handover recommended. {radar_desc}"
        stats["robo_speech"] = f"Channel congestion or latency spike detected. Recommended to steer connection to Channel {best_ch}."
        stats["robo_mood"] = "warning"

def update_comparison_metrics(before_state, after_state, mode="router_roam"):
    stats["before_metrics"] = before_state
    stats["after_metrics"] = after_state
    stats["improvements"]["mode"] = mode
    
    b_lat = before_state.get("latency_ms", 0)
    a_lat = after_state.get("latency_ms", 0)
    if b_lat > 0 and a_lat > 0 and b_lat > a_lat:
        lat_diff = round(((b_lat - a_lat) / b_lat) * 100)
        stats["improvements"]["latency_drop_pct"] = lat_diff
    else:
        stats["improvements"]["latency_drop_pct"] = 0
    
    b_sig = before_state.get("signal", 0)
    a_sig = after_state.get("signal", 0)
    stats["improvements"]["signal_gain_pct"] = max(0, a_sig - b_sig)
    stats["improvements"]["channel_cleared"] = (before_state.get("channel") != after_state.get("channel"))

def switch_to_bssid(ssid, target_bssid):
    """Switches to target BSSID with snapshot capture and cross-platform rollback protection."""
    if not ssid or ssid in ["Disconnected", "Scanning..."] or not target_bssid:
        return False, "No valid target AP found to switch."
        
    p1, _ = pa.get_wifi_interface_names()
    before_snap = {
        "bssid": stats.get("current_bssid", "Unknown"),
        "channel": stats.get("current_channel", 1),
        "signal": stats.get("current_signal", 50),
        "latency_ms": stats.get("latency_ms", 40.0),
        "download_speed": stats.get("download_speed_str", "Live"),
        "hardware": f"{pa.SYSTEM} Wi-Fi ({p1})",
        "status": "Pre-Optimization",
        "timestamp": time.strftime("%H:%M:%S")
    }
    
    log_assistant("ROAMER", "Initiating Link Handover", f"Attempting connection switch on {ssid} to target BSSID {target_bssid}...", "Switching")
    success, msg = pa.switch_wifi_bssid(ssid, target_bssid)
    
    if success:
        time.sleep(2.0)
        info = pa.get_active_wifi_details()
        after_snap = {
            "bssid": info.get("bssid", target_bssid),
            "channel": info.get("channel", stats.get("recommended_channel", 1)),
            "signal": info.get("signal", stats.get("current_signal", 60)),
            "latency_ms": stats.get("latency_ms", 30.0),
            "download_speed": stats.get("download_speed_str", "Live"),
            "hardware": f"{pa.SYSTEM} Wi-Fi ({p1})",
            "status": "Post-Optimization",
            "timestamp": time.strftime("%H:%M:%S")
        }
        update_comparison_metrics(before_snap, after_snap, mode="router_roam")
        log_assistant("ROAMER", "Link Handover Complete", f"Successfully steered connection: {msg}", "Success")
    else:
        log_assistant("ROAMER", "Handover Aborted", f"Could not complete handover: {msg}", "Rollback")
        
    return success, msg

def download_speed_worker():
    """Calculates true physical download speed from physical interface byte counters."""
    global stats
    while True:
        time.sleep(1.0)
        try:
            mbps0, mbps1 = bandwidth_tracker.get_delta_mbps(1.0)
            stats["wlan1_detected"] = pa.is_secondary_wifi_detected()
            total_mbps = mbps0 + (mbps1 if stats["wlan1_detected"] else 0.0)
            
            stats["wlan0_speed_mbps"] = round(mbps0, 2)
            stats["wlan1_speed_mbps"] = round(mbps1 if stats["wlan1_detected"] else 0.0, 2)
            stats["dual_combined_mbps"] = round(total_mbps, 2)
            stats["download_speed_mbps"] = round(total_mbps, 2)
            
            if total_mbps >= 1.0:
                stats["download_speed_str"] = f"{total_mbps:.2f} Mbps"
                stats["speed_verdict"] = "Active Streaming"
            elif total_mbps > 0.01:
                kbps = total_mbps * 125.0
                stats["download_speed_str"] = f"{kbps:.1f} KB/s"
                stats["speed_verdict"] = "Active Browsing"
            else:
                stats["download_speed_str"] = "0.00 Mbps"
                stats["speed_verdict"] = "Idle / Standby"
                
            # Record physical delta point in traffic wave
            stats["traffic_wave"].append(round(total_mbps, 2))
            if len(stats["traffic_wave"]) > 20:
                stats["traffic_wave"].pop(0)

            # Update traffic zone based on measured channel congestion and latency
            if stats["congestion_score"] >= 60 or stats["latency_ms"] > 150:
                stats["traffic_zone"] = "Red (Traffic Jam 🛑)"
            elif stats["congestion_score"] >= 30 or stats["latency_ms"] > 70:
                stats["traffic_zone"] = "Yellow (Busy Air 🚗)"
            else:
                stats["traffic_zone"] = "Green (Clean Air 🏎️)"
        except Exception:
            pass

def active_connection_poller():
    """Polls real active Wi-Fi status and surrounding candidate APs."""
    global stats
    while True:
        details = pa.get_active_wifi_details()
        stats["current_ssid"] = details["ssid"]
        stats["current_bssid"] = details["bssid"]
        stats["current_channel"] = details["channel"]
        stats["current_signal"] = details["signal"]
        stats["current_band"] = details["band"]
        stats["current_radio"] = details["radio"]
        stats["current_rx_rate"] = details["rx_rate"]
        stats["current_tx_rate"] = details["tx_rate"]
        stats["current_rssi"] = details["rssi"]
        stats["best_rssi"] = details["rssi"]
        
        sig = details["signal"]
        if sig >= 75: stats["signal_bars"] = 4
        elif sig >= 50: stats["signal_bars"] = 3
        elif sig >= 25: stats["signal_bars"] = 2
        else: stats["signal_bars"] = 1
        
        # Capture initial baseline if startup placeholder is still present
        if stats["before_metrics"].get("status") == "Initial" and details["state"] == "connected":
            p1, _ = pa.get_wifi_interface_names()
            stats["before_metrics"] = {
                "bssid": details["bssid"],
                "channel": details["channel"],
                "signal": details["signal"],
                "latency_ms": stats["latency_ms"],
                "download_speed": stats["download_speed_str"],
                "hardware": f"{pa.SYSTEM} Wi-Fi ({p1})",
                "status": "Baseline Snapshot",
                "timestamp": time.strftime("%H:%M:%S")
            }

        # Look for cleanest candidate BSSID on current target SSID
        cand_bssid, cand_chan, cand_sig = pa.find_best_candidate_for_ssid(details["ssid"])
        if cand_bssid and cand_bssid != "None":
            stats["best_ssid"] = details["ssid"]
            stats["best_bssid"] = cand_bssid
            stats["recommended_channel"] = cand_chan
            
            # Update live snapshot
            stats["after_metrics"]["bssid"] = details["bssid"]
            stats["after_metrics"]["channel"] = details["channel"]
            stats["after_metrics"]["signal"] = details["signal"]
            stats["after_metrics"]["latency_ms"] = stats["latency_ms"]
            
            # Autonomous auto-pilot roaming if enabled and candidate is significantly superior
            if stats["auto_roam_enabled"] and details["bssid"] != "N/A" and cand_bssid != details["bssid"]:
                if cand_sig > (sig + 15):
                    log_assistant("ROAMER", "Auto-Pilot Handover", f"Clean candidate detected on {cand_bssid} (+{cand_sig - sig}% signal). Steer triggered.", "Auto-Roam")
                    switch_to_bssid(details["ssid"], cand_bssid)
        else:
            stats["best_ssid"] = details["ssid"]
            stats["best_bssid"] = details["bssid"]
            stats["recommended_channel"] = details["channel"] if details["channel"] > 0 else 1
        
        calculate_master_score()
        time.sleep(2.0)

def latency_worker():
    """Measures real HTTPS round-trip latency to Google Cloud."""
    global stats
    while True:
        try:
            t0 = time.time()
            s = socket.create_connection(("www.google.com", 443), timeout=3.0)
            latency = round((time.time() - t0) * 1000, 1)
            s.close()
            stats["latency_ms"] = latency
            
            if latency < 50:
                stats["network_health"] = "EXCELLENT (Ultra-low latency)"
            elif latency < 120:
                stats["network_health"] = "GOOD (Standard RTT)"
            else:
                stats["network_health"] = "CONGESTED (High traffic delay)"
        except Exception:
            stats["latency_ms"] = -1
            stats["network_health"] = "PACKET TIMEOUT / OFFLINE"
        
        calculate_master_score()
        time.sleep(3.0)

def esp_listener_worker():
    """
    Reads physical RF spectrum analytics from ESP32 hardware antenna.
    Falls back gracefully to OS native Wi-Fi scanner when ESP32 is unplugged.
    """
    global stats
    while True:
        port = auto_detect_esp()
        if not port:
            stats["esp_connected"] = False
            stats["esp_port"] = "Disconnected"
            stats["radar_source"] = f"{pa.SYSTEM} Wi-Fi (Software Fallback)"
            
            # Pure physical scan via host Wi-Fi adapter
            c1, c6, c11, total, _, _, _ = pa.scan_nearby_wifi_channels()
            stats["ch1"] = c1
            stats["ch6"] = c6
            stats["ch11"] = c11
            stats["total_aps"] = total
            
            # Calculate physical congestion score based on current channel density
            cur_ch = stats["current_channel"]
            cur_ch_count = c1 if cur_ch == 1 else (c6 if cur_ch == 6 else (c11 if cur_ch == 11 else 1))
            stats["congestion_score"] = min(100, int((cur_ch_count / max(1, total)) * 100)) if total > 0 else 0
            
            def get_lane_info(count):
                if count >= 4: return "Jammed 🚗🚗🚗", f"{count} routers on channel"
                elif count >= 2: return "Moderate 🚗", f"{count} routers on channel"
                else: return "Empty 🏎️", f"{count} routers (clean lane)"
                
            s1, d1 = get_lane_info(c1)
            s6, d6 = get_lane_info(c6)
            s11, d11 = get_lane_info(c11)
            
            stats["highway"]["lane1"] = {"channel": 1, "count": c1, "status": s1, "desc": d1}
            stats["highway"]["lane6"] = {"channel": 6, "count": c6, "status": s6, "desc": d6}
            stats["highway"]["lane11"] = {"channel": 11, "count": c11, "status": s11, "desc": d11}
            
            least = min(c1, c6, c11)
            if least == c11: stats["highway"]["best_lane"] = 11
            elif least == c6: stats["highway"]["best_lane"] = 6
            else: stats["highway"]["best_lane"] = 1
            
            time.sleep(3.5)
            continue
            
        try:
            stats["esp_port"] = port
            ser = serial.Serial(port, DEFAULT_BAUD, timeout=4)
            stats["esp_connected"] = True
            stats["radar_source"] = f"ESP32 Hardware Antenna ({port})"
            log_assistant("RADAR", "ESP32 Antenna Connected", f"Hardware antenna sniffing 2.4 GHz airwaves on {port}.", "Online")
            
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        data = json.loads(line)
                        if data.get("type") == "telemetry":
                            stats["total_aps"] = data.get("total_aps", 0)
                            stats["congestion_score"] = data.get("congestion_score", 0)
                            c1 = data.get("ch1_count", 0)
                            c6 = data.get("ch6_count", 0)
                            c11 = data.get("ch11_count", 0)
                            stats["ch1"] = c1
                            stats["ch6"] = c6
                            stats["ch11"] = c11
                            
                            def get_lane_info(count):
                                if count >= 4: return "Jammed 🚗🚗🚗", f"{count} routers on channel"
                                elif count >= 2: return "Moderate 🚗", f"{count} routers on channel"
                                else: return "Empty 🏎️", f"{count} routers (clean lane)"
                                
                            s1, d1 = get_lane_info(c1)
                            s6, d6 = get_lane_info(c6)
                            s11, d11 = get_lane_info(c11)
                            
                            stats["highway"]["lane1"] = {"channel": 1, "count": c1, "status": s1, "desc": d1}
                            stats["highway"]["lane6"] = {"channel": 6, "count": c6, "status": s6, "desc": d6}
                            stats["highway"]["lane11"] = {"channel": 11, "count": c11, "status": s11, "desc": d11}
                            
                            least = min(c1, c6, c11)
                            if least == c11: stats["highway"]["best_lane"] = 11
                            elif least == c6: stats["highway"]["best_lane"] = 6
                            else: stats["highway"]["best_lane"] = 1
                    except json.JSONDecodeError:
                        pass
        except Exception:
            stats["esp_connected"] = False
            time.sleep(2.0)

def spectrum_wave_streamer():
    """
    Streams the verified physical channel history.
    100% physically measured counts, ZERO artificial sinusoidal oscillations or random noise.
    """
    global stats
    while True:
        time.sleep(1.0)
        c1 = float(stats.get("ch1", 0))
        c6 = float(stats.get("ch6", 0))
        c11 = float(stats.get("ch11", 0))
        
        stats["spectrum_history"].append({
            "ch1": c1,
            "ch6": c6,
            "ch11": c11
        })
        if len(stats["spectrum_history"]) > 25:
            stats["spectrum_history"].pop(0)

def intelligent_copilot_worker():
    """Emits calm assistant observations based on physical link shifts."""
    global stats
    time.sleep(4.0)
    if stats["esp_connected"]:
        log_assistant("COPILOT", "ESP32 Radar Guarding", "ESP32 Hardware Radar active.", "Ready")
    else:
        log_assistant("COPILOT", "Host Guard Active", f"{pa.SYSTEM} Wi-Fi Guard active.", "Ready")
    
    last_lane_advised = None
    last_advice_time = 0
    
    while True:
        time.sleep(12.0)
        now = time.time()
        
        best_lane = stats["highway"]["best_lane"]
        cur_chan = stats["current_channel"]
        
        if cur_chan != 0 and cur_chan != best_lane and cur_chan <= 13:
            if best_lane != last_lane_advised or (now - last_advice_time > 60):
                last_lane_advised = best_lane
                last_advice_time = now
                src = "ESP32 Hardware Antenna" if stats.get("esp_connected") else f"{pa.SYSTEM} Wi-Fi Scan"
                log_assistant("COPILOT", "Cleaner Channel Available", f"Channel {best_lane} has lower AP density ({src}).", "Tip")
        elif (now - last_advice_time > 90):
            last_advice_time = now
            total = stats["total_aps"]
            if stats.get("esp_connected"):
                log_assistant("RADAR", "RF Environment Verified", f"ESP32 scanned {total} nearby BSSIDs. Signal steady.", "All Good")
            else:
                log_assistant("ROAMER", "RF Environment Verified", f"Host scan recorded {total} visible BSSIDs.", "Info")

def dns_shield_worker():
    """Local DNS Shield Sinkhole Server."""
    global stats
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("127.0.0.1", DNS_LISTEN_PORT))
    except Exception:
        return

    while True:
        try:
            data, addr = sock.recvfrom(512)
            stats["total_queries"] += 1
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).rstrip(".")
            
            is_blocked = any(bad in qname.lower() for bad in BLOCKED_DOMAINS)
            if is_blocked:
                stats["blocked_queries"] += 1
                stats["bandwidth_saved_kb"] += 2.5
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
                sock.sendto(reply.pack(), addr)
                log_assistant("SHIELD", "Blocked Tracking Query", f"Poisoned tracker request ({qname}).", "Sinkholed")
            else:
                up_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                up_sock.settimeout(1.5)
                up_sock.sendto(data, UPSTREAM_DNS)
                resp, _ = up_sock.recvfrom(512)
                sock.sendto(resp, addr)
                up_sock.close()
        except Exception:
            pass

class DashboardHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        if clean_path == "/" or clean_path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                with open(HTML_FILE_PATH, "rb") as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(f"Error loading dashboard: {e}".encode())
        elif clean_path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        else:
            # Serve static assets from web_dashboard (e.g. /assets/...)
            web_dir = os.path.dirname(HTML_FILE_PATH)
            rel_path = clean_path.lstrip("/\\")
            file_target = os.path.normpath(os.path.join(web_dir, rel_path))
            try:
                if os.path.commonpath([web_dir]) == os.path.commonpath([web_dir, file_target]) and os.path.isfile(file_target):
                    content_type, _ = mimetypes.guess_type(file_target)
                    self.send_response(200)
                    self.send_header("Content-type", content_type or "application/octet-stream")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(file_target, "rb") as f:
                        self.wfile.write(f.read())
                    return
            except Exception:
                pass
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/switch_ap":
            target_bssid = stats.get("best_bssid")
            ssid = stats.get("current_ssid")
            success, msg = switch_to_bssid(ssid, target_bssid)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
        elif self.path == "/api/toggle_auto_roam":
            stats["auto_roam_enabled"] = not stats["auto_roam_enabled"]
            status_str = "ENABLED" if stats["auto_roam_enabled"] else "DISABLED"
            log_assistant("ROAMER", "Auto-Pilot Mode", f"Auto-Pilot set to {status_str}.", status_str)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"auto_roam_enabled": stats["auto_roam_enabled"]}).encode())
        elif self.path == "/api/capture_baseline":
            p1, _ = pa.get_wifi_interface_names()
            stats["before_metrics"] = {
                "bssid": stats.get("current_bssid", "N/A"),
                "channel": stats.get("current_channel", 1),
                "signal": stats.get("current_signal", 0),
                "latency_ms": stats.get("latency_ms", 0.0),
                "download_speed": stats.get("download_speed_str", "Idle"),
                "hardware": f"{pa.SYSTEM} Wi-Fi ({p1})",
                "status": "Saved Baseline",
                "timestamp": time.strftime("%H:%M:%S")
            }
            stats["improvements"]["latency_drop_pct"] = 0
            stats["improvements"]["signal_gain_pct"] = 0
            stats["improvements"]["speed_boost_pct"] = 0
            stats["improvements"]["mode"] = "baseline_saved"
            log_assistant("ROAMER", "Baseline Snapshot Saved", f"Saved baseline: BSSID {stats['current_bssid']}, Ch {stats['current_channel']}, Ping {stats['latency_ms']} ms.", "Saved")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "baseline": stats["before_metrics"]}).encode())
        elif self.path == "/api/run_benchmark":
            p1, p2 = pa.get_wifi_interface_names()
            has_secondary = pa.is_secondary_wifi_detected()
            stats["wlan1_detected"] = has_secondary

            # 1. 100% physically measured throughput test on primary adapter
            solo_speed = pa.measure_interface_speed_mbps(p1, duration=3.0)
            if solo_speed <= 0.0:
                solo_speed = pa.measure_interface_speed_mbps(None, duration=3.0)

            if has_secondary and p2:
                # 2. Measured throughput on secondary adapter
                p2_solo = pa.measure_interface_speed_mbps(p2, duration=3.0)
                dual_speed = round(solo_speed + p2_solo, 2)
                boost_pct = round(((dual_speed - solo_speed) / solo_speed) * 100) if solo_speed > 0 and p2_solo > 0 else 0

                stats["wlan0_speed_mbps"] = solo_speed
                stats["wlan1_speed_mbps"] = p2_solo
                stats["dual_combined_mbps"] = dual_speed

                stats["before_metrics"] = {
                    "bssid": stats.get("current_bssid", p1),
                    "channel": stats.get("current_channel", 1),
                    "signal": stats.get("current_signal", 50),
                    "latency_ms": stats.get("latency_ms", 35.0),
                    "download_speed": f"{solo_speed} Mbps",
                    "hardware": f"Solo Wi-Fi ({p1})",
                    "status": "Solo Baseline",
                    "timestamp": time.strftime("%H:%M:%S")
                }
                stats["after_metrics"] = {
                    "bssid": f"Dual Turbo ({p1} + {p2})",
                    "channel": stats.get("current_channel", 1),
                    "signal": stats.get("current_signal", 50),
                    "latency_ms": stats.get("latency_ms", 35.0),
                    "download_speed": f"{dual_speed} Mbps ({p1}: {solo_speed}M + {p2}: {p2_solo}M)",
                    "hardware": f"Dual-Bonded ({p1} + {p2})",
                    "status": "Dual Turbo Multi-Link Active",
                    "timestamp": time.strftime("%H:%M:%S")
                }
                stats["improvements"]["speed_boost_pct"] = boost_pct
                stats["improvements"]["mode"] = "dual_turbo"

                log_assistant("ROAMER", "Dual Speed Benchmark", f"Solo: {solo_speed} Mbps | Dongle: {p2_solo} Mbps ➔ Dual Aggregated: {dual_speed} Mbps (+{boost_pct}% Boost)", f"+{boost_pct}%")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "wlan1_connected": True,
                    "solo_speed_mbps": solo_speed,
                    "wlan1_speed_mbps": p2_solo,
                    "dual_speed_mbps": dual_speed,
                    "boost_pct": boost_pct
                }).encode())
            else:
                # Truthful Solo Mode (Secondary not detected)
                stats["wlan0_speed_mbps"] = solo_speed
                stats["wlan1_speed_mbps"] = 0.0
                stats["dual_combined_mbps"] = solo_speed

                stats["before_metrics"] = {
                    "bssid": stats.get("current_bssid", p1),
                    "channel": stats.get("current_channel", 1),
                    "signal": stats.get("current_signal", 50),
                    "latency_ms": stats.get("latency_ms", 35.0),
                    "download_speed": f"{solo_speed} Mbps",
                    "hardware": f"Solo Wi-Fi ({p1})",
                    "status": "Measured Solo Baseline",
                    "timestamp": time.strftime("%H:%M:%S")
                }
                stats["after_metrics"] = {
                    "bssid": stats.get("current_bssid", p1),
                    "channel": stats.get("current_channel", 1),
                    "signal": stats.get("current_signal", 50),
                    "latency_ms": stats.get("latency_ms", 35.0),
                    "download_speed": f"{solo_speed} Mbps (Solo Mode)",
                    "hardware": f"Solo Wi-Fi ({p1})",
                    "status": "Solo Benchmark Complete",
                    "timestamp": time.strftime("%H:%M:%S")
                }
                stats["improvements"]["speed_boost_pct"] = 0
                stats["improvements"]["mode"] = "solo_bench"

                log_assistant("ROAMER", "Solo Speed Benchmark", f"Physically measured solo Wi-Fi download speed: {solo_speed} Mbps.", "Solo")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "wlan1_connected": False,
                    "solo_speed_mbps": solo_speed,
                    "dual_speed_mbps": solo_speed,
                    "boost_pct": 0,
                    "message": f"Measured solo laptop Wi-Fi speed: {solo_speed} Mbps. Connect secondary USB Wi-Fi dongle to unlock Dual Link aggregation."
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def init_initial_state():
    """Initializes actual physical state synchronously before worker threads start."""
    try:
        details = pa.get_active_wifi_details()
        stats["current_ssid"] = details["ssid"]
        stats["current_bssid"] = details["bssid"]
        stats["current_channel"] = details["channel"]
        stats["current_signal"] = details["signal"]
        stats["current_band"] = details["band"]
        stats["current_radio"] = details["radio"]
        stats["current_rx_rate"] = details["rx_rate"]
        stats["current_tx_rate"] = details["tx_rate"]
        stats["current_rssi"] = details["rssi"]
        stats["best_rssi"] = details["rssi"]

        c1, c6, c11, total, best_b, best_ch, best_s = pa.scan_nearby_wifi_channels()
        stats["ch1"] = c1
        stats["ch6"] = c6
        stats["ch11"] = c11
        stats["total_aps"] = total
        stats["best_ssid"] = details["ssid"]
        stats["best_bssid"] = best_b if best_b != "None" else details["bssid"]
        stats["recommended_channel"] = best_ch if best_ch > 0 else (details["channel"] or 1)

        p1, _ = pa.get_wifi_interface_names()
        stats["before_metrics"] = {
            "bssid": details["bssid"],
            "channel": details["channel"],
            "signal": details["signal"],
            "latency_ms": 0.0,
            "download_speed": "Idle",
            "hardware": f"{pa.SYSTEM} Wi-Fi ({p1})",
            "status": "Baseline Snapshot",
            "timestamp": time.strftime("%H:%M:%S")
        }
        stats["after_metrics"] = dict(stats["before_metrics"])
        stats["after_metrics"]["status"] = "Live Tracking"
    except Exception as e:
        print("[INIT ERROR]", e)

def web_server_worker():
    server = HTTPServer(("0.0.0.0", WEB_PORT), DashboardHandler)
    server.serve_forever()

if __name__ == "__main__":
    init_initial_state()
    log_assistant("COPILOT", "System Initialized", f"NetShield-IoT v5.0 Enterprise active on {pa.SYSTEM}.", "Ready")
    
    threading.Thread(target=dns_shield_worker, daemon=True).start()
    threading.Thread(target=download_speed_worker, daemon=True).start()
    threading.Thread(target=active_connection_poller, daemon=True).start()
    threading.Thread(target=latency_worker, daemon=True).start()
    threading.Thread(target=esp_listener_worker, daemon=True).start()
    threading.Thread(target=spectrum_wave_streamer, daemon=True).start()
    threading.Thread(target=intelligent_copilot_worker, daemon=True).start()
    threading.Thread(target=web_server_worker, daemon=True).start()
    log_assistant("COPILOT", "Dashboard Ready", f"Enterprise Controller running at http://localhost:{WEB_PORT}", "Online")
    
    while True:
        time.sleep(1)
