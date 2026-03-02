"""
FraudMesh Graph Engine

Manages the entity relationship graph using NetworkX.
Tracks entities (users, merchants, devices, IPs) and their relationships.
"""

import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque

from models import (
    Transaction, EntityNode, GraphEdge, EntityType, EdgeType,
    EntityFeatures, FraudRing
)
from utils import (
    haversine_distance, is_within_window, merge_overlapping_sets,
    calculate_velocity
)


class GraphEngine:
    """
    Manages the entity relationship graph for fraud detection.
    
    Uses NetworkX to maintain a graph of financial entities and their
    relationships. Provides methods for graph updates, feature extraction,
    fraud ring detection, and neighborhood queries.
    """
    
    def __init__(self):
        """Initialize the graph engine."""
        self.graph = nx.Graph()
        
        # Transaction history by entity
        self.transaction_history: Dict[str, List[Transaction]] = defaultdict(list)
        
        # Device and IP tracking
        self.device_to_users: Dict[str, Set[str]] = defaultdict(set)
        self.ip_to_users: Dict[str, Set[str]] = defaultdict(set)
        
        # Detected fraud rings
        self.detected_fraud_rings: List[FraudRing] = []
        
        # Last fraud ring detection time
        self.last_fraud_ring_detection = datetime.now()
        
        # Entity creation timestamps
        self.entity_created_at: Dict[str, datetime] = {}
    
    def add_transaction(self, txn: Transaction) -> None:
        """
        Add a transaction to the graph, creating/updating entities and edges.
        
        Args:
            txn: Transaction to add to the graph
        """
        # Create or update entity nodes
        self._ensure_entity_node(txn.user_id, EntityType.USER)
        self._ensure_entity_node(txn.merchant_id, EntityType.MERCHANT)
        self._ensure_entity_node(txn.device_id, EntityType.DEVICE)
        self._ensure_entity_node(f"ip_{txn.ip_address}", EntityType.IP)
        
        # Add transaction edge (user → merchant)
        self._add_edge(
            txn.user_id,
            txn.merchant_id,
            EdgeType.TRANSACTION,
            weight=txn.amount,
            timestamp=txn.timestamp,
            attributes={"transaction_id": txn.id}
        )
        
        # Add uses_device edge (user → device)
        self._add_edge(
            txn.user_id,
            txn.device_id,
            EdgeType.USES_DEVICE,
            timestamp=txn.timestamp
        )
        
        # Add same_ip_session edge (user → ip)
        self._add_edge(
            txn.user_id,
            f"ip_{txn.ip_address}",
            EdgeType.SAME_IP_SESSION,
            timestamp=txn.timestamp
        )
        
        # Track device and IP usage
        self.device_to_users[txn.device_id].add(txn.user_id)
        self.ip_to_users[txn.ip_address].add(txn.user_id)
        
        # Create shares_device edges if multiple users share device
        if len(self.device_to_users[txn.device_id]) > 1:
            self._create_shares_device_edges(txn.device_id)
        
        # Create same_ip_session edges if multiple users share IP
        if len(self.ip_to_users[txn.ip_address]) > 1:
            self._create_same_ip_edges(txn.ip_address)
        
        # Update transaction history
        self.transaction_history[txn.user_id].append(txn)
        
        # Keep only last 24 hours of transactions
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.transaction_history[txn.user_id] = [
            t for t in self.transaction_history[txn.user_id]
            if t.timestamp > cutoff_time
        ]
        
        # Update entity node attributes
        self._update_entity_stats(txn)
    
    def _ensure_entity_node(self, entity_id: str, entity_type: EntityType) -> None:
        """Create entity node if it doesn't exist."""
        if not self.graph.has_node(entity_id):
            created_at = self.entity_created_at.get(entity_id, datetime.now())
            self.entity_created_at[entity_id] = created_at
            
            self.graph.add_node(
                entity_id,
                type=entity_type.value,
                created_at=created_at,
                transaction_count=0,
                total_amount=0.0,
                flagged=False,
                in_fraud_ring=False,
                attributes={}
            )
    
    def _add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        weight: float = 1.0,
        timestamp: datetime = None,
        attributes: Dict = None
    ) -> None:
        """Add or update an edge in the graph."""
        if timestamp is None:
            timestamp = datetime.now()
        
        if attributes is None:
            attributes = {}
        
        if self.graph.has_edge(source, target):
            # Update existing edge
            edge_data = self.graph[source][target]
            edge_data['weight'] = edge_data.get('weight', 0) + weight
            edge_data['timestamp'] = timestamp
            edge_data['attributes'].update(attributes)
        else:
            # Create new edge
            self.graph.add_edge(
                source,
                target,
                edge_type=edge_type.value,
                weight=weight,
                timestamp=timestamp,
                attributes=attributes
            )
    
    def _create_shares_device_edges(self, device_id: str) -> None:
        """Create shares_device edges between users sharing a device."""
        users = list(self.device_to_users[device_id])
        
        # Create edges between all pairs of users
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                self._add_edge(
                    users[i],
                    users[j],
                    EdgeType.SHARES_DEVICE,
                    weight=0.7,  # High risk weight
                    attributes={"device_id": device_id}
                )
    
    def _create_same_ip_edges(self, ip_address: str) -> None:
        """Create same_ip_session edges between users sharing an IP."""
        users = list(self.ip_to_users[ip_address])
        
        # Only create edges if users accessed within 10-minute window
        recent_users = []
        now = datetime.now()
        
        for user_id in users:
            # Check if user has recent transaction from this IP
            recent_txns = [
                t for t in self.transaction_history[user_id]
                if t.ip_address == ip_address and is_within_window(t.timestamp, 10, now)
            ]
            if recent_txns:
                recent_users.append(user_id)
        
        # Create edges between recent users
        for i in range(len(recent_users)):
            for j in range(i + 1, len(recent_users)):
                self._add_edge(
                    recent_users[i],
                    recent_users[j],
                    EdgeType.SAME_IP_SESSION,
                    weight=0.5,
                    attributes={"ip_address": ip_address}
                )
    
    def _update_entity_stats(self, txn: Transaction) -> None:
        """Update entity node statistics."""
        if self.graph.has_node(txn.user_id):
            node_data = self.graph.nodes[txn.user_id]
            node_data['transaction_count'] += 1
            node_data['total_amount'] += txn.amount
            
            # Update location history
            if 'location_history' not in node_data['attributes']:
                node_data['attributes']['location_history'] = []
            node_data['attributes']['location_history'].append(txn.location)
            
            # Keep only last 10 locations
            if len(node_data['attributes']['location_history']) > 10:
                node_data['attributes']['location_history'] = \
                    node_data['attributes']['location_history'][-10:]
    
    def get_entity_features(self, entity_id: str) -> EntityFeatures:
        """
        Compute graph features for an entity.
        
        Args:
            entity_id: Entity identifier
        
        Returns:
            EntityFeatures object with computed features
        """
        if not self.graph.has_node(entity_id):
            return EntityFeatures()
        
        node_data = self.graph.nodes[entity_id]
        
        # Degree: number of connections
        degree = self.graph.degree(entity_id)
        
        # Transaction velocity
        txn_history = self.transaction_history.get(entity_id, [])
        timestamps = [t.timestamp for t in txn_history]
        transaction_velocity = calculate_velocity(timestamps, window_minutes=60)
        
        # Neighbor risk: average fraud score of connected entities
        neighbors = list(self.graph.neighbors(entity_id))
        neighbor_scores = [
            self.graph.nodes[n].get('fraud_score', 0.0)
            for n in neighbors
        ]
        neighbor_risk = sum(neighbor_scores) / len(neighbor_scores) if neighbor_scores else 0.0
        
        # Account age
        created_at = node_data.get('created_at', datetime.now())
        account_age_days = (datetime.now() - created_at).days
        
        # Device sharing count
        device_sharing_count = sum(
            1 for n in neighbors
            if self.graph.nodes[n].get('type') == EntityType.DEVICE.value
            and len(self.device_to_users.get(n, set())) > 1
        )
        
        # IP sharing count
        ip_sharing_count = sum(
            1 for n in neighbors
            if self.graph.nodes[n].get('type') == EntityType.IP.value
            and len(self.ip_to_users.get(n.replace('ip_', ''), set())) > 1
        )
        
        # Geographic distance from previous transaction
        location_history = node_data.get('attributes', {}).get('location_history', [])
        geographic_distance_km = 0.0
        if len(location_history) >= 2:
            geographic_distance_km = haversine_distance(
                location_history[-1],
                location_history[-2]
            )
        
        # Average amount
        total_amount = node_data.get('total_amount', 0.0)
        transaction_count = node_data.get('transaction_count', 0)
        avg_amount = total_amount / transaction_count if transaction_count > 0 else 0.0
        
        # Check for late-night history
        has_late_night_history = any(
            2 <= t.timestamp.hour <= 5
            for t in txn_history
        )
        
        return EntityFeatures(
            degree=degree,
            transaction_velocity=transaction_velocity,
            neighbor_risk=neighbor_risk,
            account_age_days=account_age_days,
            device_sharing_count=device_sharing_count,
            ip_sharing_count=ip_sharing_count,
            geographic_distance_km=geographic_distance_km,
            avg_amount=avg_amount,
            total_transactions=transaction_count,
            has_late_night_history=has_late_night_history
        )
    
    def detect_fraud_rings(self) -> List[FraudRing]:
        """
        Detect fraud rings (coordinated fraud operations).
        
        Returns:
            List of detected fraud rings
        """
        # Only run detection every 5 minutes to save resources
        if (datetime.now() - self.last_fraud_ring_detection).seconds < 300:
            return self.detected_fraud_rings
        
        self.last_fraud_ring_detection = datetime.now()
        fraud_rings = []
        
        # Device-based fraud rings
        for device_id, users in self.device_to_users.items():
            if len(users) >= 3:
                ring = FraudRing(
                    ring_id=f"device_ring_{device_id}",
                    entity_ids=users.copy(),
                    shared_device=device_id,
                    detection_timestamp=datetime.now()
                )
                fraud_rings.append(ring)
                
                # Mark users as in fraud ring
                for user_id in users:
                    if self.graph.has_node(user_id):
                        self.graph.nodes[user_id]['in_fraud_ring'] = True
        
        # IP-based fraud rings (within 10-minute window)
        now = datetime.now()
        for ip_address, users in self.ip_to_users.items():
            # Check for recent activity
            recent_users = []
            for user_id in users:
                recent_txns = [
                    t for t in self.transaction_history.get(user_id, [])
                    if t.ip_address == ip_address and is_within_window(t.timestamp, 10, now)
                ]
                if recent_txns:
                    recent_users.append(user_id)
            
            if len(recent_users) >= 3:
                ring = FraudRing(
                    ring_id=f"ip_ring_{ip_address}",
                    entity_ids=set(recent_users),
                    shared_ip=ip_address,
                    detection_timestamp=datetime.now()
                )
                fraud_rings.append(ring)
                
                # Mark users as in fraud ring
                for user_id in recent_users:
                    if self.graph.has_node(user_id):
                        self.graph.nodes[user_id]['in_fraud_ring'] = True
        
        # Merge overlapping rings
        if fraud_rings:
            entity_sets = [ring.entity_ids for ring in fraud_rings]
            merged_sets = merge_overlapping_sets(entity_sets)
            
            self.detected_fraud_rings = [
                FraudRing(
                    ring_id=f"merged_ring_{i}",
                    entity_ids=entity_set,
                    detection_timestamp=datetime.now()
                )
                for i, entity_set in enumerate(merged_sets)
            ]
        else:
            self.detected_fraud_rings = []
        
        return self.detected_fraud_rings
    
    def is_in_fraud_ring(self, entity_id: str) -> bool:
        """Check if entity is part of a detected fraud ring."""
        if not self.graph.has_node(entity_id):
            return False
        return self.graph.nodes[entity_id].get('in_fraud_ring', False)
    
    def get_neighborhood(self, entity_id: str, hops: int = 2) -> Dict:
        """
        Get N-hop neighborhood of an entity.
        
        Args:
            entity_id: Entity identifier
            hops: Number of hops (default: 2)
        
        Returns:
            Dictionary with first_degree and second_degree neighbors
        """
        if not self.graph.has_node(entity_id):
            return {"first_degree": [], "second_degree": []}
        
        # First-degree neighbors
        first_degree = []
        for neighbor in self.graph.neighbors(entity_id):
            edge_data = self.graph[entity_id][neighbor]
            first_degree.append({
                "id": neighbor,
                "type": self.graph.nodes[neighbor].get('type'),
                "edge_type": edge_data.get('edge_type'),
                "weight": edge_data.get('weight', 1.0)
            })
        
        # Second-degree neighbors (if hops >= 2)
        second_degree = []
        if hops >= 2:
            first_degree_ids = {n["id"] for n in first_degree}
            for first_neighbor in first_degree_ids:
                for second_neighbor in self.graph.neighbors(first_neighbor):
                    if second_neighbor != entity_id and second_neighbor not in first_degree_ids:
                        edge_data = self.graph[first_neighbor][second_neighbor]
                        second_degree.append({
                            "id": second_neighbor,
                            "type": self.graph.nodes[second_neighbor].get('type'),
                            "edge_type": edge_data.get('edge_type'),
                            "connection_path": [entity_id, first_neighbor, second_neighbor]
                        })
        
        return {
            "first_degree": first_degree,
            "second_degree": second_degree
        }
    
    def get_graph_data_for_frontend(self, max_nodes: int = 150, max_edges: int = 300) -> Dict:
        """
        Get graph data formatted for frontend visualization.
        
        Args:
            max_nodes: Maximum number of nodes to return
            max_edges: Maximum number of edges to return
        
        Returns:
            Dictionary with nodes and edges arrays
        """
        # Get most recent/active nodes
        nodes_data = []
        for node_id, node_attrs in self.graph.nodes(data=True):
            nodes_data.append({
                "id": node_id,
                "type": node_attrs.get('type'),
                "transaction_count": node_attrs.get('transaction_count', 0),
                "flagged": node_attrs.get('flagged', False),
                "in_fraud_ring": node_attrs.get('in_fraud_ring', False),
                "degree": self.graph.degree(node_id)
            })
        
        # Sort by transaction count and limit
        nodes_data.sort(key=lambda x: x['transaction_count'], reverse=True)
        nodes_data = nodes_data[:max_nodes]
        node_ids = {n['id'] for n in nodes_data}
        
        # Get edges between included nodes
        edges_data = []
        for source, target, edge_attrs in self.graph.edges(data=True):
            if source in node_ids and target in node_ids:
                edges_data.append({
                    "source": source,
                    "target": target,
                    "edge_type": edge_attrs.get('edge_type'),
                    "weight": edge_attrs.get('weight', 1.0)
                })
        
        # Limit edges
        edges_data = edges_data[:max_edges]
        
        return {
            "nodes": nodes_data,
            "links": edges_data,  # Changed from "edges" to "links" for D3.js compatibility
            "metadata": {
                "node_count": len(nodes_data),
                "edge_count": len(edges_data),
                "fraud_ring_count": len(self.detected_fraud_rings)
            }
        }
    
    def prune_old_edges(self, hours: int = 24) -> int:
        """
        Remove edges older than specified hours.
        
        Args:
            hours: Age threshold in hours
        
        Returns:
            Number of edges removed
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        edges_to_remove = []
        
        for source, target, edge_attrs in self.graph.edges(data=True):
            timestamp = edge_attrs.get('timestamp')
            if timestamp and timestamp < cutoff_time:
                edges_to_remove.append((source, target))
        
        for source, target in edges_to_remove:
            self.graph.remove_edge(source, target)
        
        return len(edges_to_remove)
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "fraud_rings": len(self.detected_fraud_rings),
            "users_tracked": len([
                n for n, d in self.graph.nodes(data=True)
                if d.get('type') == EntityType.USER.value
            ]),
            "devices_tracked": len(self.device_to_users),
            "ips_tracked": len(self.ip_to_users)
        }
    
    def get_fraud_rings_details(self) -> List[Dict]:
        """Get detailed information about detected fraud rings."""
        rings_data = []
        for ring in self.detected_fraud_rings:
            rings_data.append({
                "ring_id": ring.ring_id,
                "members": list(ring.entity_ids),
                "member_count": len(ring.entity_ids),
                "detection_time": ring.detection_timestamp.isoformat(),
                "shared_device": ring.shared_device,
                "shared_ip": ring.shared_ip,
                "transaction_count": ring.transaction_count
            })
        return rings_data
