import { useState, useEffect, useRef } from 'react';
import GraphView from './components/GraphView';
import AlertPanel from './components/AlertPanel';
import SystemStats from './components/SystemStats';
import ThresholdMeter from './components/ThresholdMeter';
import ThresholdAuditTrail from './components/ThresholdAuditTrail';
import FairnessPanel from './components/FairnessPanel';
import Header from './components/Header';

function App() {
  const [wsConnected, setWsConnected] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    transaction_rate: 0,
    fraud_rate: 0,
    avg_fraud_score: 0,
    active_entities: 0,
    adaptive_threshold: 0.5,
    total_transactions: 0,
    flagged_transactions: 0
  });
  const [fairnessMetrics, setFairnessMetrics] = useState(null);
  const [thresholdHistory, setThresholdHistory] = useState([]);
  const [thresholdAuditTrail, setThresholdAuditTrail] = useState([]);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        await fetchGraphData();
        await fetchAlerts();
        await fetchStats();
        await fetchFairness();
      } catch (err) {
        console.error('Error fetching initial data:', err);
        setError('Failed to load initial data. Make sure backend is running on port 8000.');
      }
    };
    fetchData();
  }, []);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/transactions');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      // Reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    wsRef.current = ws;
  };

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'alert':
        setAlerts(prev => {
          // Check if alert already exists to avoid duplicates
          const exists = prev.some(a => a.alert_id === message.data.alert_id);
          if (exists) return prev;
          return [message.data, ...prev].slice(0, 50);
        });
        break;
        
      case 'transaction':
        // Update graph periodically
        break;
        
      case 'stats_update':
        setStats(prev => ({ ...prev, ...message.data }));
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const fetchGraphData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/graph');
      const data = await response.json();
      setGraphData(data);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts?limit=50');
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      const data = await response.json();
      setStats(data);
      
      // Track performance history
      setPerformanceHistory(prev => {
        const newEntry = {
          time: new Date().toLocaleTimeString(),
          latency: data.avg_processing_latency_ms || 0,
          rate: data.transaction_rate || 0,
          fraudRate: (data.fraud_rate || 0) * 100
        };
        return [...prev, newEntry].slice(-20); // Keep last 20 data points
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchFairness = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/fairness');
      const data = await response.json();
      setFairnessMetrics(data);
    } catch (error) {
      console.error('Error fetching fairness metrics:', error);
    }
  };

  const fetchThresholdAuditTrail = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/threshold-audit-trail?count=50');
      const data = await response.json();
      setThresholdAuditTrail(data.decisions || []);
    } catch (error) {
      console.error('Error fetching threshold audit trail:', error);
    }
  };

  // Periodic refresh
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStats();
      fetchFairness();
      fetchGraphData(); // Refresh graph every 5 seconds
      fetchThresholdAuditTrail(); // Refresh audit trail
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {error && (
        <div className="bg-red-500 text-white p-4 text-center">
          <strong>Error:</strong> {error}
          <button 
            onClick={() => window.location.reload()} 
            className="ml-4 bg-white text-red-500 px-4 py-1 rounded"
          >
            Reload
          </button>
        </div>
      )}
      <Header wsConnected={wsConnected} stats={stats} />
      
      <div className="container mx-auto px-4 py-6">
        {/* Top Stats Bar */}
        <SystemStats stats={stats} performanceHistory={performanceHistory} />
        
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left Column - Graph */}
          <div className="lg:col-span-2">
            <GraphView data={graphData} />
          </div>
          
          {/* Right Column - Alerts & Threshold */}
          <div className="space-y-6">
            <ThresholdMeter 
              current={stats.adaptive_threshold} 
              history={thresholdHistory}
              sensitivity={stats.sensitivity}
            />
            <AlertPanel alerts={alerts} />
          </div>
        </div>
        
        {/* Bottom - Fairness Dashboard */}
        <div className="mt-6">
          <FairnessPanel metrics={fairnessMetrics} />
        </div>
        
        {/* Threshold Audit Trail - Proves NOT a Black Box */}
        <div className="mt-6">
          <ThresholdAuditTrail 
            decisions={thresholdAuditTrail} 
            currentThreshold={stats.adaptive_threshold}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
