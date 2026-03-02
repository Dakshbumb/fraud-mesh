"""
FraudMesh FastAPI Application

Main application server providing REST API and WebSocket streaming
for real-time fraud detection.
"""

import os
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Set
from contextlib import asynccontextmanager
from collections import deque
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables from .env file in parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from models import Transaction, FraudAlert, SystemStats
from data_simulator import TransactionSimulator
from graph_engine import GraphEngine
from fraud_detector import FraudDetector
from threshold_engine import ThresholdEngine
from threshold_explainer import ThresholdExplainer
from gemini_explainer import GeminiExplainer
from fairness_monitor import FairnessMonitor


# Global state
graph_engine: GraphEngine = None
fraud_detector: FraudDetector = None
threshold_engine: ThresholdEngine = None
threshold_explainer: ThresholdExplainer = None
gemini_explainer: GeminiExplainer = None
fairness_monitor: FairnessMonitor = None
simulator: TransactionSimulator = None

# Alert and transaction storage
fraud_alerts: deque = deque(maxlen=50)
all_transactions: deque = deque(maxlen=200)

# WebSocket connections
active_connections: Set[WebSocket] = set()

# Statistics
total_transactions_processed = 0
total_flagged = 0
processing_times: deque = deque(maxlen=100)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global graph_engine, fraud_detector, threshold_engine, threshold_explainer, gemini_explainer
    global fairness_monitor, simulator
    
    print("🚀 Starting FraudMesh...")
    
    # Initialize components
    graph_engine = GraphEngine()
    fraud_detector = FraudDetector(graph_engine)
    threshold_engine = ThresholdEngine(base_threshold=0.5)
    threshold_explainer = ThresholdExplainer()
    fairness_monitor = FairnessMonitor()
    simulator = TransactionSimulator(fraud_rate=0.06)
    
    # Initialize Gemini explainer (with error handling)
    try:
        gemini_explainer = GeminiExplainer()
        print("✅ Google Gemini initialized")
    except Exception as e:
        print(f"⚠️  Gemini API not available: {e}")
        print("⚠️  Will use fallback explanations")
        gemini_explainer = None
    
    # Pre-generate 20 transactions to build graph history
    print("📊 Pre-generating graph history...")
    for i in range(20):
        txn = simulator.generate_transaction()
        graph_engine.add_transaction(txn)
    print(f"✅ Graph initialized with {graph_engine.get_stats()['node_count']} nodes")
    
    # Start background transaction processing
    asyncio.create_task(process_transaction_stream())
    
    print("✅ FraudMesh ready!")
    print(f"📡 WebSocket: ws://localhost:8000/ws/transactions")
    print(f"🌐 REST API: http://localhost:8000/api/")
    
    yield
    
    # Cleanup
    print("🛑 Shutting down FraudMesh...")


# Create FastAPI app
app = FastAPI(
    title="FraudMesh API",
    description="Real-time graph-based fraud detection",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "FraudMesh running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/graph")
