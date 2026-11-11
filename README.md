# NetShield-IoT: Advanced Wireless Network Monitoring & Optimization Platform

**NetShield-IoT** is an enterprise-grade, cross-platform wireless network optimization and intelligence platform designed to discover wireless access points, monitor channel congestion, detect sticky-client trapping, execute seamless BSS transitions, provide an RFC-compliant DNS ad/tracking sinkhole, and manage multi-link transport.

---

## 🏛️ System Architecture

```
NetShield-IoT/
├── core/                       # Core Decision & Optimization Logic
│   ├── interfaces.py           # Dataclasses & Type Contracts
│   ├── roaming.py              # Intelligent Roaming Engine (Hysteresis & Cooldowns)
│   ├── scanner.py              # Unified Hardware & Software Scanner Coordinator
│   ├── network_monitor.py      # Real-Time Throughput & Ping RTT Monitor
│   └── optimizer.py            # Master 0-100 Score & Highway Traffic Analogy
│
├── platforms/                  # OS Abstraction Layer
│   ├── base.py                 # Abstract Base Platform Adapter Contract
│   ├── linux.py                # Linux Adapter (wpa_cli Fast Roam, nmcli, nl80211/iw)
│   ├── windows.py              # Windows Adapter (netsh wlan Native WLAN API)
│   └── macos.py                # macOS Adapter (Apple CoreWLAN / AirPort binary)
│
├── hardware/                   # External RF Hardware Layer
│   ├── serial_manager.py       # Cross-Platform Serial Discovery (CP210x, CH340, FTDI)
│   └── esp32.py                # ESP32 JSON Telemetry Parser & Watchdog
│
├── dns/                        # DNS Sinkhole Subsystem
│   ├── server.py               # Dual UDP & TCP Port 53 Server (dnslib parser)
│   ├── filter.py               # Allowlist & Blocklist Policy Manager
│   └── interceptor.py          # iptables / nftables Redirection Command Helper
│
├── proxy/                      # Multi-Link & Transport Subsystem
│   ├── mptcp.py                # True Multipath TCP (RFC 8684) Kernel Manager
│   ├── dispatch.py             # SOCKS5 Multi-Interface Socket Dispatcher Bridge
│   └── path_manager.py         # Physical Interface Metric & Link State Monitor
│
├── api/                        # HTTP REST API & Web Server
│   ├── routes.py               # Request Dispatcher & Schema Validator
│   └── server.py               # Multi-threaded HTTP Server
│
├── config/                     # Centralized Configuration
│   └── settings.py             # Global Parameters, Thresholds, & Upstreams
│
├── tests/                      # Automated Verification & Regression Suite
│   ├── test_roaming.py         # Roaming Hysteresis & Anti-Oscillation Tests
│   ├── test_dns.py             # Port 53 UDP/TCP & mDNS Isolation Tests
│   ├── test_platforms.py       # Platform Adapter & 802.11 Capabilities Tests
│   ├── test_mptcp.py           # MPTCP Kernel Detection & Socket Factory Tests
│   ├── test_hardware.py        # ESP32 Telemetry & Serial Auto-Detection Tests
│   └── test_integration.py     # End-to-End REST API & Pipeline Tests
│
├── laptop_engine/
│   └── netshield.py            # Main Engine Coordinator & Legacy Runner
├── web_dashboard/
│   └── index.html              # Responsive Cyberpunk-Glassmorphic Dashboard
└── esp32_radar/
    └── esp32_radar.ino         # ESP32 2.4GHz Channel Sniffer Firmware
```

---

## 🚦 Feature Status Matrix

