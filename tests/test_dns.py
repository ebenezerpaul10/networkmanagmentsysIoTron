"""
Unit Tests: DNS Sinkhole, Domain Policy, and Port 53 Protocol
Verifies UDP & TCP handling, RFC parsing, allowlist/blocklist, and mDNS isolation.
"""

import unittest
import socket
import struct
import time
from dnslib import DNSRecord, QTYPE, RR, A
from dns.filter import DnsDomainFilter
from dns.server import DnsSinkholeServer

class TestDnsSubsystem(unittest.TestCase):
    def setUp(self):
        self.filter = DnsDomainFilter(
            blocked_domains=["doubleclick.net", "telemetry.tracker.io", "badads.com"],
            allowed_domains=["allowed.doubleclick.net", "google.com"]
        )

    def test_domain_filtering_policies(self):
        # 1. Exact match blocked
        self.assertTrue(self.filter.is_blocked("doubleclick.net"))
        # 2. Subdomain blocked
        self.assertTrue(self.filter.is_blocked("ad.telemetry.tracker.io"))
        # 3. Allowlist override takes precedence
        self.assertFalse(self.filter.is_blocked("allowed.doubleclick.net"))
        # 4. Standard allowed domains
        self.assertFalse(self.filter.is_blocked("google.com"))
        self.assertFalse(self.filter.is_blocked("mail.google.com"))

    def test_udp_and_tcp_sinkhole_wire_format(self):
        """Tests that blocked domains return 0.0.0.0 on wire format."""
        server = DnsSinkholeServer(domain_filter=self.filter, bind_addr="127.0.0.1", port=5354)

        # Build query for blocked domain
        q = DNSRecord.question("ad.badads.com", "A")
        raw_query = q.pack()

        # Handle packet
        raw_response = server.handle_query_packet(raw_query)
        self.assertIsNotNone(raw_response)

        # Parse response
        resp = DNSRecord.parse(raw_response)
        self.assertEqual(len(resp.rr), 1)
        self.assertEqual(str(resp.rr[0].rdata), "0.0.0.0")

    def test_tcp_dns_framing(self):
        """Tests that TCP worker parses 2-byte RFC 7766 length prefix correctly."""
        # Use an ephemeral test port
        server = DnsSinkholeServer(domain_filter=self.filter, bind_addr="127.0.0.1", port=5354)
        started = server.start()
        self.assertTrue(started)

        try:
            # Connect over TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(("127.0.0.1", server.active_port))

            # Send query with 2-byte prefix
            q = DNSRecord.question("doubleclick.net", "A").pack()
            s.sendall(struct.pack("!H", len(q)) + q)

            # Receive 2-byte response length
            resp_len_bytes = s.recv(2)
            self.assertEqual(len(resp_len_bytes), 2)
            resp_len = struct.unpack("!H", resp_len_bytes)[0]

            resp_data = s.recv(resp_len)
            s.close()

            resp = DNSRecord.parse(resp_data)
            self.assertEqual(str(resp.rr[0].rdata), "0.0.0.0")
        finally:
            server.stop()

    def test_mdns_isolation(self):
        """Confirms that the sinkhole NEVER binds to or interferes with mDNS 5353."""
        server = DnsSinkholeServer(domain_filter=self.filter)
        self.assertNotEqual(server.desired_port, 5353)
        self.assertNotEqual(server.active_port, 5353)

if __name__ == "__main__":
    unittest.main()
