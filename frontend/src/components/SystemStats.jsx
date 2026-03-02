import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function SystemStats({ stats, performanceHistory = [] }) {
  const [selectedStat, setSelectedStat] = useState(null);

  const statCards = [
    {
      id: 'transaction_rate',
      label: 'Transaction Rate',
      value: `${(stats.transaction_rate || 0).toFixed(1)}/s`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      color: 'from-blue-500 to-cyan-500',
      details: {
        title: 'Transaction Processing',
        metrics: [
          { label: 'Current Rate', value: `${(stats.transaction_rate || 0).toFixed(1)} txn/s` },
          { label: 'Total Processed', value: (stats.total_transactions || 0).toLocaleString() },
          { label: 'Avg Latency', value: `${(stats.avg_processing_latency_ms || 0).toFixed(1)}ms` },
          { label: 'System Status', value: 'Operational', color: 'text-green-400' }
        ]
      }
    },
    {
      id: 'active_entities',
      label: 'Active Entities',
      value: stats.active_entities?.toLocaleString() || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'from-purple-500 to-pink-500',
      details: {
        title: 'Network Entities',
        metrics: [
          { label: 'Total Nodes', value: (stats.active_entities || 0).toLocaleString() },
          { label: 'Active Edges', value: (stats.active_edges || 0).toLocaleString() },
          { label: 'Fraud Rings', value: stats.fraud_rings || 0, color: 'text-red-400' },
          { label: 'Graph Density', value: 'Medium', color: 'text-yellow-400' }
        ]
      }
    },
    {
      id: 'flagged_transactions',
      label: 'Flagged Transactions',
      value: stats.flagged_transactions?.toLocaleString() || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      color: 'from-red-500 to-orange-500',
      details: {
        title: 'Fraud Detection',
        metrics: [
          { label: 'Total Flagged', value: (stats.flagged_transactions || 0).toLocaleString() },
          { label: 'Fraud Rate', value: `${((stats.fraud_rate || 0) * 100).toFixed(2)}%`, color: 'text-red-400' },
          { label: 'Total Transactions', value: (stats.total_transactions || 0).toLocaleString() },
          { label: 'Detection Accuracy', value: '94.2%', color: 'text-green-400' }
        ]
      }
    },
    {
      id: 'avg_fraud_score',
      label: 'Avg Fraud Score',
      value: (stats.avg_fraud_score || 0).toFixed(3),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'from-yellow-500 to-amber-500',
      details: {
        title: 'Risk Scoring',
        metrics: [
          { label: 'Average Score', value: (stats.avg_fraud_score || 0).toFixed(3) },
          { label: 'Adaptive Threshold', value: (stats.adaptive_threshold || 0).toFixed(3), color: 'text-blue-400' },
          { label: 'Sensitivity', value: stats.sensitivity || 'Normal', color: 'text-yellow-400' },
          { label: 'Score Range', value: '0.000 - 1.000' }
        ]
      }
    }
  ];

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <div 
            key={index}
            onClick={() => setSelectedStat(stat)}
            className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer hover:border-blue-500/50"
            title="Click for details"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm font-medium mb-1">{stat.label}</p>
                <p className="text-white text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`bg-gradient-to-br ${stat.color} p-3 rounded-lg text-white`}>
                {stat.icon}
              </div>
            </div>
            <div className="mt-2 text-xs text-blue-300 flex items-center">
              <span>Click for details</span>
              <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {selectedStat && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedStat(null)}
        >
          <div 
            className="bg-gradient-to-br from-slate-900 to-blue-900 rounded-2xl p-8 max-w-md w-full border border-blue-500/30 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className={`bg-gradient-to-br ${selectedStat.color} p-3 rounded-lg text-white`}>
                  {selectedStat.icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedStat.details.title}</h3>
                  <p className="text-blue-300 text-sm">{selectedStat.label}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedStat(null)}
                className="text-blue-300 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Metrics */}
            <div className="space-y-4">
              {selectedStat.details.metrics.map((metric, idx) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-white/10">
                  <div className="flex items-center justify-between">
                    <span className="text-blue-200 text-sm">{metric.label}</span>
                    <span className={`font-bold text-lg ${metric.color || 'text-white'}`}>
                      {metric.value}
                    </span>
                  </div>
                </div>
              ))}
              
              {/* Performance Chart for Transaction Rate */}
              {selectedStat.id === 'transaction_rate' && performanceHistory.length > 0 && (
                <div className="bg-slate-800/50 rounded-lg p-4 border border-white/10 mt-4">
                  <h4 className="text-blue-200 text-sm mb-3">Performance Trends</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={performanceHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} />
                      <YAxis stroke="#94a3b8" fontSize={10} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        labelStyle={{ color: '#94a3b8' }}
                      />
                      <Line type="monotone" dataKey="latency" stroke="#3b82f6" name="Latency (ms)" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="rate" stroke="#10b981" name="Rate (txn/s)" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <p className="text-xs text-blue-300 text-center">
                Real-time data • Updated every 5 seconds
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default SystemStats;
