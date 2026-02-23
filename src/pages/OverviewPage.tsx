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
    <div className="space-y-6">
      {/* GitHub Analyzer */}
      {onAnalyzeGitHub && (
        <GitHubAnalyzer 
          onAnalyze={onAnalyzeGitHub}
          isLoading={isLoading}
          currentRepo={currentRepo}
        />
      )}

      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold text-white">System Overview</h1>
        <RefreshButton
          onClick={onRefresh}
          isLoading={isLoading}
          lastUpdated={data.metrics.lastUpdated}
        />
      </div>

      {/* Risk Score Hero Section */}
      <RiskScoreHero
        riskScore={data.metrics.failureRiskScore}
        systemHealth={data.metrics.systemHealth}
      />

      {/* Signals Feed */}
      <SemanticSignalFeed signals={data.signals} />
    </div>
  );
};
