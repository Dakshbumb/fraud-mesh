# FraudMesh Backend Setup Guide

## Quick Start (5 minutes)

### Step 1: Install Python Dependencies

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

**Get a Gemini API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste it in your `.env` file

### Step 3: Test the Backend

```bash
cd backend
python test_backend.py
```

You should see:
```
✅ All core backend components are working!
```

### Step 4: Start the Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
🚀 Starting FraudMesh...
✅ Google Gemini initialized
📊 Pre-generating graph history...
✅ Graph initialized with X nodes
✅ FraudMesh ready!
📡 WebSocket: ws://localhost:8000/ws/transactions
🌐 REST API: http://localhost:8000/api/
```

### Step 5: Test the API

Open your browser and visit:
- http://localhost:8000 - Health check
- http://localhost:8000/api/stats - System statistics
- http://localhost:8000/api/graph - Graph data
- http://localhost:8000/api/alerts - Fraud alerts

## What's Running?

The backend is now:
- ✅ Generating realistic transactions (10/second)
- ✅ Building entity relationship graph
- ✅ Detecting fraud patterns
- ✅ Computing adaptive thresholds
- ✅ Generating AI explanations with Gemini
- ✅ Monitoring fairness across segments
- ✅ Streaming data via WebSocket

## Architecture

```
Transaction Simulator
        ↓
   Graph Engine (NetworkX)
        ↓
   Fraud Detector (GNN + Rules)
        ↓
   Threshold Engine (Adaptive)
        ↓
   Gemini Explainer (AI)
        ↓
   WebSocket Broadcast
```

## API Endpoints

### REST API

- `GET /` - Health check
- `GET /api/graph` - Current graph state (nodes & edges)
- `GET /api/alerts` - Recent fraud alerts (last 50)
- `GET /api/stats` - System metrics
- `GET /api/fairness` - Fairness metrics by segment
- `GET /api/threshold-history` - Threshold history (60 min)
- `GET /api/graph/neighborhood/{entity_id}` - Entity neighborhood

### WebSocket

- `WS /ws/transactions` - Real-time transaction stream

Connect with:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transactions');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created the `.env` file in the project root
- Check that the API key is correctly set
- Restart the server after adding the key

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version` (should be 3.10+)

### "Port 8000 already in use"
- Stop any other process using port 8000
- Or use a different port: `uvicorn main:app --port 8001`

### Gemini API errors
- Verify your API key is valid
- Check you have API quota remaining
- The system will use fallback explanations if Gemini fails

## Performance Targets

The backend is designed to meet these targets:
- ⚡ Transaction processing: <200ms (95th percentile)
- 🤖 Gemini explanations: <3 seconds
- 📊 Graph updates: <50ms
- 🔄 WebSocket broadcast: <100ms

## Next Steps

Once the backend is running:
1. ✅ Backend is complete and working
2. 🔄 Frontend implementation (React dashboard)
3. 🎨 D3.js graph visualization
4. 📊 Recharts metrics dashboards

## Demo Data

The simulator generates:
- 200 users (user_0000 - user_0199)
- 50 merchants (merchant_000 - merchant_049)
- 80 devices (device_000 - device_079)
- 60 IP addresses
- 5 hidden fraud rings (4 users each)
- 6 fraud pattern types
- ~6% fraud rate

Within 30 seconds of starting, you should see:
- ✅ First fraud alert
- ✅ Fraud ring detection
- ✅ AI-generated explanations
- ✅ Adaptive threshold adjustments

## Monitoring

Watch the console output for:
- Transaction processing rate
- Fraud alerts
- Gemini API calls
- WebSocket connections
- Error messages

## Support

If you encounter issues:
1. Check the console output for error messages
2. Run `python test_backend.py` to verify components
3. Check that all dependencies are installed
4. Verify your Gemini API key is valid

Happy fraud detecting! 🔐
