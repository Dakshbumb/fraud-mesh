import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle, Info } from 'lucide-react';

function ThresholdAuditTrail({ decisions = [], currentThreshold = 0.5 }) {
  const [expandedDecision, setExpandedDecision] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'major', 'moderate', 'minor'

  const toggleExpand = (decisionId) => {
    setExpandedDecision(expandedDecision === decisionId ? null : decisionId);
  };

  const getSensitivityBadge = (level) => {
    const badges = {
      HIGH: { color: 'bg-red-500/20 text-red-300 border-red-500/50', icon: AlertCircle },
      MEDIUM: { color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50', icon: Info },
      LOW: { color: 'bg-green-500/20 text-green-300 border-green-500/50', icon: CheckCircle }
    };
    const badge = badges[level] || badges.MEDIUM;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${badge.color}`}>
        <Icon size={12} />
        {level}
      </span>
    );
  };

  const getAdjustmentBadge = (magnitude) => {
    const colors = {
      MAJOR: 'bg-purple-500/20 text-purple-300 border-purple-500/50',
      MODERATE: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
      MINOR: 'bg-gray-500/20 text-gray-300 border-gray-500/50',
      NONE: 'bg-gray-700/20 text-gray-400 border-gray-700/50'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[magnitude] || colors.NONE}`}>
        {magnitude}
      </span>
    );
  };

  const getAdjustmentColor = (value) => {
    if (value < 0) return 'text-red-400'; // More sensitive (lower threshold)
    if (value > 0) return 'text-green-400'; // Less sensitive (higher threshold)
    return 'text-gray-400';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const filteredDecisions = decisions.filter(d => {
    if (filter === 'all') return true;
    return d.adjustment_magnitude.toLowerCase() === filter;
  });

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Threshold Decision Audit Trail</h2>
          <p className="text-sm text-blue-200 mt-1">
            Complete transparency - every threshold adjustment explained
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-white">{currentThreshold.toFixed(2)}</div>
          <div className="text-xs text-blue-200">Current Threshold</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            filter === 'all' 
              ? 'bg-blue-500 text-white' 
              : 'bg-slate-800 text-blue-200 hover:bg-slate-700'
          }`}
        >
          All ({decisions.length})
        </button>
        <button
          onClick={() => setFilter('major')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            filter === 'major' 
              ? 'bg-purple-500 text-white' 
              : 'bg-slate-800 text-blue-200 hover:bg-slate-700'
          }`}
        >
          Major
        </button>
        <button
          onClick={() => setFilter('moderate')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            filter === 'moderate' 
              ? 'bg-blue-500 text-white' 
              : 'bg-slate-800 text-blue-200 hover:bg-slate-700'
          }`}
        >
          Moderate
        </button>
        <button
          onClick={() => setFilter('minor')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            filter === 'minor' 
              ? 'bg-gray-500 text-white' 
              : 'bg-slate-800 text-blue-200 hover:bg-slate-700'
          }`}
        >
          Minor
        </button>
      </div>

      {/* Decision List */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {filteredDecisions.length === 0 ? (
          <div className="text-center py-8 text-blue-200">
            No threshold decisions yet
          </div>
        ) : (
          filteredDecisions.map((decision) => (
            <div
              key={decision.decision_id}
              className="bg-slate-800/50 rounded-lg border border-blue-500/20 overflow-hidden hover:border-blue-500/40 transition-colors"
            >
              {/* Decision Header */}
              <div
                className="p-4 cursor-pointer"
                onClick={() => toggleExpand(decision.decision_id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-blue-300">
                        {decision.decision_id}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatTime(decision.timestamp)}
                      </span>
                    </div>
                    <div className="text-sm text-white font-medium">
                      {decision.primary_reason}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getSensitivityBadge(decision.sensitivity_level)}
                    {getAdjustmentBadge(decision.adjustment_magnitude)}
                    {expandedDecision === decision.decision_id ? (
                      <ChevronUp size={20} className="text-blue-300" />
                    ) : (
                      <ChevronDown size={20} className="text-blue-300" />
                    )}
                  </div>
                </div>

                {/* Threshold Change Indicator */}
                <div className="flex items-center gap-3 mt-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Base:</span>
                    <span className="text-sm font-mono text-white">
                      {decision.base_threshold.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-gray-500">→</div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Final:</span>
                    <span className="text-sm font-mono text-white font-bold">
                      {decision.final_threshold.toFixed(2)}
                    </span>
                  </div>
                  <div className={`text-xs font-medium ${getAdjustmentColor(decision.final_threshold - decision.base_threshold)}`}>
                    {decision.final_threshold - decision.base_threshold > 0 ? '+' : ''}
                    {(decision.final_threshold - decision.base_threshold).toFixed(3)}
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedDecision === decision.decision_id && (
                <div className="border-t border-blue-500/20 p-4 bg-slate-900/50">
                  {/* Risk Context */}
                  <div className="mb-4">
                    <div className="text-xs font-semibold text-blue-300 mb-2">RISK CONTEXT</div>
                    <div className="text-sm text-gray-300 bg-slate-800/50 rounded p-3">
                      {decision.risk_context}
                    </div>
                  </div>

                  {/* Detailed Explanation */}
                  <div className="mb-4">
                    <div className="text-xs font-semibold text-blue-300 mb-2">DETAILED EXPLANATION</div>
                    <div className="text-sm text-gray-300 bg-slate-800/50 rounded p-3 whitespace-pre-line font-mono">
                      {decision.detailed_explanation}
                    </div>
                  </div>

                  {/* Adjustment Factors */}
                  <div className="mb-4">
                    <div className="text-xs font-semibold text-blue-300 mb-2">ADJUSTMENT FACTORS</div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-gray-400 mb-1">Time</div>
                        <div className={`text-lg font-mono font-bold ${getAdjustmentColor(decision.time_adjustment)}`}>
                          {decision.time_adjustment > 0 ? '+' : ''}{decision.time_adjustment.toFixed(3)}
                        </div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-gray-400 mb-1">Amount</div>
                        <div className={`text-lg font-mono font-bold ${getAdjustmentColor(decision.amount_adjustment)}`}>
                          {decision.amount_adjustment > 0 ? '+' : ''}{decision.amount_adjustment.toFixed(3)}
                        </div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-gray-400 mb-1">Network</div>
                        <div className={`text-lg font-mono font-bold ${getAdjustmentColor(decision.network_adjustment)}`}>
                          {decision.network_adjustment > 0 ? '+' : ''}{decision.network_adjustment.toFixed(3)}
                        </div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-3">
                        <div className="text-xs text-gray-400 mb-1">FPR</div>
                        <div className={`text-lg font-mono font-bold ${getAdjustmentColor(decision.fpr_adjustment)}`}>
                          {decision.fpr_adjustment > 0 ? '+' : ''}{decision.fpr_adjustment.toFixed(3)}
                        </div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-3 col-span-2">
                        <div className="text-xs text-gray-400 mb-1">Fairness (Bias Mitigation)</div>
                        <div className={`text-lg font-mono font-bold ${getAdjustmentColor(decision.fairness_adjustment)}`}>
                          {decision.fairness_adjustment > 0 ? '+' : ''}{decision.fairness_adjustment.toFixed(3)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Transaction Context */}
                  <div>
                    <div className="text-xs font-semibold text-blue-300 mb-2">TRANSACTION CONTEXT</div>
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div className="bg-slate-800/50 rounded p-2">
                        <div className="text-gray-400 mb-1">Amount</div>
                        <div className="text-white font-medium">${decision.transaction_amount.toFixed(2)}</div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-2">
                        <div className="text-gray-400 mb-1">Time</div>
                        <div className="text-white font-medium">{decision.transaction_time}</div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-2">
                        <div className="text-gray-400 mb-1">Network Fraud Rate</div>
                        <div className="text-white font-medium">{(decision.network_fraud_rate * 100).toFixed(1)}%</div>
                      </div>
                      <div className="bg-slate-800/50 rounded p-2">
                        <div className="text-gray-400 mb-1">System FPR</div>
                        <div className="text-white font-medium">{(decision.system_fpr * 100).toFixed(1)}%</div>
                      </div>
                      {decision.segment_fpr !== null && (
                        <div className="bg-slate-800/50 rounded p-2">
                          <div className="text-gray-400 mb-1">Segment FPR</div>
                          <div className="text-white font-medium">{(decision.segment_fpr * 100).toFixed(1)}%</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Export Button */}
      <div className="mt-4 pt-4 border-t border-blue-500/20">
        <button
          onClick={() => {
            // Trigger export via API call
            console.log('Export audit trail');
          }}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Export Complete Audit Trail (JSON)
        </button>
      </div>
    </div>
  );
}

export default ThresholdAuditTrail;
