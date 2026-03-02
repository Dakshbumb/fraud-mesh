# Design Document: FraudMesh

## Overview

FraudMesh is a real-time fraud detection platform that models financial entities and their relationships as a dynamic graph. The system combines Graph Neural Networks (GNN), rule-based structural analysis, temporal pattern detection, and adaptive thresholding to identify fraudulent transactions. Claude Opus 4.5 provides natural language explanations for detected fraud, while a fairness monitoring system ensures unbiased detection across user segments.

### System Goals

- Process transactions with <200ms latency for real-time fraud detection
- Achieve >85% fraud detection recall with <8% false positive rate
- Provide human-readable explanations for every fraud alert within 3 seconds
- Visualize the entity relationship graph in real time with <800ms update latency
- Monitor and mitigate bias across user segments continuously

### Technology Stack

**Backend:**
- FastAPI: Async web framework with WebSocket support
- NetworkX: Graph data structure and algorithms
- PyTorch Geometric: Graph Neural Network implementation
- Anthropic SDK: Claude Opus 4.5 API integration
- Python 3.10+

**Frontend:**
- React 18: Component-based UI framework
- D3.js: Force-directed graph visualization
- Recharts: Metrics and fairness dashboards
- Tailwind CSS: Dark-mode styling
- WebSocket API: Real-time bidirectional communication

**Infrastructure:**
- Local development environment
- Environment variables for API key management
- Python virtualenv for backend isolation
- Node.js/npm for frontend build


## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  GraphView   │  │ AlertPanel   │  │FairnessPanel │      │
│  │   (D3.js)    │  │              │  │  (Recharts)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ExplainCard  │  │ThresholdMeter│  │ SystemStats  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    WebSocket + REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              main.py (FastAPI App)                    │  │
│  │  - WebSocket endpoint: /ws/transactions               │  │
│  │  - REST endpoints: /graph, /alerts, /stats, /fairness│  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Transaction  │→ │  Detection  │→ │   Threshold │        │
│  │ Simulator   │  │   Engine    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                 │                 │               │
│         ↓                 ↓                 ↓               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Graph     │  │  GNN Model  │  │   Claude    │        │
│  │   Engine    │  │             │  │  Explainer  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                                   │               │
│         ↓                                   ↓               │
│  ┌─────────────┐                   ┌─────────────┐        │
│  │  Fairness   │                   │  Anthropic  │        │
│  │   Monitor   │                   │     API     │        │
│  └─────────────┘                   └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Transaction Generation**: Transaction_Simulator generates realistic transactions with embedded fraud patterns
2. **Graph Update**: Graph_Engine creates/updates entity nodes and relationship edges
3. **Feature Extraction**: Graph_Engine computes graph features (degree, velocity, neighbor_risk)
4. **Fraud Scoring**: Detection_Engine combines GNN inference, structural rules, and temporal rules to compute fraud score
5. **Threshold Comparison**: Threshold_Engine provides adaptive threshold based on context (time, amount, network fraud rate)
6. **Alert Generation**: If fraud_score > adaptive_threshold, generate fraud alert
7. **Explanation Generation**: Claude_Explainer receives fraud case context and generates natural language explanation
8. **WebSocket Broadcast**: Alert with explanation streamed to all connected frontend clients
9. **Visualization Update**: Frontend updates graph visualization, alert feed, and metrics dashboards


## Components and Interfaces

### Backend Components

#### 1. data_simulator.py - Transaction Generator

**Purpose**: Generate realistic transaction streams with embedded fraud patterns for demonstration.

**Key Classes:**
- `TransactionSimulator`: Main simulator class
- `FraudRing`: Represents a coordinated fraud ring with shared devices/IPs

**Key Methods:**
```python
class TransactionSimulator:
    def __init__(self, fraud_rate: float = 0.05):
        """Initialize simulator with target fraud rate (3-8%)"""
        
    def generate_transaction(self) -> Transaction:
        """Generate a single transaction (normal or fraudulent)"""
        
    def create_fraud_ring(self, size: int) -> FraudRing:
        """Create a fraud ring with shared device/IP"""
        
    async def stream_transactions(self, rate: int = 10):
        """Stream transactions at specified rate per second"""
```

**Fraud Pattern Types:**
- Account Takeover: Unusual location, time, velocity
- Synthetic Identity Fraud: New accounts with shared devices
- Money Mule Operation: Rapid transfers between connected accounts
- Coordinated Fraud Ring: 3+ accounts sharing device/IP
- Card-Not-Present Fraud: High-value transactions with velocity anomalies

**Transaction Structure:**
```python
@dataclass
class Transaction:
    id: str
    user_id: str
    merchant_id: str
    device_id: str
    ip_address: str
    amount: float
    timestamp: datetime
    location: tuple[float, float]  # (lat, lon)
    is_fraudulent: bool  # Ground truth for evaluation
    fraud_pattern: Optional[str]
```

#### 2. graph_engine.py - Graph Management

**Purpose**: Maintain entity relationship graph and compute graph features.

**Key Classes:**
- `GraphEngine`: NetworkX-based graph manager
- `Entity`: Node representing user, merchant, device, or IP

**Key Methods:**
```python
class GraphEngine:
    def __init__(self):
        self.graph = nx.Graph()
        self.entity_history: dict[str, list[Transaction]] = {}
        
    def add_transaction(self, txn: Transaction) -> None:
        """Add transaction to graph, creating/updating entities and edges"""
        
    def get_entity_features(self, entity_id: str) -> dict:
        """Compute graph features for entity: degree, velocity, neighbor_risk"""
        
    def detect_fraud_rings(self) -> list[set[str]]:
        """Identify clusters of 3+ entities sharing device/IP"""
        
    def get_neighborhood(self, entity_id: str, hops: int = 2) -> dict:
        """Return entities within N hops"""
        
    def compute_structural_anomaly_score(self) -> float:
        """Detect rapid cluster formation in 5-minute window"""
```

**Graph Schema:**

Nodes:
- `user:{id}`: User account entity
- `merchant:{id}`: Merchant entity
- `device:{id}`: Device fingerprint entity
- `ip:{ip_address}`: IP address entity

Edges:
- `TRANSACTION`: User → Merchant (weight: amount, timestamp)
- `USES_DEVICE`: User → Device (timestamp)
- `SHARES_DEVICE`: User → User (via common device)
- `SAME_IP_SESSION`: User → User (via common IP within 10 min)

**Graph Features:**
```python
@dataclass
class EntityFeatures:
    degree: int  # Number of connections
    transaction_velocity: float  # Transactions per hour
    neighbor_risk: float  # Average fraud score of neighbors
    account_age_days: int
    device_sharing_count: int  # Number of users sharing device
    ip_sharing_count: int  # Number of users sharing IP
```


#### 3. fraud_detector.py - Detection Engine

**Purpose**: Compute fraud scores using hybrid rule-based + GNN approach.

**Key Classes:**
- `FraudDetector`: Main detection engine
- `RuleEngine`: Structural and temporal rule evaluation
- `GNNModel`: Graph Neural Network for risk propagation

**Key Methods:**
```python
class FraudDetector:
    def __init__(self, graph_engine: GraphEngine):
        self.graph_engine = graph_engine
        self.rule_engine = RuleEngine()
        self.gnn_model = GNNModel()
        
    def compute_fraud_score(self, txn: Transaction) -> FraudScore:
        """Compute fraud score combining rules and GNN"""
        
    def classify_fraud_pattern(self, triggered_rules: list[str]) -> str:
        """Classify fraud pattern based on triggered rules"""
        
    def assemble_fraud_case_context(self, txn: Transaction) -> dict:
        """Assemble complete context for fraud explanation"""
```

**Rule-Based Scoring:**

Structural Rules:
- `device_sharing_rule`: +0.3 if device shared by 3+ users
- `ip_sharing_rule`: +0.25 if IP shared by 3+ users in 10 min
- `fraud_ring_rule`: +0.4 if entity in detected fraud ring
- `new_account_rule`: +0.15 if account age < 7 days

Temporal Rules:
- `velocity_rule`: +0.35 if >5 transactions in 60 seconds
- `timing_rule`: +0.2 if transaction at 2-5 AM with no history
- `geographic_rule`: +0.3 if location change >500km in 30 min
- `amount_rule`: +0.15 if amount >$1000

**GNN Architecture:**

```python
class GNNModel(torch.nn.Module):
    def __init__(self, hidden_dim: int = 64):
        super().__init__()
        self.conv1 = GCNConv(in_channels=10, out_channels=hidden_dim)
        self.conv2 = GCNConv(in_channels=hidden_dim, out_channels=hidden_dim)
        self.classifier = Linear(hidden_dim, 1)
        
    def forward(self, x, edge_index) -> torch.Tensor:
        """
        x: Node features [num_nodes, 10]
        edge_index: Graph connectivity [2, num_edges]
        Returns: Fraud probability [num_nodes, 1]
        """
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        return torch.sigmoid(self.classifier(x))
```

