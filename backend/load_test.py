"""
FraudMesh Load Test & Scalability Benchmark
============================================

Generates comprehensive scalability evidence for the hackathon track:
"Adaptive Real-Time Fraud Detection Using Graph-Based Behavioral Analytics"

Tests:
  1. Transaction Processing Throughput (txn/s at increasing loads)
  2. End-to-End Latency Percentiles (p50, p95, p99)
  3. Graph Engine Scalability (node/edge growth over time)
  4. Fraud Detection Pipeline Latency Breakdown
  5. Memory Profile Under Load

Run:
  cd backend && python load_test.py
"""

import time
import sys
import os
import statistics
import tracemalloc
from datetime import datetime, timedelta
from collections import defaultdict

# Ensure local imports work
sys.path.insert(0, os.path.dirname(__file__))

from data_simulator import TransactionSimulator
from graph_engine import GraphEngine
from fraud_detector import FraudDetector
from threshold_engine import ThresholdEngine
from fairness_monitor import FairnessMonitor
from gnn_model import GNNModel
from utils import extract_region_from_location


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def percentile(data, p):
    """Compute p-th percentile of a list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    d = k - f
    return sorted_data[f] + d * (sorted_data[c] - sorted_data[f])


def fmt_ms(seconds):
    """Format seconds as milliseconds string."""
    return f"{seconds * 1000:.2f}ms"


def print_header(title):
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_result(label, value, unit=""):
    print(f"  {label:<40} {value:>12} {unit}")


# ──────────────────────────────────────────────────────────────────────
# Test 1: Transaction Processing Throughput
# ──────────────────────────────────────────────────────────────────────

def test_throughput():
    """
    Measure sustained transaction processing throughput.
    Processes batches of increasing size and measures txn/s.
    """
    print_header("TEST 1: Transaction Processing Throughput")

    batch_sizes = [100, 500, 1000, 2000, 5000]
    results = []

    for batch_size in batch_sizes:
        # Fresh components for each batch
        simulator = TransactionSimulator(fraud_rate=0.06)
        graph = GraphEngine()
        detector = FraudDetector(graph)
        threshold = ThresholdEngine(base_threshold=0.5)
        fairness = FairnessMonitor()

        # Generate transactions first (don't count generation time)
        transactions = [simulator.generate_transaction() for _ in range(batch_size)]

        # Time the processing pipeline
        start = time.perf_counter()

        for txn in transactions:
            # Full pipeline: graph → detect → threshold → fairness
            graph.add_transaction(txn)
            fraud_score = detector.compute_fraud_score(txn)
            adaptive_threshold = threshold.compute_adaptive_threshold(
                txn,
                network_fraud_rate=0.05,
                false_positive_rate=0.08
            )
            is_flagged = fraud_score.score > adaptive_threshold
            fairness.record_transaction(txn, was_flagged=is_flagged)

        elapsed = time.perf_counter() - start
        throughput = batch_size / elapsed
        avg_latency = elapsed / batch_size

        results.append({
            "batch_size": batch_size,
            "elapsed": elapsed,
            "throughput": throughput,
            "avg_latency": avg_latency,
            "graph_nodes": graph.graph.number_of_nodes(),
            "graph_edges": graph.graph.number_of_edges()
        })

        print_result(
            f"  {batch_size:,} transactions",
            f"{throughput:,.0f}",
            f"txn/s  ({fmt_ms(avg_latency)} avg)"
        )

    return results


# ──────────────────────────────────────────────────────────────────────
# Test 2: End-to-End Latency Percentiles
# ──────────────────────────────────────────────────────────────────────

def test_latency_percentiles():
    """
    Measure per-transaction latency distribution across 2,000 transactions.
    Reports p50, p90, p95, p99, and max.
    """
    print_header("TEST 2: End-to-End Latency Percentiles (2,000 txns)")

    simulator = TransactionSimulator(fraud_rate=0.06)
    graph = GraphEngine()
    detector = FraudDetector(graph)
    threshold = ThresholdEngine(base_threshold=0.5)
    fairness = FairnessMonitor()

    latencies = []
    num_transactions = 2000

    for _ in range(num_transactions):
        txn = simulator.generate_transaction()

        start = time.perf_counter()

        graph.add_transaction(txn)
        fraud_score = detector.compute_fraud_score(txn)
        adaptive_threshold = threshold.compute_adaptive_threshold(
            txn, network_fraud_rate=0.05, false_positive_rate=0.08
        )
        is_flagged = fraud_score.score > adaptive_threshold
        fairness.record_transaction(txn, was_flagged=is_flagged)

        elapsed = time.perf_counter() - start
        latencies.append(elapsed)

    print_result("p50 (median)", fmt_ms(percentile(latencies, 50)))
    print_result("p90", fmt_ms(percentile(latencies, 90)))
    print_result("p95", fmt_ms(percentile(latencies, 95)))
    print_result("p99", fmt_ms(percentile(latencies, 99)))
    print_result("Max", fmt_ms(max(latencies)))
    print_result("Min", fmt_ms(min(latencies)))
    print_result("Mean", fmt_ms(statistics.mean(latencies)))
    print_result("Std Dev", fmt_ms(statistics.stdev(latencies)))

    return {
        "count": num_transactions,
        "p50": percentile(latencies, 50),
        "p90": percentile(latencies, 90),
        "p95": percentile(latencies, 95),
        "p99": percentile(latencies, 99),
        "max": max(latencies),
        "min": min(latencies),
        "mean": statistics.mean(latencies),
        "stdev": statistics.stdev(latencies),
    }


# ──────────────────────────────────────────────────────────────────────
# Test 3: Pipeline Stage Latency Breakdown
# ──────────────────────────────────────────────────────────────────────

def test_pipeline_breakdown():
    """
    Break down latency by pipeline stage over 1,000 transactions.
    Stages: Graph Update → Feature Extraction → Scoring → Threshold → Fairness
    """
    print_header("TEST 3: Pipeline Stage Latency Breakdown (1,000 txns)")

    simulator = TransactionSimulator(fraud_rate=0.06)
    graph = GraphEngine()
    detector = FraudDetector(graph)
    threshold = ThresholdEngine(base_threshold=0.5)
    fairness = FairnessMonitor()

    stage_times = defaultdict(list)
    num = 1000

    for _ in range(num):
        txn = simulator.generate_transaction()

        # Stage 1: Graph update
        t0 = time.perf_counter()
        graph.add_transaction(txn)
        t1 = time.perf_counter()
        stage_times["graph_update"].append(t1 - t0)

        # Stage 2: Feature extraction + GNN scoring + rule evaluation
        t2 = time.perf_counter()
        fraud_score = detector.compute_fraud_score(txn)
        t3 = time.perf_counter()
        stage_times["fraud_scoring"].append(t3 - t2)

        # Stage 3: Adaptive threshold
        t4 = time.perf_counter()
        adaptive_threshold = threshold.compute_adaptive_threshold(
            txn, network_fraud_rate=0.05, false_positive_rate=0.08
        )
        t5 = time.perf_counter()
        stage_times["threshold"].append(t5 - t4)

        # Stage 4: Fairness tracking
        t6 = time.perf_counter()
        is_flagged = fraud_score.score > adaptive_threshold
        fairness.record_transaction(txn, was_flagged=is_flagged)
        t7 = time.perf_counter()
        stage_times["fairness"].append(t7 - t6)

    total_avg = 0
    for stage, times in stage_times.items():
        avg = statistics.mean(times)
        total_avg += avg
        pct = 0
        print_result(
            f"  {stage}",
            fmt_ms(avg),
            f"avg  (p99: {fmt_ms(percentile(times, 99))})"
        )

    print("  " + "-" * 60)
    print_result("  TOTAL pipeline", fmt_ms(total_avg), "avg")

    return {
        stage: {
            "mean": statistics.mean(times),
            "p99": percentile(times, 99),
        }
        for stage, times in stage_times.items()
    }


# ──────────────────────────────────────────────────────────────────────
# Test 4: Graph Scalability (Node/Edge Growth)
# ──────────────────────────────────────────────────────────────────────

def test_graph_scalability():
    """
    Measure graph size growth and per-transaction latency as graph scales.
    Shows that latency remains bounded even as graph grows.
    """
    print_header("TEST 4: Graph Scalability — Latency vs Graph Size")

    simulator = TransactionSimulator(fraud_rate=0.06)
    graph = GraphEngine()
    detector = FraudDetector(graph)

    checkpoints = [100, 250, 500, 1000, 2000, 3000, 5000]
    current_checkpoint = 0
    results = []
    latencies_window = []

    print(f"  {'Txns':>8}  {'Nodes':>8}  {'Edges':>8}  {'Avg Latency':>14}  {'p99 Latency':>14}")
    print("  " + "-" * 60)

    for i in range(1, max(checkpoints) + 1):
        txn = simulator.generate_transaction()

        start = time.perf_counter()
        graph.add_transaction(txn)
        fraud_score = detector.compute_fraud_score(txn)
        elapsed = time.perf_counter() - start

        latencies_window.append(elapsed)

        if current_checkpoint < len(checkpoints) and i == checkpoints[current_checkpoint]:
            nodes = graph.graph.number_of_nodes()
            edges = graph.graph.number_of_edges()
            avg_lat = statistics.mean(latencies_window[-100:])
            p99_lat = percentile(latencies_window[-100:], 99)

            print(f"  {i:>8,}  {nodes:>8,}  {edges:>8,}  {fmt_ms(avg_lat):>14}  {fmt_ms(p99_lat):>14}")

            results.append({
                "transactions": i,
                "nodes": nodes,
                "edges": edges,
                "avg_latency": avg_lat,
                "p99_latency": p99_lat
            })

            current_checkpoint += 1

    return results


# ──────────────────────────────────────────────────────────────────────
# Test 5: Fraud Ring Detection Scalability
# ──────────────────────────────────────────────────────────────────────

def test_fraud_ring_detection():
    """
    Measure fraud ring detection performance with increasing graph complexity.
    """
    print_header("TEST 5: Fraud Ring Detection Performance")

    simulator = TransactionSimulator(fraud_rate=0.10)  # Higher fraud rate for ring creation
    graph = GraphEngine()

    # Process transactions to build up graph
    for _ in range(2000):
        txn = simulator.generate_transaction()
        graph.add_transaction(txn)

    # Force fraud ring detection to be eligible
    graph.last_fraud_ring_detection = datetime.now() - timedelta(minutes=10)

    # Time the fraud ring detection
    start = time.perf_counter()
    rings = graph.detect_fraud_rings()
    elapsed = time.perf_counter() - start

    stats = graph.get_stats()

    print_result("Graph nodes", f"{stats['node_count']:,}")
    print_result("Graph edges", f"{stats['edge_count']:,}")
    print_result("Fraud rings detected", f"{len(rings)}")
    print_result("Detection latency", fmt_ms(elapsed))

    # Test ring details retrieval
    start2 = time.perf_counter()
    details = graph.get_fraud_rings_details()
    elapsed2 = time.perf_counter() - start2

    print_result("Ring details retrieval", fmt_ms(elapsed2))

    total_members = sum(d["member_count"] for d in details)
    print_result("Total ring members", f"{total_members}")

    return {
        "nodes": stats["node_count"],
        "edges": stats["edge_count"],
        "rings": len(rings),
        "detection_latency": elapsed,
        "details_latency": elapsed2,
    }


# ──────────────────────────────────────────────────────────────────────
# Test 6: Memory Profile Under Load
# ──────────────────────────────────────────────────────────────────────

def test_memory_profile():
    """
    Track memory growth while processing 5,000 transactions.
    """
    print_header("TEST 6: Memory Profile Under Load")

    tracemalloc.start()

    simulator = TransactionSimulator(fraud_rate=0.06)
    graph = GraphEngine()
    detector = FraudDetector(graph)
    threshold = ThresholdEngine(base_threshold=0.5)
    fairness = FairnessMonitor()

    checkpoints = [0, 500, 1000, 2000, 3000, 5000]
    current_checkpoint = 1
    results = []

    snapshot_initial = tracemalloc.take_snapshot()
    initial_mem = sum(stat.size for stat in snapshot_initial.statistics('filename'))

    print(f"  {'Txns':>8}  {'Memory (MB)':>14}  {'Delta (MB)':>12}")
    print("  " + "-" * 40)
    print(f"  {0:>8,}  {initial_mem / 1024 / 1024:>14.2f}  {'baseline':>12}")

    for i in range(1, max(checkpoints) + 1):
        txn = simulator.generate_transaction()
        graph.add_transaction(txn)
        fraud_score = detector.compute_fraud_score(txn)
        adaptive_threshold = threshold.compute_adaptive_threshold(
            txn, network_fraud_rate=0.05, false_positive_rate=0.08
        )
        is_flagged = fraud_score.score > adaptive_threshold
        fairness.record_transaction(txn, was_flagged=is_flagged)

        if current_checkpoint < len(checkpoints) and i == checkpoints[current_checkpoint]:
            snapshot = tracemalloc.take_snapshot()
            current_mem = sum(stat.size for stat in snapshot.statistics('filename'))
            delta = current_mem - initial_mem

            print(f"  {i:>8,}  {current_mem / 1024 / 1024:>14.2f}  {delta / 1024 / 1024:>+12.2f}")

            results.append({
                "transactions": i,
                "memory_mb": current_mem / 1024 / 1024,
                "delta_mb": delta / 1024 / 1024,
            })

            current_checkpoint += 1

    tracemalloc.stop()
    return results


# ──────────────────────────────────────────────────────────────────────
# Generate Summary Report
# ──────────────────────────────────────────────────────────────────────

def generate_report(throughput_results, latency_results, pipeline_results,
                     scalability_results, ring_results, memory_results):
    """Generate a markdown report of load test results."""

    report_path = os.path.join(os.path.dirname(__file__), '..', 'LOAD_TEST_RESULTS.md')

    peak_throughput = max(r["throughput"] for r in throughput_results)
    final_scale = scalability_results[-1] if scalability_results else {}

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# FraudMesh — Load Test & Scalability Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Platform:** Python {sys.version.split()[0]}, {sys.platform}  \n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write("| Metric | Result |\n")
        f.write("|--------|--------|\n")
        f.write(f"| Peak throughput | **{peak_throughput:,.0f} txn/s** |\n")
        f.write(f"| p50 latency | **{latency_results['p50']*1000:.2f}ms** |\n")
        f.write(f"| p95 latency | **{latency_results['p95']*1000:.2f}ms** |\n")
        f.write(f"| p99 latency | **{latency_results['p99']*1000:.2f}ms** |\n")
        f.write(f"| Max graph size tested | **{final_scale.get('nodes', 'N/A'):,} nodes / {final_scale.get('edges', 'N/A'):,} edges** |\n")
        f.write(f"| Fraud rings detected | **{ring_results['rings']}** (in {ring_results['detection_latency']*1000:.2f}ms) |\n")
        if memory_results:
            f.write(f"| Memory at 5K txns | **{memory_results[-1]['memory_mb']:.1f} MB** ({memory_results[-1]['delta_mb']:+.1f} MB from baseline) |\n")
        f.write("\n")

        # Throughput
        f.write("## 1. Transaction Processing Throughput\n\n")
        f.write("| Batch Size | Throughput (txn/s) | Avg Latency | Graph Nodes | Graph Edges |\n")
        f.write("|------------|-------------------|-------------|-------------|-------------|\n")
        for r in throughput_results:
            f.write(f"| {r['batch_size']:,} | {r['throughput']:,.0f} | {r['avg_latency']*1000:.2f}ms | {r['graph_nodes']:,} | {r['graph_edges']:,} |\n")
        f.write("\n")

        # Latency
        f.write("## 2. Latency Distribution (2,000 transactions)\n\n")
        f.write("| Percentile | Latency |\n")
        f.write("|------------|--------|\n")
        for p_label, p_key in [("p50", "p50"), ("p90", "p90"), ("p95", "p95"), ("p99", "p99"), ("Max", "max")]:
            f.write(f"| {p_label} | {latency_results[p_key]*1000:.2f}ms |\n")
        f.write(f"\nMean: {latency_results['mean']*1000:.2f}ms · Std Dev: {latency_results['stdev']*1000:.2f}ms\n\n")

        # Pipeline breakdown
        f.write("## 3. Pipeline Stage Breakdown\n\n")
        f.write("| Stage | Mean | p99 |\n")
        f.write("|-------|------|-----|\n")
        total_mean = 0
        for stage, data in pipeline_results.items():
            f.write(f"| {stage} | {data['mean']*1000:.2f}ms | {data['p99']*1000:.2f}ms |\n")
            total_mean += data["mean"]
        f.write(f"| **TOTAL** | **{total_mean*1000:.2f}ms** | — |\n\n")

        # Graph scalability
        f.write("## 4. Graph Scalability — Latency vs Size\n\n")
        f.write("| Transactions | Nodes | Edges | Avg Latency | p99 Latency |\n")
        f.write("|-------------|-------|-------|-------------|-------------|\n")
        for r in scalability_results:
            f.write(f"| {r['transactions']:,} | {r['nodes']:,} | {r['edges']:,} | {r['avg_latency']*1000:.2f}ms | {r['p99_latency']*1000:.2f}ms |\n")
        f.write("\n")

        # Memory
        if memory_results:
            f.write("## 5. Memory Profile\n\n")
            f.write("| Transactions | Memory (MB) | Delta |\n")
            f.write("|-------------|------------|-------|\n")
            for r in memory_results:
                f.write(f"| {r['transactions']:,} | {r['memory_mb']:.1f} | {r['delta_mb']:+.1f} MB |\n")
            f.write("\n")

        # Fraud ring detection
        f.write("## 6. Fraud Ring Detection\n\n")
        f.write(f"- Graph: {ring_results['nodes']:,} nodes, {ring_results['edges']:,} edges\n")
        f.write(f"- Rings detected: {ring_results['rings']}\n")
        f.write(f"- Detection latency: {ring_results['detection_latency']*1000:.2f}ms\n")
        f.write(f"- Details retrieval: {ring_results['details_latency']*1000:.2f}ms\n\n")

        f.write("---\n\n")
        f.write(f"*All tests performed on CPU only — no GPU acceleration.*  \n")
        f.write(f"*Excludes Gemini API call latency (external network dependency).*\n")

    print_header("REPORT SAVED")
    print(f"  📄 {os.path.abspath(report_path)}")

    return report_path


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       FraudMesh — Load Test & Scalability Benchmark            ║")
    print("║       Track: Adaptive Real-Time Fraud Detection                ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    start_time = time.perf_counter()

    # Run all tests
    throughput_results = test_throughput()
    latency_results = test_latency_percentiles()
    pipeline_results = test_pipeline_breakdown()
    scalability_results = test_graph_scalability()
    ring_results = test_fraud_ring_detection()
    memory_results = test_memory_profile()

    total_time = time.perf_counter() - start_time

    # Generate report
    report_path = generate_report(
        throughput_results, latency_results, pipeline_results,
        scalability_results, ring_results, memory_results
    )

    print_header("ALL TESTS COMPLETE")
    print_result("Total benchmark time", f"{total_time:.1f}s")
    print()
