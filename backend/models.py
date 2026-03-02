"""
FraudMesh Data Models

This module defines all data structures used throughout the FraudMesh system.
All models use dataclasses for type safety and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Set
from enum import Enum


class EntityType(str, Enum):
    """Types of entities in the graph"""
    USER = "user"
    MERCHANT = "merchant"
    DEVICE = "device"
    IP = "ip"


class EdgeType(str, Enum):
    """Types of relationships between entities"""
    TRANSACTION = "TRANSACTION"
    USES_DEVICE = "USES_DEVICE"
    SHARES_DEVICE = "SHARES_DEVICE"
    SAME_IP_SESSION = "SAME_IP_SESSION"


class FraudPattern(str, Enum):
    """Types of fraud patterns detected"""
    ACCOUNT_TAKEOVER = "Account Takeover"
    SYNTHETIC_IDENTITY = "Synthetic Identity Fraud"
    MONEY_MULE = "Money Mule Operation"
    FRAUD_RING = "Coordinated Fraud Ring"
    CARD_NOT_PRESENT = "Card-Not-Present Fraud"
    VELOCITY_ABUSE = "Velocity Abuse"
    UNKNOWN = "Unknown Pattern"


class RiskLevel(str, Enum):
    """Risk level classifications"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Recommendation(str, Enum):
    """Recommended actions for flagged transactions"""
    APPROVE = "Approve"
    REVIEW = "Review"
    BLOCK = "Block"
    ESCALATE = "Escalate"