**Node Features for GNN (10 dimensions):**
1. Transaction amount (normalized)
2. Transaction velocity (txns/hour)
3. Account age (days, normalized)
4. Device sharing count
5. IP sharing count
6. Hour of day (sin/cos encoded)
7. Geographic distance from previous txn
8. Neighbor risk (average)
9. Degree centrality
10. Clustering coefficient

**Final Score Combination:**
```python
final_score = (
    0.4 * gnn_score +
    0.3 * max(structural_rule_scores) +
    0.3 * max(temporal_rule_scores)
)
```

**Fraud Score Output:**
```python
@dataclass
class FraudScore:
    score: float  # 0-1
    triggered_rules: list[str]
    gnn_contribution: float
    structural_contribution: float
    temporal_contribution: float
    fraud_pattern: str  # Classified pattern type
```


#### 4. threshold_engine.py - Adaptive Threshold

**Purpose**: Dynamically adjust fraud detection threshold based on context.

**Key Classes:**
- `ThresholdEngine`: Adaptive threshold calculator

**Key Methods:**
```python
class ThresholdEngine:
    def __init__(self, base_threshold: float = 0.5):
        self.base_threshold = base_threshold
        self.threshold_history: list[tuple[datetime, float]] = []
        self.network_fraud_rate_window: deque = deque(maxlen=100)
        
    def compute_adaptive_threshold(
        self, 
        txn: Transaction,
        network_fraud_rate: float,
        false_positive_rate: float
    ) -> float:
        """Compute context-aware threshold"""
        
    def get_threshold_factors(self) -> dict:
        """Return current factors influencing threshold"""
```

**Threshold Adjustment Logic:**

Base threshold: 0.5

Time-based adjustment:
- If 10 PM - 6 AM: threshold -= 0.1 (more sensitive at night)

Amount-based adjustment:
- If amount > $1000: threshold -= 0.05 (more sensitive for high amounts)

Network fraud rate adjustment:
- If network fraud rate > 5% in last 10 min: threshold -= 0.15 (more sensitive during attack)

False positive rate adjustment:
- If FPR > 10% in last 30 min: threshold += 0.05 (less sensitive to reduce FP)

**Threshold bounds:** [0.2, 0.8]

**Update frequency:** Every 60 seconds

**Threshold History:**
```python
@dataclass
class ThresholdSnapshot:
    timestamp: datetime
    threshold: float
    time_factor: float
    amount_factor: float
    network_factor: float
    fpr_factor: float
```

#### 5. claude_explainer.py - Natural Language Explanations

**Purpose**: Generate human-readable fraud explanations using Claude Opus 4.5.

**Key Classes:**
- `ClaudeExplainer`: Anthropic API integration

**Key Methods:**
```python
class ClaudeExplainer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    async def explain_fraud(
        self, 
        fraud_case_context: dict
    ) -> FraudExplanation:
        """Generate natural language explanation"""
        
    def _build_prompt(self, context: dict) -> str:
        """Build structured prompt for Claude"""
```

**Fraud Case Context Structure:**
```python
fraud_case_context = {
    "transaction": {
        "id": str,
        "amount": float,
        "timestamp": str,
        "location": tuple[float, float]
    },
    "fraud_score": {
        "score": float,
        "triggered_rules": list[str],
        "gnn_contribution": float,
        "structural_contribution": float,
        "temporal_contribution": float
    },
    "entity_history": {
        "user_id": str,
        "account_age_days": int,
        "transaction_count": int,
        "recent_transactions": list[dict]
    },
    "graph_features": {
        "degree": int,
        "velocity": float,
        "neighbor_risk": float,
        "device_sharing_count": int,
        "ip_sharing_count": int
    },
    "neighborhood": {
        "connected_entities": list[str],
        "fraud_ring_detected": bool
    }
}
```

**Claude Prompt Template:**
```
You are a fraud detection expert analyzing a flagged transaction.

Transaction Details:
- ID: {transaction_id}
- Amount: ${amount}
- Time: {timestamp}
- Location: {location}

Fraud Score: {score} (threshold: {threshold})

Triggered Risk Signals:
{triggered_rules}

Graph Analysis:
- Account age: {account_age_days} days
- Transaction velocity: {velocity} txns/hour
- Device sharing: {device_sharing_count} users
- IP sharing: {ip_sharing_count} users
- Connected to {neighbor_count} entities
- Fraud ring detected: {fraud_ring_detected}

Provide a fraud explanation with:
1. Headline: One-sentence summary
2. Narrative: 2-3 sentence explanation of why this is suspicious
3. Pattern: Classify as Account Takeover, Synthetic Identity, Money Mule, Fraud Ring, or CNP Fraud
4. Key Signal: The single most important risk factor
5. Recommendation: Approve, Review, or Block
6. Confidence: Low, Medium, or High
```

**Explanation Output:**
```python
@dataclass
class FraudExplanation:
    headline: str
    narrative: str
    fraud_pattern: str
    key_signal: str
    recommendation: str  # "Approve", "Review", "Block"
    confidence: str  # "Low", "Medium", "High"
    generation_time_ms: int
```


#### 6. fairness_monitor.py - Bias Detection

**Purpose**: Monitor false positive rates across user segments to ensure fairness.

**Key Classes:**
- `FairnessMonitor`: Segment-based FPR tracking

**Key Methods:**
```python
class FairnessMonitor:
    def __init__(self):
        self.segment_stats: dict[str, SegmentStats] = {}
        
    def record_alert(
        self, 
        txn: Transaction, 
        fraud_score: float,
        is_true_positive: bool
    ) -> None:
        """Record alert outcome by segment"""
        
    def compute_fairness_metrics(self) -> FairnessMetrics:
        """Compute FPR by segment and demographic parity"""
        
    def detect_bias_alerts(self) -> list[BiasAlert]:
        """Identify segments with FPR > 2x baseline"""
```

**Segmentation Dimensions:**
- Geographic region: Derived from transaction location
- Amount band: <$100, $100-$500, $500-$1000, >$1000
- Account age: <7 days, 7-30 days, 30-90 days, >90 days

**Segment Statistics:**
```python
@dataclass
class SegmentStats:
    segment_id: str
    total_transactions: int
    flagged_transactions: int
    true_positives: int
    false_positives: int
    false_positive_rate: float
```

**Fairness Metrics:**
```python
@dataclass
class FairnessMetrics:
    baseline_fpr: float  # System-wide FPR
    segment_fprs: dict[str, float]  # FPR by segment
    demographic_parity_score: float  # Max FPR / Min FPR
    biased_segments: list[str]  # Segments with FPR > 2x baseline
    update_timestamp: datetime
```

**Bias Alert:**
```python
@dataclass
class BiasAlert:
    segment_id: str
    segment_fpr: float
    baseline_fpr: float
    ratio: float  # segment_fpr / baseline_fpr
    timestamp: datetime
```

#### 7. main.py - FastAPI Application

**Purpose**: HTTP and WebSocket server for frontend communication.

**Key Endpoints:**

REST API:
- `GET /`: Serve frontend static files
- `GET /api/graph`: Return current graph state (nodes, edges)
- `GET /api/alerts`: Return last 50 fraud alerts
- `GET /api/stats`: Return system metrics (txn rate, fraud rate, etc.)
- `GET /api/fairness`: Return fairness metrics by segment
- `GET /api/threshold-history`: Return threshold history for last 60 min

WebSocket:
- `WS /ws/transactions`: Real-time stream of transactions, alerts, graph updates

**WebSocket Message Types:**
```python
# Client → Server
{
    "type": "subscribe",
    "channels": ["transactions", "alerts", "graph_updates"]
}

# Server → Client
{
    "type": "transaction",
    "data": {
        "transaction": {...},
        "fraud_score": {...},
        "graph_update": {...}
    }
}

{
    "type": "alert",
    "data": {
        "transaction": {...},
        "fraud_score": {...},
        "explanation": {...},
        "timestamp": "..."
    }
}

{
    "type": "stats_update",
    "data": {
        "txn_rate": 10.5,
        "fraud_rate": 0.06,
        "avg_fraud_score": 0.23,
        "active_entities": 150,
        "adaptive_threshold": 0.48
    }
}
```

**Application Lifecycle:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    graph_engine = GraphEngine()
    fraud_detector = FraudDetector(graph_engine)
    threshold_engine = ThresholdEngine()
    claude_explainer = ClaudeExplainer(api_key=os.getenv("ANTHROPIC_API_KEY"))
    fairness_monitor = FairnessMonitor()
    simulator = TransactionSimulator()
    
    # Start transaction stream
    asyncio.create_task(process_transaction_stream(simulator, ...))
    
    yield
    
    # Shutdown
    # Clean up resources

