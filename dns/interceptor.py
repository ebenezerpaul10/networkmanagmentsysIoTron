"""
NetShield-IoT: DNS Traffic Routing & Interception Helper
Provides explicit firewall redirection commands and system resolver guidance.
Does NOT execute destructive or silent system modifications without explicit authorization.
"""

from typing import Dict, List

class DnsTrafficInterceptor:
    """Generates transparent, verifiable firewall rules to direct local DNS queries to NetShield."""

    @staticmethod
    def generate_iptables_commands(port: int = 53) -> Dict[str, List[str]]:
        """Returns iptables redirect and rollback commands."""
        apply_cmds = [
            f"sudo iptables -t nat -A OUTPUT -p udp --dport 53 -d 127.0.0.1 -j REDIRECT --to-ports {port}",
            f"sudo iptables -t nat -A OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j REDIRECT --to-ports {port}"
        ]
        revert_cmds = [
            f"sudo iptables -t nat -D OUTPUT -p udp --dport 53 -d 127.0.0.1 -j REDIRECT --to-ports {port}",
            f"sudo iptables -t nat -D OUTPUT -p tcp --dport 53 -d 127.0.0.1 -j REDIRECT --to-ports {port}"
        ]
        return {"apply": apply_cmds, "revert": revert_cmds}

    @staticmethod
    def generate_nftables_commands(port: int = 53) -> Dict[str, List[str]]:
        """Returns nftables redirection rules."""
        apply_cmds = [
            "sudo nft add table nat",
            "sudo nft 'add chain nat output { type nat hook output priority -100; }'",
            f"sudo nft add rule nat output ip daddr 127.0.0.1 udp dport 53 redirect to {port}",
            f"sudo nft add rule nat output ip daddr 127.0.0.1 tcp dport 53 redirect to {port}"
        ]
        revert_cmds = [
            "sudo nft delete table nat"
        ]
        return {"apply": apply_cmds, "revert": revert_cmds}

    @staticmethod
    def get_systemd_resolved_instructions(port: int = 53) -> str:
        """Returns instructions for systemd-resolved integration."""
        return (
            f"# To point systemd-resolved to NetShield DNS:\n"
            f"resolvectl dns wlan0 127.0.0.1:{port}\n"
            f"# To restore default DNS:\n"
            f"resolvectl revert wlan0\n"
        )
