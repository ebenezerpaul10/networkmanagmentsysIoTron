# NetShield-IoT: Hardware RF Radar & Network Optimization System

## 📂 Project Structure
- `esp32_radar/esp32_radar.ino` : Firmware for the ESP32 (Scans 2.4GHz channels, measures latency, detects cleanest AP).
- `laptop_engine/netshield.py` : Host engine (Serial listener + Hardware-grade DNS Ad & Spyware Shield + Live Terminal Dashboard).

## 🚀 How to Launch Arduino IDE (GUI)
Run this command in any terminal:
```bash
arduino-ide
```
(Installed at `~/.local/bin/arduino-ide` pointing to `/home/octopaul/Applications/arduino-ide.AppImage`)

## ⚡ How to Flash ESP32
1. Plug your ESP32 into a laptop USB port.
2. Open `esp32_radar/esp32_radar.ino` in Arduino IDE.
3. Select Board: **ESP32 Dev Module**, Port: `/dev/ttyUSB0` (or `/dev/ttyACM0`).
4. Click **Upload**!

## 🛡️ How to Run the Laptop Engine & Dashboard
```bash
python3 /home/octopaul/antigravity/NetShield-IoT/laptop_engine/netshield.py
```

## 🚀 How to Enable Dual-Network Bonding (Speed Doubler)
1. Keep Laptop connected to Hostel Wi-Fi.
2. Connect your Mobile Phone to Laptop via USB cable and turn on **USB Tethering** (or 2nd Wi-Fi adapter).
3. Start dispatch-proxy to combine speeds:
```bash
dispatch start
```
