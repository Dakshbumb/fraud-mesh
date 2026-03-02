# Implementation Plan: FraudMesh

## Overview

This implementation plan breaks down the FraudMesh fraud detection platform into sequential, actionable tasks. The system combines a Python/FastAPI backend with a React frontend to provide real-time fraud detection with graph visualization, adaptive thresholding, and AI-powered explanations.

The implementation follows a bottom-up approach: core backend components first, then API layer, then frontend components, and finally integration and testing.

## Tasks

- [x] 1. Project setup and infrastructure
  - Create project directory structure (backend/, frontend/, docs/)
  - Set up Python virtual environment with requirements.txt
  - Set up React frontend with Vite
  - Create .env.example file for API keys
  - Create README.md with setup instructions
  - _Requirements: All_

- [x] 2. Backend core data models and utilities
  - [x] 2.1 Create data models in backend/models.py
    - Implement Transaction, EntityNode, GraphEdge, FraudScore, FraudAlert, FraudExplanation, SystemStats, FairnessMetrics dataclasses
    - Add type hints and validation
    - _Requirements: 2.1, 7.3, 8.3_
  
  - [ ]* 2.2 Write property test for data model structure
    - **Property 24: Alert Structure Completeness**
    - **Validates: Requirements 7.3**
  
  - [x] 2.3 Create utility functions in backend/utils.py
    - Implement haversine_distance for geographic calculations
    - Implement time window helpers (is_within_window)
    - Implement set merging for fraud ring detection
    - _Requirements: 5.3, 4.1_

- [x] 3. Transaction simulator implementation
  - [x] 3.1 Implement TransactionSimulator class in backend/data_simulator.py
    - Create generate_transaction method with fraud pattern logic
    - Implement create_fraud_ring method for coordinated fraud
    - Implement stream_transactions async generator
    - Support 5 fraud pattern types: Account Takeover, Synthetic Identity, Money Mule, Fraud Ring, CNP Fraud
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 13.1_
  
  - [ ]* 3.2 Write property tests for transaction simulator
    - **Property 28: Transaction Generation Rate**
    - **Property 29: Fraud Pattern Diversity**
    - **Property 30: Fraud Ring Pattern Generation**
    - **Property 31: Simulated Fraud Rate**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
  
  - [ ]* 3.3 Write unit tests for fraud pattern generation
    - Test each of 5 fraud pattern types individually
    - Test edge cases: empty entity IDs, negative amounts
    - _Requirements: 9.2, 13.1_

- [x] 4. Graph engine implementation
  - [x] 4.1 Implement GraphEngine class in backend/graph_engine.py
    - Initialize NetworkX graph
    - Implement add_transaction method (create/update nodes and edges)
    - Implement get_entity_features method (degree, velocity, neighbor_risk)
    - Implement detect_fraud_rings method (device and IP clustering)
    - Implement get_neighborhood method (N-hop queries)
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 4.1, 19.1, 19.2_
  
  - [ ]* 4.2 Write property tests for graph structure
    - **Property 4: Entity Node Creation**
    - **Property 5: Device Sharing Edge Creation**
    - **Property 6: IP Sharing Edge Creation**
    - **Property 7: Neighborhood Query Performance**
    - **Property 16: Transaction History Retention**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.5, 5.4**
  
  - [ ]* 4.3 Write property tests for fraud ring detection
    - **Property 47: Device-Based Fraud Ring Detection**
    - **Property 48: IP-Based Fraud Ring Detection**
    - **Validates: Requirements 19.1, 19.2**
  
  - [ ]* 4.4 Write unit tests for graph operations
    - Test edge creation for all 4 edge types
    - Test graph pruning (remove old edges)
    - Test edge cases: disconnected nodes, duplicate edges
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Checkpoint - Core data structures complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. GNN model implementation
  - [x] 6.1 Implement GNNModel class in backend/gnn_model.py
    - Create PyTorch Geometric model with 2 GCN layers
    - Implement forward pass with 10-dimensional node features
    - Implement extract_node_features helper function
    - Add CPU inference support (no GPU required)
    - _Requirements: 3.1, 3.3_
  
  - [ ]* 6.2 Write property tests for GNN inference
    - **Property 8: Fraud Score Range Validity**
    - **Property 10: GNN Inference Latency**
    - **Validates: Requirements 3.1, 3.3**
  
  - [ ]* 6.3 Write unit tests for GNN model
    - Test model initialization
    - Test forward pass with mock graph data
    - Test edge cases: single node, disconnected graph
    - _Requirements: 3.1_

