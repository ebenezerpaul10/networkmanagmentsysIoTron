#!/usr/bin/env bash
# NetShield-IoT: Master One-Click Launcher

PROJECT_DIR="/home/octopaul/antigravity/NetShield-IoT"

echo "=========================================================="
echo "        🛡️  STARTING NETSHIELD-IoT SYSTEM...             "
echo "=========================================================="

# Check if browser is available and launch dashboard in 2 seconds in background
(sleep 2 && which brave >/dev/null 2>&1 && brave http://localhost:8080 >/dev/null 2>&1 || xdg-open http://localhost:8080 >/dev/null 2>&1) &

# Run the Python Engine (DNS Shield + Serial Radar + Web Server + Terminal HUD)
python3 "$PROJECT_DIR/laptop_engine/netshield.py"
