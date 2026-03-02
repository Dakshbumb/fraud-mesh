# FraudMesh — Real-Time Graph-Based Fraud Detection

FraudMesh is an adaptive, real-time fraud detection platform that models financial entities and their relationships as a living graph. The system combines Graph Neural Networks for relational anomaly detection, a context-aware adaptive threshold engine, and Claude Opus 4.5 for natural language fraud explanations.

## Features

- **Real-Time Graph Visualization**: Live D3.js visualization of entity relationships with fraud clusters highlighted
- **Graph Neural Network Scoring**: Neighborhood-aware risk propagation across connected entities
- **Adaptive Thresholds**: Context-aware fraud detection sensitivity based on time, amount, and network fraud rate
- **AI-Powered Explanations**: Claude Opus 4.5 generates human-readable fraud analysis for every alert
- **Fairness Monitoring**: Continuous auditing of false positive rates across user segments
- **WebSocket Streaming**: Real-time transaction processing with <200ms latency

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  - GraphView (D3.js force-directed graph)                   │
│  - AlertPanel (fraud alert feed)                            │
│  - ExplainCard (Claude explanations)                        │
│  - FairnessPanel (bias monitoring)                          │
│  - ThresholdMeter (adaptive threshold visualization)        │
└─────────────────────────────────────────────────────────────┘
                            │
                    WebSocket + REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - Transaction Simulator (realistic fraud patterns)         │
│  - Graph Engine (NetworkX entity relationships)             │
│  - Fraud Detector (GNN + rule-based scoring)                │
│  - Threshold Engine (adaptive sensitivity)                  │
│  - Claude Explainer (Anthropic API integration)             │
│  - Fairness Monitor (bias detection)                        │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google Gemini API key (for AI-powered fraud explanations)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fraudmesh
```

### 2. Set Up Environment Variables

Copy the example environment file and add your Google Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and replace `your_gemini_api_key_here` with your actual API key.

To get a Gemini API key:
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy it to your `.env` file

### 3. Backend Setup

Create a Python virtual environment and install dependencies:

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Frontend Setup

Install Node.js dependencies:

```bash
cd frontend
npm install
```

## Running the Application

### Option 1: Using the Start Script (Recommended)

From the project root directory:

```bash
# On Windows
.\start.sh

# On macOS/Linux
bash start.sh
```

This will start both the backend and frontend servers simultaneously.

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
# Activate virtual environment first
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Open the Dashboard

Navigate to `http://localhost:5173` in your web browser.

## Usage

Once the application is running:

1. **Watch the Live Graph**: The entity graph updates in real-time as transactions are processed
2. **Monitor Fraud Alerts**: Alerts appear in the right panel when fraud is detected
3. **View AI Explanations**: Click any alert to see Claude's detailed fraud analysis
4. **Check Fairness Metrics**: Switch to the Fairness Dashboard tab to monitor bias
5. **Track Adaptive Threshold**: Observe how the threshold adjusts based on context

## API Endpoints

### REST API

- `GET /api/graph` - Current graph state (nodes and edges)
- `GET /api/alerts` - Recent fraud alerts (last 50)
- `GET /api/stats` - System metrics (transaction rate, fraud rate, etc.)
- `GET /api/fairness` - Fairness metrics by segment
- `GET /api/threshold-history` - Threshold history (last 60 minutes)
- `GET /api/graph/neighborhood/:entity_id` - Entity neighborhood data

### WebSocket

- `WS /ws/transactions` - Real-time stream of transactions, alerts, and updates

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Property-Based Tests

```bash
cd backend
pytest -m property
```

## Performance Targets

- Transaction processing: <200ms (95th percentile)
- Claude explanation generation: <3 seconds
- Dashboard update frequency: 800ms
- Fraud detection recall: >85%
- False positive rate: <8%

## Technology Stack

**Backend:**
- FastAPI (async web framework)
- NetworkX (graph data structure)
- PyTorch Geometric (GNN implementation)
- Google Gemini API (AI-powered explanations)
- Hypothesis (property-based testing)

**Frontend:**
- React 18 (UI framework)
- D3.js (graph visualization)
- Recharts (metrics dashboards)
- Tailwind CSS (styling)
- fast-check (property-based testing)

## Project Structure

```
fraudmesh/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── data_simulator.py       # Transaction generator
│   ├── graph_engine.py         # NetworkX graph management
│   ├── fraud_detector.py       # Fraud scoring engine
│   ├── threshold_engine.py     # Adaptive threshold
│   ├── claude_explainer.py     # Claude API integration
│   ├── fairness_monitor.py     # Bias detection
│   ├── gnn_model.py            # Graph Neural Network
│   ├── models.py               # Data models
│   ├── utils.py                # Utility functions
│   └── requirements.txt        # Python dependencies
├── frontend/
│   └── src/
│       ├── App.jsx             # Main application
│       ├── GraphView.jsx       # D3.js graph visualization
│       ├── AlertPanel.jsx      # Fraud alert feed
│       ├── ExplainCard.jsx     # Claude explanation display
│       ├── FairnessPanel.jsx   # Fairness dashboard
│       └── ThresholdMeter.jsx  # Threshold visualization
├── docs/                       # Documentation
├── .env.example                # Environment variables template
├── README.md                   # This file
└── start.sh                    # Startup script
```

## Troubleshooting

**Backend won't start:**
- Ensure Python 3.10+ is installed: `python --version`
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip list`
- Verify GEMINI_API_KEY is set in `.env`

**Frontend won't start:**
- Ensure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running on port 8000

**WebSocket connection fails:**
- Verify backend is running and accessible at `http://localhost:8000`
- Check browser console for connection errors
- Ensure no firewall is blocking WebSocket connections

**Claude API errors:**
- Verify your API key is valid and has sufficient credits
- Check Google AI Studio status
- Review backend logs for detailed error messages

## License

This project is a hackathon prototype for demonstration purposes.

## Acknowledgments

- Built for the FinTech Fraud Detection hackathon track
- Powered by Google Gemini API
- Graph visualization with D3.js
