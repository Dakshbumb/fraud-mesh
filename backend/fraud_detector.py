"""
FraudMesh Fraud Detection Engine

Hybrid fraud scoring combining rule-based detection and GNN inference.
Classifies fraud patterns and assembles complete fraud case context.
"""

from typing import Dict, List, Tuple
from datetime import datetime

from models import (
    Transaction, FraudScore, EntityFeatures, FraudPattern,
    RiskLevel
)
from graph_engine import GraphEngine
from gnn_model import GNNModel


class RuleEngine:
    """
    Rule-based fraud detection engine.
    
    Evaluates structural and temporal rules to identify fraud signals.
    """
    
    def __init__(self):
        """Initialize the rule engine."""
        # Rule weights
        self.structural_rules = {
            'device_sharing_rule': 0.35,
            'ip_sharing_rule': 0.25,
            'fraud_ring_rule': 0.40,
            'new_account_rule': 0.15
        }
        
        self.temporal_rules = {
            'velocity_rule': 0.35,
            'timing_rule': 0.20,
            'geographic_rule': 0.30,
            'amount_rule': 0.15
        }
    
    def evaluate_structural_rules(
        self,
        txn: Transaction,
        features: EntityFeatures,
        in_fraud_ring: bool
    ) -> Tuple[float, List[str]]:
        """
        Evaluate structural fraud rules.
        
        Args:
            txn: Transaction object
            features: Entity features
            in_fraud_ring: Whether entity is in detected fraud ring
        
        Returns:
            Tuple of (max_score, triggered_rules)
        """
        scores = []
        triggered = []
        
        # Device sharing rule
        if features.device_sharing_count > 0:
            score = self.structural_rules['device_sharing_rule']
            scores.append(score)
            triggered.append(
                f"Device shared with {features.device_sharing_count} other users"
            )
        
        # IP sharing rule
        if features.ip_sharing_count > 0:
            score = self.structural_rules['ip_sharing_rule']
            scores.append(score)
            triggered.append(
                f"IP address shared with {features.ip_sharing_count} other users"
            )
        
        # Fraud ring rule
        if in_fraud_ring:
            score = self.structural_rules['fraud_ring_rule']
            scores.append(score)
            triggered.append("Entity is part of detected fraud ring")
        
        # New account rule
        if features.account_age_days < 7:
            score = self.structural_rules['new_account_rule']
            scores.append(score)
            triggered.append(
                f"New account with limited history ({features.account_age_days} days old)"
            )
        
        max_score = max(scores) if scores else 0.0
        return max_score, triggered
    
    def evaluate_temporal_rules(
        self,
        txn: Transaction,
        features: EntityFeatures
    ) -> Tuple[float, List[str]]:
        """
        Evaluate temporal fraud rules.
        
        Args:
            txn: Transaction object
            features: Entity features
        
        Returns:
            Tuple of (max_score, triggered_rules)
        """
        scores = []
        triggered = []
        
        # Velocity rule
        if features.transaction_velocity > 5:
            score = self.temporal_rules['velocity_rule']
            scores.append(score)
            triggered.append(
                f"High velocity: {features.transaction_velocity:.1f} transactions recently"
            )
        
        # Timing rule (late night activity)
        hour = txn.timestamp.hour
        if 2 <= hour <= 5 and not features.has_late_night_history:
            score = self.temporal_rules['timing_rule']
            scores.append(score)
            triggered.append(
                f"Unusual timing: transaction at {hour}:00 with no late-night history"
            )
        
        # Geographic rule
        if features.geographic_distance_km > 500:
            score = self.temporal_rules['geographic_rule']
            scores.append(score)
            triggered.append(
                f"Geographic anomaly: {features.geographic_distance_km:.0f}km from previous transaction"
            )
        
        # Amount rule
        if txn.amount > 1000:
            score = self.temporal_rules['amount_rule']
            scores.append(score)
            triggered.append(
                f"High value transaction: ${txn.amount:,.2f}"
            )
        
        max_score = max(scores) if scores else 0.0
        return max_score, triggered


