"""
FraudMesh Threshold Decision Explainer

Provides human-readable explanations for every threshold adjustment,
creating a complete audit trail to prove the system is NOT a black box.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from models import Transaction, ThresholdSnapshot


@dataclass
class ThresholdDecision:
    """
    Complete audit record of a threshold decision with human-readable explanation.
    """
    decision_id: str
    timestamp: datetime
    transaction_id: str
    
    # Threshold values
    base_threshold: float
    final_threshold: float
    
    # Individual adjustments
    time_adjustment: float
    amount_adjustment: float
    network_adjustment: float
    fpr_adjustment: float
    fairness_adjustment: float
    
    # Human-readable explanations
    primary_reason: str  # Main reason for adjustment
    detailed_explanation: str  # Full explanation
    risk_context: str  # What triggered this decision
    
    # Supporting data
    transaction_amount: float
    transaction_time: str
    network_fraud_rate: float
    system_fpr: float
    segment_fpr: Optional[float]
    
    # Decision outcome
    sensitivity_level: str  # "HIGH", "MEDIUM", "LOW"
    adjustment_magnitude: str  # "MAJOR", "MODERATE", "MINOR", "NONE"


class ThresholdExplainer:
    """
    Generates human-readable explanations for threshold decisions.
    
    This class transforms raw threshold adjustments into transparent,
    auditable decisions that prove the system is explainable.
    """
    
    def __init__(self):
        self.decision_log: List[ThresholdDecision] = []
    
    def explain_threshold_decision(
        self,
        txn: Transaction,
        snapshot: ThresholdSnapshot,
        base_threshold: float,
        network_fraud_rate: float,
        system_fpr: float,
        segment_fpr: Optional[float] = None
    ) -> ThresholdDecision:
        """
        Generate a complete, human-readable explanation for a threshold decision.
        
        Args:
            txn: The transaction being evaluated
            snapshot: Threshold snapshot with all factors
            base_threshold: Base threshold value
            network_fraud_rate: Current network fraud rate
            system_fpr: System-wide false positive rate
            segment_fpr: Segment-specific FPR (optional)
        
        Returns:
            ThresholdDecision with complete audit trail
        """
        # Calculate total adjustment
        total_adjustment = snapshot.threshold - base_threshold
        
        # Determine primary reason (largest adjustment factor)
        factors = {
            "time": abs(snapshot.time_factor),
            "amount": abs(snapshot.amount_factor),
            "network": abs(snapshot.network_factor),
            "fpr": abs(snapshot.fpr_factor),
            "fairness": abs(getattr(snapshot, 'fairness_factor', 0.0))
        }
        primary_factor = max(factors, key=factors.get)
        
        # Generate explanations
        primary_reason = self._generate_primary_reason(
            primary_factor, snapshot, txn, network_fraud_rate, system_fpr, segment_fpr
        )
        
        detailed_explanation = self._generate_detailed_explanation(
            snapshot, txn, base_threshold, network_fraud_rate, system_fpr, segment_fpr
        )
        
        risk_context = self._generate_risk_context(
            txn, network_fraud_rate, system_fpr, segment_fpr
        )
        
        # Determine sensitivity level
        sensitivity_level = self._determine_sensitivity_level(snapshot.threshold)
        
        # Determine adjustment magnitude
        adjustment_magnitude = self._determine_adjustment_magnitude(total_adjustment)
        
        # Create decision record
        decision = ThresholdDecision(
            decision_id=f"TD-{txn.id[:8]}-{int(snapshot.timestamp.timestamp())}",
            timestamp=snapshot.timestamp,
            transaction_id=txn.id,
            base_threshold=base_threshold,
            final_threshold=snapshot.threshold,
            time_adjustment=snapshot.time_factor,
            amount_adjustment=snapshot.amount_factor,
            network_adjustment=snapshot.network_factor,
            fpr_adjustment=snapshot.fpr_factor,
            fairness_adjustment=getattr(snapshot, 'fairness_factor', 0.0),
            primary_reason=primary_reason,
            detailed_explanation=detailed_explanation,
            risk_context=risk_context,
            transaction_amount=txn.amount,
            transaction_time=txn.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            network_fraud_rate=network_fraud_rate,
            system_fpr=system_fpr,
            segment_fpr=segment_fpr,
            sensitivity_level=sensitivity_level,
            adjustment_magnitude=adjustment_magnitude
        )
        
        # Log decision
        self.decision_log.append(decision)
        
        return decision
    
    def _generate_primary_reason(
        self,
        primary_factor: str,
        snapshot: ThresholdSnapshot,
        txn: Transaction,
        network_fraud_rate: float,
        system_fpr: float,
        segment_fpr: Optional[float]
    ) -> str:
        """Generate the primary reason for threshold adjustment."""
        
        if primary_factor == "time":
            hour = txn.timestamp.hour
            if 22 <= hour or hour <= 6:
                return f"Late-night transaction at {hour:02d}:00 - increased sensitivity"
            elif 9 <= hour < 17:
                return f"Business hours transaction at {hour:02d}:00 - decreased sensitivity"
            else:
                return f"Standard hours transaction at {hour:02d}:00"
        
        elif primary_factor == "amount":
            if txn.amount > 1000:
                return f"High-value transaction (${txn.amount:,.2f}) - increased sensitivity"
            else:
                return f"Standard amount transaction (${txn.amount:,.2f})"
        
        elif primary_factor == "network":
            if network_fraud_rate > 0.05:
                return f"Network under attack ({network_fraud_rate*100:.1f}% fraud rate) - increased sensitivity"
            elif network_fraud_rate < 0.02:
                return f"Low network fraud rate ({network_fraud_rate*100:.1f}%) - decreased sensitivity"
            else:
                return f"Normal network fraud rate ({network_fraud_rate*100:.1f}%)"
        
        elif primary_factor == "fpr":
            if system_fpr > 0.10:
                return f"High false positive rate ({system_fpr*100:.1f}%) - decreased sensitivity to reduce false alarms"
            else:
                return f"Acceptable false positive rate ({system_fpr*100:.1f}%)"
        
        elif primary_factor == "fairness":
            if segment_fpr and system_fpr > 0:
                ratio = segment_fpr / system_fpr
                if ratio > 1.5:
                    return f"Bias mitigation active - segment FPR {ratio:.1f}x baseline, decreased sensitivity for fairness"
            return "Fairness adjustment applied"
        
        else:
            return "Standard threshold applied"
    
    def _generate_detailed_explanation(
        self,
        snapshot: ThresholdSnapshot,
        txn: Transaction,
        base_threshold: float,
        network_fraud_rate: float,
        system_fpr: float,
        segment_fpr: Optional[float]
    ) -> str:
        """Generate detailed multi-factor explanation."""
        
        parts = [f"Starting from base threshold of {base_threshold:.2f}:"]
        
        # Time factor
        if snapshot.time_factor != 0:
            hour = txn.timestamp.hour
            direction = "decreased" if snapshot.time_factor < 0 else "increased"
            parts.append(
                f"• Time adjustment ({snapshot.time_factor:+.2f}): {direction} threshold "
                f"because transaction occurred at {hour:02d}:00"
            )
        
        # Amount factor
        if snapshot.amount_factor != 0:
            direction = "decreased" if snapshot.amount_factor < 0 else "increased"
            parts.append(
                f"• Amount adjustment ({snapshot.amount_factor:+.2f}): {direction} threshold "
                f"for ${txn.amount:,.2f} transaction"
            )
        
        # Network factor
        if snapshot.network_factor != 0:
            direction = "decreased" if snapshot.network_factor < 0 else "increased"
            parts.append(
                f"• Network adjustment ({snapshot.network_factor:+.2f}): {direction} threshold "
                f"due to {network_fraud_rate*100:.1f}% network fraud rate"
            )
        
        # FPR factor
        if snapshot.fpr_factor != 0:
            direction = "decreased" if snapshot.fpr_factor < 0 else "increased"
            parts.append(
                f"• FPR adjustment ({snapshot.fpr_factor:+.2f}): {direction} threshold "
                f"due to {system_fpr*100:.1f}% false positive rate"
            )
        
        # Fairness factor
        fairness_factor = getattr(snapshot, 'fairness_factor', 0.0)
        if fairness_factor != 0 and segment_fpr and system_fpr > 0:
            ratio = segment_fpr / system_fpr
            parts.append(
                f"• Fairness adjustment ({fairness_factor:+.2f}): increased threshold "
                f"because segment FPR ({segment_fpr*100:.1f}%) is {ratio:.1f}x baseline ({system_fpr*100:.1f}%)"
            )
        
        parts.append(f"\nFinal threshold: {snapshot.threshold:.2f} (bounded to [0.2, 0.8])")
        
        return "\n".join(parts)
    
    def _generate_risk_context(
        self,
        txn: Transaction,
        network_fraud_rate: float,
        system_fpr: float,
        segment_fpr: Optional[float]
    ) -> str:
        """Generate risk context summary."""
        
        contexts = []
        
        # Time context
        hour = txn.timestamp.hour
        if 22 <= hour or hour <= 6:
            contexts.append("late-night hours (high-risk period)")
        elif 9 <= hour < 17:
            contexts.append("business hours (low-risk period)")
        
        # Amount context
        if txn.amount > 1000:
            contexts.append(f"high-value transaction (${txn.amount:,.2f})")
        elif txn.amount > 500:
            contexts.append(f"medium-value transaction (${txn.amount:,.2f})")
        
        # Network context
        if network_fraud_rate > 0.05:
            contexts.append(f"network under attack ({network_fraud_rate*100:.1f}% fraud rate)")
        elif network_fraud_rate < 0.02:
            contexts.append(f"low network fraud activity ({network_fraud_rate*100:.1f}%)")
        
        # FPR context
        if system_fpr > 0.10:
            contexts.append(f"high false positive rate ({system_fpr*100:.1f}%)")
        
        # Fairness context
        if segment_fpr and system_fpr > 0:
            ratio = segment_fpr / system_fpr
            if ratio > 1.5:
                contexts.append(f"segment bias detected ({ratio:.1f}x baseline FPR)")
        
        if contexts:
            return "Risk context: " + ", ".join(contexts)
        else:
            return "Risk context: normal operating conditions"
    
    def _determine_sensitivity_level(self, threshold: float) -> str:
        """Determine sensitivity level from threshold value."""
        if threshold < 0.4:
            return "HIGH"
        elif threshold < 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_adjustment_magnitude(self, adjustment: float) -> str:
        """Determine magnitude of adjustment."""
        abs_adj = abs(adjustment)
        if abs_adj >= 0.15:
            return "MAJOR"
        elif abs_adj >= 0.08:
            return "MODERATE"
        elif abs_adj >= 0.03:
            return "MINOR"
        else:
            return "NONE"
    
    def get_decision_by_id(self, decision_id: str) -> Optional[ThresholdDecision]:
        """Retrieve a specific decision by ID."""
        for decision in self.decision_log:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def get_recent_decisions(self, count: int = 50) -> List[Dict]:
        """Get recent threshold decisions for audit trail."""
        recent = self.decision_log[-count:] if len(self.decision_log) > count else self.decision_log
        
        # Convert to dict and handle datetime serialization
        decisions = []
        for d in reversed(recent):
            decision_dict = asdict(d)
            # Convert datetime to ISO format string
            if isinstance(decision_dict.get('timestamp'), datetime):
                decision_dict['timestamp'] = decision_dict['timestamp'].isoformat()
            decisions.append(decision_dict)
        
        return decisions
    
    def get_decision_summary(self) -> Dict:
        """Get summary statistics of threshold decisions."""
        if not self.decision_log:
            return {
                "total_decisions": 0,
                "avg_threshold": 0.5,
                "sensitivity_distribution": {},
                "adjustment_distribution": {}
            }
        
        sensitivity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        adjustment_counts = {"MAJOR": 0, "MODERATE": 0, "MINOR": 0, "NONE": 0}
        
        total_threshold = 0
        
        for decision in self.decision_log:
            sensitivity_counts[decision.sensitivity_level] += 1
            adjustment_counts[decision.adjustment_magnitude] += 1
            total_threshold += decision.final_threshold
        
        return {
            "total_decisions": len(self.decision_log),
            "avg_threshold": total_threshold / len(self.decision_log),
            "sensitivity_distribution": sensitivity_counts,
            "adjustment_distribution": adjustment_counts
        }
    
    def export_audit_trail(self, filepath: str) -> None:
        """Export complete audit trail to JSON file."""
        import json
        
        audit_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_decisions": len(self.decision_log),
            "decisions": [asdict(d) for d in self.decision_log]
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2, default=str)
