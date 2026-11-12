"""
NetShield-IoT: Standard RFC-Compliant DNS Sinkhole Server
Listens on UDP Port 53 and TCP Port 53 with dnslib query parsing and upstream failover.
"""

import os
import socket
import struct
import threading
import logging
from typing import Tuple, Optional, Callable
from dnslib import DNSRecord, QTYPE, RR, A, AAAA
from dns.filter import DnsDomainFilter
from config.settings import (
    DNS_BIND_ADDR,
    DNS_STANDARD_PORT,
    DNS_FALLBACK_PORT,
    DNS_UPSTREAM_PRIMARY,
    DNS_UPSTREAM_SECONDARY,
    DNS_QUERY_TIMEOUT
)

logger = logging.getLogger(__name__)

class DnsSinkholeServer:
    """
    Standard DNS sinkhole operating on UDP & TCP port 53.
    Separates multicast DNS (port 5353) entirely.
    """

    def __init__(
        self,
        domain_filter: Optional[DnsDomainFilter] = None,
        bind_addr: str = DNS_BIND_ADDR,
        port: int = DNS_STANDARD_PORT,
        on_query_event: Optional[Callable[[str, bool, str], None]] = None
    ):
        self.filter = domain_filter or DnsDomainFilter()
        self.bind_addr = bind_addr
        self.desired_port = port
        self.active_port = port
        self.on_query_event = on_query_event

        self.total_queries = 0
        self.blocked_queries = 0
        self.forwarded_queries = 0
        self.bandwidth_saved_kb = 0.0

        self.is_running = False
        self._udp_sock: Optional[socket.socket] = None
        self._tcp_sock: Optional[socket.socket] = None
        self._threads = []

    def start(self) -> bool:
        """Starts the DNS server on UDP and TCP port 53 (or fallback)."""
        # 1. Bind UDP Socket
        bound = self._bind_sockets(self.desired_port)
        if not bound and self.desired_port != DNS_FALLBACK_PORT:
            logger.warning(
                f"Could not bind standard port {self.desired_port}. "
                f"Falling back to unprivileged port {DNS_FALLBACK_PORT}."
            )
            bound = self._bind_sockets(DNS_FALLBACK_PORT)
            if bound:
                self.active_port = DNS_FALLBACK_PORT

        if not bound:
            logger.error("Failed to bind DNS server to any port")
            return False

        self.is_running = True

        # 2. Launch listener threads
        t_udp = threading.Thread(target=self._udp_worker, name="DNS-UDP-Worker", daemon=True)
        t_tcp = threading.Thread(target=self._tcp_worker, name="DNS-TCP-Worker", daemon=True)

        t_udp.start()
        t_tcp.start()
        self._threads.extend([t_udp, t_tcp])

        logger.info(f"DNS Sinkhole active on {self.bind_addr}:{self.active_port} (UDP & TCP)")
        return True

    def _bind_sockets(self, port: int) -> bool:
        try:
            # UDP Socket
            u_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            u_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            u_sock.bind((self.bind_addr, port))

            # TCP Socket
            t_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            t_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            t_sock.bind((self.bind_addr, port))
            t_sock.listen(10)

            self._udp_sock = u_sock
            self._tcp_sock = t_sock
            self.active_port = port
            return True
        except Exception as e:
            logger.debug(f"Socket bind failed on port {port}: {e}")
            if self._udp_sock:
                try: self._udp_sock.close()
                except Exception: pass
            if self._tcp_sock:
                try: self._tcp_sock.close()
                except Exception: pass
            return False

    def stop(self):
        self.is_running = False
        if self._udp_sock:
            try: self._udp_sock.close()
            except Exception: pass
        if self._tcp_sock:
            try: self._tcp_sock.close()
            except Exception: pass

    def handle_query_packet(self, data: bytes) -> Optional[bytes]:
        """
        Processes a raw DNS wire-format request.
        Returns wire-format response (sinkholed or forwarded from upstream).
        """
        self.total_queries += 1
        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).rstrip(".")
            qtype = QTYPE[request.q.qtype]
        except Exception:
            return None

        # Check blocklist policy
        is_blocked = self.filter.is_blocked(qname)

        if is_blocked:
            self.blocked_queries += 1
            self.bandwidth_saved_kb += 2.5
            reply = request.reply()
            # Sinkhole answer
            if qtype == "A" or request.q.qtype == QTYPE.A:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            elif qtype == "AAAA" or request.q.qtype == QTYPE.AAAA:
                reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA("::"), ttl=60))
            else:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))

            if self.on_query_event:
                self.on_query_event(qname, True, "Blocked Ad/Telemetry")
            return reply.pack()

        # Forward non-blocked query to upstream with fallback
        self.forwarded_queries += 1
        response = self._forward_to_upstream(data)
        if self.on_query_event and response:
            self.on_query_event(qname, False, "Allowed")
        return response

    def _get_upstreams(self) -> list:
        """Discovers host nameservers dynamically, falling back to public DNS."""
        servers = []
        try:
            if os.path.exists("/etc/resolv.conf"):
                with open("/etc/resolv.conf") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("nameserver"):
                            parts = line.split()
                            if len(parts) > 1:
                                ip = parts[1].strip()
                                if not ip.startswith("127."):
                                    servers.append((ip, 53))
        except Exception:
            pass

        if not servers:
            servers = [DNS_UPSTREAM_PRIMARY, DNS_UPSTREAM_SECONDARY]
        else:
            if DNS_UPSTREAM_PRIMARY not in servers:
                servers.append(DNS_UPSTREAM_PRIMARY)
        return servers

    def _forward_to_upstream(self, data: bytes) -> Optional[bytes]:
        """Forwards query to host / configured upstreams with fallback."""
        upstreams = self._get_upstreams()
        # Loop prevention: Ensure we are not sending to our own address & port
        for upstream in upstreams:
            if upstream[0] == self.bind_addr and upstream[1] == self.active_port:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(DNS_QUERY_TIMEOUT)
                s.sendto(data, upstream)
                resp, _ = s.recvfrom(4096)
                s.close()
                return resp
            except Exception:
                pass
        return None

    def _udp_worker(self):
        """Worker thread for UDP DNS queries."""
        while self.is_running and self._udp_sock:
            try:
                data, addr = self._udp_sock.recvfrom(4096)
                if not data:
                    continue
                response = self.handle_query_packet(data)
                if response and self._udp_sock:
                    self._udp_sock.sendto(response, addr)
            except Exception:
                if not self.is_running:
                    break

    def _tcp_worker(self):
        """Worker thread for TCP DNS queries (RFC 7766)."""
        while self.is_running and self._tcp_sock:
            try:
                conn, _ = self._tcp_sock.accept()
                threading.Thread(target=self._handle_tcp_client, args=(conn,), daemon=True).start()
            except Exception:
                if not self.is_running:
                    break

    def _handle_tcp_client(self, conn: socket.socket):
        """Handles a single TCP DNS client connection."""
        try:
            conn.settimeout(3.0)
            # TCP DNS uses 2-byte length prefix
            len_bytes = conn.recv(2)
            if len(len_bytes) == 2:
                q_len = struct.unpack("!H", len_bytes)[0]
                data = conn.recv(q_len)
                if data:
                    response = self.handle_query_packet(data)
                    if response:
                        resp_len = struct.pack("!H", len(response))
                        conn.sendall(resp_len + response)
        except Exception:
            pass
        finally:
            try: conn.close()
            except Exception: pass

    def get_metrics(self) -> dict:
        return {
            "bind_address": self.bind_addr,
            "port": self.active_port,
            "is_running": self.is_running,
            "zero_sudo_active": True,
            "mode": "standard_port_53" if self.active_port == 53 else f"unprivileged_fallback_port_{self.active_port}",
            "total_queries": self.total_queries,
            "blocked_queries": self.blocked_queries,
            "forwarded_queries": self.forwarded_queries,
            "bandwidth_saved_kb": round(self.bandwidth_saved_kb, 1),
            "filter_stats": self.filter.get_stats()
        }
