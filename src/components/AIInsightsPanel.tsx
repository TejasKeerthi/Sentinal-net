import { Zap, BookOpen, AlertCircle } from 'lucide-react';
import type { AIInsight } from '../types';

interface AIInsightsPanelProps {
  insight: AIInsight;
}

export const AIInsightsPanel = ({ insight }: AIInsightsPanelProps) => {
  return (
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-electric-blue border-opacity-30 p-6 shadow-cyber-glow">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-electric-blue bg-opacity-20 rounded-lg">
          <Zap size={24} className="text-electric-blue" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Explainable GenAI Insights</h2>
          <p className="text-gray-400 text-sm">AI-powered risk analysis & recommendations</p>
        </div>
      </div>

      {/* Main Insight */}
      <div className="mb-8 p-4 bg-electric-blue bg-opacity-5 border border-electric-blue border-opacity-20 rounded-lg">
        <h3 className="text-electric-blue font-bold mb-2">{insight.title}</h3>
        <p className="text-gray-300 leading-relaxed">{insight.description}</p>
      </div>

      {/* Contributing Factors */}
      <div className="mb-8">
        <h3 className="text-white font-bold mb-4 flex items-center gap-2">
          <AlertCircle size={18} className="text-warning-orange" />
          Contributing Factors
        </h3>
        <div className="space-y-3">
          {insight.factors.map((factor, index) => (
            <div key={index} className="flex items-start gap-3 p-3 bg-cyber-gray-light rounded-lg hover:border-electric-blue border border-transparent transition-colors">
              <div className="w-2 h-2 bg-warning-orange rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-gray-300 text-sm">{factor}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="p-4 bg-gradient-to-r from-green-900 from-opacity-20 to-transparent border border-green-700 border-opacity-30 rounded-lg">
        <h3 className="text-green-400 font-bold mb-3 flex items-center gap-2">
          <BookOpen size={18} />
          Recommended Actions
        </h3>
        <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-line">
          {insight.recommendation}
        </p>
      </div>

      {/* AI Confidence Indicator */}
      <div className="mt-6 pt-4 border-t border-cyber-gray">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-electric-blue rounded-full animate-pulse"></div>
            <span className="text-gray-500 text-xs">AI Confidence: High (92%)</span>
          </div>
          <span className="text-gray-500 text-xs">Last Analysis: Just now</span>
        </div>
      </div>
    </div>
  );
};