- [x] 7. Fraud detection engine implementation
  - [x] 7.1 Implement RuleEngine class in backend/fraud_detector.py
    - Implement 4 structural rules (device_sharing, ip_sharing, fraud_ring, new_account)
    - Implement 4 temporal rules (velocity, timing, geographic, amount)
    - _Requirements: 4.1, 5.1, 5.2, 5.3_
  
  - [x] 7.2 Implement FraudDetector class in backend/fraud_detector.py
    - Implement compute_fraud_score method (combine GNN + rules)
    - Implement classify_fraud_pattern method
    - Implement assemble_fraud_case_context method
    - Use 0.4 GNN + 0.3 structural + 0.3 temporal weighting
    - _Requirements: 3.4, 13.2, 13.3, 17.1, 17.2_
  
  - [ ]* 7.3 Write property tests for anomaly detection
    - **Property 13: Velocity Anomaly Detection**
    - **Property 14: Timing Anomaly Detection**
    - **Property 15: Geographic Anomaly Detection**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [ ]* 7.4 Write property tests for fraud scoring
    - **Property 9: Neighbor Risk Propagation**
    - **Property 11: Fraud Score Composition**
    - **Property 12: Structural Anomaly Score Elevation**
    - **Property 22: Alert Generation Trigger**
    - **Property 39: Fraud Pattern Assignment**
    - **Property 49: Fraud Ring Score Elevation**
    - **Validates: Requirements 3.2, 3.4, 4.1, 4.4, 7.1, 13.2, 13.3, 19.3**
  
  - [ ]* 7.5 Write unit tests for fraud detection
    - Test each structural rule individually
    - Test each temporal rule individually
    - Test fraud pattern classification logic
    - Test edge cases: zero features, missing history
    - _Requirements: 4.1, 5.1, 5.2, 5.3, 13.2_

- [x] 8. Adaptive threshold engine implementation
  - [x] 8.1 Implement ThresholdEngine class in backend/threshold_engine.py
    - Implement compute_adaptive_threshold method
    - Add time-based adjustment (night: -0.1)
    - Add amount-based adjustment (>$1000: -0.05)
    - Add network fraud rate adjustment (>5%: -0.15)
    - Add FPR adjustment (>10%: +0.05)
    - Enforce bounds [0.2, 0.8]
    - Implement get_threshold_factors method
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 8.2 Write property tests for threshold adjustments
    - **Property 17: Night-Time Threshold Adjustment**
    - **Property 18: High-Amount Threshold Adjustment**
    - **Property 19: Network Fraud Rate Threshold Adjustment**
    - **Property 20: False Positive Rate Threshold Adjustment**
    - **Property 21: Threshold Update Frequency**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  
  - [ ]* 8.3 Write unit tests for threshold engine
    - Test each adjustment factor individually
    - Test threshold bounds enforcement
    - Test edge cases: midnight boundary, exactly $1000
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 9. Claude explainer implementation
  - [x] 9.1 Implement ClaudeExplainer class in backend/claude_explainer.py
    - Initialize Anthropic client with API key
    - Implement explain_fraud async method
    - Implement _build_prompt method with structured template
    - Add timeout handling (5 seconds)
    - Add fallback to rule-based explanation on failure
    - Parse response into FraudExplanation dataclass
    - _Requirements: 8.1, 8.2, 8.3, 8.5, 17.3_
  
  - [ ] 9.2 Write property tests for explanation generation
    - **Property 25: Explanation Generation Latency**
    - **Property 26: Explanation Input Completeness**
    - **Property 27: Explanation Structure Completeness**
    - **Property 45: Claude Explainer Input Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.5, 17.3**
  
  - [ ]* 9.3 Write unit tests for Claude explainer
    - Test prompt construction with various fraud cases
    - Test explanation parsing from mock API response
    - Test fallback explanation generation
    - Test timeout handling
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 10. Fairness monitor implementation
  - [x] 10.1 Implement FairnessMonitor class in backend/fairness_monitor.py
    - Implement record_alert method (track by segment)
    - Implement compute_fairness_metrics method (FPR by segment)
    - Implement detect_bias_alerts method (FPR > 2x baseline)
    - Support 3 segmentation dimensions: region, amount band, account age
    - Calculate demographic parity score (max FPR / min FPR)
    - _Requirements: 11.1, 11.2, 11.4_
  
  - [ ]* 10.2 Write property tests for fairness monitoring
    - **Property 33: Fairness Monitoring Segmentation**
    - **Property 34: Fairness Alert Generation**
    - **Property 35: Demographic Parity Computation Frequency**
    - **Validates: Requirements 11.1, 11.2, 11.4**
  
  - [ ]* 10.3 Write unit tests for fairness monitor
    - Test FPR calculation for each segment
    - Test demographic parity score calculation
    - Test edge cases: zero transactions, all false positives
    - _Requirements: 11.1, 11.2_

