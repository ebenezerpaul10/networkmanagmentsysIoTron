"""
Unit Tests: ESP32 Hardware Radar & Serial Port Manager
Verifies port discovery logic, JSON packet decoding, and schema validation.
"""

import unittest
from hardware.serial_manager import SerialPortManager
from hardware.esp32 import Esp32RadarClient

class DummySerial:
    def __init__(self, lines):
        self.lines = [l.encode() for l in lines]
    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return b""
    def close(self): pass

class TestHardwareSubsystem(unittest.TestCase):
    def test_serial_port_auto_detect(self):
        # Auto detect should return str or None without throwing exception
        port = SerialPortManager.auto_detect_esp32_port()
        self.assertTrue(port is None or isinstance(port, str))

    def test_esp32_packet_parsing(self):
        received_packets = []
        def handler(pkt):
            received_packets.append(pkt)

        client = Esp32RadarClient(on_telemetry=handler)
        client.is_connected = True
        client._serial_conn = DummySerial([
            '{"type": "telemetry", "total_aps": 21, "ch1_count": 5, "ch6_count": 10, "ch11_count": 6, "congestion_score": 48}\n',
            'MALFORMED_LINE\n',
            '{"type": "telemetry", "total_aps": 22, "ch1_count": 6, "ch6_count": 10, "ch11_count": 6, "congestion_score": 50}\n'
        ])

        p1 = client.read_packet()
        self.assertIsNotNone(p1)
        self.assertEqual(p1["total_aps"], 21)
        self.assertEqual(p1["ch6_count"], 10)

        # Malformed line should be ignored
        p2 = client.read_packet()
        self.assertIsNone(p2)

        # Third packet should be read
        p3 = client.read_packet()
        self.assertIsNotNone(p3)
        self.assertEqual(p3["total_aps"], 22)

        self.assertEqual(len(received_packets), 2)

if __name__ == "__main__":
    unittest.main()
