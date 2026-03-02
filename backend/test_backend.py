"""
Simple test script to verify backend components work correctly.
Run this before starting the full server.
"""

import sys
from datetime import datetime

print("🧪 Testing FraudMesh Backend Components...\n")

# Test 1: Import all modules
print("1️⃣  Testing imports...")
try:
    from models import Transaction, FraudScore, EntityType
    from data_simulator import TransactionSimulator
    from graph_engine import GraphEngine
    from fraud_detector import FraudDetector
    from threshold_engine import ThresholdEngine
    from fairness_monitor import FairnessMonitor
    from gnn_model import GNNModel
    from utils import haversine_distance, is_within_window
    print("   ✅ All imports successful\n")
except Exception as e:
    print(f"   ❌ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Transaction Simulator
print("2️⃣  Testing Transaction Simulator...")
try:
    simulator = TransactionSimulator(fraud_rate=0.05)
    txn = simulator.generate_transaction()
    print(f"   ✅ Generated transaction: {txn.id}")
    print(f"      Amount: ${txn.amount:.2f}, User: {txn.user_id}")
    print(f"      Fraud rings created: {len(simulator.get_fraud_rings())}\n")
except Exception as e:
    print(f"   ❌ Simulator failed: {e}\n")
    sys.exit(1)

# Test 3: Graph Engine
print("3️⃣  Testing Graph Engine...")
try:
    graph = GraphEngine()
    
    # Add some transactions
    for i in range(10):
        txn = simulator.generate_transaction()
        graph.add_transaction(txn)
    
    stats = graph.get_stats()
    print(f"   ✅ Graph created with {stats['node_count']} nodes, {stats['edge_count']} edges")
    
    # Test feature extraction
    features = graph.get_entity_features(txn.user_id)
    print(f"      Features: degree={features.degree}, velocity={features.transaction_velocity:.1f}\n")
except Exception as e:
    print(f"   ❌ Graph engine failed: {e}\n")
    sys.exit(1)

# Test 4: Fraud Detector
print("4️⃣  Testing Fraud Detector...")
try:
    detector = FraudDetector(graph)
    
    # Score a transaction
    txn = simulator.generate_transaction()
    graph.add_transaction(txn)
    fraud_score = detector.compute_fraud_score(txn)
    
    print(f"   ✅ Fraud score computed: {fraud_score.score:.3f}")
    print(f"      Risk level: {fraud_score.risk_level.value}")
    print(f"      Pattern: {fraud_score.fraud_pattern}")
    print(f"      Rules triggered: {len(fraud_score.triggered_rules)}\n")
except Exception as e:
    print(f"   ❌ Fraud detector failed: {e}\n")
    sys.exit(1)

# Test 5: Threshold Engine
print("5️⃣  Testing Threshold Engine...")
try:
    threshold_engine = ThresholdEngine(base_threshold=0.5)
    
    # Compute adaptive threshold
    adaptive_threshold = threshold_engine.compute_adaptive_threshold(
        txn,
        network_fraud_rate=0.05,
        false_positive_rate=0.08
    )
    
    stats = threshold_engine.get_stats()
    print(f"   ✅ Adaptive threshold: {adaptive_threshold:.3f}")
    print(f"      Sensitivity: {stats['sensitivity']}\n")
except Exception as e:
    print(f"   ❌ Threshold engine failed: {e}\n")
    sys.exit(1)

# Test 6: Fairness Monitor
print("6️⃣  Testing Fairness Monitor...")
try:
    fairness = FairnessMonitor()
    
    # Record some transactions
    for i in range(20):
        txn = simulator.generate_transaction()
        fairness.record_transaction(txn, was_flagged=(i % 5 == 0))
    
    metrics = fairness.compute_fairness_metrics()
    print(f"   ✅ Fairness metrics computed")
    print(f"      Baseline FPR: {metrics.baseline_fpr:.3f}")
    print(f"      Segments tracked: {len(metrics.segment_fprs)}\n")
except Exception as e:
    print(f"   ❌ Fairness monitor failed: {e}\n")
    sys.exit(1)

# Test 7: GNN Model
print("7️⃣  Testing GNN Model...")
try:
    gnn = GNNModel()
    
    # Extract features and predict
    features = graph.get_entity_features(txn.user_id)
    score = gnn.predict(txn, features)
    
    print(f"   ✅ GNN prediction: {score:.3f}\n")
except Exception as e:
    print(f"   ❌ GNN model failed: {e}\n")
    sys.exit(1)

# Test 8: Utility Functions
print("8️⃣  Testing Utility Functions...")
try:
    # Test haversine distance
    dist = haversine_distance((40.7128, -74.0060), (34.0522, -118.2437))
    print(f"   ✅ Haversine distance (NYC to LA): {dist:.0f} km")
    
    # Test time window
    now = datetime.now()
    is_within = is_within_window(now, minutes=10)
    print(f"      Time window check: {is_within}\n")
except Exception as e:
    print(f"   ❌ Utility functions failed: {e}\n")
    sys.exit(1)

# Test 9: Gemini Explainer (optional - requires API key)
print("9️⃣  Testing Gemini Explainer...")
try:
    from gemini_explainer import GeminiExplainer
    
    try:
        explainer = GeminiExplainer()
        print("   ✅ Gemini explainer initialized")
        print("      Note: Actual API calls will be made during runtime\n")
    except ValueError as e:
        print(f"   ⚠️  Gemini API key not set: {e}")
        print("      This is OK - fallback explanations will be used\n")
except Exception as e:
    print(f"   ❌ Gemini explainer failed: {e}\n")

# Final summary
print("=" * 60)
print("✅ All core backend components are working!")
print("=" * 60)
print("\n📝 Next steps:")
print("   1. Set your GEMINI_API_KEY in .env file")
print("   2. Run: uvicorn main:app --reload --port 8000")
print("   3. Visit: http://localhost:8000")
print("\n🚀 Ready to start FraudMesh!\n")