- [x] 11. Checkpoint - All backend components complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. FastAPI application and endpoints
  - [x] 12.1 Create FastAPI app in backend/main.py
    - Set up FastAPI application with lifespan context manager
    - Initialize all components (GraphEngine, FraudDetector, ThresholdEngine, ClaudeExplainer, FairnessMonitor, TransactionSimulator)
    - Implement process_transaction_stream background task
    - Add CORS middleware for frontend communication
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 12.2 Implement REST API endpoints in backend/main.py
    - GET /api/graph: Return current graph state
    - GET /api/alerts: Return last 50 fraud alerts with pagination
    - GET /api/stats: Return system metrics
    - GET /api/fairness: Return fairness metrics by segment
    - GET /api/threshold-history: Return threshold history for last 60 min
    - GET /api/graph/neighborhood/:entity_id: Return N-hop neighborhood
    - _Requirements: 2.5, 7.3, 11.1, 15.5, 18.4_
  
  - [ ]* 12.3 Write property tests for API performance
    - **Property 43: REST API Response Latency**
    - **Validates: Requirements 15.5**
  
  - [x] 12.4 Implement WebSocket endpoint in backend/main.py
    - WS /ws/transactions: Real-time bidirectional communication
    - Handle client subscription to channels
    - Broadcast transaction updates, fraud alerts, graph updates, stats updates
    - Implement connection management (max 5 clients)
    - Add heartbeat ping/pong every 30 seconds
    - _Requirements: 1.3, 7.2, 12.2, 12.4, 18.4_
  
  - [ ]* 12.5 Write property tests for WebSocket communication
    - **Property 3: WebSocket Broadcast Latency**
    - **Property 23: Alert Broadcast Latency**
    - **Property 36: WebSocket Message Type Coverage**
    - **Property 37: WebSocket Reconnection Behavior**
    - **Validates: Requirements 1.3, 7.2, 12.2, 12.4**
  
  - [ ]* 12.6 Write unit tests for FastAPI endpoints
    - Test each REST endpoint with valid requests
    - Test WebSocket connection establishment
    - Test error handling for invalid requests
    - _Requirements: 2.5, 7.3, 12.2_

- [x] 13. Transaction processing pipeline integration
  - [x] 13.1 Implement main processing loop in backend/main.py
    - Consume transactions from simulator stream
    - Update graph with transaction
    - Compute fraud score
    - Compare against adaptive threshold
    - Generate alert if threshold exceeded
    - Request Claude explanation asynchronously
    - Broadcast updates via WebSocket
    - Track performance metrics
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 7.1, 7.2, 8.1_
  
  - [ ]* 13.2 Write property tests for processing pipeline
    - **Property 1: Transaction Processing Latency**
    - **Property 2: Graph Update Latency**
    - **Property 44: Fraud Case Context Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.4, 17.1, 17.2**
  
  - [ ]* 13.3 Write integration tests for end-to-end flow
    - Test transaction → graph update → fraud detection → alert → explanation
    - Test error handling and fallback mechanisms
    - _Requirements: 1.1, 1.2, 1.3, 7.1, 7.2, 8.1_

