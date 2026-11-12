#!/usr/bin/env bash
# ==============================================================================
# NetShield-IoT: Permanent Zero-Sudo Port 53 Enabler for Linux
# ==============================================================================
# By default, Linux reserves ports < 1024 for root.
# This script sets Linux kernel 'ip_unprivileged_port_start = 53' permanently.
# After running this once, ANY non-root user can run NetShield on Port 53
# directly with 'python3 start_netshield.py' without ever needing sudo!
# ==============================================================================

set -e

echo "=========================================================="
echo "   🛡️ NetShield-IoT: Zero-Sudo Port 53 Permanent Setup    "
echo "=========================================================="

# Check if already enabled
CURRENT_VAL=$(cat /proc/sys/net/ipv4/ip_unprivileged_port_start 2>/dev/null || echo "1024")
if [ "$CURRENT_VAL" -le 53 ]; then
    echo "✅ Port 53 is ALREADY enabled for non-root users (Current start port: $CURRENT_VAL)."
    echo "Any user can run NetShield on Port 53 without sudo!"
    exit 0
fi

echo "Current unprivileged port start is $CURRENT_VAL."
echo "Setting net.ipv4.ip_unprivileged_port_start = 53 permanently..."

# Write persistent sysctl configuration file
SYSCTL_FILE="/etc/sysctl.d/99-netshield-port53.conf"

if command -v sudo >/dev/null 2>&1; then
    echo "net.ipv4.ip_unprivileged_port_start = 53" | sudo tee "$SYSCTL_FILE" >/dev/null
    sudo sysctl -w net.ipv4.ip_unprivileged_port_start=53 >/dev/null
else
    echo "net.ipv4.ip_unprivileged_port_start = 53" > "$SYSCTL_FILE"
    sysctl -w net.ipv4.ip_unprivileged_port_start=53 >/dev/null
fi

NEW_VAL=$(cat /proc/sys/net/ipv4/ip_unprivileged_port_start)
echo "=========================================================="
echo "✅ SUCCESS! Linux kernel unprivileged port start is now: $NEW_VAL"
echo "All users can now launch NetShield on Port 53 WITHOUT sudo:"
echo "   python3 start_netshield.py"
echo "=========================================================="
