import { Zap, BookOpen, AlertCircle } from 'lucide-react';
import type { AIInsight } from '../types';

interface AIInsightsPanelProps {
  insight: AIInsight;
}

export const AIInsightsPanel = ({ insight }: AIInsightsPanelProps) => {
  return (
    <div className="glass-card p-6 anim-fade-up relative overflow-hidden" style={{ animationDelay: '0.25s' }}>
      {/* Ambient glow */}
      <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #a855f7, transparent 70%)' }} />

      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-xl glass" style={{ boxShadow: '0 0 16px rgba(168,85,247,0.12)' }}>
          <Zap size={20} className="text-purple" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">GenAI Insights</h2>
          <p className="text-gray-600 text-xs">AI-powered risk analysis</p>
        </div>
      </div>

      {/* Main Insight */}
      <div className="mb-6 p-4 glass rounded-xl" style={{ borderColor: 'rgba(168,85,247,0.1)' }}>
        <h3 className="text-accent font-bold text-sm mb-2">{insight.title}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{insight.description}</p>
      </div>

      {/* Contributing Factors */}
      <div className="mb-6">
        <h3 className="text-white font-semibold text-sm mb-3 flex items-center gap-2">
          <AlertCircle size={14} className="text-warn" />
          Contributing Factors
        </h3>
        <div className="space-y-2">
          {insight.factors.map((factor, index) => (
            <div key={index} className="flex items-start gap-2.5 p-2.5 glass rounded-lg transition-all duration-300 hover:bg-white/[0.04]">
              <div className="w-1.5 h-1.5 bg-warn rounded-full mt-1.5 flex-shrink-0" />
              <p className="text-gray-400 text-xs leading-relaxed">{factor}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="p-4 glass rounded-xl" style={{ borderColor: 'rgba(34,197,94,0.1)' }}>
        <h3 className="text-success font-semibold text-sm mb-2 flex items-center gap-2">
          <BookOpen size={14} />
          Recommended Actions
        </h3>
        <p className="text-gray-400 text-xs leading-relaxed whitespace-pre-line">
          {insight.recommendation}
        </p>
      </div>

      {/* AI Confidence */}
      <div className="mt-5 pt-4 border-t border-white/[0.04]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-2 h-2 bg-accent rounded-full" />
              <div className="absolute inset-0 w-2 h-2 bg-accent rounded-full animate-ping opacity-30" />
            </div>
            <span className="text-gray-600 text-[10px]">AI Confidence: High (92%)</span>
          </div>
          <span className="text-gray-600 text-[10px]">Last Analysis: Just now</span>
        </div>
      </div>
    </div>
  );
};
