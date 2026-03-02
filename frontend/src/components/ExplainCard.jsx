import React from 'react';

function ExplainCard({ explanation }) {
  if (!explanation) return null;
  
  const getRecommendationColor = (rec) => {
    if (rec === 'Block') return 'text-red-400 bg-red-900/30 border-red-500/30';
    if (rec === 'Review') return 'text-yellow-400 bg-yellow-900/30 border-yellow-500/30';
    return 'text-green-400 bg-green-900/30 border-green-500/30';
  };
  
  const getConfidenceColor = (conf) => {
    if (conf === 'High') return 'text-green-400';
    if (conf === 'Medium') return 'text-yellow-400';
    return 'text-orange-400';
  };
  
  return (
    <div className="mt-4 bg-gradient-to-br from-slate-900/90 to-blue-900/30 rounded-lg p-4 border border-blue-500/30">
      {/* AI Badge */}
      <div className="flex items-center space-x-2 mb-3">
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <span className="text-blue-300 text-sm font-medium">Gemini AI Analysis</span>
      </div>
      
      {/* Headline */}
      <h3 className="text-yellow-400 font-bold text-lg mb-3">
        {explanation.headline}
      </h3>
      
      {/* Narrative */}
      <p className="text-blue-100 text-sm leading-relaxed mb-4">
        {explanation.narrative}
      </p>
      
      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-800/50 rounded-lg p-3 border border-white/10">
          <div className="text-blue-300 text-xs mb-1">Pattern Type</div>
          <div className="text-white font-medium text-sm">{explanation.fraud_pattern}</div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg p-3 border border-white/10">
          <div className="text-blue-300 text-xs mb-1">Confidence</div>
          <div className={`font-bold text-sm ${getConfidenceColor(explanation.confidence)}`}>
            {explanation.confidence}
          </div>
        </div>
      </div>
      
      {/* Key Signal */}
      <div className="bg-slate-800/50 rounded-lg p-3 border border-white/10 mb-4">
        <div className="text-blue-300 text-xs mb-1">Key Risk Signal</div>
        <div className="text-white text-sm">{explanation.key_signal}</div>
      </div>
      
      {/* Recommendation */}
      <div className={`rounded-lg p-3 border ${getRecommendationColor(explanation.recommendation)}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs opacity-75 mb-1">Recommended Action</div>
            <div className="font-bold text-lg">{explanation.recommendation}</div>
          </div>
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {explanation.recommendation === 'Block' ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            ) : explanation.recommendation === 'Review' ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            )}
          </svg>
        </div>
      </div>
      
      {/* Generation Time */}
      {explanation.generation_time_ms && (
        <div className="text-xs text-blue-400 mt-3 text-right">
          Generated in {explanation.generation_time_ms}ms
        </div>
      )}
    </div>
  );
}

export default ExplainCard;
