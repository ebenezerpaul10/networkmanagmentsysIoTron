#!/usr/bin/env bash
# NetShield-IoT: Auto Compile & Flash Script for ESP32

SKETCH_DIR="/home/octopaul/antigravity/NetShield-IoT/esp32_radar"
ARDUINO_CLI="/home/octopaul/.local/bin/arduino-cli"

echo "=========================================================="
echo "        ⚡ NETSHIELD-IoT: AUTO-FLASH ENGINE               "
echo "=========================================================="

# 1. Detect Port
PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -n 1)

if [ -z "$PORT" ]; then
    echo "❌ No ESP32 detected on USB."
    echo "👉 Please plug your ESP32 into a laptop USB port and run this script again!"
    exit 1
fi

echo "✅ Found ESP32 on port: $PORT"
echo "🔨 Compiling & Uploading sketch to ESP32..."

# 2. Compile and Upload
$ARDUINO_CLI compile --fqbn esp32:esp32:esp32 "$SKETCH_DIR"
if [ $? -eq 0 ]; then
    echo "🚀 Flashing ESP32 now..."
    $ARDUINO_CLI upload -p "$PORT" --fqbn esp32:esp32:esp32 "$SKETCH_DIR"
    if [ $? -eq 0 ]; then
        echo "🎉 SUCCESS! ESP32 is flashed and ready."
        echo "👉 Now run: ./start_netshield.sh"
    else
        echo "⚠️ Upload failed. If using an older ESP32, hold down the 'BOOT' button on the board while flashing!"
    fi
else
    echo "❌ Compilation failed. Please make sure the board core is fully installed."
fi
