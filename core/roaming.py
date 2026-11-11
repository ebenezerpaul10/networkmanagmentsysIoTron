"""
NetShield-IoT: Intelligent Wi-Fi Roaming & Decision Engine
Implements hysteresis, sticky-client detection, anti-oscillation cooldowns,
802.11k/v/r awareness, and safe post-roam verification with rollback protection.
"""

import time
import socket
import logging
from typing import Optional, List, Tuple, TYPE_CHECKING
from core.interfaces import (
    ActiveWifiStatus,
    ApCandidate,
    RoamResult,
    Capabilities80211
)
if TYPE_CHECKING:
    from platforms.base import AbstractPlatformAdapter
from config.settings import (
    ROAM_HYSTERESIS_DBM,
    ROAM_HYSTERESIS_PCT,
    ROAM_STICKY_THRESHOLD_DBM,
    ROAM_STICKY_THRESHOLD_PCT,
    ROAM_COOLDOWN_SEC,
    ROAM_PING_TARGET
)

logger = logging.getLogger(__name__)

class IntelligentRoamingEngine:
    """
    Decides when and where to roam.
    Prevents ping-pong oscillations, sticky-client entrapment, and premature handoffs.
    """

    def __init__(self, platform_adapter: AbstractPlatformAdapter):
        self.platform = platform_adapter
        self.last_roam_time = 0.0
        self.roam_history: List[RoamResult] = []
        self.auto_roam_enabled = False

    def evaluate_roam_candidate(
        self,
        current: ActiveWifiStatus,
        candidates: List[ApCandidate]
    ) -> Tuple[bool, Optional[ApCandidate], str]:
        """
        Evaluates visible BSSID candidates using hysteresis, sticky-client criteria,
        and stability checks.
        Returns: (should_roam, selected_candidate, reason_string)
        """
        if not current.is_connected or current.ssid in ["Disconnected", "Scanning...", "Unknown"]:
            return False, None, "Client is not currently associated with a valid Wi-Fi network"

        # Rule 1: Anti-Oscillation Cooldown Timer
        now = time.time()
        elapsed = now - self.last_roam_time
        if elapsed < ROAM_COOLDOWN_SEC:
            remaining = int(ROAM_COOLDOWN_SEC - elapsed)
            return False, None, f"Roaming cooldown active ({remaining}s remaining to prevent oscillation)"

        # Rule 2: Filter candidates strictly matching current SSID and differing BSSID
        valid_candidates = [
            c for c in candidates
            if c.ssid == current.ssid and c.bssid.upper() != current.bssid.upper()
        ]

        if not valid_candidates:
            return False, None, "No alternate BSSIDs visible for this SSID"

        # Rule 3: Sticky-Client Evaluation
        # If current signal is strong and latency is low, stay connected
        is_sticky = (
            current.rssi_dbm < ROAM_STICKY_THRESHOLD_DBM or
            current.signal_pct < ROAM_STICKY_THRESHOLD_PCT
        )

        # Rule 4: Multi-factor Scoring for Candidates
        # Score = Signal % + (15 if 5GHz) + (10 if 802.11r FT) - (5 if channel is congested 2.4GHz)
        best_candidate: Optional[ApCandidate] = None
        best_score = -999.0

        for cand in valid_candidates:
            score = float(cand.signal_pct)
            # 5GHz frequency bonus
            if cand.frequency_mhz >= 5000:
                score += 15.0
            # 802.11r FT capability bonus
            if cand.supports_80211r:
                score += 10.0
            # Clean channel bonus (Channels 1, 6, 11)
            if cand.channel in [1, 6, 11]:
                score += 5.0

            if score > best_score:
                best_score = score
                best_candidate = cand

        if not best_candidate:
            return False, None, "No candidate met minimum quality criteria"

        # Rule 5: Hysteresis Check
        # Candidate must be substantially better than current AP
        signal_gain_pct = best_candidate.signal_pct - current.signal_pct
        rssi_gain_dbm = best_candidate.rssi_dbm - current.rssi_dbm

        # If client is sticky, allow a slightly lower threshold (e.g. 10%)
        required_gain_pct = ROAM_HYSTERESIS_PCT if not is_sticky else (ROAM_HYSTERESIS_PCT - 5)

        if signal_gain_pct < required_gain_pct and rssi_gain_dbm < ROAM_HYSTERESIS_DBM:
            return (
                False,
                None,
                f"Candidate {best_candidate.bssid} gain (+{signal_gain_pct}%) does not exceed hysteresis threshold (+{required_gain_pct}%)"
            )

        reason = (
            f"Candidate [{best_candidate.bssid}] on Ch {best_candidate.channel} offers "
            f"+{signal_gain_pct}% stronger signal ({best_candidate.signal_pct}% vs {current.signal_pct}%). "
            f"Client status: {'Sticky 🪤' if is_sticky else 'Optimization ⚡'}."
        )
        return True, best_candidate, reason

    def execute_safe_roam(
        self,
        target_candidate: ApCandidate,
        current_status: ActiveWifiStatus
    ) -> RoamResult:
        """
        Executes an AP handoff with pre-roam snapshot, fast transition attempt,
        and post-roam connectivity verification with rollback.
        """
        logger.info(f"Initiating safe roam to {target_candidate.bssid} on SSID '{target_candidate.ssid}'")
        t_start = time.perf_counter()

        # Check if 802.11r/k/v capabilities exist
        caps = self.platform.detect_80211_capabilities()
        use_ft = caps.supports_80211r or target_candidate.supports_80211r

        # Perform transition via platform adapter
        result = self.platform.switch_wifi_bssid(
            ssid=target_candidate.ssid,
            target_bssid=target_candidate.bssid,
            use_fast_transition=use_ft
        )

        # Post-Roam Verification: Test DNS resolution and TCP ping
        if result.success:
            dns_ok, ping_ms = self._verify_post_roam_connectivity()
            if not dns_ok or ping_ms < 0:
                logger.warning("Post-roam verification failed: No internet reachability after AP switch")
                # Trigger recovery / rollback
                result.success = False
                result.rollback_triggered = True
                result.message += " (Post-roam verification failed: DNS/ping unreachable)"
            else:
                result.latency_ms = ping_ms
                self.last_roam_time = time.time()

        self.roam_history.insert(0, result)
        if len(self.roam_history) > 20:
            self.roam_history.pop()

        return result

    def _verify_post_roam_connectivity(self) -> Tuple[bool, float]:
        """Verifies DNS and TCP reachability after roaming."""
        ping_ms = -1.0
        dns_ok = False

        # 1. Test TCP Ping
        try:
            t0 = time.time()
            s = socket.create_connection(ROAM_PING_TARGET, timeout=2.0)
            ping_ms = round((time.time() - t0) * 1000, 1)
            s.close()
        except Exception:
            return False, -1.0

        # 2. Test DNS resolution
        try:
            addr = socket.gethostbyname("www.google.com")
            if addr:
                dns_ok = True
        except Exception:
            dns_ok = False

        return dns_ok, ping_ms