async def get_graph():
    """Get current graph state."""
    try:
        graph_data = graph_engine.get_graph_data_for_frontend(
            max_nodes=150,
            max_edges=300
        )
        return JSONResponse(content=graph_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(limit: int = 50, offset: int = 0):
    """Get recent fraud alerts."""
    try:
        alerts_list = list(fraud_alerts)
        alerts_list.reverse()  # Most recent first
        
        # Pagination
        paginated = alerts_list[offset:offset + limit]
        
        # Convert to JSON-serializable format
        alerts_data = [
            {
                "alert_id": alert.alert_id,
                "transaction": {
                    "id": alert.transaction.id,
                    "user_id": alert.transaction.user_id,
                    "merchant_id": alert.transaction.merchant_id,
                    "amount": alert.transaction.amount,
                    "timestamp": alert.transaction.timestamp.isoformat(),
                    "location": alert.transaction.location,
                    "channel": alert.transaction.channel
                },
                "fraud_score": {
                    "score": alert.fraud_score.score,
                    "triggered_rules": alert.fraud_score.triggered_rules,
                    "fraud_pattern": alert.fraud_score.fraud_pattern,
                    "risk_level": alert.fraud_score.risk_level.value
                },
                "explanation": {
                    "headline": alert.explanation.headline,
                    "narrative": alert.explanation.narrative,
                    "fraud_pattern": alert.explanation.fraud_pattern,
                    "key_signal": alert.explanation.key_signal,
                    "recommendation": alert.explanation.recommendation,
                    "confidence": alert.explanation.confidence,
                    "generation_time_ms": alert.explanation.generation_time_ms
                } if alert.explanation else None,
                "adaptive_threshold": alert.adaptive_threshold,
                "timestamp": alert.timestamp.isoformat()
            }
            for alert in paginated
        ]
        
        return JSONResponse(content={
            "alerts": alerts_data,
            "total_count": len(alerts_list),
            "has_more": (offset + limit) < len(alerts_list)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    try:
        graph_stats = graph_engine.get_stats()
        threshold_stats = threshold_engine.get_stats()
        
        # Compute transaction rate
        txn_rate = len(all_transactions) / 60.0 if all_transactions else 0.0
        
        # Compute fraud rate
        fraud_rate = total_flagged / total_transactions_processed if total_transactions_processed > 0 else 0.0
        
        # Compute average fraud score
        if all_transactions:
            avg_score = sum(t.get('fraud_score', 0) for t in all_transactions) / len(all_transactions)
        else:
            avg_score = 0.0
        
        # Compute average processing latency
        avg_latency = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "transaction_rate": round(txn_rate, 2),
            "total_transactions": total_transactions_processed,
            "flagged_transactions": total_flagged,
            "fraud_rate": round(fraud_rate, 4),
            "avg_fraud_score": round(avg_score, 3),
            "active_entities": graph_stats["node_count"],
            "active_edges": graph_stats["edge_count"],
            "fraud_rings": graph_stats["fraud_rings"],
            "adaptive_threshold": round(threshold_stats["current_threshold"], 3),
            "avg_processing_latency_ms": round(avg_latency, 1),
            "sensitivity": threshold_stats["sensitivity"]
        }
        
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fairness")
async def get_fairness():
    """Get fairness metrics."""
    try:
        metrics = fairness_monitor.compute_fairness_metrics()
        
        fairness_data = {
            "timestamp": metrics.timestamp.isoformat(),
            "baseline_fpr": round(metrics.baseline_fpr, 4),
            "segment_fprs": {k: round(v, 4) for k, v in metrics.segment_fprs.items()},
            "demographic_parity_score": round(metrics.demographic_parity_score, 3),
            "biased_segments": metrics.biased_segments,
            "segment_details": {
                segment_id: {
                    "segment_id": stats.segment_id,
                    "total_transactions": stats.total_transactions,
                    "flagged_transactions": stats.flagged_transactions,
                    "true_positives": stats.true_positives,
                    "false_positives": stats.false_positives,
                    "false_positive_rate": round(stats.false_positive_rate, 4)
                }
                for segment_id, stats in metrics.segment_details.items()
            }
        }
        
        return JSONResponse(content=fairness_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threshold-history")
async def get_threshold_history(minutes: int = 60):
    """Get threshold history."""
    try:
        history = threshold_engine.get_threshold_history(minutes=minutes)
        return JSONResponse(content={"history": history})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threshold-audit-trail")
async def get_threshold_audit_trail(count: int = 50):
    """
    Get threshold decision audit trail with human-readable explanations.
    
    This endpoint proves the threshold system is NOT a black box by providing
    complete transparency into every threshold adjustment decision.
    """
    try:
        decisions = threshold_explainer.get_recent_decisions(count=count)
        summary = threshold_explainer.get_decision_summary()
        
        return JSONResponse(content={
            "decisions": decisions,
            "summary": summary,
            "current_threshold": threshold_engine.current_threshold
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/threshold-audit-trail/export")
async def export_threshold_audit_trail():
    """Export complete threshold audit trail to JSON file."""
    try:
        filepath = f"threshold_audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        threshold_explainer.export_audit_trail(filepath)
        
        return JSONResponse(content={
            "success": True,
            "filepath": filepath,
            "message": "Audit trail exported successfully"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/neighborhood/{entity_id}")
async def get_neighborhood(entity_id: str, hops: int = 2):
    """Get entity neighborhood."""
    try:
        neighborhood = graph_engine.get_neighborhood(entity_id, hops=hops)
        return JSONResponse(content=neighborhood)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fraud-rings")
async def get_fraud_rings():
    """Get detected fraud rings."""
    try:
        rings = graph_engine.get_fraud_rings_details()
        return JSONResponse(content={"fraud_rings": rings})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyst-feedback")
async def submit_analyst_feedback(feedback: Dict):
    """
    Submit analyst feedback for continuous learning.
    
    PRODUCTION ROADMAP ENDPOINT: This endpoint demonstrates the analyst
    feedback loop architecture. In production, this would:
    1. Adjust segment-level thresholds based on false positive patterns
    2. Update GNN training data with corrected labels
    3. Refine rule weights in the hybrid scoring system
    
    Request body:
    {
        "alert_id": "string",
        "transaction_id": "string", 
        "analyst_decision": "approve" | "block" | "escalate",
        "is_false_positive": boolean,
        "feedback_notes": "string (optional)"
    }
    """
    try:
        alert_id = feedback.get("alert_id")
        transaction_id = feedback.get("transaction_id")
        analyst_decision = feedback.get("analyst_decision")
        is_false_positive = feedback.get("is_false_positive", False)
        feedback_notes = feedback.get("feedback_notes", "")
        
        # Validate required fields
        if not alert_id or not transaction_id or not analyst_decision:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: alert_id, transaction_id, analyst_decision"
            )
        
        # MOCK IMPLEMENTATION: In production, this would:
        # 1. Store feedback in database
        # 2. Update segment threshold adjustments
        # 3. Queue transaction for GNN retraining
        # 4. Update rule weight optimizer
        
        response = {
            "status": "received",
            "alert_id": alert_id,
            "transaction_id": transaction_id,
            "analyst_decision": analyst_decision,
            "is_false_positive": is_false_positive,
            "timestamp": datetime.now().isoformat(),
            "message": "Feedback received. In production, this would trigger: "
                      "(1) Segment threshold adjustment, "
                      "(2) GNN retraining queue update, "
                      "(3) Rule weight refinement.",
            "production_actions": {
                "threshold_adjustment": "Would adjust threshold for affected segment",
                "gnn_retraining": "Would add to retraining dataset with corrected label",
                "rule_refinement": "Would update rule weights based on feedback pattern"
            }
        }
        
        print(f"📝 Analyst feedback received: {alert_id} - {analyst_decision}")
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time transaction streaming."""
    await websocket.accept()
    active_connections.add(websocket)
    
    print(f"✅ WebSocket client connected (total: {len(active_connections)})")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.now().isoformat(),
            "client_id": str(uuid.uuid4())
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (with timeout)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)
                
                # Handle client messages (e.g., subscription requests)
                if data.get("type") == "subscribe":
                    # Client subscription handling (future feature)
                    pass
                    
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(websocket)
        print(f"❌ WebSocket client disconnected (remaining: {len(active_connections)})")


async def broadcast_message(message: Dict):
    """Broadcast message to all connected WebSocket clients."""
    if not active_connections:
        return
    
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.add(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.discard(conn)


# ============================================================================
# Background Transaction Processing
# ============================================================================

async def process_transaction_stream():
    """Background task to process transaction stream."""
    global total_transactions_processed, total_flagged
    
    print("🔄 Starting transaction processing stream...")
    
    async for txn in simulator.stream_transactions(rate=10):
        start_time = datetime.now()
        
        try:
            # Add to graph
            graph_engine.add_transaction(txn)
            
            # Compute fraud score
            fraud_score = fraud_detector.compute_fraud_score(txn)
            
            # Get adaptive threshold
            network_fraud_rate = total_flagged / total_transactions_processed if total_transactions_processed > 0 else 0.0
            
            # Get segment FPR for fairness adjustment
            # Use amount-based segment as primary segment for threshold adjustment
            from utils import get_segment_id
            segment_id = get_segment_id("amount", txn.amount)
            segment_fpr = None
            baseline_fpr = None
            if segment_id in fairness_monitor.segment_stats:
                segment_stats = fairness_monitor.segment_stats[segment_id]
                if segment_stats.flagged_transactions > 0:
                    segment_fpr = segment_stats.false_positives / segment_stats.flagged_transactions
            
            # Compute baseline FPR
            metrics = fairness_monitor.compute_fairness_metrics()
            baseline_fpr = metrics.baseline_fpr
            
            # Compute adaptive threshold
            adaptive_threshold = threshold_engine.compute_adaptive_threshold(
                txn,
                network_fraud_rate=network_fraud_rate,
                false_positive_rate=baseline_fpr,
                segment_fpr=segment_fpr,
                baseline_fpr=baseline_fpr
            )
            
            # Generate threshold decision explanation
            if len(threshold_engine.threshold_history) > 0:
                latest_snapshot = threshold_engine.threshold_history[-1]
                threshold_decision = threshold_explainer.explain_threshold_decision(
                    txn=txn,
                    snapshot=latest_snapshot,
                    base_threshold=threshold_engine.base_threshold,
                    network_fraud_rate=network_fraud_rate,
                    system_fpr=baseline_fpr,
                    segment_fpr=segment_fpr
                )
            
            # Check if flagged
            is_flagged = fraud_score.score > adaptive_threshold
            
            # Update counters
            total_transactions_processed += 1
            if is_flagged:
                total_flagged += 1
            
            # Record for fairness monitoring
            fairness_monitor.record_transaction(txn, was_flagged=is_flagged)
            
            # Generate explanation if flagged
            explanation = None
            if is_flagged and gemini_explainer:
                try:
                    fraud_case_context = fraud_detector.assemble_fraud_case_context(txn, fraud_score)
                    explanation = await gemini_explainer.explain_fraud_async(fraud_case_context)
                except Exception as e:
                    print(f"⚠️  Gemini explanation failed: {e}")
                    # Use fallback
                    fraud_case_context = fraud_detector.assemble_fraud_case_context(txn, fraud_score)
                    explanation = gemini_explainer._create_fallback_explanation(
                        fraud_case_context, str(e), 0
                    )
            
            # Create alert if flagged
            if is_flagged:
                alert = FraudAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:12]}",
                    transaction=txn,
                    fraud_score=fraud_score,
                    explanation=explanation,
                    timestamp=datetime.now(),
                    adaptive_threshold=adaptive_threshold,
                    is_true_positive=txn.is_fraudulent  # Ground truth
                )
                fraud_alerts.append(alert)
                
                # Record for fairness
                if txn.is_fraudulent is not None:
                    fairness_monitor.record_alert(txn, fraud_score.score, txn.is_fraudulent)
            
            # Track processing time
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            processing_times.append(processing_time_ms)
            
            # Store transaction summary
            all_transactions.append({
                "id": txn.id,
                "amount": txn.amount,
                "fraud_score": fraud_score.score,
                "is_flagged": is_flagged,
                "timestamp": txn.timestamp.isoformat()
            })
            
            # Broadcast to WebSocket clients
            if is_flagged:
                # Send alert
                await broadcast_message({
                    "type": "alert",
                    "data": {
                        "alert_id": alert.alert_id,
                        "transaction": {
                            "id": txn.id,
                            "user_id": txn.user_id,
                            "amount": txn.amount,
                            "timestamp": txn.timestamp.isoformat()
                        },
                        "fraud_score": {
                            "score": fraud_score.score,
                            "triggered_rules": fraud_score.triggered_rules,
                            "fraud_pattern": fraud_score.fraud_pattern
                        },
                        "explanation": {
                            "headline": explanation.headline,
                            "narrative": explanation.narrative,
                            "fraud_pattern": explanation.fraud_pattern,
                            "key_signal": explanation.key_signal,
                            "recommendation": explanation.recommendation,
                            "confidence": explanation.confidence,
                            "generation_time_ms": explanation.generation_time_ms
                        } if explanation else None,
                        "adaptive_threshold": adaptive_threshold,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            else:
                # Send transaction update
                await broadcast_message({
                    "type": "transaction",
                    "data": {
                        "transaction_id": txn.id,
                        "fraud_score": fraud_score.score,
                        "is_flagged": False,
                        "timestamp": txn.timestamp.isoformat()
                    }
                })
            
            # Broadcast stats update every 5 seconds
            if total_transactions_processed % 50 == 0:
                threshold_stats = threshold_engine.get_stats()
                await broadcast_message({
                    "type": "stats_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "transaction_rate": len(all_transactions) / 60.0,
                        "fraud_rate": network_fraud_rate,
                        "avg_fraud_score": fraud_score.score,
                        "active_entities": graph_engine.get_stats()["node_count"],
                        "adaptive_threshold": adaptive_threshold,
                        "sensitivity": threshold_stats["sensitivity"]
                    }
                })
            
        except Exception as e:
            print(f"❌ Error processing transaction: {e}")
            import traceback
            traceback.print_exc()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
