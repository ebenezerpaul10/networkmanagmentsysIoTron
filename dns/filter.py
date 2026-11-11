"""
NetShield-IoT: DNS Domain Filter & Policy Manager
Evaluates queries against allowlists and blocklists with wildcards and subdomains.
"""

from typing import Set, Iterable
from config.settings import DEFAULT_BLOCKED_DOMAINS, DEFAULT_ALLOWED_DOMAINS

class DnsDomainFilter:
    """Manages domain allowlisting and blocklisting for the DNS sinkhole."""

    def __init__(
        self,
        blocked_domains: Iterable[str] = DEFAULT_BLOCKED_DOMAINS,
        allowed_domains: Iterable[str] = DEFAULT_ALLOWED_DOMAINS
    ):
        self._blocked: Set[str] = {d.strip().lower() for d in blocked_domains if d.strip()}
        self._allowed: Set[str] = {d.strip().lower() for d in allowed_domains if d.strip()}

    def add_blocked(self, domain: str):
        self._blocked.add(domain.strip().lower())

    def remove_blocked(self, domain: str):
        self._blocked.discard(domain.strip().lower())

    def add_allowed(self, domain: str):
        self._allowed.add(domain.strip().lower())

    def remove_allowed(self, domain: str):
        self._allowed.discard(domain.strip().lower())

    def is_blocked(self, query_domain: str) -> bool:
        """
        Returns True if query_domain is blocked and not explicitly allowed.
        Supports subdomain matching: 'ad.doubleclick.net' matches 'doubleclick.net'.
        """
        q = query_domain.strip().rstrip(".").lower()
        if not q:
            return False

        # 1. Allowlist override takes absolute precedence
        for allowed in self._allowed:
            if q == allowed or q.endswith("." + allowed):
                return False

        # 2. Blocklist matching
        for blocked in self._blocked:
            if q == blocked or q.endswith("." + blocked):
                return True

        return False

    def get_stats(self) -> dict:
        return {
            "blocked_domains_count": len(self._blocked),
            "allowed_domains_count": len(self._allowed)
        }
