import React from 'react';

function ThresholdMeter({ current = 0.5, history = [], sensitivity = 'medium' }) {
  const percentage = (current * 100).toFixed(0);
  
  const getSensitivityColor = () => {
    if (current < 0.4) return 'text-red-400';
    if (current < 0.6) return 'text-yellow-400';
    return 'text-green-400';
  };
  
  const getSensitivityLabel = () => {
    if (current < 0.4) return 'High Sensitivity';
    if (current < 0.6) return 'Medium Sensitivity';
    return 'Low Sensitivity';
  };
  
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
      <h2 className="text-xl font-bold text-white mb-4">Adaptive Threshold</h2>
      
      {/* Current Value */}
      <div className="text-center mb-6">
        <div className="text-5xl font-bold text-white mb-2">
          {current.toFixed(2)}
        </div>
        <div className={`text-sm font-medium ${getSensitivityColor()}`}>
          {getSensitivityLabel()}
        </div>
      </div>
      
      {/* Visual Meter */}
      <div className="relative mb-6">
        <div className="h-6 bg-slate-800 rounded-full overflow-hidden border border-white/20">
          <div 
            className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-blue-200 mt-2">
          <span>0.0 (Strict)</span>
          <span>1.0 (Lenient)</span>
        </div>
      </div>
      
      {/* Threshold Info */}
      <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
        <div className="text-sm text-blue-200 mb-2">Threshold Factors:</div>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-blue-300">Base Threshold:</span>
            <span className="text-white font-medium">0.50</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-300">Time Adjustment:</span>
            <span className="text-white font-medium">
              {current < 0.5 ? '↓ Night Mode' : '→ Normal'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-300">Network Status:</span>
            <span className="text-white font-medium">
              {current < 0.45 ? '⚠ High Fraud' : '✓ Normal'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Mini Chart */}
      {history.length > 0 && (
        <div className="mt-4">
          <div className="text-xs text-blue-200 mb-2">Last Hour</div>
          <div className="h-16 flex items-end space-x-1">
            {history.slice(-20).map((point, i) => (
              <div 
                key={i}
                className="flex-1 bg-blue-500 rounded-t opacity-70 hover:opacity-100 transition-opacity"
                style={{ height: `${point.threshold * 100}%` }}
                title={`${point.threshold.toFixed(2)}`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ThresholdMeter;
