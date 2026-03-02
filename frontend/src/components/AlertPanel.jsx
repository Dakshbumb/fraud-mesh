import { useState, memo } from 'react';
import ExplainCard from './ExplainCard';

// Memoized individual alert card to prevent unnecessary re-renders
const AlertCard = memo(({ alert, isExpanded, onToggle }) => {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  const getRiskColor = (score) => {
    if (score >= 0.8) return 'from-red-600 to-red-700';
    if (score >= 0.6) return 'from-orange-600 to-orange-700';
    return 'from-yellow-600 to-yellow-700';
  };
  
  const getRiskLabel = (score) => {
    if (score >= 0.8) return 'CRITICAL';
    if (score >= 0.6) return 'HIGH';
    return 'MEDIUM';
  };

  return (
    <div 
      className="bg-slate-800/80 backdrop-blur-sm rounded-lg p-4 border border-white/10 hover:border-blue-500/50 hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer"
      onClick={onToggle}
      title="Click to see Gemini AI explanation"
    >
      {/* Alert Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`bg-gradient-to-r ${getRiskColor(alert.fraud_score.score)} text-white px-3 py-1 rounded-full text-xs font-bold`}>
              {getRiskLabel(alert.fraud_score.score)}
            </span>
            <span className="text-white font-bold text-lg">
              {alert.fraud_score.score.toFixed(3)}
            </span>
          </div>
          <div className="text-blue-200 text-sm">
            ${alert.transaction.amount.toFixed(2)} • {alert.transaction.user_id.substring(0, 8)}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-blue-300">{formatTimestamp(alert.timestamp)}</div>
          <div className="text-xs text-blue-400 mt-1">ID: {alert.transaction.id.substring(0, 8)}</div>
        </div>
      </div>
      
      {/* Fraud Pattern Badge */}
      {alert.fraud_score.fraud_pattern && (
        <div className="mb-3">
          <span className="inline-block bg-red-900/50 text-red-200 px-3 py-1 rounded-full text-xs font-medium border border-red-500/30">
            {alert.fraud_score.fraud_pattern}
          </span>
        </div>
      )}
      
      {/* Triggered Rules */}
      {alert.fraud_score.triggered_rules && alert.fraud_score.triggered_rules.length > 0 && (
        <div className="mb-3">
          <div className="text-xs text-blue-300 mb-1">Triggered Rules:</div>
          <div className="flex flex-wrap gap-1">
            {alert.fraud_score.triggered_rules.slice(0, 3).map((rule, i) => (
              <span key={i} className="bg-blue-900/30 text-blue-200 px-2 py-1 rounded text-xs border border-blue-500/20">
                {rule}
              </span>
            ))}
            {alert.fraud_score.triggered_rules.length > 3 && (
              <span className="text-blue-300 text-xs px-2 py-1">
                +{alert.fraud_score.triggered_rules.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}
      
      {/* Expanded Explanation */}
      {isExpanded && alert.explanation && (
        <ExplainCard explanation={alert.explanation} />
      )}
      
      {/* Expand Indicator */}
      <div className="text-center mt-2 pt-2 border-t border-white/10">
        <div className="flex items-center justify-center space-x-2 text-blue-400 text-xs">
          <span>{isExpanded ? 'Hide' : 'Show'} Gemini AI Explanation</span>
          <svg 
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>
  );
});

AlertCard.displayName = 'AlertCard';

function AlertPanel({ alerts = [] }) {
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [frozenAlerts, setFrozenAlerts] = useState([]);
  
  // Freeze alerts when paused
  const displayAlerts = isPaused ? frozenAlerts : alerts;
  
  // Update frozen alerts when pausing
  const handlePauseToggle = () => {
    if (!isPaused) {
      setFrozenAlerts([...alerts]);
    }
    setIsPaused(!isPaused);
  };
  
  // Export alerts as JSON
  const exportAsJSON = () => {
    const dataStr = JSON.stringify(displayAlerts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fraudmesh-alerts-${new Date().toISOString()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  // Export alerts as CSV
  const exportAsCSV = () => {
    const headers = ['Alert ID', 'Transaction ID', 'User ID', 'Amount', 'Fraud Score', 'Pattern', 'Recommendation', 'Timestamp'];
    const rows = displayAlerts.map(alert => [
      alert.alert_id,
      alert.transaction.id,
      alert.transaction.user_id,
      alert.transaction.amount,
      alert.fraud_score.score,
      alert.fraud_score.fraud_pattern || '',
      alert.explanation?.recommendation || '',
      alert.timestamp
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const dataBlob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fraudmesh-alerts-${new Date().toISOString()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Fraud Alerts</h2>
        <div className="flex items-center space-x-2">
          {/* Export Dropdown */}
          <div className="relative group">
            <button
              className="px-3 py-1 rounded-full text-xs font-medium border bg-blue-500/20 text-blue-300 border-blue-500/30 hover:bg-blue-500/30 transition-colors flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Export</span>
            </button>
            <div className="absolute right-0 mt-2 w-32 bg-slate-800 rounded-lg shadow-xl border border-white/10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                onClick={exportAsJSON}
                className="w-full px-4 py-2 text-left text-sm text-blue-200 hover:bg-blue-500/20 rounded-t-lg transition-colors"
              >
                JSON
              </button>
              <button
                onClick={exportAsCSV}
                className="w-full px-4 py-2 text-left text-sm text-blue-200 hover:bg-blue-500/20 rounded-b-lg transition-colors"
              >
                CSV
              </button>
            </div>
          </div>
          
          <button
            onClick={handlePauseToggle}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
              isPaused 
                ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30 hover:bg-yellow-500/30' 
                : 'bg-green-500/20 text-green-300 border-green-500/30 hover:bg-green-500/30'
            }`}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
          <span className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full text-sm font-medium border border-red-500/30">
            {displayAlerts.length} Active
          </span>
        </div>
      </div>
      
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
        {displayAlerts.length === 0 ? (
          <div className="text-center py-12 text-blue-200">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No fraud alerts detected</p>
          </div>
        ) : (
          displayAlerts.map((alert) => (
            <AlertCard
              key={alert.alert_id}
              alert={alert}
              isExpanded={expandedAlert === alert.alert_id}
              onToggle={() => setExpandedAlert(expandedAlert === alert.alert_id ? null : alert.alert_id)}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default AlertPanel;