| Subsystem | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Wi-Fi Roaming** | Hysteresis & Sticky-Client Detection | **IMPLEMENTED** | Prevents AP flapping with dBm & % signal thresholds |
| **Wi-Fi Roaming** | Anti-Oscillation Cooldown Timer | **IMPLEMENTED** | Configurable 45s cooldown between automatic roams |
| **Wi-Fi Roaming** | 802.11r (Fast Transition) Aware | **IMPLEMENTED** | Uses `wpa_cli roam` to preserve active TCP/SSH connections |
| **Wi-Fi Roaming** | 802.11k (RRM) & 802.11v (BTM) Check | **IMPLEMENTED** | Inspects `iw phy` and supplicant IEs for AP/driver support |
| **Wi-Fi Roaming** | Safe Execution & Rollback | **IMPLEMENTED** | Verifies association, DNS, and ping; reverts on failure |
| **DNS Sinkhole** | UDP & TCP Port 53 Support | **IMPLEMENTED** | RFC-compliant standard DNS listening on Port 53 |
| **DNS Sinkhole** | mDNS Port 5353 Isolation | **IMPLEMENTED** | Port 5353 is strictly left untouched for Avahi/Bonjour |
| **DNS Sinkhole** | Dynamic Local Upstream Discovery | **IMPLEMENTED** | Reads host nameservers (`resolv.conf`) before public fallback |
| **DNS Sinkhole** | Open-Resolver Prevention | **IMPLEMENTED** | Binds to `127.0.0.1` loopback by default |
| **Platform Portability** | Linux (nl80211, wpa_cli, nmcli) | **IMPLEMENTED** | Fully tested and verified live |
| **Platform Portability** | Windows (`netsh wlan`) | **PARTIALLY IMPLEMENTED** | Native WLAN CLI parsing; tested in abstraction |
| **Platform Portability** | macOS (Apple `airport`) | **PARTIALLY IMPLEMENTED** | CoreWLAN parsing; tested in abstraction |
| **Transport** | True Multipath TCP (RFC 8684) | **EXPERIMENTAL** | Creates native MPTCP sockets; requires server support |
| **Transport** | SOCKS5 Multi-Socket Dispatcher | **IMPLEMENTED** | Distributes application sockets across interfaces |
| **Hardware Radar** | ESP32 Out-of-band RF Sniffing | **IMPLEMENTED** | Continuous 2.4GHz channel sniffing over UART |
| **Hardware Fallback** | Host Wi-Fi Software Scan | **IMPLEMENTED** | Truthfully displays host card scan when ESP32 unplugged |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Required packages: `pyserial`, `psutil`, `dnslib` (automatically installed by `start_netshield.py`)

### 1. Launching NetShield

#### 🐧 Linux / 🍎 macOS:
```bash
./start_netshield.sh
```

#### 🪟 Windows:
Double click `start_netshield.bat` or run:
```cmd
start_netshield.bat
```

#### 🐍 Universal Python:
```bash
python3 start_netshield.py
```

Dashboard will open automatically at: **`http://localhost:8080`**

---

## 🧪 Running Automated Tests

Run the complete test suite (25 unit and integration tests):
```bash
python3 -m unittest discover -v -s tests -p "test_*.py"
```

---

## 🛡️ Intelligent Roaming Engine Details

### 1. Sticky-Client Entrapment Prevention
Laptops frequently hold onto a weak access point (`-75 dBm` to `-85 dBm`) even when standing right next to a stronger access point. NetShield detects this condition when current RSSI drops below `-72 dBm` or signal falls below `45%`.

### 2. Roaming Hysteresis
To prevent "ping-ponging" (rapid oscillation between two access points of similar strength), NetShield enforces:
$$\Delta\text{Signal} \ge 15\% \quad \text{and} \quad \Delta\text{RSSI} \ge 10\,\text{dBm}$$
A candidate access point must substantially exceed the current AP before a handoff is considered.

### 3. IEEE 802.11r/k/v Fast Transition
- **Without 802.11r:** Roaming via standard connection switching causes an 802.11 disassociation, tearing down active TCP streams, SSH sessions, and video calls.
- **With NetShield's 802.11r Integration:** NetShield instructs `wpa_supplicant` via `wpa_cli roam <BSSID>`. When the wireless driver and AP support Fast Transition (FT), authentication keys are derived without a full 4-way EAP re-handshake, resulting in sub-100ms handoffs with zero TCP connection drops.