app = FastAPI(lifespan=lifespan)
```


### Frontend Components

#### 1. App.jsx - Main Application

**Purpose**: Root component managing global state and layout.

**State Management:**
```javascript
const [transactions, setTransactions] = useState([]);
const [alerts, setAlerts] = useState([]);
const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
const [stats, setStats] = useState({});
const [fairnessMetrics, setFairnessMetrics] = useState({});
const [thresholdHistory, setThresholdHistory] = useState([]);
const [wsConnected, setWsConnected] = useState(false);
```

**WebSocket Connection:**
```javascript
useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/transactions');
    
    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => {
        setWsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(() => connectWebSocket(), 5000);
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    return () => ws.close();
}, []);
```

**Layout:**
```jsx
<div className="min-h-screen bg-gray-900 text-white">
    <Header wsConnected={wsConnected} />
    <div className="grid grid-cols-12 gap-4 p-4">
        <div className="col-span-8">
            <GraphView data={graphData} />
        </div>
        <div className="col-span-4">
            <SystemStats stats={stats} />
            <ThresholdMeter 
                current={stats.adaptive_threshold} 
                history={thresholdHistory} 
            />
            <AlertPanel alerts={alerts} />
        </div>
        <div className="col-span-12">
            <FairnessPanel metrics={fairnessMetrics} />
        </div>
    </div>
</div>
```

#### 2. GraphView.jsx - D3.js Graph Visualization

**Purpose**: Render entity relationship graph with force-directed layout.

**D3 Force Simulation:**
```javascript
useEffect(() => {
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(30));
    
    simulation.on("tick", () => {
        // Update node and edge positions
        updateVisualization();
    });
    
    return () => simulation.stop();
}, [nodes, edges]);
```

**Node Rendering:**
```javascript
// Color coding by entity type and fraud status
const getNodeColor = (node) => {
    if (node.in_fraud_ring) return '#ef4444'; // red
    if (node.flagged) return '#f59e0b'; // amber
    if (node.type === 'user') return '#3b82f6'; // blue
    if (node.type === 'merchant') return '#10b981'; // green
    if (node.type === 'device') return '#8b5cf6'; // purple
    return '#6b7280'; // gray
};

// Node size by degree
const getNodeRadius = (node) => {
    return 5 + Math.sqrt(node.degree) * 2;
};
```

**Interaction:**
```javascript
const handleNodeClick = (node) => {
    // Fetch neighborhood data
    fetch(`/api/graph/neighborhood/${node.id}`)
        .then(res => res.json())
        .then(data => setSelectedNeighborhood(data));
};

// Zoom and pan
const zoom = d3.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", (event) => {
        svg.attr("transform", event.transform);
    });
```

#### 3. AlertPanel.jsx - Fraud Alert Feed

**Purpose**: Display scrollable feed of fraud alerts with expandable details.

**Component Structure:**
```jsx
<div className="bg-gray-800 rounded-lg p-4 h-96 overflow-y-auto">
    <h2 className="text-xl font-bold mb-4">Fraud Alerts</h2>
    {alerts.map(alert => (
        <AlertCard 
            key={alert.transaction.id}
            alert={alert}
            onExpand={() => setExpandedAlert(alert)}
        />
    ))}
</div>
```

**Alert Card:**
```jsx
<div className="bg-gray-700 rounded p-3 mb-2 cursor-pointer hover:bg-gray-600">
    <div className="flex justify-between items-start">
        <div>
            <span className="text-red-400 font-bold">
                {alert.fraud_score.score.toFixed(2)}
            </span>
            <span className="ml-2 text-sm text-gray-300">
                ${alert.transaction.amount}
            </span>
        </div>
        <span className="text-xs text-gray-400">
            {formatTimestamp(alert.timestamp)}
        </span>
    </div>
    <div className="mt-1">
        <span className="inline-block bg-red-900 text-red-200 text-xs px-2 py-1 rounded">
            {alert.fraud_score.fraud_pattern}
        </span>
    </div>
    {expanded && (
        <ExplainCard explanation={alert.explanation} />
    )}
</div>
```


#### 4. ExplainCard.jsx - Claude Explanation Display

**Purpose**: Display natural language fraud explanation from Claude.

**Component:**
```jsx
<div className="mt-3 p-3 bg-gray-900 rounded border border-gray-600">
    <h3 className="font-bold text-amber-400 mb-2">
        {explanation.headline}
    </h3>
    <p className="text-sm text-gray-300 mb-2">
        {explanation.narrative}
    </p>
    <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
            <span className="text-gray-400">Pattern:</span>
            <span className="ml-1 text-white">{explanation.fraud_pattern}</span>
        </div>
        <div>
            <span className="text-gray-400">Confidence:</span>
            <span className="ml-1 text-white">{explanation.confidence}</span>
        </div>
        <div>
            <span className="text-gray-400">Key Signal:</span>
            <span className="ml-1 text-white">{explanation.key_signal}</span>
        </div>
        <div>
            <span className="text-gray-400">Recommendation:</span>
            <span className={`ml-1 font-bold ${
                explanation.recommendation === 'Block' ? 'text-red-400' :
                explanation.recommendation === 'Review' ? 'text-amber-400' :
                'text-green-400'
            }`}>
                {explanation.recommendation}
            </span>
        </div>
    </div>
    <div className="mt-2 text-xs text-gray-500">
        Generated in {explanation.generation_time_ms}ms
    </div>
