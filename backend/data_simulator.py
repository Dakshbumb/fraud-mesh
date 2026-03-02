"""
FraudMesh Transaction Simulator

Generates realistic financial transactions with embedded fraud patterns for demonstration.
Creates coordinated fraud rings, synthetic identities, and various fraud scenarios.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Set
import asyncio

from models import Transaction, FraudPattern, FraudRing


class TransactionSimulator:
    """
    Generates realistic transaction streams with embedded fraud patterns.
    
    Creates a pool of users, merchants, devices, and IPs, then generates
    transactions with approximately 5-8% fraud rate including coordinated
    fraud rings and various fraud pattern types.
    """
    
    def __init__(self, fraud_rate: float = 0.06):
        """
        Initialize the transaction simulator.
        
        Args:
            fraud_rate: Target fraud rate (default: 0.06 = 6%)
        """
        self.fraud_rate = fraud_rate
        
        # Entity pools
        self.users = [f"user_{i:04d}" for i in range(200)]  # U0000-U0199
        self.merchants = [f"merchant_{i:03d}" for i in range(50)]  # M000-M049
        self.devices = [f"device_{i:03d}" for i in range(80)]  # D000-D079
        self.ips = [f"192.168.{i//256}.{i%256}" for i in range(60)]  # 60 IPs
        
        # High-risk merchants (last 10)
        self.high_risk_merchants = self.merchants[-10:]
        self.low_risk_merchants = self.merchants[:-10]
        
        # Create 5 fraud rings
        self.fraud_rings: List[FraudRing] = []
        self._create_fraud_rings()
        
        # Track transaction history for velocity patterns
        self.user_transaction_history: dict = {user: [] for user in self.users}
        
        # Transaction counter
        self.transaction_count = 0
    
    def _create_fraud_rings(self):
        """Create 5 hidden fraud rings with shared devices and IPs."""
        for ring_id in range(5):
            # Each ring has 4 users sharing 1 device and 1 IP
            ring_users = random.sample(self.users, 4)
            shared_device = random.choice(self.devices)
            shared_ip = random.choice(self.ips)
            
            fraud_ring = FraudRing(
                ring_id=f"ring_{ring_id}",
                entity_ids=set(ring_users),
                shared_device=shared_device,
                shared_ip=shared_ip,
                detection_timestamp=datetime.now()
            )
            
            self.fraud_rings.append(fraud_ring)
    
    def _is_fraud_ring_member(self, user_id: str) -> Optional[FraudRing]:
        """Check if user is part of a fraud ring."""
        for ring in self.fraud_rings:
            if user_id in ring.entity_ids:
                return ring
        return None
    
    def _generate_location(self) -> tuple:
        """Generate random geographic coordinates."""
        # Simplified: generate coordinates in major regions
        regions = [
            (40.7128, -74.0060),   # New York
            (51.5074, -0.1278),    # London
            (35.6762, 139.6503),   # Tokyo
            (-23.5505, -46.6333),  # São Paulo
            (25.2048, 55.2708),    # Dubai
        ]
        
        base_lat, base_lon = random.choice(regions)
        # Add some random variation (±2 degrees)
        lat = base_lat + random.uniform(-2, 2)
        lon = base_lon + random.uniform(-2, 2)
        
        return (lat, lon)
    
    def _generate_normal_transaction(self) -> Transaction:
        """Generate a normal (non-fraudulent) transaction."""
        user_id = random.choice(self.users)
        merchant_id = random.choice(self.low_risk_merchants)
        device_id = random.choice(self.devices)
        ip_address = random.choice(self.ips)
        amount = random.uniform(5, 500)
        location = self._generate_location()
        channel = random.choice(["web", "mobile", "pos"])
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel=channel,
            is_fraudulent=False,
            fraud_pattern=None
        )
        
        return txn
    
    def _generate_account_takeover(self) -> Transaction:
        """Generate an Account Takeover fraud transaction."""
        user_id = random.choice(self.users)
        merchant_id = random.choice(self.high_risk_merchants)
        
        # New device and IP (different from user's normal pattern)
        device_id = random.choice(self.devices)
        ip_address = random.choice(self.ips)
        
        # High value transaction
        amount = random.uniform(800, 5000)
        
        # Unusual location
        location = self._generate_location()
        
        # Unusual time (late night)
        timestamp = datetime.now().replace(
            hour=random.randint(2, 5),
            minute=random.randint(0, 59)
        )
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=timestamp,
            location=location,
            channel="web",
            is_fraudulent=True,
            fraud_pattern=FraudPattern.ACCOUNT_TAKEOVER.value
        )
        
        return txn
    
    def _generate_synthetic_identity(self) -> Transaction:
        """Generate a Synthetic Identity Fraud transaction."""
        # New account (low user ID number suggests recent creation)
        user_id = random.choice(self.users[:20])  # First 20 users are "new"
        merchant_id = random.choice(self.high_risk_merchants)
        
        # Shared device with other new accounts
        device_id = random.choice(self.devices[:10])
        ip_address = random.choice(self.ips[:10])
        
        # High value transaction
        amount = random.uniform(1000, 5000)
        location = self._generate_location()
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel="web",
            is_fraudulent=True,
            fraud_pattern=FraudPattern.SYNTHETIC_IDENTITY.value
        )
        
        return txn
    
    def _generate_money_mule(self) -> Transaction:
        """Generate a Money Mule Operation transaction."""
        user_id = random.choice(self.users)
        merchant_id = random.choice(self.high_risk_merchants)
        device_id = random.choice(self.devices)
        ip_address = random.choice(self.ips)
        
        # Rapid high-value transfer
        amount = random.uniform(1500, 5000)
        location = self._generate_location()
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel="web",
            is_fraudulent=True,
            fraud_pattern=FraudPattern.MONEY_MULE.value
        )
        
        return txn
    
    def _generate_fraud_ring_transaction(self) -> Transaction:
        """Generate a Coordinated Fraud Ring transaction."""
        # Select a random fraud ring
        ring = random.choice(self.fraud_rings)
        user_id = random.choice(list(ring.entity_ids))
        merchant_id = random.choice(self.high_risk_merchants)
        
        # Use ring's shared device and IP
        device_id = ring.shared_device
        ip_address = ring.shared_ip
        
        # High value transaction
        amount = random.uniform(1000, 5000)
        location = self._generate_location()
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel="web",
            is_fraudulent=True,
            fraud_pattern=FraudPattern.FRAUD_RING.value
        )
        
        ring.transaction_count += 1
        return txn
    
    def _generate_card_not_present(self) -> Transaction:
        """Generate a Card-Not-Present Fraud transaction."""
        user_id = random.choice(self.users)
        merchant_id = random.choice(self.high_risk_merchants)
        device_id = random.choice(self.devices)
        ip_address = random.choice(self.ips)
        
        # High value online transaction
        amount = random.uniform(800, 3000)
        location = self._generate_location()
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel="web",  # Always web for CNP
            is_fraudulent=True,
            fraud_pattern=FraudPattern.CARD_NOT_PRESENT.value
        )
        
        return txn
    
    def _generate_velocity_abuse(self) -> Transaction:
        """Generate a Velocity Abuse fraud transaction."""
        user_id = random.choice(self.users)
        merchant_id = random.choice(self.high_risk_merchants)
        device_id = random.choice(self.devices)
        ip_address = random.choice(self.ips)
        
        # Multiple rapid transactions
        amount = random.uniform(500, 2000)
        location = self._generate_location()
        
        txn = Transaction(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            merchant_id=merchant_id,
            device_id=device_id,
            ip_address=ip_address,
            amount=round(amount, 2),
            timestamp=datetime.now(),
            location=location,
            channel=random.choice(["web", "mobile"]),
            is_fraudulent=True,
            fraud_pattern=FraudPattern.VELOCITY_ABUSE.value
        )
        
        return txn
    
    def generate_transaction(self, force_fraud: bool = False) -> Transaction:
        """
        Generate a single transaction (normal or fraudulent).
        
        Args:
            force_fraud: If True, always generate a fraudulent transaction
        
        Returns:
            Transaction object
        """
        self.transaction_count += 1
        
        # Decide if this should be fraudulent
        is_fraud = force_fraud or (random.random() < self.fraud_rate)
        
        if not is_fraud:
            txn = self._generate_normal_transaction()
        else:
            # Select fraud pattern type with balanced distribution for demo
            fraud_types = [
                (0.20, self._generate_fraud_ring_transaction),      # 20% - Fraud rings
                (0.20, self._generate_account_takeover),            # 20% - Account takeover
                (0.20, self._generate_synthetic_identity),          # 20% - Synthetic identity
                (0.15, self._generate_card_not_present),            # 15% - Card testing
                (0.15, self._generate_money_mule),                  # 15% - Money laundering
                (0.10, self._generate_velocity_abuse),              # 10% - Velocity abuse
            ]
            
            rand = random.random()
            cumulative = 0.0
            for probability, generator in fraud_types:
                cumulative += probability
                if rand < cumulative:
                    txn = generator()
                    break
            else:
                txn = self._generate_fraud_ring_transaction()
        
        # Track transaction history for velocity calculations
        self.user_transaction_history[txn.user_id].append(txn.timestamp)
        
        return txn
    
    async def stream_transactions(self, rate: int = 10, duration: Optional[int] = None):
        """
        Stream transactions at specified rate per second.
        
        Args:
            rate: Transactions per second (default: 10)
            duration: Duration in seconds (None = infinite)
        
        Yields:
            Transaction objects
        """
        interval = 1.0 / rate
        start_time = datetime.now()
        
        while True:
            if duration and (datetime.now() - start_time).seconds >= duration:
                break
            
            txn = self.generate_transaction()
            yield txn
            
            await asyncio.sleep(interval)
    
    def get_fraud_rings(self) -> List[FraudRing]:
        """Get all fraud rings."""
        return self.fraud_rings
    
    def get_stats(self) -> dict:
        """Get simulator statistics."""
        return {
            "total_transactions": self.transaction_count,
            "fraud_rings": len(self.fraud_rings),
            "users": len(self.users),
            "merchants": len(self.merchants),
            "devices": len(self.devices),
            "ips": len(self.ips),
            "target_fraud_rate": self.fraud_rate
        }
