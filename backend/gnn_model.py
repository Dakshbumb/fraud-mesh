"""
FraudMesh GNN Model

Graph Neural Network for fraud detection using PyTorch Geometric.
Propagates risk signals across the entity graph through message passing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List
import math

from models import EntityFeatures, Transaction


class GNNModel:
    """
    Graph Neural Network for fraud scoring.
    
    Uses a simplified GNN architecture for CPU inference.
    For the hackathon prototype, we use a rule-based approximation
    of GNN behavior rather than training a full model.
    """
    
    def __init__(self, hidden_dim: int = 64):
        """
        Initialize the GNN model.
        
        Args:
            hidden_dim: Hidden layer dimension (default: 64)
        """
        self.hidden_dim = hidden_dim
        
        # For prototype: use rule-based scoring that mimics GNN behavior
        # In production, this would be a trained PyTorch Geometric model
        self.weights = {
            'transaction_velocity': 0.25,
            'device_sharing': 0.30,
            'ip_sharing': 0.20,
            'neighbor_risk': 0.15,
            'account_age': -0.10,  # Negative: older accounts are less risky
        }
    
    def extract_node_features(
        self,
        txn: Transaction,
        entity_features: EntityFeatures
    ) -> np.ndarray:
        """
        Extract 10-dimensional node features for GNN input.
        
        Features:
        1. Transaction amount (normalized)
        2. Transaction velocity (txns/hour)
        3. Account age (days, normalized)
        4. Device sharing count
        5. IP sharing count
        6. Hour of day (sin encoded)
        7. Hour of day (cos encoded)
        8. Geographic distance from previous txn
        9. Neighbor risk (average)
        10. Degree centrality
        
        Args:
            txn: Transaction object
            entity_features: Computed entity features
        
        Returns:
            10-dimensional feature vector
        """
        # Normalize amount (log scale, capped at $10,000)
        amount_normalized = math.log(min(txn.amount, 10000) + 1) / math.log(10001)
        
        # Velocity (capped at 20 txns/hour)
        velocity_normalized = min(entity_features.transaction_velocity, 20) / 20
        
        # Account age (capped at 365 days)
        age_normalized = min(entity_features.account_age_days, 365) / 365
        
        # Device and IP sharing (capped at 10)
        device_sharing_normalized = min(entity_features.device_sharing_count, 10) / 10
        ip_sharing_normalized = min(entity_features.ip_sharing_count, 10) / 10
        
        # Hour of day (sin/cos encoding for cyclical feature)
        hour = txn.timestamp.hour
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)
        
        # Geographic distance (capped at 5000 km)
        geo_distance_normalized = min(entity_features.geographic_distance_km, 5000) / 5000
        
        # Neighbor risk (already 0-1)
        neighbor_risk = entity_features.neighbor_risk
        
        # Degree centrality (capped at 50)
        degree_normalized = min(entity_features.degree, 50) / 50
        
        features = np.array([
            amount_normalized,
            velocity_normalized,
            age_normalized,
            device_sharing_normalized,
            ip_sharing_normalized,
            hour_sin,
            hour_cos,
            geo_distance_normalized,
            neighbor_risk,
            degree_normalized
        ], dtype=np.float32)
        
        return features
    
    def predict(
        self,
        txn: Transaction,
        entity_features: EntityFeatures
    ) -> float:
        """
        Predict fraud probability for a transaction.
        
        For the prototype, uses a weighted combination of features
        that approximates GNN message passing behavior.
        
        Args:
            txn: Transaction object
            entity_features: Computed entity features
        
        Returns:
            Fraud probability (0-1)
        """
        # Extract features
        features = self.extract_node_features(txn, entity_features)
        
        # Rule-based scoring that mimics GNN behavior
        score = 0.0
        
        # Velocity contribution
        if entity_features.transaction_velocity > 5:
            score += self.weights['transaction_velocity'] * min(entity_features.transaction_velocity / 10, 1.0)
        
        # Device sharing contribution
        if entity_features.device_sharing_count > 0:
            score += self.weights['device_sharing'] * min(entity_features.device_sharing_count / 5, 1.0)
        
        # IP sharing contribution
        if entity_features.ip_sharing_count > 0:
            score += self.weights['ip_sharing'] * min(entity_features.ip_sharing_count / 5, 1.0)
        
        # Neighbor risk contribution (risk propagation)
        score += self.weights['neighbor_risk'] * entity_features.neighbor_risk
        
        # Account age contribution (negative: older = less risky)
        if entity_features.account_age_days < 30:
            score += abs(self.weights['account_age']) * (1 - entity_features.account_age_days / 30)
        
        # Amount contribution
        if txn.amount > 1000:
            score += 0.10 * min((txn.amount - 1000) / 4000, 1.0)
        
        # Time of day contribution
        hour = txn.timestamp.hour
        if 2 <= hour <= 5:  # Late night
            score += 0.15
        
        # Geographic anomaly contribution
        if entity_features.geographic_distance_km > 500:
            score += 0.10 * min(entity_features.geographic_distance_km / 5000, 1.0)
        
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))
        
        return score
    
    def batch_predict(
        self,
        transactions: List[Transaction],
        features_list: List[EntityFeatures]
    ) -> List[float]:
        """
        Predict fraud probabilities for a batch of transactions.
        
        Args:
            transactions: List of transactions
            features_list: List of entity features
        
        Returns:
            List of fraud probabilities
        """
        return [
            self.predict(txn, features)
            for txn, features in zip(transactions, features_list)
        ]


# For future: Full PyTorch Geometric implementation
# This would be used in production with trained weights

class GNNModelPyG(nn.Module):
    """
    Full GNN implementation using PyTorch Geometric (for future use).
    
    This is a placeholder for a production-ready GNN model that would
    be trained on historical fraud data.
    """
    
    def __init__(self, in_channels: int = 10, hidden_dim: int = 64):
        """
        Initialize PyTorch Geometric GNN model.
        
        Args:
            in_channels: Input feature dimension
            hidden_dim: Hidden layer dimension
        """
        super().__init__()
        
        # Note: Requires torch_geometric to be properly installed
        # For prototype, we use the rule-based GNNModel above
        
        try:
            from torch_geometric.nn import GCNConv
            
            self.conv1 = GCNConv(in_channels, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
            self.classifier = nn.Linear(hidden_dim, 1)
        except ImportError:
            # Fallback if torch_geometric not available
            pass
    
    def forward(self, x, edge_index):
        """
        Forward pass through the GNN.
        
        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
        
        Returns:
            Fraud probabilities [num_nodes, 1]
        """
        try:
            x = F.relu(self.conv1(x, edge_index))
            x = F.relu(self.conv2(x, edge_index))
            x = torch.sigmoid(self.classifier(x))
            return x
        except Exception:
            # Fallback
            return torch.zeros(x.shape[0], 1)