- [x] 14. Checkpoint - Backend complete and tested
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Frontend project setup
  - [ ] 15.1 Initialize React project with Vite in frontend/
    - Set up TypeScript configuration
    - Install dependencies: react, react-dom, d3, recharts, tailwindcss
    - Configure Tailwind CSS with dark mode
    - Create src/ directory structure (components/, hooks/, utils/)
    - _Requirements: 10.1, 10.2_
  
  - [ ] 15.2 Create WebSocket hook in frontend/src/hooks/useWebSocket.js
    - Implement WebSocket connection management
    - Handle reconnection logic (every 5 seconds)
    - Parse incoming messages by type
    - Expose connection state and message handlers
    - _Requirements: 12.4_

- [ ] 16. Frontend core components
  - [ ] 16.1 Implement App.jsx main component
    - Set up global state management (transactions, alerts, graphData, stats, fairnessMetrics)
    - Initialize WebSocket connection
    - Handle WebSocket message routing
    - Create responsive grid layout
    - _Requirements: 10.1, 12.2_
  
  - [ ] 16.2 Implement Header component
    - Display connection status indicator
    - Show system title and branding
    - _Requirements: 10.1_
  
  - [ ] 16.3 Implement SystemStats component
    - Display transaction rate, fraud rate, active entities
    - Update every 5 seconds from WebSocket
    - _Requirements: 18.4_

- [ ] 17. Graph visualization implementation
  - [ ] 17.1 Implement GraphView component with D3.js
    - Create SVG canvas with zoom and pan
    - Implement force-directed layout simulation
    - Render nodes with color coding by entity type and fraud status
    - Render edges with labels
    - Add node click handler for neighborhood details
    - Implement debounced updates (max 1 per 800ms)
    - _Requirements: 10.2, 14.3_
  
  - [ ]* 17.2 Write property test for graph visualization performance
    - **Property 32: Graph Visualization Update Latency**
    - **Validates: Requirements 10.2**
  
  - [ ]* 17.3 Write unit tests for GraphView component
    - Test node rendering with various entity types
    - Test edge rendering
    - Test zoom and pan interactions
    - _Requirements: 10.2_

- [ ] 18. Alert and explanation components
  - [ ] 18.1 Implement AlertPanel component
    - Display scrollable feed of last 50 alerts
    - Implement AlertCard with expandable details
    - Show fraud score, amount, timestamp, pattern badge
    - _Requirements: 7.3, 10.1_
  
  - [ ] 18.2 Implement ExplainCard component
    - Display Claude explanation with headline, narrative
    - Show fraud pattern, confidence, recommendation
    - Display key signal and generation time
    - Color-code recommendation (Block=red, Review=amber, Approve=green)
    - _Requirements: 8.3, 8.5_
  
  - [ ]* 18.3 Write unit tests for alert components
    - Test AlertCard rendering with various fraud patterns
    - Test ExplainCard rendering with different recommendations
    - _Requirements: 7.3, 8.3_

- [ ] 19. Threshold and fairness visualization
  - [ ] 19.1 Implement ThresholdMeter component
    - Display current adaptive threshold value
    - Show gradient bar visualization
    - Display threshold history line chart (last 60 min)
    - Show adjustment factors breakdown
    - _Requirements: 6.5_
  
  - [ ] 19.2 Implement FairnessPanel component
    - Display baseline FPR
    - Show FPR by segment bar chart (Recharts)
    - Highlight biased segments (FPR > 2x baseline) in red
    - Display demographic parity score
    - Show bias alerts
    - _Requirements: 11.1, 11.2, 11.4_
  
  - [ ]* 19.3 Write unit tests for visualization components
    - Test ThresholdMeter with various threshold values
    - Test FairnessPanel with biased and unbiased segments
    - _Requirements: 6.5, 11.1, 11.2_

- [ ] 20. Checkpoint - Frontend components complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Frontend-backend integration
  - [ ] 21.1 Wire WebSocket message handlers in App.jsx
    - Handle "transaction" messages → update graphData
    - Handle "alert" messages → update alerts feed
    - Handle "stats_update" messages → update stats
    - Handle "graph_update" messages → update fraud rings
    - Handle "fairness_alert" messages → update fairnessMetrics
    - _Requirements: 1.3, 7.2, 12.2_
  
  - [ ] 21.2 Implement REST API calls for initial data load
    - Fetch /api/graph on mount
    - Fetch /api/alerts on mount
    - Fetch /api/stats on mount
    - Fetch /api/fairness on mount
    - Fetch /api/threshold-history on mount
    - _Requirements: 2.5, 7.3, 11.1_
  
  - [ ]* 21.3 Write integration tests for frontend-backend communication
    - Test WebSocket message handling
    - Test REST API data fetching
    - Test error handling and reconnection
    - _Requirements: 1.3, 7.2, 12.2, 12.4_

