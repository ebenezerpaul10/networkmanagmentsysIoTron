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

def main():
    system = platform.system()
    print("=" * 60)
    print(f"       🛡️  NETSHIELD-IoT CROSS-PLATFORM SYSTEM  🛡️")
    print(f"       Operating System Detected: {system} ({platform.machine()})")
    print("=" * 60)

    check_and_install_dependencies()

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