</div>
```

#### 5. FairnessPanel.jsx - Fairness Metrics Dashboard

**Purpose**: Display false positive rates by segment with bias alerts.

**Component:**
```jsx
<div className="bg-gray-800 rounded-lg p-4">
    <h2 className="text-xl font-bold mb-4">Fairness Monitoring</h2>
    
    <div className="mb-4">
        <div className="text-sm text-gray-400">Baseline FPR</div>
        <div className="text-2xl font-bold">
            {(metrics.baseline_fpr * 100).toFixed(1)}%
        </div>
    </div>
    
    <div className="mb-4">
        <div className="text-sm text-gray-400 mb-2">FPR by Segment</div>
        <ResponsiveContainer width="100%" height={200}>
            <BarChart data={segmentData}>
                <XAxis dataKey="segment" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="fpr" fill="#3b82f6">
                    {segmentData.map((entry, index) => (
                        <Cell 
                            key={`cell-${index}`}
                            fill={entry.fpr > metrics.baseline_fpr * 2 ? '#ef4444' : '#3b82f6'}
                        />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    </div>
    
    {metrics.biased_segments.length > 0 && (
        <div className="bg-red-900 bg-opacity-20 border border-red-700 rounded p-3">
            <div className="text-red-400 font-bold mb-1">Bias Alert</div>
            <div className="text-sm text-gray-300">
                {metrics.biased_segments.length} segment(s) exceed 2x baseline FPR
            </div>
        </div>
    )}
    
    <div className="mt-4">
        <div className="text-sm text-gray-400">Demographic Parity Score</div>
        <div className="text-lg font-bold">
            {metrics.demographic_parity_score.toFixed(2)}
        </div>
        <div className="text-xs text-gray-500">
            (Max FPR / Min FPR - lower is better)
        </div>
    </div>
</div>
```

#### 6. ThresholdMeter.jsx - Threshold Visualization

**Purpose**: Display current adaptive threshold with history chart.

**Component:**
```jsx
<div className="bg-gray-800 rounded-lg p-4">
    <h2 className="text-xl font-bold mb-4">Adaptive Threshold</h2>
    
    <div className="mb-4">
        <div className="text-3xl font-bold text-center">
            {current.toFixed(2)}
        </div>
        <div className="text-sm text-gray-400 text-center">
            Current Sensitivity
        </div>
    </div>
    
    <div className="relative h-4 bg-gray-700 rounded-full overflow-hidden mb-4">
        <div 
            className="absolute h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500"
            style={{ width: `${current * 100}%` }}
        />
    </div>
    
    <div className="mb-4">
        <ResponsiveContainer width="100%" height={100}>
            <LineChart data={history}>
                <XAxis dataKey="timestamp" hide />
                <YAxis domain={[0, 1]} hide />
                <Tooltip />
                <Line 
                    type="monotone" 
                    dataKey="threshold" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                />
            </LineChart>
        </ResponsiveContainer>
    </div>
    
    <div className="text-xs text-gray-400">
        <div>Factors:</div>
        <ul className="list-disc list-inside">
            {factors.time_adjustment !== 0 && (
                <li>Time: {factors.time_adjustment > 0 ? '+' : ''}{factors.time_adjustment}</li>
            )}
            {factors.amount_adjustment !== 0 && (
                <li>Amount: {factors.amount_adjustment > 0 ? '+' : ''}{factors.amount_adjustment}</li>
            )}
            {factors.network_adjustment !== 0 && (
                <li>Network: {factors.network_adjustment > 0 ? '+' : ''}{factors.network_adjustment}</li>
            )}
        </ul>
    </div>
</div>
```


## Data Models

### Transaction

```python
@dataclass
class Transaction:
    id: str  # UUID
    user_id: str  # "user_12345"
    merchant_id: str  # "merchant_789"
    device_id: str  # Device fingerprint hash
    ip_address: str  # IPv4 address
    amount: float  # USD
    timestamp: datetime
    location: tuple[float, float]  # (latitude, longitude)
    is_fraudulent: bool  # Ground truth for evaluation
    fraud_pattern: Optional[str]  # Pattern type if fraudulent
```

### Graph Node Types

```python
@dataclass
class EntityNode:
    id: str  # Unique identifier
    type: str  # "user", "merchant", "device", "ip"
    created_at: datetime
    transaction_count: int
    total_amount: float
    flagged: bool  # Currently flagged for fraud
    in_fraud_ring: bool  # Part of detected fraud ring
    
    # Type-specific attributes
    attributes: dict  # Flexible storage for entity-specific data
```

**User Node Attributes:**
```python
{
    "account_age_days": int,
    "location_history": list[tuple[float, float]],
    "device_ids": set[str],
    "ip_addresses": set[str]
}
```

**Device Node Attributes:**
```python
{
    "user_count": int,  # Number of users sharing this device
    "first_seen": datetime,
    "last_seen": datetime
}
```

### Graph Edge Types

```python
@dataclass
class GraphEdge:
    source: str  # Source entity ID
    target: str  # Target entity ID
    edge_type: str  # "TRANSACTION", "USES_DEVICE", "SHARES_DEVICE", "SAME_IP_SESSION"
    weight: float  # Transaction amount or connection strength
    timestamp: datetime
    attributes: dict  # Edge-specific metadata
```

**TRANSACTION Edge:**
```python
{
    "transaction_id": str,
    "amount": float,
    "timestamp": datetime
}
```

**SHARES_DEVICE Edge:**
```python
{
    "device_id": str,
    "shared_since": datetime,
    "transaction_count": int
}
```

**SAME_IP_SESSION Edge:**
```python
{
    "ip_address": str,
    "session_start": datetime,
    "session_end": datetime
}
```

### Fraud Alert

```python
@dataclass
class FraudAlert:
    alert_id: str  # UUID
    transaction: Transaction
    fraud_score: FraudScore
    explanation: FraudExplanation
    timestamp: datetime
    adaptive_threshold: float  # Threshold at time of alert
    is_true_positive: Optional[bool]  # For fairness tracking
```

### Fraud Score

```python
@dataclass
class FraudScore:
    score: float  # 0-1
    triggered_rules: list[str]  # Rule names that fired
    gnn_contribution: float  # GNN model output
    structural_contribution: float  # Max structural rule score
    temporal_contribution: float  # Max temporal rule score
    fraud_pattern: str  # Classified pattern type
    entity_features: dict  # Graph features used
```

### Fraud Explanation

```python
@dataclass
class FraudExplanation:
    headline: str  # One-sentence summary
    narrative: str  # 2-3 sentence explanation
    fraud_pattern: str  # Pattern classification
    key_signal: str  # Most important risk factor
    recommendation: str  # "Approve", "Review", "Block"
    confidence: str  # "Low", "Medium", "High"
    generation_time_ms: int  # Claude API latency
```

### System Statistics

```python
@dataclass
class SystemStats:
    timestamp: datetime
    transaction_rate: float  # Transactions per second
    total_transactions: int
    flagged_transactions: int
    fraud_rate: float  # Percentage of flagged transactions
    avg_fraud_score: float
    active_entities: int  # Total nodes in graph
    active_edges: int
    adaptive_threshold: float
    avg_processing_latency_ms: float
```

### Fairness Metrics

```python
@dataclass
class FairnessMetrics:
    timestamp: datetime
    baseline_fpr: float  # System-wide false positive rate
    segment_fprs: dict[str, float]  # FPR by segment ID
    demographic_parity_score: float  # Max FPR / Min FPR
    biased_segments: list[str]  # Segments with FPR > 2x baseline
    segment_details: dict[str, SegmentStats]
```

```python
@dataclass
class SegmentStats:
    segment_id: str  # e.g., "region_US", "amount_high", "age_new"
    total_transactions: int
    flagged_transactions: int
    true_positives: int
    false_positives: int
    false_positive_rate: float
```


## Algorithms

### Fraud Scoring Algorithm

**Input:** Transaction, Graph State
**Output:** FraudScore

```python
def compute_fraud_score(txn: Transaction, graph: GraphEngine) -> FraudScore:
    # 1. Extract graph features
    user_features = graph.get_entity_features(txn.user_id)
    
    # 2. Evaluate structural rules
    structural_scores = []
    triggered_rules = []
    
    if user_features.device_sharing_count >= 3:
        structural_scores.append(0.3)
        triggered_rules.append("device_sharing_rule")
    
    if user_features.ip_sharing_count >= 3:
        structural_scores.append(0.25)
        triggered_rules.append("ip_sharing_rule")
    
    if graph.is_in_fraud_ring(txn.user_id):
        structural_scores.append(0.4)
        triggered_rules.append("fraud_ring_rule")
    
    if user_features.account_age_days < 7:
        structural_scores.append(0.15)
        triggered_rules.append("new_account_rule")
    
    structural_contribution = max(structural_scores) if structural_scores else 0.0
    
    # 3. Evaluate temporal rules
    temporal_scores = []
    
    if user_features.transaction_velocity > 5:  # >5 txns in 60 sec
        temporal_scores.append(0.35)
        triggered_rules.append("velocity_rule")
    
    hour = txn.timestamp.hour
    if 2 <= hour <= 5 and not user_features.has_late_night_history:
        temporal_scores.append(0.2)
        triggered_rules.append("timing_rule")
    
    if user_features.geographic_distance_km > 500:  # >500km in 30 min
        temporal_scores.append(0.3)
        triggered_rules.append("geographic_rule")
    
    if txn.amount > 1000:
        temporal_scores.append(0.15)
        triggered_rules.append("amount_rule")
    
    temporal_contribution = max(temporal_scores) if temporal_scores else 0.0
    
    # 4. GNN inference
    node_features = extract_node_features(txn, user_features)
    gnn_contribution = gnn_model.predict(node_features, graph.edge_index)
    
    # 5. Combine scores
    final_score = (
        0.4 * gnn_contribution +
        0.3 * structural_contribution +
        0.3 * temporal_contribution
    )
    
    # 6. Classify fraud pattern
    fraud_pattern = classify_fraud_pattern(triggered_rules)
    
    return FraudScore(
        score=final_score,
        triggered_rules=triggered_rules,
        gnn_contribution=gnn_contribution,
        structural_contribution=structural_contribution,
        temporal_contribution=temporal_contribution,
        fraud_pattern=fraud_pattern,
        entity_features=user_features
    )
```

### Adaptive Threshold Algorithm

**Input:** Transaction, Network State, Fairness State
**Output:** Adaptive Threshold

```python
def compute_adaptive_threshold(
    txn: Transaction,
    network_fraud_rate: float,
    false_positive_rate: float,
    base_threshold: float = 0.5
) -> float:
    threshold = base_threshold
    
    # Time-based adjustment
    hour = txn.timestamp.hour
    if 22 <= hour or hour <= 6:  # 10 PM - 6 AM
        threshold -= 0.1
    
    # Amount-based adjustment
    if txn.amount > 1000:
        threshold -= 0.05
    
    # Network fraud rate adjustment
    if network_fraud_rate > 0.05:  # >5% fraud rate
        threshold -= 0.15
    
    # False positive rate adjustment
    if false_positive_rate > 0.10:  # >10% FPR
        threshold += 0.05
    
    # Enforce bounds
    threshold = max(0.2, min(0.8, threshold))
    
    return threshold
```

### Fraud Ring Detection Algorithm

**Input:** Graph State
**Output:** List of Fraud Rings (sets of entity IDs)

```python
def detect_fraud_rings(graph: nx.Graph) -> list[set[str]]:
    fraud_rings = []
    
    # Find device-sharing clusters
    device_nodes = [n for n, d in graph.nodes(data=True) if d['type'] == 'device']
    
    for device_node in device_nodes:
        # Get all users connected to this device
        connected_users = [
            n for n in graph.neighbors(device_node)
            if graph.nodes[n]['type'] == 'user'
        ]
        
        # If 3+ users share device, flag as fraud ring
        if len(connected_users) >= 3:
            fraud_rings.append(set(connected_users))
    
    # Find IP-sharing clusters (within 10-minute window)
    ip_nodes = [n for n, d in graph.nodes(data=True) if d['type'] == 'ip']
    
    for ip_node in ip_nodes:
        # Get users who accessed from this IP in last 10 minutes
        recent_users = []
        for user_node in graph.neighbors(ip_node):
            if graph.nodes[user_node]['type'] == 'user':
                edge_data = graph.get_edge_data(user_node, ip_node)
                if edge_data and is_within_window(edge_data['timestamp'], minutes=10):
                    recent_users.append(user_node)
        
        # If 3+ users from same IP in 10 min, flag as fraud ring
        if len(recent_users) >= 3:
            fraud_rings.append(set(recent_users))
    
    # Merge overlapping rings
    merged_rings = merge_overlapping_sets(fraud_rings)
    
    return merged_rings
```

### Graph Feature Extraction Algorithm

**Input:** Entity ID, Graph State
**Output:** EntityFeatures

```python
def get_entity_features(entity_id: str, graph: nx.Graph) -> EntityFeatures:
    node_data = graph.nodes[entity_id]
    
    # Degree: number of connections
    degree = graph.degree(entity_id)
    
    # Transaction velocity: txns per hour in last 60 minutes
    recent_txns = get_recent_transactions(entity_id, minutes=60)
    transaction_velocity = len(recent_txns)
    
    # Neighbor risk: average fraud score of connected entities
    neighbors = list(graph.neighbors(entity_id))
    neighbor_scores = [graph.nodes[n].get('fraud_score', 0) for n in neighbors]
    neighbor_risk = sum(neighbor_scores) / len(neighbor_scores) if neighbor_scores else 0
    
    # Account age
    account_age_days = (datetime.now() - node_data['created_at']).days
    
    # Device sharing count
    device_neighbors = [
        n for n in neighbors 
        if graph.nodes[n]['type'] == 'device'
    ]
    device_sharing_count = sum(
        graph.nodes[d].get('user_count', 0) for d in device_neighbors
    )
    
    # IP sharing count
    ip_neighbors = [
        n for n in neighbors 
        if graph.nodes[n]['type'] == 'ip'
    ]
    ip_sharing_count = sum(
        len(list(graph.neighbors(ip))) for ip in ip_neighbors
    )
    
    # Geographic distance from previous transaction
    location_history = node_data.get('location_history', [])
    geographic_distance_km = 0
    if len(location_history) >= 2:
        geographic_distance_km = haversine_distance(
            location_history[-1], 
            location_history[-2]
        )
    
    return EntityFeatures(
        degree=degree,
        transaction_velocity=transaction_velocity,
        neighbor_risk=neighbor_risk,
        account_age_days=account_age_days,
        device_sharing_count=device_sharing_count,
        ip_sharing_count=ip_sharing_count,
        geographic_distance_km=geographic_distance_km
    )
```

### Fraud Pattern Classification Algorithm

**Input:** List of triggered rules
**Output:** Fraud pattern type

```python
def classify_fraud_pattern(triggered_rules: list[str]) -> str:
    # Account Takeover: velocity + timing + geographic anomalies
    if any(r in triggered_rules for r in ['velocity_rule', 'timing_rule', 'geographic_rule']):
        return "Account Takeover"
    
    # Synthetic Identity Fraud: new account + device sharing
    if 'new_account_rule' in triggered_rules and 'device_sharing_rule' in triggered_rules:
        return "Synthetic Identity Fraud"
    
    # Coordinated Fraud Ring: fraud ring detection
    if 'fraud_ring_rule' in triggered_rules:
        return "Coordinated Fraud Ring"
    
    # Money Mule Operation: high neighbor risk + velocity
    if 'velocity_rule' in triggered_rules and any(
        'neighbor' in r for r in triggered_rules
    ):
        return "Money Mule Operation"
    
    # Card-Not-Present Fraud: high amount + velocity
    if 'amount_rule' in triggered_rules and 'velocity_rule' in triggered_rules:
        return "Card-Not-Present Fraud"
    
    # Default
    return "Unknown Pattern"
```


## API Design

### REST Endpoints

#### GET /api/graph

**Purpose:** Fetch current graph state for initial dashboard load.

**Response:**
```json
{
    "nodes": [
        {
            "id": "user_12345",
            "type": "user",
            "created_at": "2024-01-15T10:30:00Z",
            "transaction_count": 15,
            "total_amount": 2500.00,
            "flagged": false,
            "in_fraud_ring": false,
            "degree": 8
        },
        {
            "id": "device_abc123",
            "type": "device",
            "user_count": 2,
            "flagged": false
        }
    ],
    "edges": [
        {
            "source": "user_12345",
            "target": "merchant_789",
            "edge_type": "TRANSACTION",
            "weight": 150.00,
            "timestamp": "2024-01-15T14:22:00Z"
        },
        {
            "source": "user_12345",
            "target": "device_abc123",
            "edge_type": "USES_DEVICE",
            "timestamp": "2024-01-15T14:22:00Z"
        }
    ],
    "metadata": {
        "node_count": 150,
        "edge_count": 320,
        "fraud_ring_count": 2
    }
}
```

**Performance:** <500ms

#### GET /api/alerts

**Purpose:** Fetch recent fraud alerts for initial dashboard load.

**Query Parameters:**
- `limit`: Number of alerts to return (default: 50)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
    "alerts": [
        {
            "alert_id": "alert_uuid_123",
            "transaction": {
                "id": "txn_456",
                "user_id": "user_789",
                "merchant_id": "merchant_101",
                "amount": 1500.00,
                "timestamp": "2024-01-15T14:30:00Z"
            },
            "fraud_score": {
                "score": 0.78,
                "triggered_rules": ["velocity_rule", "amount_rule"],
                "fraud_pattern": "Account Takeover"
            },
            "explanation": {
                "headline": "Suspicious velocity and high-value transaction detected",
                "narrative": "This transaction shows unusual velocity...",
                "recommendation": "Block",
                "confidence": "High"
            },
            "adaptive_threshold": 0.48,
            "timestamp": "2024-01-15T14:30:01Z"
        }
    ],
    "total_count": 127,
    "has_more": true
}
```

**Performance:** <500ms

#### GET /api/stats

**Purpose:** Fetch current system statistics.

**Response:**
```json
{
    "timestamp": "2024-01-15T14:35:00Z",
    "transaction_rate": 10.5,
    "total_transactions": 5420,
    "flagged_transactions": 312,
    "fraud_rate": 0.0576,
    "avg_fraud_score": 0.23,
    "active_entities": 150,
    "active_edges": 320,
    "adaptive_threshold": 0.48,
    "avg_processing_latency_ms": 145
}
```

**Performance:** <500ms

#### GET /api/fairness

**Purpose:** Fetch fairness metrics by segment.

**Response:**
```json
{
    "timestamp": "2024-01-15T14:35:00Z",
    "baseline_fpr": 0.065,
    "segment_fprs": {
        "region_US": 0.058,
        "region_EU": 0.072,
        "amount_low": 0.045,
        "amount_high": 0.089,
        "age_new": 0.135,
        "age_established": 0.042
    },
    "demographic_parity_score": 3.21,
    "biased_segments": ["age_new"],
    "segment_details": {
        "age_new": {
            "segment_id": "age_new",
            "total_transactions": 450,
            "flagged_transactions": 68,
            "true_positives": 7,
            "false_positives": 61,
            "false_positive_rate": 0.135
        }
    }
}
```

**Performance:** <500ms

#### GET /api/threshold-history

**Purpose:** Fetch adaptive threshold history for visualization.

**Query Parameters:**
- `minutes`: Time window in minutes (default: 60)

**Response:**
```json
{
    "history": [
        {
            "timestamp": "2024-01-15T13:35:00Z",
            "threshold": 0.50,
            "time_factor": 0.0,
            "amount_factor": 0.0,
            "network_factor": 0.0,
            "fpr_factor": 0.0
        },
        {
            "timestamp": "2024-01-15T13:36:00Z",
            "threshold": 0.45,
            "time_factor": 0.0,
            "amount_factor": 0.0,
            "network_factor": -0.15,
            "fpr_factor": 0.0
        }
    ]
}
```

**Performance:** <500ms

#### GET /api/graph/neighborhood/:entity_id

**Purpose:** Fetch neighborhood data for selected entity.

**Response:**
```json
{
    "entity_id": "user_12345",
    "first_degree": [
        {
            "id": "merchant_789",
            "type": "merchant",
            "edge_type": "TRANSACTION",
            "transaction_count": 5
        }
    ],
    "second_degree": [
        {
            "id": "user_456",
            "type": "user",
            "edge_type": "SHARES_DEVICE",
            "connection_path": ["user_12345", "device_abc", "user_456"]
        }
    ]
}
```

**Performance:** <50ms


### WebSocket Endpoint

#### WS /ws/transactions

**Purpose:** Real-time bidirectional communication for transaction stream, alerts, and updates.

**Connection Flow:**
1. Client connects to `ws://localhost:8000/ws/transactions`
2. Server sends initial connection confirmation
3. Client subscribes to channels
4. Server streams updates
5. Client can send commands (future: manual review actions)

**Client → Server Messages:**

Subscribe to channels:
```json
{
    "type": "subscribe",
    "channels": ["transactions", "alerts", "graph_updates", "stats"]
}
```

Unsubscribe from channels:
```json
{
    "type": "unsubscribe",
    "channels": ["transactions"]
}
```

**Server → Client Messages:**

Connection confirmation:
```json
{
    "type": "connected",
    "timestamp": "2024-01-15T14:30:00Z",
    "client_id": "client_uuid_123"
}
```

Transaction update:
```json
{
    "type": "transaction",
    "data": {
        "transaction": {
            "id": "txn_456",
            "user_id": "user_789",
            "amount": 150.00,
            "timestamp": "2024-01-15T14:30:00Z"
        },
        "fraud_score": {
            "score": 0.23,
            "triggered_rules": [],
            "fraud_pattern": "Normal"
        },
        "graph_update": {
            "new_nodes": [],
            "new_edges": [
                {
                    "source": "user_789",
                    "target": "merchant_101",
                    "edge_type": "TRANSACTION"
                }
            ],
            "updated_nodes": ["user_789"]
        }
    }
}
```

Fraud alert:
```json
{
    "type": "alert",
    "data": {
        "alert_id": "alert_uuid_456",
        "transaction": {
            "id": "txn_789",
            "user_id": "user_123",
            "amount": 1500.00,
            "timestamp": "2024-01-15T14:31:00Z"
        },
        "fraud_score": {
            "score": 0.78,
            "triggered_rules": ["velocity_rule", "amount_rule"],
            "fraud_pattern": "Account Takeover"
        },
        "explanation": {
            "headline": "Suspicious velocity detected",
            "narrative": "This account executed 7 transactions...",
            "recommendation": "Block",
            "confidence": "High",
            "key_signal": "velocity_rule"
        },
        "adaptive_threshold": 0.48,
        "timestamp": "2024-01-15T14:31:01Z"
    }
}
```

Stats update (every 5 seconds):
```json
{
    "type": "stats_update",
    "data": {
        "timestamp": "2024-01-15T14:31:05Z",
        "transaction_rate": 10.5,
        "fraud_rate": 0.058,
        "avg_fraud_score": 0.23,
        "active_entities": 152,
        "adaptive_threshold": 0.48
    }
}
```

Graph update (structural changes):
```json
{
    "type": "graph_update",
    "data": {
        "fraud_rings_detected": [
            {
                "ring_id": "ring_123",
                "entity_ids": ["user_456", "user_789", "user_101"],
                "shared_device": "device_xyz"
            }
        ],
        "flagged_entities": ["user_456", "user_789", "user_101"]
    }
}
```

Fairness alert:
```json
{
    "type": "fairness_alert",
    "data": {
        "segment_id": "age_new",
        "segment_fpr": 0.145,
        "baseline_fpr": 0.065,
        "ratio": 2.23,
        "timestamp": "2024-01-15T14:32:00Z"
    }
}
```

**Connection Management:**
- Server supports up to 5 concurrent WebSocket connections
- Client reconnects every 5 seconds on disconnect
- Server sends heartbeat ping every 30 seconds
- Client responds with pong to maintain connection

**Message Rate:**
- Transactions: ~10 per second
- Alerts: Variable (depends on fraud rate, ~0.5 per second)
- Stats updates: Every 5 seconds
- Graph updates: As needed (fraud ring detection)


## Performance Considerations

### Latency Requirements

**Transaction Processing Pipeline:**
- Transaction arrival → Fraud score computation: <200ms (95th percentile)
  - Graph update: <50ms
  - Feature extraction: <30ms
  - GNN inference: <100ms
  - Rule evaluation: <20ms
- Fraud score → WebSocket broadcast: <100ms
- Total end-to-end: <300ms

**Claude Explanation Generation:**
- Fraud alert → Explanation ready: <3 seconds
- Asynchronous generation (non-blocking)
- Explanation streamed to frontend when ready

**Dashboard Updates:**
- WebSocket message → UI update: <800ms
- Graph visualization re-render: <500ms
- Chart updates: <300ms

**API Response Times:**
- REST endpoints: <500ms (95th percentile)
- Graph neighborhood query: <50ms

### Scalability Limits (Prototype)

**Graph Size:**
- Maximum nodes: 500 entities
- Maximum edges: 1000 relationships
- Rationale: In-memory NetworkX graph, demo environment

**Transaction Rate:**
- Target: 10 transactions per second
- Peak: 20 transactions per second (burst)
- Rationale: Single-threaded processing, demo workload

**WebSocket Connections:**
- Maximum concurrent: 5 clients
- Rationale: Demo environment, limited resources

**GNN Model:**
- Inference batch size: 1 (single transaction)
- Model size: ~64 hidden dimensions
- Rationale: Real-time inference requirement

### Optimization Strategies

**Graph Operations:**
- Use NetworkX for flexibility (prototype)
- Cache entity features for 60 seconds
- Lazy fraud ring detection (every 5 minutes)
- Prune old edges (>24 hours) to limit graph growth

**GNN Inference:**
- Pre-compute static node embeddings
- Incremental updates for new nodes
- CPU inference (no GPU required for demo)

**WebSocket Broadcasting:**
- Async message dispatch
- Message batching for stats updates
- Selective channel subscriptions

**Claude API:**
- Async API calls (non-blocking)
- Timeout after 5 seconds
- Fallback to rule-based explanation if API fails
- Rate limiting: 1 explanation per alert (no retries)

**Frontend Rendering:**
- D3.js force simulation throttling (60 FPS)
- Virtual scrolling for alert feed (render only visible)
- Debounced graph updates (max 1 per 800ms)
- Memoized React components

### Memory Management

**Backend:**
- Graph: ~10 MB (500 nodes, 1000 edges)
- Transaction history: ~5 MB (24-hour rolling window)
- Alert history: ~2 MB (last 1000 alerts)
- Total: ~20 MB working set

**Frontend:**
- Graph visualization: ~5 MB (D3.js state)
- Alert feed: ~1 MB (last 50 alerts)
- Charts: ~1 MB (Recharts data)
- Total: ~10 MB working set

**Cleanup:**
- Prune transactions older than 24 hours
- Prune alerts older than 1 hour
- Prune graph edges with no recent activity
- Run cleanup every 10 minutes


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, several redundancies were identified and consolidated:
- Requirements 1.1 and 1.4 both test 200ms processing latency (consolidated into Property 1)
- Multiple UI display requirements are better tested as integration examples rather than properties
- Several properties about "containing required fields" can be combined into comprehensive structure validation properties

### Property 1: Transaction Processing Latency

For any transaction under normal load, the detection engine should process it and compute a fraud score within 200ms for at least 95% of transactions.

**Validates: Requirements 1.1, 1.4**

### Property 2: Graph Update Latency

For any processed transaction, the graph engine should complete entity and edge updates within 50ms of fraud score computation.

**Validates: Requirements 1.2**

### Property 3: WebSocket Broadcast Latency

For any graph update, the WebSocket message should be sent to connected clients within 100ms.

**Validates: Requirements 1.3**

### Property 4: Entity Node Creation

For any transaction, after processing, the graph should contain nodes for the user, merchant, device, and IP address entities referenced in that transaction.

**Validates: Requirements 2.1**

### Property 5: Device Sharing Edge Creation

For any set of users that have used the same device, the graph should contain SHARES_DEVICE edges connecting those user nodes.

**Validates: Requirements 2.2**

### Property 6: IP Sharing Edge Creation

For any set of users that have accessed from the same IP address, the graph should contain SAME_IP_SESSION edges connecting those user nodes.

**Validates: Requirements 2.3**

### Property 7: Neighborhood Query Performance

For any entity in the graph, querying its first and second-degree connections should complete within 50ms.

**Validates: Requirements 2.5**

### Property 8: Fraud Score Range Validity

For any transaction processed by the GNN model, the computed fraud score should be in the range [0, 1].

**Validates: Requirements 3.1**

### Property 9: Neighbor Risk Propagation

For any entity with flagged neighbors, the fraud score for that entity's transactions should be higher than an equivalent entity with no flagged neighbors (holding all other features constant).

**Validates: Requirements 3.2**

### Property 10: GNN Inference Latency

For any transaction, GNN model inference should complete within 100ms.

**Validates: Requirements 3.3**

### Property 11: Fraud Score Composition

For any transaction, the final fraud score should incorporate contributions from the GNN model, structural rules, and temporal rules (all three components should have non-zero weight in the final score calculation).

**Validates: Requirements 3.4**

### Property 12: Structural Anomaly Score Elevation

For any transaction involving an entity in a detected structural anomaly cluster, the fraud score should be elevated compared to the same transaction without the structural anomaly.

**Validates: Requirements 4.1, 4.4**

### Property 13: Velocity Anomaly Detection

For any entity that executes more than 5 transactions within 60 seconds, the detection engine should flag a velocity anomaly and include "velocity_rule" in the triggered rules.

**Validates: Requirements 5.1**

### Property 14: Timing Anomaly Detection

For any entity with no prior late-night transaction history, a transaction occurring between 2 AM and 5 AM local time should trigger a timing anomaly and include "timing_rule" in the triggered rules.

**Validates: Requirements 5.2**

### Property 15: Geographic Anomaly Detection

For any entity with two transactions more than 500 kilometers apart occurring within 30 minutes, the detection engine should flag a geographic anomaly and include "geographic_rule" in the triggered rules.

**Validates: Requirements 5.3**

### Property 16: Transaction History Retention

For any entity, the system should maintain a rolling 24-hour transaction history that includes all transactions from the past 24 hours and excludes transactions older than 24 hours.

**Validates: Requirements 5.4**

### Property 17: Night-Time Threshold Adjustment

For any transaction occurring between 10 PM and 6 AM, the adaptive threshold should be decreased by 0.1 compared to the base threshold (before other adjustments).

**Validates: Requirements 6.1**

### Property 18: High-Amount Threshold Adjustment

For any transaction with amount exceeding $1000, the adaptive threshold should be decreased by 0.05 compared to the base threshold (before other adjustments).

**Validates: Requirements 6.2**

### Property 19: Network Fraud Rate Threshold Adjustment

For any 10-minute window where the network-wide fraud rate exceeds 5%, the adaptive threshold should be decreased by 0.15 globally.

**Validates: Requirements 6.3**

### Property 20: False Positive Rate Threshold Adjustment

For any 30-minute window where the false positive rate exceeds 10%, the adaptive threshold should be increased by 0.05.

**Validates: Requirements 6.4**

### Property 21: Threshold Update Frequency

The adaptive threshold should be recomputed and updated every 60 seconds based on current context factors.

**Validates: Requirements 6.5**

### Property 22: Alert Generation Trigger

For any transaction where the fraud score exceeds the adaptive threshold, a fraud alert should be generated.

**Validates: Requirements 7.1**

### Property 23: Alert Broadcast Latency

For any generated fraud alert, the alert should be streamed via WebSocket to connected clients within 500ms.

**Validates: Requirements 7.2**

### Property 24: Alert Structure Completeness

For any fraud alert, the alert data structure should include transaction ID, entity IDs, fraud score, amount, timestamp, and triggered risk signals.

**Validates: Requirements 7.3**

### Property 25: Explanation Generation Latency

For any fraud alert, the Claude explainer should generate a natural language explanation within 3 seconds.

**Validates: Requirements 8.1**

### Property 26: Explanation Input Completeness

For any fraud alert, the input to the Claude explainer should include fraud score, triggered rules, graph features, transaction metadata, and entity behavioral history.

**Validates: Requirements 8.2**

### Property 27: Explanation Structure Completeness

For any generated explanation, it should include a headline, narrative, fraud pattern classification, key signal, recommended action, and confidence level.

**Validates: Requirements 8.3, 8.5**

### Property 28: Transaction Generation Rate

The transaction simulator should generate at least 10 transactions per second on average over any 10-second window.

**Validates: Requirements 9.1**

### Property 29: Fraud Pattern Diversity

The transaction simulator should generate transactions containing at least 3 distinct fraud pattern types over any 5-minute window.

**Validates: Requirements 9.2**

### Property 30: Fraud Ring Pattern Generation

The transaction simulator should create fraud ring patterns where 3 or more entities share device or IP relationships.

**Validates: Requirements 9.3**

### Property 31: Simulated Fraud Rate

The transaction simulator should generate transactions with a fraud rate between 3% and 8% over any 5-minute window.

**Validates: Requirements 9.4**

### Property 32: Graph Visualization Update Latency

For any processed transaction, the frontend graph visualization should update within 800ms of receiving the WebSocket message.

**Validates: Requirements 10.2**

### Property 33: Fairness Monitoring Segmentation

The fairness monitor should track false positive rates across all three segmentation dimensions: geographic region, transaction amount band, and account age.

**Validates: Requirements 11.1**

### Property 34: Fairness Alert Generation

For any segment where the false positive rate exceeds 2 times the system baseline FPR, the fairness monitor should generate a fairness alert.

**Validates: Requirements 11.2**

### Property 35: Demographic Parity Computation Frequency

The fairness monitor should compute demographic parity scores every 5 minutes.

**Validates: Requirements 11.4**

### Property 36: WebSocket Message Type Coverage

The WebSocket stream should support streaming transaction updates, fraud alerts, and graph changes (all three message types).

**Validates: Requirements 12.2**

### Property 37: WebSocket Reconnection Behavior

For any WebSocket disconnection, the frontend should attempt to reconnect every 5 seconds until connection is re-established.

**Validates: Requirements 12.4**

### Property 38: Fraud Pattern Classification Coverage

The detection engine should support classification into all 5 fraud pattern types: Account Takeover, Synthetic Identity Fraud, Money Mule Operation, Coordinated Fraud Ring, and Card-Not-Present Fraud.

**Validates: Requirements 13.1**

### Property 39: Fraud Pattern Assignment

For any flagged transaction, the detection engine should assign a fraud pattern type based on the triggered risk signals.

**Validates: Requirements 13.2, 13.3**

### Property 40: Fraud Detection Recall

For any labeled test dataset with embedded fraud patterns, the system should achieve fraud detection recall above 85%.

**Validates: Requirements 14.1**

### Property 41: False Positive Rate Limit

For any set of flagged transactions, the false positive rate should be below 8%.

**Validates: Requirements 14.2**

### Property 42: Visualization Update Frequency

The frontend dashboard should update visualizations every 800ms when receiving real-time data.

**Validates: Requirements 14.3**

### Property 43: REST API Response Latency

For any REST API endpoint under normal load, the response should be returned within 500ms.

**Validates: Requirements 15.5**

### Property 44: Fraud Case Context Completeness

For any fraud alert, the assembled fraud case context should include transaction details, entity behavioral history, graph neighborhood (2 hops), and all triggered risk signals.

**Validates: Requirements 17.1, 17.2**

### Property 45: Claude Explainer Input Completeness

For any fraud alert, the Claude explainer should receive the complete fraud case context as input.

**Validates: Requirements 17.3**

### Property 46: System Metrics Update Frequency

System metrics should be broadcast via WebSocket every 5 seconds.

**Validates: Requirements 18.4**

### Property 47: Device-Based Fraud Ring Detection

For any set of 3 or more entities sharing the same device fingerprint, the detection engine should flag a potential fraud ring.

**Validates: Requirements 19.1**

### Property 48: IP-Based Fraud Ring Detection

For any set of 3 or more entities sharing the same IP address with transactions within a 10-minute window, the detection engine should flag a potential fraud ring.

**Validates: Requirements 19.2**

### Property 49: Fraud Ring Score Elevation

For any transaction involving an entity in a detected fraud ring, the fraud score should be increased by 0.2 compared to the same transaction without fraud ring membership.

**Validates: Requirements 19.3**


## Error Handling

### Backend Error Handling

**Transaction Processing Errors:**
- Invalid transaction data: Log error, skip transaction, continue processing
- Graph update failure: Retry once, log error if fails, continue with stale graph
- GNN inference failure: Fall back to rule-based scoring only, log warning
- Timeout (>200ms): Log performance warning, complete processing, flag for investigation

**Claude API Errors:**
- API timeout (>5 seconds): Return fallback rule-based explanation
- API rate limit: Queue explanation request, return "Explanation pending" message
- API authentication error: Log critical error, return fallback explanation, alert operator
- Network error: Retry once with exponential backoff, fall back to rule-based explanation

**WebSocket Errors:**
- Client disconnection: Clean up client state, log disconnection
- Message serialization error: Log error, skip message, continue streaming
- Broadcast failure: Log error, continue with other clients
- Connection limit exceeded: Reject new connection with 503 error

**Graph Engine Errors:**
- Memory limit exceeded: Trigger graph pruning (remove old edges), log warning
- Query timeout: Return partial results, log performance warning
- Invalid entity ID: Return empty result, log warning
- Cycle detection in fraud ring: Break cycle arbitrarily, log warning

**Fairness Monitor Errors:**
- Insufficient data for segment: Skip segment in FPR calculation, log info
- Division by zero (no transactions): Set FPR to 0, log info
- Segment definition error: Use default segmentation, log error

### Frontend Error Handling

**WebSocket Errors:**
- Connection failure: Display "Disconnected" indicator, attempt reconnection every 5 seconds
- Message parse error: Log error to console, skip message, continue processing
- Unexpected message type: Log warning, ignore message

**REST API Errors:**
- Network error: Display error toast, retry after 5 seconds
- 500 server error: Display error message, provide manual retry button
- Timeout: Display timeout message, provide retry button
- 404 not found: Log error, display "Data not available" message

**Visualization Errors:**
- D3.js rendering error: Log error, display fallback message "Graph unavailable"
- Invalid graph data: Log error, render with available valid data
- Performance degradation (>1000 nodes): Display warning, limit rendering to most recent 500 nodes

**State Management Errors:**
- Invalid state update: Log error, revert to previous valid state
- Memory leak detection: Clear old data (>1 hour), log warning

### Error Recovery Strategies

**Graceful Degradation:**
- If GNN fails: Use rule-based scoring only (reduced accuracy, but functional)
- If Claude fails: Use template-based explanations (reduced quality, but functional)
- If graph query slow: Use cached features (stale data, but functional)
- If WebSocket fails: Fall back to polling REST API every 5 seconds

**Circuit Breaker Pattern:**
- Claude API: After 3 consecutive failures, stop calling for 60 seconds, use fallback
- Graph queries: After 5 consecutive timeouts, reduce query complexity for 60 seconds

**Retry Logic:**
- Transient failures: Retry once with exponential backoff (100ms, 200ms)
- Network errors: Retry up to 3 times with 1-second delay
- API rate limits: Exponential backoff starting at 5 seconds

**Logging and Monitoring:**
- Error severity levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log all errors with context (transaction ID, entity ID, timestamp)
- Aggregate error metrics: error rate, error types, affected components
- Alert on critical errors: Claude API auth failure, database corruption, memory exhaustion


## Testing Strategy

### Dual Testing Approach

FraudMesh requires both unit testing and property-based testing for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property tests**: Verify universal properties across all inputs through randomization

Together, these approaches provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness across the input space.

### Property-Based Testing

**Framework Selection:**
- Python backend: **Hypothesis** (mature, well-integrated with pytest)
- JavaScript frontend: **fast-check** (TypeScript support, good React integration)

**Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Timeout: 30 seconds per property test
- Shrinking enabled to find minimal failing examples
- Seed-based reproducibility for debugging

**Property Test Structure:**

Each property test must reference its design document property using a comment tag:

```python
# Feature: fraudmesh, Property 1: Transaction Processing Latency
@given(st.builds(Transaction))
@settings(max_examples=100)
def test_transaction_processing_latency(transaction):
    start_time = time.time()
    fraud_score = detector.compute_fraud_score(transaction)
    latency_ms = (time.time() - start_time) * 1000
    
    # 95th percentile requirement - collect latencies
    assert latency_ms < 500  # Generous upper bound for individual test
```

**Property Test Coverage:**

Performance Properties (Properties 1-3, 7, 10, 23, 25, 32, 42, 43, 46):
- Generate random transactions with varying complexity
- Measure latency for each operation
- Assert latency requirements are met
- Track 95th percentile across test runs

Graph Structure Properties (Properties 4-6, 16):
- Generate random transaction sequences
- Verify graph structure matches expected topology
- Check entity nodes and edges are created correctly
- Verify history retention windows

Scoring Properties (Properties 8-12, 22, 39, 49):
- Generate random transactions with known features
- Verify fraud scores are in valid ranges
- Verify score composition includes all components
- Verify score elevation for risk factors

Anomaly Detection Properties (Properties 13-15, 47-48):
- Generate transaction sequences with embedded anomalies
- Verify anomalies are detected and flagged
- Verify triggered rules match expected patterns

Threshold Properties (Properties 17-21):
- Generate transactions at different times and amounts
- Verify threshold adjustments match specifications
- Verify threshold bounds are enforced

Data Structure Properties (Properties 24, 27, 44-45):
- Generate random fraud alerts
- Verify all required fields are present
- Verify data types are correct
- Verify nested structures are complete

Simulator Properties (Properties 28-31):
- Run simulator for fixed time windows
- Measure generation rate, fraud rate, pattern diversity
- Verify fraud rings are created with correct topology

Fairness Properties (Properties 33-35):
- Generate transactions across different segments
- Verify FPR tracking across all dimensions
- Verify fairness alerts trigger correctly

### Unit Testing

**Backend Unit Tests:**

Transaction Simulator:
- Test fraud ring creation with specific device/IP sharing
- Test fraud pattern embedding (each of 5 types)
- Test edge cases: empty entity IDs, negative amounts, future timestamps

Graph Engine:
- Test entity node creation and updates
- Test edge creation for all edge types
- Test neighborhood queries with various hop counts
- Test fraud ring detection with 2, 3, 4+ entities
- Test graph pruning (remove old edges)
- Test edge cases: disconnected nodes, self-loops, duplicate edges

Fraud Detector:
- Test each structural rule individually
- Test each temporal rule individually
- Test GNN model with mock graph data
- Test fraud pattern classification logic
- Test score combination formula
- Test edge cases: zero features, missing history, null values

Threshold Engine:
- Test each threshold adjustment factor individually
- Test threshold bounds enforcement
- Test threshold history tracking
- Test edge cases: midnight boundary, exactly $1000, exactly 5% fraud rate

Claude Explainer:
- Test prompt construction with various fraud cases
- Test explanation parsing from API response
- Test fallback explanation generation
- Test timeout handling
- Test edge cases: empty triggered rules, missing features

Fairness Monitor:
- Test FPR calculation for each segment
- Test demographic parity score calculation
- Test fairness alert generation
- Test edge cases: zero transactions, all false positives, missing segments

FastAPI Application:
- Test each REST endpoint with valid requests
- Test WebSocket connection establishment
- Test WebSocket message broadcasting
- Test concurrent client handling
- Test error responses (400, 404, 500)
- Test edge cases: malformed JSON, missing auth, rate limiting

**Frontend Unit Tests:**

Component Tests (React Testing Library):
- Test GraphView renders with empty graph
- Test GraphView renders with nodes and edges
- Test AlertPanel displays alerts in correct order
- Test ExplainCard displays all explanation fields
- Test FairnessPanel displays segments and alerts
- Test ThresholdMeter displays current value and history

Integration Tests:
- Test WebSocket connection and message handling
- Test REST API data fetching on mount
- Test state updates from WebSocket messages
- Test user interactions (node click, zoom, pan)
- Test error handling (connection loss, API errors)

**Integration Testing:**

End-to-End Flow:
1. Start backend with simulator
2. Connect frontend via WebSocket
3. Verify transactions stream to frontend
4. Verify fraud alerts appear in UI
5. Verify graph updates in real-time
6. Verify Claude explanations are displayed
7. Verify fairness metrics update

Performance Testing:
- Load test: 20 transactions/second for 5 minutes
- Verify 95th percentile latency <200ms
- Verify memory usage stays below 100 MB
- Verify no memory leaks over 30-minute run

Fraud Detection Accuracy:
- Test dataset: 1000 transactions (50 fraudulent, 950 legitimate)
- Measure recall (true positives / actual fraud)
- Measure precision (true positives / flagged transactions)
- Measure false positive rate
- Verify recall >85%, FPR <8%

### Test Data Generation

**Hypothesis Strategies (Python):**

```python
# Transaction generator
@st.composite
def transaction_strategy(draw):
    return Transaction(
        id=draw(st.uuids()),
        user_id=draw(st.text(min_size=5, max_size=20)),
        merchant_id=draw(st.text(min_size=5, max_size=20)),
        device_id=draw(st.text(min_size=10, max_size=40)),
        ip_address=draw(st.ip_addresses(v=4)),
        amount=draw(st.floats(min_value=1.0, max_value=10000.0)),
        timestamp=draw(st.datetimes()),
        location=draw(st.tuples(
            st.floats(min_value=-90, max_value=90),
            st.floats(min_value=-180, max_value=180)
        )),
        is_fraudulent=draw(st.booleans()),
        fraud_pattern=draw(st.one_of(st.none(), st.sampled_from([
            "Account Takeover",
            "Synthetic Identity Fraud",
            "Money Mule Operation",
            "Coordinated Fraud Ring",
            "Card-Not-Present Fraud"
        ])))
    )

# Fraud ring generator
@st.composite
def fraud_ring_strategy(draw):
    size = draw(st.integers(min_value=3, max_value=10))
    device_id = draw(st.text(min_size=10, max_size=40))
    user_ids = [draw(st.text(min_size=5, max_size=20)) for _ in range(size)]
    return FraudRing(device_id=device_id, user_ids=user_ids)
```

**fast-check Arbitraries (JavaScript):**

```javascript
// Transaction arbitrary
const transactionArbitrary = fc.record({
    id: fc.uuid(),
    user_id: fc.string({ minLength: 5, maxLength: 20 }),
    merchant_id: fc.string({ minLength: 5, maxLength: 20 }),
    amount: fc.float({ min: 1.0, max: 10000.0 }),
    timestamp: fc.date(),
    fraud_score: fc.float({ min: 0.0, max: 1.0 })
});

// Alert arbitrary
const alertArbitrary = fc.record({
    alert_id: fc.uuid(),
    transaction: transactionArbitrary,
    fraud_score: fc.record({
        score: fc.float({ min: 0.0, max: 1.0 }),
        triggered_rules: fc.array(fc.string(), { minLength: 0, maxLength: 5 }),
        fraud_pattern: fc.constantFrom(
            "Account Takeover",
            "Synthetic Identity Fraud",
            "Money Mule Operation",
            "Coordinated Fraud Ring",
            "Card-Not-Present Fraud"
        )
    })
});
```

### Continuous Testing

**Pre-commit Hooks:**
- Run unit tests on changed files
- Run linting and type checking
- Verify no console.log statements in production code

**CI/CD Pipeline:**
1. Run all unit tests (backend + frontend)
2. Run property tests with 100 iterations
3. Run integration tests
4. Measure code coverage (target: >80%)
5. Run performance benchmarks
6. Generate test report

**Test Metrics:**
- Code coverage: >80% line coverage, >70% branch coverage
- Property test pass rate: 100% (no flaky tests)
- Performance test pass rate: >95% (allow occasional variance)
- Integration test pass rate: 100%