- [ ] 22. Error handling and resilience
  - [ ] 22.1 Add backend error handling
    - Add try-catch blocks for transaction processing
    - Implement Claude API fallback explanations
    - Add WebSocket error handling and cleanup
    - Add graph memory limit handling with pruning
    - Log all errors with context
    - _Requirements: 8.1_
  
  - [ ] 22.2 Add frontend error handling
    - Display connection status indicator
    - Show error toasts for API failures
    - Implement retry buttons for failed requests
    - Add fallback UI for visualization errors
    - _Requirements: 12.4_
  
  - [ ]* 22.3 Write unit tests for error scenarios
    - Test Claude API timeout handling
    - Test WebSocket disconnection handling
    - Test invalid data handling
    - _Requirements: 8.1, 12.4_

- [ ] 23. Performance optimization
  - [ ] 23.1 Optimize backend performance
    - Add entity feature caching (60 seconds)
    - Implement lazy fraud ring detection (every 5 minutes)
    - Add graph pruning for old edges (>24 hours)
    - Optimize GNN inference with pre-computed embeddings
    - _Requirements: 1.1, 1.4, 5.4_
  
  - [ ] 23.2 Optimize frontend performance
    - Add React.memo for expensive components
    - Implement virtual scrolling for alert feed
    - Throttle D3.js force simulation to 60 FPS
    - Debounce graph updates (max 1 per 800ms)
    - _Requirements: 10.2, 14.3_
  
  - [ ]* 23.3 Write performance tests
    - Test transaction processing under load (20 txns/sec burst)
    - Test graph rendering with 500 nodes
    - Test WebSocket message throughput
    - _Requirements: 1.1, 1.4, 10.2_

- [ ] 24. Documentation and deployment preparation
  - [ ] 24.1 Create comprehensive README.md
    - Add project overview and architecture diagram
    - Document setup instructions for backend and frontend
    - Document environment variables (.env.example)
    - Add usage instructions and demo walkthrough
    - Document API endpoints
    - _Requirements: All_
  
  - [ ] 24.2 Create start.sh script
    - Start backend server (uvicorn)
    - Start frontend dev server (vite)
    - Handle graceful shutdown
    - _Requirements: All_
  
  - [ ] 24.3 Create requirements.txt for Python dependencies
    - fastapi, uvicorn, websockets
    - networkx, torch, torch-geometric
    - anthropic
    - hypothesis (for testing)
    - _Requirements: All_
  
  - [ ] 24.4 Create package.json for frontend dependencies
    - react, react-dom
    - d3, recharts
    - tailwindcss
    - fast-check (for testing)
    - _Requirements: All_

- [ ] 25. End-to-end validation
  - [ ]* 25.1 Write property tests for system-level requirements
    - **Property 40: Fraud Detection Recall**
    - **Property 41: False Positive Rate Limit**
    - **Property 42: Visualization Update Frequency**
    - **Property 46: System Metrics Update Frequency**
    - **Validates: Requirements 14.1, 14.2, 14.3, 18.4**
  
  - [ ]* 25.2 Run full system integration test
    - Start backend and frontend
    - Verify transaction stream processing
    - Verify fraud detection and alerts
    - Verify Claude explanations
    - Verify graph visualization updates
    - Verify fairness monitoring
    - _Requirements: All_
  
  - [ ] 25.3 Validate against acceptance criteria
    - Review all 49 correctness properties
    - Verify performance targets (<200ms processing, <3s explanations)
    - Verify fraud detection metrics (>85% recall, <8% FPR)
    - Verify visualization performance (<800ms updates)
    - _Requirements: All_

- [ ] 26. Final checkpoint - System complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation follows a bottom-up approach: data models → core logic → API → frontend → integration
- Backend uses Python 3.10+ with FastAPI, NetworkX, PyTorch Geometric, and Anthropic SDK
- Frontend uses React 18 with D3.js, Recharts, and Tailwind CSS
- All 49 correctness properties from the design document are covered by property tests
