import { RiskScoreHero } from '../components/RiskScoreHero';
import { SemanticSignalFeed } from '../components/SemanticSignalFeed';
import { RefreshButton } from '../components/RefreshButton';
import { GitHubAnalyzer } from '../components/GitHubAnalyzer';
import type { SystemData } from '../types';

interface OverviewPageProps {
  data: SystemData;
  isLoading: boolean;
  onRefresh: () => void;
  onAnalyzeGitHub?: (repo: string) => void;
  currentRepo?: string | null;
}

export const OverviewPage = ({ 
  data, 
  isLoading, 
  onRefresh,
  onAnalyzeGitHub,
  currentRepo
}: OverviewPageProps) => {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* GitHub Analyzer - Hero Section */}
      {onAnalyzeGitHub && (
        <GitHubAnalyzer 
          onAnalyze={onAnalyzeGitHub}
          isLoading={isLoading}
          currentRepo={currentRepo}
        />
      )}

      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tight">System Overview</h1>
          {currentRepo && (
            <p className="text-electric-blue text-sm mt-1 font-medium">
              Analyzing: {currentRepo}
            </p>
          )}
        </div>
        <RefreshButton
          onClick={onRefresh}
          isLoading={isLoading}
          lastUpdated={data.metrics.lastUpdated}
        />
      </div>

      {/* Two-Column Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
        {/* Risk Score Hero - Takes 3 columns */}
        <div className="lg:col-span-3">
          <RiskScoreHero
            riskScore={data.metrics.failureRiskScore}
            systemHealth={data.metrics.systemHealth}
            metadata={data.metrics.metadata}
          />
        </div>

        {/* Quick Stats Sidebar - Takes 2 columns */}
        <div className="lg:col-span-2 space-y-4">
          {/* Repository Health Summary Card */}
          <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal p-6 rounded-xl border border-cyber-gray-light shadow-cyber-glow">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-electric-blue animate-pulse"></span>
              Analysis Summary
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-cyber-gray">
                <span className="text-gray-400 text-sm">Total Signals</span>
                <span className="text-electric-blue font-bold text-lg">{data.signals.length}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-cyber-gray">
                <span className="text-gray-400 text-sm">Urgent Issues</span>
                <span className="text-red-400 font-bold text-lg">
                  {data.signals.filter(s => s.status === 'Urgent').length}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-cyber-gray">
                <span className="text-gray-400 text-sm">Warnings</span>
                <span className="text-warning-orange font-bold text-lg">
                  {data.signals.filter(s => s.status === 'Negative').length}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-gray-400 text-sm">Healthy Signals</span>
                <span className="text-green-400 font-bold text-lg">
                  {data.signals.filter(s => s.status === 'Neutral').length}
                </span>
              </div>
            </div>
          </div>

          {/* AI Insight Preview Card */}
          {data.aiInsights && (
            <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal p-6 rounded-xl border border-cyan-500 border-opacity-20">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <span className="text-electric-blue">⚡</span>
                AI Insight
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed line-clamp-4">
                {data.aiInsights.title}
              </p>
              {data.aiInsights.recommendation && (
                <p className="text-gray-400 text-xs mt-3 leading-relaxed line-clamp-3 border-t border-cyber-gray pt-3">
                  {data.aiInsights.recommendation.substring(0, 150)}...
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Signals Feed - Full Width */}
      <SemanticSignalFeed signals={data.signals} />
    </div>
  );
};
