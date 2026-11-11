#!/usr/bin/env bash
# NetShield-IoT: macOS & Linux One-Click Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "        🛡️  STARTING NETSHIELD-IoT SYSTEM...             "
echo "=========================================================="

cd "$SCRIPT_DIR"

# Check if python3 is available
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi

# Run via universal launcher
python3 "$SCRIPT_DIR/start_netshield.py"
