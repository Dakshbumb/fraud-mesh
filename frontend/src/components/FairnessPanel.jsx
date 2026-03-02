import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function FairnessPanel({ metrics }) {
  if (!metrics) {
    return (
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-4">Fairness Monitoring</h2>
        <div className="text-center py-8 text-blue-200">
          <p>Loading fairness metrics...</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = Object.entries(metrics.segment_fprs || {}).map(([segment, fpr]) => ({
    segment: segment.replace(/_/g, ' '),
    fpr: (fpr * 100).toFixed(2),
    isHigh: fpr > (metrics.baseline_fpr * 2)
  }));

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">Fairness Monitoring</h2>
        {metrics.biased_segments && metrics.biased_segments.length > 0 && (
          <span className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full text-sm font-medium border border-red-500/30 animate-pulse">
            ⚠ {metrics.biased_segments.length} Bias Alert{metrics.biased_segments.length > 1 ? 's' : ''}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Baseline FPR */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
          <div className="text-blue-300 text-sm mb-2">Baseline False Positive Rate</div>
          <div className="text-white text-3xl font-bold">
            {((metrics.baseline_fpr || 0) * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-blue-400 mt-1">System-wide average</div>
        </div>

        {/* Demographic Parity */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
          <div className="text-blue-300 text-sm mb-2">Demographic Parity Score</div>
          <div className="text-white text-3xl font-bold">
            {(metrics.demographic_parity_score || 0).toFixed(2)}
          </div>
          <div className="text-xs text-blue-400 mt-1">Max FPR / Min FPR (lower is better)</div>
        </div>

        {/* Segment Count */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
          <div className="text-blue-300 text-sm mb-2">Monitored Segments</div>
          <div className="text-white text-3xl font-bold">
            {Object.keys(metrics.segment_fprs || {}).length}
          </div>
          <div className="text-xs text-blue-400 mt-1">Active monitoring groups</div>
        </div>
      </div>

      {/* FPR by Segment Chart */}
      {chartData.length > 0 && (
        <div className="mt-6 bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
          <h3 className="text-white font-bold mb-4">False Positive Rate by Segment</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <XAxis 
                dataKey="segment" 
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1', fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis 
                stroke="#94a3b8"
                tick={{ fill: '#cbd5e1', fontSize: 12 }}
                label={{ value: 'FPR (%)', angle: -90, position: 'insideLeft', fill: '#cbd5e1' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #3b82f6',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="fpr" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.isHigh ? '#ef4444' : '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded bg-blue-500"></div>
              <span className="text-blue-200">Normal</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded bg-red-500"></div>
              <span className="text-blue-200">Exceeds 2x Baseline</span>
            </div>
          </div>
        </div>
      )}

      {/* Bias Alerts */}
      {metrics.biased_segments && metrics.biased_segments.length > 0 && (
        <div className="mt-6 bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="flex-1">
              <div className="text-red-400 font-bold mb-2">Fairness Alert Detected</div>
              <div className="text-red-200 text-sm mb-2">
                The following segments have false positive rates exceeding 2x the baseline:
              </div>
              <div className="flex flex-wrap gap-2">
                {metrics.biased_segments.map((segment, i) => (
                  <span key={i} className="bg-red-800/30 text-red-200 px-3 py-1 rounded-full text-xs font-medium border border-red-500/30">
                    {segment.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Segment Details Table */}
      {metrics.segment_details && Object.keys(metrics.segment_details).length > 0 && (
        <div className="mt-6 bg-slate-800/50 rounded-lg p-4 border border-blue-500/20">
          <h3 className="text-white font-bold mb-4">Detailed Segment Statistics</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-blue-500/20">
                  <th className="text-left text-blue-300 py-2 px-3">Segment</th>
                  <th className="text-right text-blue-300 py-2 px-3">Total Txns</th>
                  <th className="text-right text-blue-300 py-2 px-3">Flagged</th>
                  <th className="text-right text-blue-300 py-2 px-3">False Positives</th>
                  <th className="text-right text-blue-300 py-2 px-3">FPR</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metrics.segment_details).map(([segmentId, stats]) => (
                  <tr key={segmentId} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                    <td className="text-white py-2 px-3">{segmentId.replace(/_/g, ' ')}</td>
                    <td className="text-right text-blue-200 py-2 px-3">{stats.total_transactions}</td>
                    <td className="text-right text-blue-200 py-2 px-3">{stats.flagged_transactions}</td>
                    <td className="text-right text-blue-200 py-2 px-3">{stats.false_positives}</td>
                    <td className="text-right py-2 px-3">
                      <span className={`font-medium ${stats.false_positive_rate > metrics.baseline_fpr * 2 ? 'text-red-400' : 'text-green-400'}`}>
                        {(stats.false_positive_rate * 100).toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default FairnessPanel;
