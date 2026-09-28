"""
MultiSignalConfidenceScorer - Calculates weighted confidence scores.

Combines multiple signals (taint hints, sanitizer status, tier confirmations,
skeptic pass) into a final 0.0-1.0 confidence score and severity label.
"""

from typing import Dict, List


class MultiSignalConfidenceScorer:
    """Scores findings based on multiple confidence signals.

    Outputs confidence scores on a 0-100 scale (percentage) for clear presentation.
    """

    # Signal weights (sum to 1.0)
    WEIGHTS = {
        "taint_hint_present": 0.25,
        "sanitizer_registry_clear": 0.25,
        "tier1_exploitable": 0.20,
        "tier23_confirmed": 0.20,
        "skeptic_survived": 0.10,
        "entrypoint_source_confirmed": 0.10,
    }

    # Severity bands on 0-100 scale
    SEVERITY_BANDS = [
        (0, 40, "INFORMATIONAL"),
        (40, 60, "LOW"),
        (60, 75, "MEDIUM"),
        (75, 90, "HIGH"),
        (90, 100, "CRITICAL"),
    ]

    def __init__(self):
        pass

    def score(self, finding: Dict) -> Dict:
        """
        Calculate multi-signal confidence score for a finding.

        Args:
            finding: The finding to score

        Returns:
            Updated finding with confidence_score (0-100 scale) and severity
        """
        signals_present = []
        weighted_score = 0.0

        # Signal 1: Taint hint present
        if finding.get("tainted_variable"):
            signals_present.append("taint_hint_present")
            weighted_score += self.WEIGHTS["taint_hint_present"]

        # Signal 2: Sanitizer registry clear (no sanitizer covers this)
        # Check if sanitizers_checked is True and no sanitizer was found
        if finding.get("sanitizers_checked") and not finding.get("sanitizer_blocked"):
            signals_present.append("sanitizer_registry_clear")
            weighted_score += self.WEIGHTS["sanitizer_registry_clear"]

        # Signal 3: Tier 1 (`CHEAP_MODEL`) verdict was exploitable
        # Check if confidence_score from Tier 1 is high (normalized to 0-100)
        tier1_confidence = finding.get("confidence_score", 0)
        # Handle both 0-1 and 0-100 scales from upstream
        if tier1_confidence <= 1.0 and tier1_confidence > 0:
            tier1_confidence = tier1_confidence * 100  # Convert to 0-100
        if tier1_confidence >= 70:
            signals_present.append("tier1_exploitable")
            weighted_score += self.WEIGHTS["tier1_exploitable"]

        # Signal 4: Tier 2/3 (`SMART_MODEL` / `TIER2_MODEL`) confirmed
        # Check tier1_was_correct field
        if finding.get("tier1_was_correct"):
            signals_present.append("tier23_confirmed")
            weighted_score += self.WEIGHTS["tier23_confirmed"]

        # Signal 5: Skeptic pass survived (for high CVSS findings)
        if finding.get("skeptic_passed"):
            signals_present.append("skeptic_survived")
            weighted_score += self.WEIGHTS["skeptic_survived"]

        if finding.get("source_is_public_entry") or finding.get("distance_to_entry_point") == 0:
            signals_present.append("entrypoint_source_confirmed")
            weighted_score += self.WEIGHTS["entrypoint_source_confirmed"]

        # Normalize to 0-100 range (percentage scale)
        max_possible = sum(self.WEIGHTS.values())
        normalized_score = min(100.0, (weighted_score / max_possible) * 100.0)

        # Apply some baseline for findings that made it this far
        # Minimum 30% for findings that passed all filters
        normalized_score = max(30.0, normalized_score)

        distance = finding.get("distance_to_entry_point")
        if isinstance(distance, int):
            if distance <= 2:
                normalized_score = min(100.0, normalized_score + 8.0)
            elif distance >= 5:
                normalized_score = max(20.0, normalized_score - 8.0)

        if finding.get("is_dead"):
            normalized_score = max(15.0, normalized_score - 20.0)
        elif finding.get("is_test_only"):
            normalized_score = max(20.0, normalized_score - 15.0)

        # Determine severity from score
        severity = "LOW"
        for low, high, sev in self.SEVERITY_BANDS:
            if low <= normalized_score <= high:
                severity = sev
                break

        # When confidence is at the floor (no strong signals), derive severity from CVSS
        # so we don't mislabel high-impact findings as INFORMATIONAL (30 falls in 0–40 band).
        at_floor = normalized_score <= 40.0
        cvss = finding.get("cvss_score")
        if at_floor and cvss is not None and isinstance(cvss, (int, float)):
            try:
                cvss_f = float(cvss)
                if cvss_f >= 9.0:
                    severity = "CRITICAL"
                elif cvss_f >= 7.0:
                    severity = "HIGH"
                elif cvss_f >= 4.0:
                    severity = "MEDIUM"
                elif cvss_f >= 0.1:
                    severity = "LOW"
                # else keep INFORMATIONAL for cvss 0 or missing
            except (TypeError, ValueError):
                pass

        if finding.get("is_dead") or finding.get("is_test_only"):
            severity_order = ["INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
            try:
                idx = severity_order.index(severity)
                severity = severity_order[max(0, idx - 1)]
            except ValueError:
                pass

        # Update finding with 0-100 scale confidence score
        finding["confidence_score"] = round(normalized_score)
        finding["severity"] = severity
        finding["signals_present"] = signals_present
        # Store original scale indicator for debugging
        finding["_confidence_scale"] = "0-100 (percentage)"

        return finding

    def score_all(self, findings: List[Dict]) -> List[Dict]:
        """
        Score all findings in a list.

        Args:
            findings: List of findings to score

        Returns:
            List of scored findings
        """
        return [self.score(f) for f in findings]