class Confidence(str, Enum):
    """Confidence levels for fraud detection"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class Transaction:
    """
    Represents a financial transaction with entity identifiers and metadata.
    
    Attributes:
        id: Unique transaction identifier
        user_id: User account identifier
        merchant_id: Merchant identifier
        device_id: Device fingerprint hash
        ip_address: IPv4 address
        amount: Transaction amount in USD
        timestamp: Transaction timestamp
        location: Geographic coordinates (latitude, longitude)
        channel: Transaction channel (web/mobile/pos)
        currency: Currency code (default: USD)
        is_fraudulent: Ground truth fraud label (for evaluation)
        fraud_pattern: Type of fraud pattern if fraudulent
    """
    id: str
    user_id: str
    merchant_id: str
    device_id: str
    ip_address: str
    amount: float
    timestamp: datetime
    location: Tuple[float, float]  # (latitude, longitude)
    channel: str = "web"  # web, mobile, pos
    currency: str = "USD"
    is_fraudulent: bool = False
    fraud_pattern: Optional[str] = None


@dataclass
class EntityNode:
    """
    Represents a node in the entity relationship graph.
    
    Attributes:
        id: Unique entity identifier
        type: Entity type (user, merchant, device, ip)
        created_at: Entity creation timestamp
        transaction_count: Number of transactions involving this entity
        total_amount: Total transaction amount for this entity
        flagged: Whether entity is currently flagged for fraud
        in_fraud_ring: Whether entity is part of a detected fraud ring
        attributes: Flexible storage for entity-specific data
    """
    id: str
    type: EntityType
    created_at: datetime
    transaction_count: int = 0
    total_amount: float = 0.0
    flagged: bool = False
    in_fraud_ring: bool = False
    attributes: Dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    """
    Represents an edge (relationship) in the entity graph.
    
    Attributes:
        source: Source entity ID
        target: Target entity ID
        edge_type: Type of relationship
        weight: Connection strength or transaction amount
        timestamp: Edge creation timestamp
        attributes: Edge-specific metadata
    """
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict = field(default_factory=dict)


@dataclass
class EntityFeatures:
    """
    Graph-derived features for an entity used in fraud scoring.
    
    Attributes:
        degree: Number of graph connections
        transaction_velocity: Transactions per hour
        neighbor_risk: Average fraud score of connected entities
        account_age_days: Age of account in days
        device_sharing_count: Number of users sharing devices
        ip_sharing_count: Number of users sharing IPs
        geographic_distance_km: Distance from previous transaction
        avg_amount: Average transaction amount
        total_transactions: Total transaction count
        has_late_night_history: Whether entity has late-night activity history
    """
    degree: int = 0
    transaction_velocity: float = 0.0
    neighbor_risk: float = 0.0
    account_age_days: int = 0
    device_sharing_count: int = 0
    ip_sharing_count: int = 0
    geographic_distance_km: float = 0.0
    avg_amount: float = 0.0
    total_transactions: int = 0
    has_late_night_history: bool = False


@dataclass
class FraudScore:
    """
    Fraud scoring result for a transaction.
    
    Attributes:
        score: Final fraud probability (0-1)
        triggered_rules: List of rule names that fired
        gnn_contribution: GNN model output contribution
        structural_contribution: Structural rule contribution
        temporal_contribution: Temporal rule contribution
        fraud_pattern: Classified fraud pattern type
        entity_features: Graph features used in scoring
        risk_level: Risk level classification (LOW/MEDIUM/HIGH)
    """
    score: float
    triggered_rules: List[str] = field(default_factory=list)
    gnn_contribution: float = 0.0
    structural_contribution: float = 0.0
    temporal_contribution: float = 0.0
    fraud_pattern: str = FraudPattern.UNKNOWN.value
    entity_features: Optional[EntityFeatures] = None
    risk_level: RiskLevel = RiskLevel.LOW


@dataclass
class FraudExplanation:
    """
    Natural language explanation of fraud detection from Claude.
    
    Attributes:
        headline: One-sentence summary of fraud type
        narrative: 2-3 sentence detailed explanation
        fraud_pattern: Classified fraud pattern type
        key_signal: Most important risk factor
        recommendation: Recommended action (Approve/Review/Block)
        confidence: Confidence level (Low/Medium/High)
        generation_time_ms: Claude API latency in milliseconds
    """
    headline: str
    narrative: str
    fraud_pattern: str
    key_signal: str
    recommendation: str
    confidence: str
    generation_time_ms: int = 0


@dataclass
class FraudAlert:
    """
    Complete fraud alert with transaction, score, and explanation.
    
    Attributes:
        alert_id: Unique alert identifier
        transaction: The flagged transaction
        fraud_score: Fraud scoring result
        explanation: Natural language explanation (optional)
        timestamp: Alert generation timestamp
        adaptive_threshold: Threshold value at time of alert
        is_true_positive: Ground truth for fairness tracking (optional)
    """
    alert_id: str
    transaction: Transaction
    fraud_score: FraudScore
    explanation: Optional[FraudExplanation] = None
    timestamp: datetime = field(default_factory=datetime.now)
    adaptive_threshold: float = 0.5
    is_true_positive: Optional[bool] = None


@dataclass
class SystemStats:
    """
    System-wide metrics and statistics.
    
    Attributes:
        timestamp: Metrics collection timestamp
        transaction_rate: Transactions per second
        total_transactions: Total transactions processed
        flagged_transactions: Total transactions flagged
        fraud_rate: Percentage of flagged transactions
        avg_fraud_score: Average fraud score across all transactions
        active_entities: Total nodes in graph
        active_edges: Total edges in graph
        adaptive_threshold: Current adaptive threshold value
        avg_processing_latency_ms: Average processing latency
    """
    timestamp: datetime = field(default_factory=datetime.now)
    transaction_rate: float = 0.0
    total_transactions: int = 0
    flagged_transactions: int = 0
    fraud_rate: float = 0.0
    avg_fraud_score: float = 0.0
    active_entities: int = 0
    active_edges: int = 0
    adaptive_threshold: float = 0.5
    avg_processing_latency_ms: float = 0.0


@dataclass
class SegmentStats:
    """
    Statistics for a specific user segment.
    
    Attributes:
        segment_id: Segment identifier (e.g., "region_US", "amount_high")
        total_transactions: Total transactions in segment
        flagged_transactions: Flagged transactions in segment
        true_positives: Correctly flagged fraudulent transactions
        false_positives: Incorrectly flagged legitimate transactions
        false_positive_rate: FPR for this segment
    """
    segment_id: str
    total_transactions: int = 0
    flagged_transactions: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_positive_rate: float = 0.0


@dataclass
class FairnessMetrics:
    """
    Fairness monitoring metrics across user segments.
    
    Attributes:
        timestamp: Metrics collection timestamp
        baseline_fpr: System-wide false positive rate
        segment_fprs: FPR by segment ID
        demographic_parity_score: Max FPR / Min FPR ratio
        biased_segments: Segments with FPR > 2x baseline
        segment_details: Detailed statistics by segment
    """
    timestamp: datetime = field(default_factory=datetime.now)
    baseline_fpr: float = 0.0
    segment_fprs: Dict[str, float] = field(default_factory=dict)
    demographic_parity_score: float = 1.0
    biased_segments: List[str] = field(default_factory=list)
    segment_details: Dict[str, SegmentStats] = field(default_factory=dict)


@dataclass
class BiasAlert:
    """
    Alert for detected bias in fraud detection.
    
    Attributes:
        segment_id: Segment with detected bias
        segment_fpr: False positive rate for segment
        baseline_fpr: System-wide baseline FPR
        ratio: segment_fpr / baseline_fpr
        timestamp: Alert generation timestamp
    """
    segment_id: str
    segment_fpr: float
    baseline_fpr: float
    ratio: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ThresholdSnapshot:
    """
    Snapshot of adaptive threshold state at a point in time.
    
    Attributes:
        timestamp: Snapshot timestamp
        threshold: Threshold value
        time_factor: Time-based adjustment
        amount_factor: Amount-based adjustment
        network_factor: Network fraud rate adjustment
        fpr_factor: False positive rate adjustment
        fairness_factor: Fairness-based adjustment for bias mitigation
    """
    timestamp: datetime
    threshold: float
    time_factor: float = 0.0
    amount_factor: float = 0.0
    network_factor: float = 0.0
    fpr_factor: float = 0.0
    fairness_factor: float = 0.0


@dataclass
class FraudRing:
    """
    Represents a detected fraud ring (coordinated fraud operation).
    
    Attributes:
        ring_id: Unique ring identifier
        entity_ids: Set of entity IDs in the ring
        shared_device: Shared device ID (if device-based ring)
        shared_ip: Shared IP address (if IP-based ring)
        detection_timestamp: When ring was detected
        transaction_count: Number of transactions by ring members
    """
    ring_id: str
    entity_ids: Set[str]
    shared_device: Optional[str] = None
    shared_ip: Optional[str] = None
    detection_timestamp: datetime = field(default_factory=datetime.now)
    transaction_count: int = 0
