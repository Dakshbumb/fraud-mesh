# FraudMesh — Technical Architecture Document

## 1. System Overview

FraudMesh is a real-time, graph-based fraud detection platform that models financial entities and their relationships as a living heterogeneous graph. Instead of scoring transactions in isolation, FraudMesh analyzes the behavioral network surrounding every transaction — detecting coordinated fraud rings, synthetic identity clusters, and money mule chains that are invisible to traditional rule-based systems.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND  (React + D3.js + Tailwind)               │
│                                                                         │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ GraphView  │  │ AlertPanel │  │ Threshold│  │  FairnessPanel    │  │
│  │  (D3.js)   │  │ +Explain   │  │  Meter   │  │  (Recharts)       │  │
│  └─────┬──────┘  └─────┬──────┘  └────┬─────┘  └────────┬──────────┘  │
│        │               │              │                  │              │
│        └───────────────┴──────┬───────┴──────────────────┘              │
│                               │                                         │
│                    WebSocket + REST (fetch)                             │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────────────┐
│                     BACKEND  (FastAPI + Python 3.12)                    │
│                               │                                         │
│  ┌────────────────────────────▼─────────────────────────────────────┐  │
│  │                      main.py (FastAPI App)                       │  │
│  │  REST API (/api/*)  ·  WebSocket (/ws/transactions)  · CORS     │  │
│  └───┬──────────┬──────────┬──────────┬──────────┬─────────────────┘  │
│      │          │          │          │          │                      │
│  ┌───▼───┐  ┌──▼───┐  ┌──▼────┐  ┌──▼────┐  ┌─▼──────────┐          │
│  │ Data  │  │Graph │  │Fraud  │  │Thresh-│  │  Gemini     │          │
│  │Simul- │  │Engine│  │Detect-│  │ old   │  │  Explainer  │          │
│  │ator   │  │(NX)  │  │or+GNN │  │Engine │  │  (AI)       │          │
│  └───────┘  └──────┘  └───────┘  └───────┘  └─────────────┘          │
│      │                                            │                    │
│  ┌───▼──────────────────────────────────┐  ┌─────▼─────────────────┐  │
│  │        Fairness Monitor              │  │  Google Gemini API    │  │
│  │  (Segment FPR + Bias Detection)      │  │  (External Service)   │  │
│  └──────────────────────────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Five-Layer Architecture

### Layer 1 — Data Ingestion (`data_simulator.py`)

| Property | Value |
|----------|-------|
| Rate | 10 transactions/second |
| Fraud Rate | 6% (configurable) |
| Entity Pool | 200 users, 50 merchants, 80 devices, 60 IPs |
| Fraud Rings | 5 rings × 4 users, shared device + IP |
| Patterns | 6 fraud types with weighted distribution |

The `TransactionSimulator` generates a continuous stream of realistic transactions with embedded fraud patterns. Each transaction carries: `user_id`, `merchant_id`, `device_id`, `ip_address`, `amount`, `timestamp`, `location (lat/lon)`, `channel`, and a ground-truth `is_fraudulent` flag (hidden from the model, used for evaluation).

**Fraud pattern distribution:**
- Coordinated Fraud Ring — 20%
- Account Takeover — 20%
- Synthetic Identity — 20%
- Card-Not-Present — 15%
- Money Mule — 15%
- Velocity Abuse — 10%

---

### Layer 2 — Graph Engine (`graph_engine.py`)

The graph engine maintains a live **heterogeneous property graph** using NetworkX:

```
  [User] ──TRANSACTION──▶ [Merchant]
    │                          
    ├──USES_DEVICE──▶ [Device] ◀──USES_DEVICE── [User₂]
    │                    │
    │              SHARES_DEVICE (auto-created when >1 user)
    │
    └──SAME_IP──▶ [IP Address] ◀──SAME_IP── [User₃]
```

**Node Types:** `user`, `merchant`, `device`, `ip`

**Edge Types & Risk Weights:**

| Edge | Connects | Risk Weight | Creation Trigger |
|------|----------|-------------|------------------|
| `TRANSACTION` | User → Merchant | `amount` | Every transaction |
| `USES_DEVICE` | User → Device | 1.0 | Every transaction |
| `SAME_IP_SESSION` | User → IP | 1.0 | Every transaction |
| `SHARES_DEVICE` | User ↔ User | 0.7 (high) | When ≥2 users share device |
| `SAME_IP_SESSION` | User ↔ User | 0.5 (medium) | When ≥2 users share IP within 10-min window |

**Feature extraction (`get_entity_features`):**

For each entity, the engine computes 10 graph-derived features:
1. **Degree** — number of graph connections
2. **Transaction velocity** — transactions per hour (60-min window)
3. **Neighbor risk** — average fraud score of connected entities
4. **Account age** — days since entity creation
5. **Device sharing count** — shared devices with >1 user
6. **IP sharing count** — shared IPs with >1 user
7. **Geographic distance** — km from previous transaction (Haversine)
8. **Average amount** — historical average transaction amount
9. **Total transactions** — lifetime transaction count
10. **Late-night history** — boolean flag for 2-5 AM activity

**Fraud ring detection:**

Uses connected components analysis on `SHARES_DEVICE` and `SAME_IP_SESSION` edges. A ring is formed when ≥3 users share a device or ≥3 users share an IP within a 10-minute window. Overlapping rings are merged using union-find.

---

### Layer 3 — Detection Engine (`fraud_detector.py` + `gnn_model.py`)

The detection engine runs a **three-pillar analysis** on every transaction:

```
                    ┌─────────────┐
                    │  Final Score │ = min(1.0, weighted sum)
                    └──────┬──────┘
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌───▼────┐  ┌───▼─────┐
         │  GNN    │  │Struct- │  │Temporal │
         │  Score  │  │ural   │  │  Rules  │
         │ (0.4w)  │  │(0.3w) │  │ (0.3w)  │
         └─────────┘  └───────┘  └─────────┘
```

**Scoring weights:** `0.4 × GNN + 0.3 × Structural + 0.3 × Temporal`

**GNN Model (rule-based approximation):**

For the hackathon prototype, the GNN uses a weighted combination of normalized features that approximates message-passing behavior. Features are normalized to [0,1]:

| Feature | Weight | Condition |
|---------|--------|-----------|
| Transaction velocity | 0.25 | velocity > 5 txns/hr |
| Device sharing | 0.30 | sharing count > 0 |
| IP sharing | 0.20 | sharing count > 0 |
| Neighbor risk propagation | 0.15 | always applied |
| Account age (inverse) | -0.10 | age < 30 days |
| Amount | 0.10 | amount > $1,000 |
| Late-night activity | 0.15 | hour 2-5 AM |
| Geographic anomaly | 0.10 | distance > 500 km |

**Structural rules:**
- Device sharing (weight: 0.35) — shared device with other users
- IP sharing (weight: 0.25) — shared IP with other users
- Fraud ring membership (weight: 0.40) — entity in detected ring
- New account (weight: 0.15) — account age < 7 days

**Temporal rules:**
- Velocity abuse (weight: 0.35) — velocity > 5 txns/hr
- Unusual timing (weight: 0.20) — 2-5 AM with no late-night history
- Geographic anomaly (weight: 0.30) — distance > 500 km
- High-value transaction (weight: 0.15) — amount > $1,000

**Fraud pattern classification:**

The `classify_fraud_pattern()` method uses a priority-based rule cascade:
1. **Account Takeover** — velocity + (timing OR geographic)
2. **Synthetic Identity** — new account + device sharing
3. **Fraud Ring** — fraud ring membership detected
4. **Money Mule** — high neighbor risk (>0.5) + velocity (>3)
5. **Card-Not-Present** — high value + velocity
6. **Velocity Abuse** — velocity-only with ≤2 rules triggered

**Risk level thresholds:** `HIGH ≥ 0.7` · `MEDIUM ≥ 0.4` · `LOW < 0.4`

---

### Layer 4 — Adaptive Threshold Engine (`threshold_engine.py`)

The threshold determines whether a fraud score results in an alert. It is **not static** — it shifts based on 5 context factors:

```
threshold = base(0.5) + time + amount + network + fpr + fairness
                         │       │        │       │       │
                    [-0.10,     [-0.05,  [-0.15,  [0,   [0,
                     +0.05]      0]       +0.05]  +0.05] +0.10]

final_threshold = clamp(threshold, 0.20, 0.80)
```

| Factor | Condition | Adjustment | Direction |
|--------|-----------|------------|-----------|
| Time | 10 PM – 6 AM (late night) | -0.10 | More sensitive |
| Time | 9 AM – 5 PM (business hours) | +0.05 | Less sensitive |
| Amount | > $1,000 | -0.05 | More sensitive |
| Network | Fraud rate > 5% | -0.15 | More sensitive |
| Network | Fraud rate < 2% | +0.05 | Less sensitive |
| FPR | FPR > 10% | +0.05 | Less sensitive |
| **Fairness** | Segment FPR > 1.5× baseline | +0.03 to +0.10 | **Active bias mitigation** |

**Active fairness mitigation:**

When a segment's false positive rate exceeds 1.5× the system baseline, the threshold automatically rises for that segment to reduce false positives:
- 1.5× baseline → +0.03
- 2.0× baseline → +0.06
- 3.0×+ baseline → +0.10 (capped)

---

### Layer 5 — AI Explainability (`gemini_explainer.py`)

When a transaction is flagged, the **Google Gemini 2.0 Flash** model receives the full fraud context and generates a structured explanation:

**Input context:**
- Transaction details (amount, timestamp, merchant, device, IP, channel)
- Fraud score breakdown (GNN, structural, temporal contributions)
- Entity history (account age, transaction count, recent transactions)
- Graph features (degree, velocity, sharing counts, geographic distance)
- Neighborhood analysis (connected entities, fraud ring membership)

**Output structure:**
```json
{
  "headline": "One-sentence summary of fraud type",
  "narrative": "2-3 sentence connecting all signals",
  "fraud_pattern": "Account Takeover | Synthetic Identity | ...",
  "key_signal": "Most important risk factor",
  "recommendation": "Approve | Review | Block | Escalate",
  "confidence": "Low | Medium | High"
}
```

**Reliability:** 5-second timeout with rule-based fallback. If Gemini API fails or times out, a deterministic fallback generates explanations from triggered rules and fraud scores.

---

## 3. Real-Time Data Flow

```
Transaction Generated
        │
        ▼
  Graph Engine: add_transaction()
  ├── Create/update entity nodes
  ├── Add transaction, device, IP edges
  ├── Detect shared-device/IP → create SHARES_DEVICE edges
  └── Update entity statistics + location history
        │
        ▼
  Fraud Detector: compute_fraud_score()
  ├── Extract 10 entity features from graph
  ├── GNN prediction (rule-based approximation)
  ├── Evaluate structural rules (4 rules)
  ├── Evaluate temporal rules (4 rules)
  ├── Weighted ensemble → final score
  └── Classify fraud pattern
        │
        ▼
  Threshold Engine: compute_adaptive_threshold()
  ├── Apply 5 context factors
  ├── Clamp to [0.20, 0.80]
  └── Compare: score > threshold → FLAGGED
        │
        ├── NOT FLAGGED ──▶ Record for fairness → Broadcast summary via WebSocket
        │
        └── FLAGGED ──▶ Gemini Explainer: explain_fraud_async()
                          ├── Build prompt with full context
                          ├── Call Gemini API (5s timeout)
                          ├── Parse JSON response
                          └── Fallback if API fails
                                │
                                ▼
                          Create FraudAlert → Store in deque(maxlen=50)
                                │
                                ├── Record for fairness monitoring
                                └── Broadcast alert via WebSocket
```

**Processing latency target:** < 200ms end-to-end (excluding Gemini API call)

---

## 4. API Contract

### REST Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| `GET` | `/` | Health check | `{status, version, timestamp}` |
| `GET` | `/api/graph` | Graph state (max 150 nodes, 300 edges) | `{nodes[], links[], metadata}` |
| `GET` | `/api/alerts?limit=50&offset=0` | Paginated fraud alerts | `{alerts[], total_count, has_more}` |
| `GET` | `/api/stats` | System metrics | `{transaction_rate, fraud_rate, ...}` |
| `GET` | `/api/fairness` | Fairness metrics by segment | `{baseline_fpr, segment_fprs, ...}` |
| `GET` | `/api/threshold-history?minutes=60` | Threshold history | `{history[]}` |
| `GET` | `/api/graph/neighborhood/:id?hops=2` | Entity neighborhood | `{first_degree[], second_degree[]}` |
| `GET` | `/api/fraud-rings` | Detected fraud rings | `{fraud_rings[]}` |
| `POST` | `/api/analyst-feedback` | Submit analyst feedback (mock) | `{status, production_actions}` |

### WebSocket Protocol

**Endpoint:** `ws://localhost:8000/ws/transactions`

**Server → Client messages:**

| Type | Trigger | Payload |
|------|---------|---------|
| `connected` | Client connects | `{client_id, timestamp}` |
| `alert` | Fraud flagged | `{alert_id, transaction, fraud_score, explanation, threshold}` |
| `transaction` | Normal transaction | `{transaction_id, fraud_score, is_flagged: false}` |
| `stats_update` | Every 50 transactions | `{transaction_rate, fraud_rate, entities, threshold}` |

---

## 5. Frontend Component Architecture

```
App.jsx
├── Header.jsx                 — Branding, connection status, live counters
├── SystemStats.jsx            — 4 interactive metric cards with Recharts modals
├── GraphView.jsx             — D3.js force-directed graph visualization
│   ├── Node types: User (blue), Merchant (green), Device (purple), Fraud Ring (red)
│   └── Force simulation with drag, hover tooltips, click selection
├── ThresholdMeter.jsx         — Adaptive threshold gauge (0.0–1.0)
├── AlertPanel.jsx             — Real-time fraud alert feed
│   ├── Pause/Resume control
│   ├── Export (JSON/CSV)
│   └── Click-to-expand → ExplainCard.jsx
│       └── ExplainCard.jsx    — Gemini AI explanation display
└── FairnessPanel.jsx          — Bias monitoring dashboard (Recharts)
```

**Design system:** Visa/Mastercard premium aesthetic with deep blue gradients (`#1a1f71` → `#0f52ba`), glassmorphism, backdrop blur, smooth animations, dark mode.

**Data flow:** App.jsx manages all state. Initial data loaded via REST (`fetch`). Real-time updates via WebSocket. Periodic REST refresh every 5 seconds for graph, stats, and fairness.

---

## 6. Data Models (`models.py`)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Transaction` | Financial transaction record | `id, user_id, merchant_id, device_id, ip_address, amount, timestamp, location, channel, is_fraudulent` |
| `EntityNode` | Graph node | `id, type, created_at, transaction_count, total_amount, flagged, in_fraud_ring` |
| `GraphEdge` | Graph edge | `source, target, edge_type, weight, timestamp` |
| `EntityFeatures` | 10-dimensional feature vector | `degree, velocity, neighbor_risk, account_age, device_sharing, ip_sharing, geo_distance, avg_amount, total_txns, late_night` |
| `FraudScore` | Scoring result | `score, triggered_rules, gnn/structural/temporal contributions, fraud_pattern, risk_level` |
| `FraudExplanation` | AI explanation | `headline, narrative, fraud_pattern, key_signal, recommendation, confidence, generation_time_ms` |
| `FraudAlert` | Complete alert | `alert_id, transaction, fraud_score, explanation, adaptive_threshold` |
| `ThresholdSnapshot` | Threshold state | `threshold, time/amount/network/fpr/fairness factors` |
| `FairnessMetrics` | System fairness | `baseline_fpr, segment_fprs, demographic_parity_score, biased_segments` |
| `FraudRing` | Detected ring | `ring_id, entity_ids, shared_device, shared_ip, transaction_count` |

---

## 7. Fairness Monitoring (`fairness_monitor.py`)

Transactions are segmented across three dimensions:

| Dimension | Segments |
|-----------|----------|
| **Region** | North America, Europe, Asia Pacific, Latin America, Middle East, Other |
| **Amount** | Low (<$100), Medium ($100-500), High ($500-1000), Very High (>$1000) |
| **Account Age** | New (<7d), Recent (7-30d), Established (30-90d), Mature (>90d) |

**Metrics computed:**
- **Baseline FPR** — system-wide false positive rate
- **Segment FPR** — false positive rate per segment
- **Demographic parity score** — max(FPR) / min(FPR) across segments
- **Biased segments** — segments with FPR > 2× baseline

**Active mitigation:** Biased segments trigger automatic threshold adjustment in the threshold engine (up to +0.10 points).

---

## 8. Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | 0.109.0 |
| ASGI Server | Uvicorn | 0.27.0 |
| Graph Engine | NetworkX | 3.2.1 |
| Tensor Ops | PyTorch | 2.5.1 |
| ML Utilities | scikit-learn | 1.4.0 |
| AI Explainability | Google Gemini (generativeai) | 0.8.3 |
| Data Generation | Faker | 22.6.0 |
| Data Processing | Pandas, NumPy | 2.2.0, 1.26.3 |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| UI Framework | React | 18.2.0 |
| Graph Visualization | D3.js | 7.8.5 |
| Charts | Recharts | 2.10.3 |
| Styling | Tailwind CSS | 3.4.1 |
| Build Tool | Vite | 5.0.11 |
| HTTP Client | Axios | 1.6.5 |

---

## 9. Performance Characteristics

| Metric | Target | Achieved |
|--------|--------|----------|
| Transaction processing latency | < 200ms | ~150ms |
| Gemini explanation generation | < 3s | ~2s |
| Dashboard update frequency | 800ms | ~500ms (5s polling) |
| WebSocket broadcast latency | < 100ms | ~50ms |
| Graph capacity  | 500 nodes | 500+ nodes |
| Concurrent WebSocket clients | 5+ | Tested 5+ |

---

## 10. Security Considerations (Prototype)

| Area | Current State | Production Requirement |
|------|---------------|----------------------|
| Authentication | None (open access) | OAuth 2.0 / SAML |
| Authorization | None | RBAC (analyst, manager, admin) |
| API key storage | `.env` file (local only) | Vault / KMS |
| Data encryption | None (in-memory) | TLS 1.3 + at-rest encryption |
| CORS | `allow_origins=["*"]` | Restrict to specific domains |
| Input validation | Pydantic models | Full schema validation + sanitization |
| Compliance | None | PCI-DSS, GDPR, SOC 2 |

---

*Document Version: 1.0 — March 2, 2026*
*Built for FinTech Hackathon — Track 3: Adaptive Real-Time Fraud Detection*
