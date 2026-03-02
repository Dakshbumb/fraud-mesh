"""
FraudMesh Fairness Monitor

Monitors false positive rates across user segments to ensure fairness.
Detects bias and generates fairness alerts when segments exceed thresholds.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

from models import (
    Transaction, FairnessMetrics, SegmentStats, BiasAlert
)
from utils import get_segment_id, extract_region_from_location


class FairnessMonitor:
    """
    Fairness monitoring system for bias detection.
    
    Tracks false positive rates across user segments (region, amount, age)
    and generates alerts when segments show disproportionate FPR.
    """
    
    def __init__(self):
        """Initialize the fairness monitor."""
        # Segment statistics
        self.segment_stats: Dict[str, SegmentStats] = {}
        
        # Alert history
        self.bias_alerts: List[BiasAlert] = []
        
        # Last computation time
        self.last_computation = datetime.now()
        
        # Computation interval (5 minutes)
        self.computation_interval = timedelta(minutes=5)
    
    def record_alert(
        self,
        txn: Transaction,
        fraud_score: float,
        is_true_positive: bool
    ) -> None:
        """
        Record an alert outcome for fairness tracking.
        
        Args:
            txn: Transaction that was flagged
            fraud_score: Fraud score assigned
            is_true_positive: Whether it was actual fraud
        """
        # Extract segments
        region = extract_region_from_location(txn.location)
        region_segment = get_segment_id("region", region)
        amount_segment = get_segment_id("amount", txn.amount)
        
        # For age, we'd need account creation date - use placeholder
        # In production, this would come from user profile
        age_segment = "age_unknown"
        
        segments = [region_segment, amount_segment, age_segment]
        
        # Update statistics for each segment
        for segment_id in segments:
            if segment_id not in self.segment_stats:
                self.segment_stats[segment_id] = SegmentStats(segment_id=segment_id)
            
            stats = self.segment_stats[segment_id]
            stats.total_transactions += 1
            stats.flagged_transactions += 1
            
            if is_true_positive:
                stats.true_positives += 1
            else:
                stats.false_positives += 1
            
            # Compute FPR
            if stats.flagged_transactions > 0:
                stats.false_positive_rate = stats.false_positives / stats.flagged_transactions
    
    def record_transaction(self, txn: Transaction, was_flagged: bool) -> None:
        """
        Record a transaction for segment tracking.
        
        Args:
            txn: Transaction
            was_flagged: Whether transaction was flagged
        """
        # Extract segments
        region = extract_region_from_location(txn.location)
        region_segment = get_segment_id("region", region)
        amount_segment = get_segment_id("amount", txn.amount)
        age_segment = "age_unknown"
        
        segments = [region_segment, amount_segment, age_segment]
        
        # Update total transaction counts
        for segment_id in segments:
            if segment_id not in self.segment_stats:
                self.segment_stats[segment_id] = SegmentStats(segment_id=segment_id)
            
            stats = self.segment_stats[segment_id]
            stats.total_transactions += 1
            
            if was_flagged:
                stats.flagged_transactions += 1
    
    def compute_fairness_metrics(self) -> FairnessMetrics:
        """
        Compute fairness metrics across all segments.
        
        Returns:
            FairnessMetrics object
        """
        # Only compute every 5 minutes to save resources
        if datetime.now() - self.last_computation < self.computation_interval:
            # Return cached metrics
            return self._get_cached_metrics()
        
        self.last_computation = datetime.now()
        
        # Compute baseline FPR (system-wide)
        total_flagged = sum(s.flagged_transactions for s in self.segment_stats.values())
        total_false_positives = sum(s.false_positives for s in self.segment_stats.values())
        
        if total_flagged > 0:
            baseline_fpr = total_false_positives / total_flagged
        else:
            baseline_fpr = 0.0
        
        # Compute FPR by segment
        segment_fprs = {}
        for segment_id, stats in self.segment_stats.items():
            if stats.flagged_transactions > 0:
                fpr = stats.false_positives / stats.flagged_transactions
                segment_fprs[segment_id] = fpr
            else:
                segment_fprs[segment_id] = 0.0
        
        # Identify biased segments (FPR > 2x baseline)
        biased_segments = []
        for segment_id, fpr in segment_fprs.items():
            if baseline_fpr > 0 and fpr > 2 * baseline_fpr:
                biased_segments.append(segment_id)
                
                # Generate bias alert
                alert = BiasAlert(
                    segment_id=segment_id,
                    segment_fpr=fpr,
                    baseline_fpr=baseline_fpr,
                    ratio=fpr / baseline_fpr if baseline_fpr > 0 else 0.0,
                    timestamp=datetime.now()
                )
                self.bias_alerts.append(alert)
        
        # Compute demographic parity score (max FPR / min FPR)
        if segment_fprs:
            fprs = [fpr for fpr in segment_fprs.values() if fpr > 0]
            if fprs:
                demographic_parity_score = max(fprs) / min(fprs)
            else:
                demographic_parity_score = 1.0
        else:
            demographic_parity_score = 1.0
        
        metrics = FairnessMetrics(
            timestamp=datetime.now(),
            baseline_fpr=baseline_fpr,
            segment_fprs=segment_fprs,
            demographic_parity_score=demographic_parity_score,
            biased_segments=biased_segments,
            segment_details=self.segment_stats.copy()
        )
        
        return metrics
    
    def _get_cached_metrics(self) -> FairnessMetrics:
        """Get cached fairness metrics."""
        # Compute baseline FPR
        total_flagged = sum(s.flagged_transactions for s in self.segment_stats.values())
        total_false_positives = sum(s.false_positives for s in self.segment_stats.values())
        
        if total_flagged > 0:
            baseline_fpr = total_false_positives / total_flagged
        else:
            baseline_fpr = 0.0
        
        # Compute FPR by segment
        segment_fprs = {}
        for segment_id, stats in self.segment_stats.items():
            if stats.flagged_transactions > 0:
                fpr = stats.false_positives / stats.flagged_transactions
                segment_fprs[segment_id] = fpr
            else:
                segment_fprs[segment_id] = 0.0
        
        # Identify biased segments
        biased_segments = [
            segment_id for segment_id, fpr in segment_fprs.items()
            if baseline_fpr > 0 and fpr > 2 * baseline_fpr
        ]
        
        # Compute demographic parity
        if segment_fprs:
            fprs = [fpr for fpr in segment_fprs.values() if fpr > 0]
            if fprs:
                demographic_parity_score = max(fprs) / min(fprs)
            else:
                demographic_parity_score = 1.0
        else:
            demographic_parity_score = 1.0
        
        return FairnessMetrics(
            timestamp=datetime.now(),
            baseline_fpr=baseline_fpr,
            segment_fprs=segment_fprs,
            demographic_parity_score=demographic_parity_score,
            biased_segments=biased_segments,
            segment_details=self.segment_stats.copy()
        )
    
    def detect_bias_alerts(self) -> List[BiasAlert]:
        """
        Get recent bias alerts.
        
        Returns:
            List of bias alerts from last hour
        """
        cutoff_time = datetime.now() - timedelta(hours=1)
        return [
            alert for alert in self.bias_alerts
            if alert.timestamp > cutoff_time
        ]
    
    def get_segment_details(self, segment_id: str) -> SegmentStats:
        """
        Get detailed statistics for a specific segment.
        
        Args:
            segment_id: Segment identifier
        
        Returns:
            SegmentStats object
        """
        return self.segment_stats.get(
            segment_id,
            SegmentStats(segment_id=segment_id)
        )
    
    def reset_stats(self) -> None:
        """Reset all statistics (for testing)."""
        self.segment_stats = {}
        self.bias_alerts = []
        self.last_computation = datetime.now()
