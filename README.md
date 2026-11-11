# NetShield-IoT: Hardware RF Radar & Network Optimization System

Cross-platform network optimization engine, RF airwave congestion scanner, DNS tracking shield, and live multi-adapter speed aggregator for **Windows, macOS, and Linux**.

---

## 📂 Project Structure
- `esp32_radar/esp32_radar.ino` : Firmware for the ESP32 (Scans 2.4GHz channels, measures congestion, sniffs nearby APs).
- `laptop_engine/platform_adapter.py` : Universal cross-platform network, serial port, and Wi-Fi abstraction layer (Windows `netsh`, macOS `airport`/`networksetup`, Linux `nmcli`/`sysfs`).
- `laptop_engine/netshield.py` : Host engine (Serial listener, DNS ad-blocker, dual Wi-Fi speed tracker, HTTP REST API & dashboard).
- `web_dashboard/index.html` : Modern glassmorphic Web UI with live airwave waveforms, highway traffic analogy, and before/after optimization proof.
- `start_netshield.bat` : One-click launcher for **Windows**.
- `start_netshield.sh` : One-click launcher for **macOS & Linux**.
- `start_netshield.py` : Universal cross-platform Python launcher.

---

## 🚀 How to Run (One-Click)

### 🪟 Windows:
Double-click `start_netshield.bat` or run:
```cmd
start_netshield.bat
```

### 🍎 macOS / 🐧 Linux:
Run in your terminal:
```bash
./start_netshield.sh
```

### 🐍 Universal Python:
Works on any system with Python 3.8+:
```bash
python3 start_netshield.py
```
*(Dependencies `pyserial`, `psutil`, `dnslib` will be automatically verified and installed if missing)*.

Dashboard opens automatically at: **`http://localhost:8080`**

---

## ⚡ ESP32 Hardware RF Sniffer (Optional)
NetShield operates with **dual-mode intelligence**:
1. **With ESP32 plugged in:** Sniffs raw RF airwaves 24/7 without interrupting laptop connectivity.
2. **Without ESP32:** Gracefully falls back to laptop OS software scanning (`Windows netsh`, `macOS airport`, `Linux nmcli`) with full transparency.

### Flashing Firmware:
1. Open `esp32_radar/esp32_radar.ino` in Arduino IDE.
2. Select Board: **ESP32 Dev Module**.
3. Select Port:
   - **Windows:** `COM3`, `COM4`, etc.
   - **macOS:** `/dev/cu.usbserial-*` or `/dev/cu.wch*`
   - **Linux:** `/dev/ttyUSB0` or `/dev/ttyACM0`
4. Click **Upload**!

---

## ⚡ Dual-Network Multi-Link (Speed Aggregator)
- Plug in a secondary USB Wi-Fi adapter or connect a phone via USB Tethering.
- NetShield detects both adapters simultaneously, measures live individual throughputs, and aggregates traffic across both links.
