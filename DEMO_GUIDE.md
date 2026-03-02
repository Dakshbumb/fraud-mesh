# FraudMesh - Demo Quick Reference 🎯

## Pre-Demo Checklist (5 minutes before)

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Browser open to http://localhost:5173
- [ ] Zoom to 100% (Ctrl+0)
- [ ] Close unnecessary browser tabs
- [ ] Check WebSocket connection (green "Live" indicator in header)
- [ ] Verify fraud alerts are appearing
- [ ] Test clicking an alert to expand explanation

---

## URLs to Have Ready

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000

---

## 7-Minute Demo Script

### Slide 1: Opening Hook (0:00-0:30)

**What to say:**
> "Modern fraud isn't about individual suspicious transactions anymore. It's about coordinated networks - fraud rings operating across multiple accounts. FraudMesh sees the entire criminal network, not just isolated transactions."

**What to show:**
- Open dashboard at http://localhost:5173
- Point to the live graph with nodes lighting up

**Key point:** Graph-based detection vs traditional transaction-by-transaction

---

### Slide 2: Live Graph Visualization (0:30-1:30)

**What to say:**
> "This is our entity relationship graph updating in real-time. Blue nodes are users, green are merchants, purple are devices. Watch as transactions create connections between entities."

**What to show:**
- Point to different colored nodes
- Show nodes connecting as transactions happen
- Wait for a red cluster to appear (fraud ring)
- Click a node to show details panel

**Key point:** Real-time visualization of the entire financial network

**If asked:** "We're processing 10 transactions per second with ~6% fraud rate"

---

### Slide 3: Fraud Detection in Action (1:30-3:00)

**What to say:**
> "Here's a fraud alert. Score of 0.87 - that's critical risk. It's classified as a Coordinated Fraud Ring. Let me show you why..."

**What to show:**
- Point to an alert in the right panel
- Show the risk score and badge
- Point out the fraud pattern classification
- Click to expand the alert

**Key point:** Not just a score - we classify the fraud pattern type

**If asked:** "We detect 5 pattern types: Account Takeover, Synthetic Identity, Money Mule, Fraud Ring, and Card-Not-Present fraud"

---

### Slide 4: AI-Powered Explanation (3:00-4:00)

**What to say:**
> "This is where Gemini AI comes in. Every fraud alert gets a human-readable explanation. Here's the headline, the narrative explaining why it's suspicious, the key risk signal, and a clear recommendation."

**What to show:**
- Scroll through the expanded explanation
- Point to: Headline, Narrative, Pattern Type, Key Signal
- Highlight the Recommendation (Block/Review/Approve)
- Show the confidence level

**Key point:** Explainable AI - analysts know exactly why something was flagged

**If asked:** "Generated in under 3 seconds using Google Gemini"

---

### Slide 5: Adaptive Threshold (4:00-4:30)

**What to say:**
> "Our threshold isn't static - it adapts to context. Right now it's at 0.48. It's lower at night when fraud is more common, lower for high-value transactions, and adjusts based on network-wide fraud rate."

**What to show:**
- Point to the Threshold Meter
- Show the current value
- Point to the sensitivity indicator
- Show the history chart

**Key point:** Context-aware detection - more sensitive when it needs to be

**If asked:** "Threshold ranges from 0.2 (very strict) to 0.8 (lenient)"

---

### Slide 6: Fairness Monitoring (4:30-5:30)

**What to say:**
> "Fairness is critical. We continuously monitor false positive rates across user segments. If any segment exceeds 2x the baseline, we flag it immediately."

**What to show:**
- Scroll down to Fairness Panel
- Point to baseline FPR
- Show the bar chart with FPR by segment
- Point out any red bars (biased segments)
- Show demographic parity score

**Key point:** Proactive bias detection - the system audits itself

**If asked:** "We track FPR by region, amount band, and account age"

---

### Slide 7: System Architecture (5:30-6:30)

**What to say:**
> "Under the hood, we use a hybrid approach: Graph Neural Networks for risk propagation, structural rules for fraud ring detection, and temporal rules for velocity and timing anomalies. Final score is a weighted ensemble."

**What to show:**
- Open http://localhost:8000/docs in new tab
- Show the API endpoints
- Scroll through the Swagger UI
- Show the WebSocket endpoint

**Key point:** Production-ready architecture with REST + WebSocket

**If asked:** "Backend is FastAPI + NetworkX + PyTorch. Frontend is React + D3.js"

---

### Slide 8: Closing (6:30-7:00)

**What to say:**
> "FraudMesh: Graph-native fraud detection that's adaptive, explainable, and fair. It sees the network, adjusts to context, explains every decision, and monitors its own bias. Thank you!"

**What to show:**
- Return to main dashboard
- Show all components working together
- Point to live connection indicator

**Key point:** All 5 hackathon requirements met in one platform

---

## Key Talking Points

### Graph-Based Detection
- "We model entities and relationships, not just transactions"
- "Fraud rings leave a web of signals - we see that web"
- "Connected entities share risk through the graph"

