#!/usr/bin/env python3
"""
NetShield-IoT: Universal Cross-Platform Launcher
Runs seamlessly on Windows, macOS, and Linux.
Automatically checks dependencies, opens the web dashboard, and starts the engine.
"""

import os
import sys
import time
import platform
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_SCRIPT = os.path.join(BASE_DIR, "laptop_engine", "netshield.py")

REQUIRED_PACKAGES = {
    "serial": "pyserial",
    "psutil": "psutil",
    "dnslib": "dnslib"
}

def check_and_install_dependencies():
    """Ensures required packages are installed."""
    missing = []
    for mod, pkg in REQUIRED_PACKAGES.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[NetShield] Installing required dependencies: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("[NetShield] All dependencies installed successfully.")
        except Exception as e:
            print(f"[NetShield Warning] Automatic dependency install failed: {e}")
            print(f"[NetShield] Please manually run: pip install {' '.join(missing)}")

def open_dashboard():
    """Opens the dashboard in the default web browser after a brief delay."""
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:8080")
    except Exception:
        pass

def check_port53_status():
    """Checks whether Port 53 is accessible without sudo on this host."""
    system = platform.system()
    if system == "Windows":
        print("[NetShield] 🪟 Windows: Port 53 is natively unprivileged for localhost.")
        return

    import socket
    can_bind = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 53))
        s.close()
        can_bind = True
    except Exception:
        can_bind = False

    if can_bind:
        print("[NetShield] 🛡️ Port 53 Access: Verified (Zero-Sudo Active ✅)")
    else:
        print("[NetShield] ℹ️ Port 53 requires elevated capability on this host.")
        print("[NetShield] 🛡️ Zero-Sudo Fallback: Operating seamlessly on Port 5354 (mDNS 5353 preserved).")
        print("[NetShield Tip] To permanently unlock Port 53 without sudo for all users, run once:")
        print("                ./scripts/enable_port53_nonroot.sh")

def main():
    system = platform.system()
    print("=" * 60)
    print(f"       🛡️  NETSHIELD-IoT CROSS-PLATFORM SYSTEM  🛡️")
    print(f"       Operating System Detected: {system} ({platform.machine()})")
    print("=" * 60)

    check_and_install_dependencies()
    check_port53_status()

    # Launch browser in a background thread
    import threading
    threading.Thread(target=open_dashboard, daemon=True).start()

    # Start the core engine
    print(f"[NetShield] Starting engine on {system}...")
    try:
        subprocess.run([sys.executable, ENGINE_SCRIPT])
    except KeyboardInterrupt:
        print("\n[NetShield] System shut down cleanly.")

if __name__ == "__main__":
    main()
