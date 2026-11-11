"""
NetShield-IoT: Hardware Serial Port Manager
Handles cross-platform UART discovery, lifecycle, and auto-reconnect.
"""

import glob
import platform
import logging
from typing import Optional, List

try:
    import serial
    import serial.tools.list_ports as serial_list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

from config.settings import DEFAULT_BAUD, ESP32_KEYWORDS

logger = logging.getLogger(__name__)

class SerialPortManager:
    """Discovers and connects to ESP32 hardware UART across OSes."""

    @staticmethod
    def auto_detect_esp32_port() -> Optional[str]:
        if not HAS_SERIAL:
            return None

        system = platform.system()

        # Strategy 1: Enumerate comports via pyserial
        try:
            ports = list(serial_list_ports.comports())
            # Pass 1: Match vendor keywords
            for p in ports:
                desc = (p.description or "").lower()
                hwid = (p.hwid or "").lower()
                if any(kw in desc or kw in hwid for kw in ESP32_KEYWORDS):
                    return p.device

            # Pass 2: Match port name patterns
            for p in ports:
                dev = p.device
                if dev.startswith("COM") or "/dev/ttyUSB" in dev or "/dev/ttyACM" in dev or "/dev/cu.usb" in dev:
                    return dev
        except Exception as e:
            logger.debug(f"Pyserial comport enumeration error: {e}")

        # Strategy 2: Direct filesystem patterns
        if system == "Linux":
            matches = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
            if matches:
                return matches[0]
        elif system == "Darwin":
            matches = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/cu.wch*")
            if matches:
                return matches[0]
        elif system == "Windows":
            for i in range(1, 21):
                p_name = f"COM{i}"
                try:
                    s = serial.Serial(p_name)
                    s.close()
                    return p_name
                except Exception:
                    pass

        return None

    @staticmethod
    def open_serial_connection(port: str, baud: int = DEFAULT_BAUD, timeout: float = 2.0):
        if not HAS_SERIAL:
            raise RuntimeError("pyserial is not installed")
        return serial.Serial(port, baudrate=baud, timeout=timeout)
