# FraudMesh — Load Test & Scalability Results

**Generated:** 2026-03-02 10:24:22  
**Platform:** Python 3.12.7, win32  

---

## Executive Summary

| Metric | Result |
|--------|--------|
| Peak throughput | **27,898 txn/s** |
| p50 latency | **0.41ms** |
| p95 latency | **1.45ms** |
| p99 latency | **1.89ms** |
| Max graph size tested | **390 nodes / 31,989 edges** |
| Fraud rings detected | **1** (in 4.82ms) |
| Memory at 5K txns | **16.0 MB** (+15.9 MB from baseline) |

## 1. Transaction Processing Throughput

| Batch Size | Throughput (txn/s) | Avg Latency | Graph Nodes | Graph Edges |
|------------|-------------------|-------------|-------------|-------------|
| 100 | 27,898 | 0.04ms | 233 | 408 |
| 500 | 14,603 | 0.07ms | 371 | 4,173 |
| 1,000 | 8,057 | 0.12ms | 389 | 11,656 |
| 2,000 | 2,922 | 0.34ms | 390 | 22,848 |
| 5,000 | 451 | 2.22ms | 390 | 32,042 |

## 2. Latency Distribution (2,000 transactions)

| Percentile | Latency |
|------------|--------|
| p50 | 0.41ms |
| p90 | 1.23ms |
| p95 | 1.45ms |
| p99 | 1.89ms |
| Max | 2.81ms |

Mean: 0.55ms · Std Dev: 0.46ms

## 3. Pipeline Stage Breakdown

| Stage | Mean | p99 |
|-------|------|-----|
| graph_update | 0.11ms | 0.49ms |
| fraud_scoring | 0.07ms | 0.29ms |
| threshold | 0.01ms | 0.01ms |
| fairness | 0.00ms | 0.01ms |
| **TOTAL** | **0.19ms** | — |

## 4. Graph Scalability — Latency vs Size

| Transactions | Nodes | Edges | Avg Latency | p99 Latency |
|-------------|-------|-------|-------------|-------------|
| 100 | 224 | 378 | 0.85ms | 0.88ms |
| 250 | 325 | 1,416 | 0.04ms | 0.08ms |
| 500 | 372 | 4,185 | 0.16ms | 0.32ms |
| 1,000 | 389 | 11,729 | 0.28ms | 0.71ms |
| 2,000 | 390 | 23,061 | 1.41ms | 3.05ms |
| 3,000 | 390 | 27,563 | 2.41ms | 4.55ms |
| 5,000 | 390 | 31,989 | 5.19ms | 7.86ms |

## 5. Memory Profile

| Transactions | Memory (MB) | Delta |
|-------------|------------|-------|
| 500 | 2.3 | +2.3 MB |
| 1,000 | 6.0 | +5.9 MB |
| 2,000 | 11.7 | +11.7 MB |
| 3,000 | 13.7 | +13.6 MB |
| 5,000 | 16.0 | +15.9 MB |

## 6. Fraud Ring Detection

- Graph: 390 nodes, 22,705 edges
- Rings detected: 1
- Detection latency: 4.82ms
- Details retrieval: 0.03ms

---

*All tests performed on CPU only — no GPU acceleration.*  
*Excludes Gemini API call latency (external network dependency).*