class FraudDetector:
    """
    Main fraud detection engine combining rules and GNN.
    
    Computes fraud scores, classifies fraud patterns, and assembles
    complete fraud case context for explanation generation.
    """
    
    def __init__(self, graph_engine: GraphEngine):
        """
        Initialize the fraud detector.
        
        Args:
            graph_engine: GraphEngine instance
        """
        self.graph_engine = graph_engine
        self.rule_engine = RuleEngine()
        self.gnn_model = GNNModel()
        
        # Scoring weights
        self.gnn_weight = 0.4
        self.structural_weight = 0.3
        self.temporal_weight = 0.3
    
    def compute_fraud_score(self, txn: Transaction) -> FraudScore:
        """
        Compute fraud score for a transaction.
        
        Combines GNN inference, structural rules, and temporal rules
        into a final fraud score.
        
        Args:
            txn: Transaction to score
        
        Returns:
            FraudScore object with complete scoring details
        """
        # Get entity features from graph
        features = self.graph_engine.get_entity_features(txn.user_id)
        
        # Check if in fraud ring
        in_fraud_ring = self.graph_engine.is_in_fraud_ring(txn.user_id)
        
        # GNN inference
        gnn_contribution = self.gnn_model.predict(txn, features)
        
        # Evaluate structural rules
        structural_contribution, structural_rules = \
            self.rule_engine.evaluate_structural_rules(txn, features, in_fraud_ring)
        
        # Evaluate temporal rules
        temporal_contribution, temporal_rules = \
            self.rule_engine.evaluate_temporal_rules(txn, features)
        
        # Combine scores
        final_score = (
            self.gnn_weight * gnn_contribution +
            self.structural_weight * structural_contribution +
            self.temporal_weight * temporal_contribution
        )
        
        # Cap at 1.0
        final_score = min(1.0, final_score)
        
        # Combine triggered rules
        triggered_rules = structural_rules + temporal_rules
        
        # Classify fraud pattern
        fraud_pattern = self.classify_fraud_pattern(triggered_rules, features)
        
        # Determine risk level
        if final_score >= 0.7:
            risk_level = RiskLevel.HIGH
        elif final_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return FraudScore(
            score=final_score,
            triggered_rules=triggered_rules,
            gnn_contribution=gnn_contribution,
            structural_contribution=structural_contribution,
            temporal_contribution=temporal_contribution,
            fraud_pattern=fraud_pattern,
            entity_features=features,
            risk_level=risk_level
        )
    
    def classify_fraud_pattern(
        self,
        triggered_rules: List[str],
        features: EntityFeatures
    ) -> str:
        """
        Classify fraud pattern based on triggered rules and features.
        
        Args:
            triggered_rules: List of triggered rule descriptions
            features: Entity features
        
        Returns:
            Fraud pattern classification
        """
        rules_text = " ".join(triggered_rules).lower()
        
        # Account Takeover: velocity + timing + geographic anomalies
        if any(keyword in rules_text for keyword in ['velocity', 'timing', 'geographic']):
            if 'velocity' in rules_text and ('timing' in rules_text or 'geographic' in rules_text):
                return FraudPattern.ACCOUNT_TAKEOVER.value
        
        # Synthetic Identity: new account + device sharing
        if 'new account' in rules_text and 'device' in rules_text:
            return FraudPattern.SYNTHETIC_IDENTITY.value
        
        # Coordinated Fraud Ring: fraud ring detection
        if 'fraud ring' in rules_text:
            return FraudPattern.FRAUD_RING.value
        
        # Money Mule: high neighbor risk + velocity
        if features.neighbor_risk > 0.5 and features.transaction_velocity > 3:
            return FraudPattern.MONEY_MULE.value
        
        # Card-Not-Present: high amount + velocity
        if 'high value' in rules_text and 'velocity' in rules_text:
            return FraudPattern.CARD_NOT_PRESENT.value
        
        # Velocity Abuse: primarily velocity-based
        if 'velocity' in rules_text and len(triggered_rules) <= 2:
            return FraudPattern.VELOCITY_ABUSE.value
        
        # Default
        return FraudPattern.UNKNOWN.value
    
    def assemble_fraud_case_context(self, txn: Transaction, fraud_score: FraudScore) -> Dict:
        """
        Assemble complete fraud case context for explanation generation.
        
        Args:
            txn: Transaction object
            fraud_score: Computed fraud score
        
        Returns:
            Dictionary with complete fraud case context
        """
        # Get transaction history for user
        txn_history = self.graph_engine.transaction_history.get(txn.user_id, [])
        recent_transactions = [
            {
                "id": t.id,
                "amount": t.amount,
                "merchant_id": t.merchant_id,
                "timestamp": t.timestamp.isoformat(),
                "location": t.location
            }
            for t in txn_history[-10:]  # Last 10 transactions
        ]
        
        # Get neighborhood data
        neighborhood = self.graph_engine.get_neighborhood(txn.user_id, hops=2)
        
        # Check for fraud ring membership
        fraud_ring_detected = self.graph_engine.is_in_fraud_ring(txn.user_id)
        
        # Assemble context
        context = {
            "transaction": {
                "id": txn.id,
                "amount": txn.amount,
                "timestamp": txn.timestamp.isoformat(),
                "location": txn.location,
                "merchant_id": txn.merchant_id,
                "device_id": txn.device_id,
                "ip_address": txn.ip_address,
                "channel": txn.channel
            },
            "fraud_score": {
                "score": fraud_score.score,
                "triggered_rules": fraud_score.triggered_rules,
                "gnn_contribution": fraud_score.gnn_contribution,
                "structural_contribution": fraud_score.structural_contribution,
                "temporal_contribution": fraud_score.temporal_contribution,
                "fraud_pattern": fraud_score.fraud_pattern,
                "risk_level": fraud_score.risk_level.value
            },
            "entity_history": {
                "user_id": txn.user_id,
                "account_age_days": fraud_score.entity_features.account_age_days,
                "transaction_count": fraud_score.entity_features.total_transactions,
                "recent_transactions": recent_transactions
            },
            "graph_features": {
                "degree": fraud_score.entity_features.degree,
                "velocity": fraud_score.entity_features.transaction_velocity,
                "neighbor_risk": fraud_score.entity_features.neighbor_risk,
                "device_sharing_count": fraud_score.entity_features.device_sharing_count,
                "ip_sharing_count": fraud_score.entity_features.ip_sharing_count,
                "geographic_distance_km": fraud_score.entity_features.geographic_distance_km,
                "avg_amount": fraud_score.entity_features.avg_amount
            },
            "neighborhood": {
                "connected_entities": len(neighborhood["first_degree"]),
                "fraud_ring_detected": fraud_ring_detected,
                "first_degree_neighbors": neighborhood["first_degree"][:5],  # Limit to 5
                "second_degree_count": len(neighborhood["second_degree"])
            }
        }
        
        return context
