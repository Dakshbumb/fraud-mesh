import React from 'react';

function Header({ wsConnected, stats }) {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 shadow-2xl border-b border-blue-500/30">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center space-x-4">
            <div className="bg-white/10 backdrop-blur-sm p-3 rounded-xl border border-white/20">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">FraudMesh</h1>
              <p className="text-blue-200 text-sm">Real-Time Fraud Detection Platform</p>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            {/* Connection Status */}
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
              <span className="text-white text-sm font-medium">
                {wsConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
            
            {/* Transaction Counter */}
            <div className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20">
              <div className="text-blue-200 text-xs">Transactions</div>
              <div className="text-white text-lg font-bold">{stats.total_transactions?.toLocaleString() || 0}</div>
            </div>
            
            {/* Fraud Rate */}
            <div className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20">
              <div className="text-blue-200 text-xs">Fraud Rate</div>
              <div className="text-white text-lg font-bold">
                {((stats.fraud_rate || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
