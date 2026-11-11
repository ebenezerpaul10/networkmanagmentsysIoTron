"""
NetShield-IoT: ESP32 Hardware Radar Decoder & Client
Decodes telemetry from the external ESP32 RF sniffing module.
"""

import json
import time
import logging
from typing import Optional, Dict, Any, Callable
from hardware.serial_manager import SerialPortManager

logger = logging.getLogger(__name__)

class Esp32RadarClient:
    """Manages the lifecycle, communication, and telemetry parsing for the ESP32 radar."""

    def __init__(self, on_telemetry: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.on_telemetry = on_telemetry
        self.port: Optional[str] = None
        self.is_connected = False
        self.last_packet_time = 0.0
        self.total_packets_received = 0
        self._serial_conn = None

    def connect(self) -> bool:
        port = SerialPortManager.auto_detect_esp32_port()
        if not port:
            self.is_connected = False
            self.port = "Disconnected"
            return False

        try:
            self._serial_conn = SerialPortManager.open_serial_connection(port, timeout=2.0)
            self.port = port
            self.is_connected = True
            self.last_packet_time = time.time()
            return True
        except Exception as e:
            logger.debug(f"Failed to connect to ESP32 on {port}: {e}")
            self.is_connected = False
            self.port = "Disconnected"
            return False

    def disconnect(self):
        if self._serial_conn:
            try:
                self._serial_conn.close()
            except Exception:
                pass
            self._serial_conn = None
        self.is_connected = False
        self.port = "Disconnected"

    def read_packet(self) -> Optional[Dict[str, Any]]:
        """Reads and parses one line of JSON telemetry from the ESP32."""
        if not self.is_connected or not self._serial_conn:
            return None

        try:
            line = self._serial_conn.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                return None

            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                if data.get("type") == "telemetry":
                    self.last_packet_time = time.time()
                    self.total_packets_received += 1
                    if self.on_telemetry:
                        self.on_telemetry(data)
                    return data
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        except Exception as e:
            logger.debug(f"ESP32 serial read error: {e}")
            self.disconnect()

        return None
