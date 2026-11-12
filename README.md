# NetShield-IoT: Hardware RF Radar & Network Optimization System

Cross-platform network optimization engine, RF airwave congestion scanner, DNS tracking shield, and live multi-adapter speed aggregator for **Windows, macOS, and Linux**.

---

## 📂 Project Structure
- `esp32_radar/esp32_radar.ino` : Firmware for the ESP32 (Scans 2.4GHz channels, measures congestion, sniffs nearby APs).
- `laptop_engine/platform_adapter.py` : Universal cross-platform network, serial port, and Wi-Fi abstraction layer (Windows `netsh`, macOS `airport`/`networksetup`, Linux `nmcli`/`sysfs`).
- `laptop_engine/netshield.py` : Host engine (Serial listener, DNS ad-blocker, dual Wi-Fi speed tracker, HTTP REST API & dashboard).
- `frontend/` : Pure White Enterprise React Controller (React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts).
- `web_dashboard/index.html` : Production build of the Pure White Enterprise Network Controller.
- `web_dashboard/index.legacy.html` : Archived legacy UI backup.
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

## 🛠️ Frontend Development (React + Vite + Tailwind)

To run the frontend in development mode with hot reload:
```bash
cd frontend
npm install
npm run dev
```
*(Proxy in `vite.config.ts` will forward all `/api` calls to `http://127.0.0.1:8080`)*.

To compile production assets into `web_dashboard/`:
```bash
cd frontend
npm run build
```

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
