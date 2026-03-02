"""
FraudMesh Adaptive Threshold Engine

Dynamically adjusts fraud detection threshold based on context:
- Time of day
- Transaction amount
- Network-wide fraud rate
- False positive rate
"""

from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List

from models import Transaction, ThresholdSnapshot
from utils import clamp


class ThresholdEngine:
    """
    Adaptive threshold engine for context-aware fraud detection.
    
    Adjusts the fraud detection threshold based on multiple contextual
    factors to balance fraud detection recall and false positive rate.
    """
    
    def __init__(self, base_threshold: float = 0.5):
        """
        Initialize the threshold engine.
        
        Args:
            base_threshold: Base threshold value (default: 0.5)
        """
        self.base_threshold = base_threshold
        
        # Threshold history (last 60 minutes)
        self.threshold_history: deque = deque(maxlen=60)
        
        # Network fraud rate tracking (rolling window)
        self.fraud_rate_window: deque = deque(maxlen=100)
        
        # False positive rate tracking
        self.fpr_window: deque = deque(maxlen=100)
        
        # Current threshold
        self.current_threshold = base_threshold
        
        # Last update time
        self.last_update = datetime.now()
    
    def compute_adaptive_threshold(
        self,
        txn: Transaction,
        network_fraud_rate: float = 0.0,
        false_positive_rate: float = 0.0,
        segment_fpr: float = None,
        baseline_fpr: float = None
    ) -> float:
        """
        Compute context-aware adaptive threshold with fairness mitigation.
        
        Args:
            txn: Current transaction
            network_fraud_rate: Network-wide fraud rate (0-1)
            false_positive_rate: Current false positive rate (0-1)
            segment_fpr: False positive rate for this transaction's segment (optional)
            baseline_fpr: Baseline system-wide FPR (optional)
        
        Returns:
            Adaptive threshold value
        """
        threshold = self.base_threshold
        
        # Time-based adjustment
        time_factor = self._compute_time_factor(txn.timestamp)
        threshold += time_factor
        
        # Amount-based adjustment
        amount_factor = self._compute_amount_factor(txn.amount)
        threshold += amount_factor
        
        # Network fraud rate adjustment
        network_factor = self._compute_network_factor(network_fraud_rate)
        threshold += network_factor
        
        # False positive rate adjustment
        fpr_factor = self._compute_fpr_factor(false_positive_rate)
        threshold += fpr_factor
        
        # FAIRNESS MITIGATION: Adjust threshold for biased segments
        fairness_factor = self._compute_fairness_factor(segment_fpr, baseline_fpr)
        threshold += fairness_factor
        
        # Enforce bounds [0.2, 0.8]
        threshold = clamp(threshold, 0.2, 0.8)
        
        # Update current threshold
        self.current_threshold = threshold
        
        # Record snapshot
        snapshot = ThresholdSnapshot(
            timestamp=datetime.now(),
            threshold=threshold,
            time_factor=time_factor,
            amount_factor=amount_factor,
            network_factor=network_factor,
            fpr_factor=fpr_factor,
            fairness_factor=fairness_factor
        )
        self.threshold_history.append(snapshot)
        
        return threshold
    
    def _compute_time_factor(self, timestamp: datetime) -> float:
        """
        Compute time-based threshold adjustment.
        
        Lower threshold (more sensitive) during late-night hours.
        
        Args:
            timestamp: Transaction timestamp
        
        Returns:
            Threshold adjustment (-0.1 to 0.0)
        """
        hour = timestamp.hour
        
        # Late night (10 PM - 6 AM): more sensitive
        if 22 <= hour or hour <= 6:
            return -0.1
        
        # Business hours (9 AM - 5 PM): less sensitive
        elif 9 <= hour < 17:
            return 0.05
        
        # Other times: no adjustment
        else:
            return 0.0
    
    def _compute_amount_factor(self, amount: float) -> float:
        """
        Compute amount-based threshold adjustment.
        
        Lower threshold (more sensitive) for high-value transactions.
        
        Args:
            amount: Transaction amount
        
        Returns:
            Threshold adjustment (-0.05 to 0.0)
        """
        if amount > 1000:
            return -0.05
        else:
            return 0.0
    
    def _compute_network_factor(self, network_fraud_rate: float) -> float:
        """
        Compute network fraud rate adjustment.
        
        Lower threshold (more sensitive) when fraud rate is high.
        
        Args:
            network_fraud_rate: Network-wide fraud rate (0-1)
        
        Returns:
            Threshold adjustment (-0.15 to +0.05)
        """
        # Track fraud rate
        self.fraud_rate_window.append(network_fraud_rate)
        
        # Compute rolling average
        if len(self.fraud_rate_window) > 0:
            avg_fraud_rate = sum(self.fraud_rate_window) / len(self.fraud_rate_window)
        else:
            avg_fraud_rate = 0.0
        
        # High fraud rate (>5%): increase sensitivity
        if avg_fraud_rate > 0.05:
            return -0.15
        
        # Low fraud rate (<2%): decrease sensitivity
        elif avg_fraud_rate < 0.02:
            return 0.05
        
        # Normal range: no adjustment
        else:
            return 0.0
    
    def _compute_fpr_factor(self, false_positive_rate: float) -> float:
        """
        Compute false positive rate adjustment.
        
        Raise threshold (less sensitive) when FPR is high.
        
        Args:
            false_positive_rate: Current false positive rate (0-1)
        
        Returns:
            Threshold adjustment (0.0 to +0.05)
        """
        # Track FPR
        self.fpr_window.append(false_positive_rate)
        
        # Compute rolling average
        if len(self.fpr_window) > 0:
            avg_fpr = sum(self.fpr_window) / len(self.fpr_window)
        else:
            avg_fpr = 0.0
        
        # High FPR (>10%): decrease sensitivity
        if avg_fpr > 0.10:
            return 0.05
        
        # Normal FPR: no adjustment
        else:
            return 0.0
    
    def _compute_fairness_factor(
        self, 
        segment_fpr: float = None, 
        baseline_fpr: float = None
    ) -> float:
        """
        Compute fairness-based threshold adjustment.
        
        ACTIVE BIAS MITIGATION: Raise threshold (less sensitive) for segments
        with disproportionately high false positive rates.
        
        Args:
            segment_fpr: False positive rate for this transaction's segment
            baseline_fpr: Baseline system-wide FPR
        
        Returns:
            Threshold adjustment (0.0 to +0.10)
        """
        # If fairness metrics not provided, no adjustment
        if segment_fpr is None or baseline_fpr is None:
            return 0.0
        
        # If baseline is zero, no adjustment
        if baseline_fpr == 0:
            return 0.0
        
        # Compute FPR ratio
        fpr_ratio = segment_fpr / baseline_fpr
        
        # If segment FPR > 1.5x baseline: raise threshold to reduce false positives
        if fpr_ratio > 1.5:
            # Scale adjustment based on severity
            # 1.5x baseline = +0.03
            # 2.0x baseline = +0.06
            # 3.0x+ baseline = +0.10 (max)
            adjustment = min(0.10, (fpr_ratio - 1.0) * 0.03)
            return adjustment
        
        # Normal range: no adjustment
        else:
            return 0.0
    
    def update(self, was_fraud: bool) -> None:
        """
        Update threshold engine with alert outcome.
        
        Args:
            was_fraud: Whether the alert was actual fraud
        """
        # Track fraud rate
        self.fraud_rate_window.append(1.0 if was_fraud else 0.0)
        
        # Apply decay if window is full
        if len(self.fraud_rate_window) >= 100:
            # Decay older values
            decayed = [v * 0.95 for v in list(self.fraud_rate_window)[:50]]
            recent = list(self.fraud_rate_window)[50:]
            self.fraud_rate_window = deque(decayed + recent, maxlen=100)
    
    def get_threshold_factors(self) -> Dict:
        """
        Get current factors influencing the threshold.
        
        Returns:
            Dictionary with current adjustment factors
        """
        if len(self.threshold_history) > 0:
            latest = self.threshold_history[-1]
            return {
                "time_factor": latest.time_factor,
                "amount_factor": latest.amount_factor,
                "network_factor": latest.network_factor,
                "fpr_factor": latest.fpr_factor,
                "fairness_factor": getattr(latest, 'fairness_factor', 0.0),
                "current_threshold": latest.threshold
            }
        else:
            return {
                "time_factor": 0.0,
                "amount_factor": 0.0,
                "network_factor": 0.0,
                "fpr_factor": 0.0,
                "fairness_factor": 0.0,
                "current_threshold": self.base_threshold
            }
    
    def get_stats(self) -> Dict:
        """
        Get threshold engine statistics.
        
        Returns:
            Dictionary with current stats
        """
        # Compute current fraud rate
        if len(self.fraud_rate_window) > 0:
            fraud_rate = sum(self.fraud_rate_window) / len(self.fraud_rate_window)
        else:
            fraud_rate = 0.0
        
        # Compute current FPR
        if len(self.fpr_window) > 0:
            fpr = sum(self.fpr_window) / len(self.fpr_window)
        else:
            fpr = 0.0
        
        # Determine sensitivity level
        if self.current_threshold < 0.60:
            sensitivity = "HIGH"
        else:
            sensitivity = "NORMAL"
        
        return {
            "current_threshold": self.current_threshold,
            "fraud_rate": fraud_rate,
            "false_positive_rate": fpr,
            "sensitivity": sensitivity,
            "base_threshold": self.base_threshold
        }
    
    def get_threshold_history(self, minutes: int = 60) -> List[Dict]:
        """
        Get threshold history for visualization.
        
        Args:
            minutes: Number of minutes of history to return
        
        Returns:
            List of threshold snapshots
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        history = [
            {
                "timestamp": snapshot.timestamp.isoformat(),
                "threshold": snapshot.threshold,
                "time_factor": snapshot.time_factor,
                "amount_factor": snapshot.amount_factor,
                "network_factor": snapshot.network_factor,
                "fpr_factor": snapshot.fpr_factor,
                "fairness_factor": getattr(snapshot, 'fairness_factor', 0.0)
            }
            for snapshot in self.threshold_history
            if snapshot.timestamp > cutoff_time
        ]
        
        return history