### 4. Post-Roam Verification & Rollback
Before declaring a roam successful, NetShield runs a post-roam connectivity check:
1. Confirms association with the target BSSID.
2. Checks IP address assignment.
3. Tests TCP RTT latency.
4. Verifies DNS resolution.
If any verification step fails, NetShield automatically rolls back to the previous AP profile.

---

## 🛑 RFC-Compliant DNS Sinkhole

### Standard Port 53 (UDP & TCP)
Conventional DNS operates on port 53. NetShield binds directly to `127.0.0.1:53` across both UDP and TCP (RFC 7766). If port 53 is unavailable due to permissions, it gracefully falls back to port `5354`.

### Strict mDNS (Port 5353) Separation
Multicast DNS (mDNS) operates on UDP port 5353 (`224.0.0.251`) for local link-local service discovery (Apple Bonjour, Avahi, KDE Connect, Chrome/Brave Cast). NetShield **never** binds port 5353 for unicast DNS queries, guaranteeing zero disruption to local device discovery.

### Transparent Traffic Redirection
NetShield does not modify system DNS settings silently. To route system traffic through the local sinkhole, run:
```bash
# Using iptables
sudo iptables -t nat -A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j REDIRECT --to-ports 53

# Or using systemd-resolved
resolvectl dns wlan0 127.0.0.1
```

---

## ⚡ True Multipath TCP (MPTCP) vs SOCKS Proxy

It is critical to distinguish between transport-layer multipath and application-layer socket distribution:

### 1. True Multipath TCP (RFC 8684) — *Transport Layer*
- Operates in the Linux kernel via protocol `IPPROTO_MPTCP` (protocol number 262).
- Enables a **single TCP stream** to be split across multiple physical interfaces (e.g. `wlan0` + `eth0`).
- **Constraint:** Requires MPTCP support at **both** client and remote server endpoints.
- Check local kernel support:
  ```bash
  sysctl net.mptcp.enabled
  ip mptcp endpoint show
  ```

### 2. Dispatch Proxy — *Application Layer*
- Distributes individual HTTP/TCP sockets in round-robin fashion across interfaces.
- Useful for multi-connection download managers (e.g. BitTorrent, Steam multi-stream).
- **Does not** combine bandwidth for a single sequential TCP socket.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Glassmorphic web dashboard UI |
| `/api/stats` | `GET` | Comprehensive system, Wi-Fi, and radar telemetry |
| `/api/capabilities` | `GET` | 802.11r/k/v hardware capabilities, MPTCP status, DNS stats |
| `/api/dns/stats` | `GET` | Total queries, blocked ad trackers, saved bandwidth |
| `/api/mptcp/status` | `GET` | MPTCP kernel schedulers, subflows, and path metrics |
| `/api/switch_ap` | `POST` | Triggers an intelligent, safe AP handoff |
| `/api/toggle_auto_roam` | `POST` | Enables / disables 24/7 intelligent auto-roaming |
| `/api/capture_baseline` | `POST` | Records a pre-optimization reference snapshot |
| `/api/run_benchmark` | `POST` | Executes a multi-stream download benchmark |

---

## ⚠️ Known Limitations & Boundaries
1. **802.11r FT Driver Dependency:** Fast BSS transition requires AP and Wi-Fi adapter support. If the AP does not advertise Mobility Domain Information Elements (MDE), NetShield safely falls back to standard reassociation.
2. **MPTCP Remote Support:** MPTCP aggregation requires an MPTCP-enabled remote web/proxy server. Ordinary web servers will fall back to single-subflow TCP.
3. **Privileged DNS Port 53:** Binding port 53 on Linux requires `CAP_NET_BIND_SERVICE` or root privileges. If run unprivileged without capabilities, NetShield falls back to port `5354`.