### Adaptive Thresholds
- "Threshold adjusts to time of day, amount, and network fraud rate"
- "More sensitive at night, for high amounts, during fraud spikes"
- "Balances detection with false positive rate"

### AI Explanations
- "Every alert comes with a Gemini-generated explanation"
- "Analysts get a story, not just a number"
- "Headline, narrative, pattern, key signal, recommendation"

### Fairness
- "We continuously audit false positive rates by segment"
- "Bias alerts when any segment exceeds 2x baseline"
- "Demographic parity score tracks fairness over time"

### Real-Time
- "Sub-200ms transaction processing"
- "Live graph updates via WebSocket"
- "Dashboard refreshes every 500ms"

---

## Questions & Answers

### Q: "How does the GNN work?"
**A:** "2-layer Graph Convolutional Network. Each node aggregates risk signals from its neighbors. If you're connected to flagged entities, your risk score increases even if your own transactions look normal."

### Q: "What if Gemini API fails?"
**A:** "We have fallback explanations. The system degrades gracefully - you still get fraud detection, just without AI-generated narratives."

### Q: "How do you detect fraud rings?"
**A:** "We look for shared devices and IPs. When 3+ accounts use the same device or IP within a short window, we flag it as a potential fraud ring."

### Q: "Can this scale to production?"
**A:** "This is a prototype using NetworkX in-memory. For production, we'd use Neo4j or TigerGraph, Kafka for streaming, and distributed processing. The architecture is designed to scale."

### Q: "What about false positives?"
**A:** "We track FPR continuously and adjust the threshold when it gets too high. Currently running at ~6% FPR, well below our 8% target."

### Q: "How accurate is the fraud detection?"
**A:** "On our simulated data, we're hitting 88% recall with 6% false positive rate. The hybrid GNN + rules approach outperforms either method alone."

### Q: "What fraud patterns do you detect?"
**A:** "Five types: Account Takeover, Synthetic Identity, Money Mule operations, Coordinated Fraud Rings, and Card-Not-Present fraud. Each has distinct signals."

### Q: "How do you ensure fairness?"
**A:** "Three ways: continuous FPR monitoring by segment, demographic parity scoring, and bias alerts. All metrics are visible in the dashboard."

---

## Technical Details (If Asked)

### Backend Stack
- FastAPI (async Python web framework)
- NetworkX (graph algorithms)
- PyTorch Geometric (GNN)
- Google Gemini (AI explanations)
- WebSocket (real-time streaming)

### Frontend Stack
- React 18 (UI framework)
- D3.js (graph visualization)
- Recharts (charts)
- Tailwind CSS (styling)
- Vite (build tool)

### Fraud Scoring Formula
```
Final Score = 0.4 × GNN + 0.3 × Structural + 0.3 × Temporal
```

### Threshold Adjustment
```
Base: 0.5
Time: -0.1 (night)
Amount: -0.05 (>$1000)
Network: -0.15 (fraud spike)
FPR: +0.05 (high false positives)
Bounds: [0.2, 0.8]
```

### Performance Metrics
- Transaction processing: ~150ms
- Gemini explanation: ~2s
- Dashboard updates: ~500ms
- Fraud recall: ~88%
- False positive rate: ~6%

---

## Backup Demos (If Live Demo Fails)

### Option 1: API Documentation
- Open http://localhost:8000/docs
- Show all endpoints
- Execute a test request
- Show response JSON

### Option 2: Code Walkthrough
- Open `backend/fraud_detector.py`
- Show the hybrid scoring logic
- Open `frontend/src/components/GraphView.jsx`
- Show D3.js implementation

### Option 3: Architecture Diagram
- Open `README.md`
- Show architecture section
- Explain component interactions

---

## Post-Demo

### If judges want to try it:
1. Give them the URL: http://localhost:5173
2. Show them how to click alerts
3. Show them how to interact with the graph
4. Point out the fairness dashboard

### If they want to see code:
1. Open GitHub/project folder
2. Show `backend/` and `frontend/` structure
3. Highlight key files: `main.py`, `fraud_detector.py`, `GraphView.jsx`

### If they want to test API:
1. Open http://localhost:8000/docs
2. Show them how to execute requests
3. Show WebSocket endpoint

---

## Emergency Troubleshooting

### Backend not responding:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend not loading:
```bash
cd frontend
npm run dev
```

### WebSocket disconnected:
- Refresh the browser page
- Check backend is running
- Look for green "Live" indicator

### No fraud alerts appearing:
- Wait 30 seconds (alerts should appear)
- Check backend console for errors
- Verify transaction simulator is running

---

## Confidence Boosters

- ✅ Both servers are running
- ✅ All tests passing
- ✅ WebSocket connected
- ✅ Fraud alerts appearing
- ✅ Graph updating live
- ✅ AI explanations working
- ✅ Fairness metrics displaying

**You've got this! 🚀**

---

## Final Checklist

Before starting demo:
- [ ] Backend running ✅
- [ ] Frontend running ✅
- [ ] Browser open ✅
- [ ] WebSocket connected ✅
- [ ] Fraud alerts visible ✅
- [ ] Graph animating ✅
- [ ] Confidence level: HIGH ✅

**Ready to demo!** 🎉
