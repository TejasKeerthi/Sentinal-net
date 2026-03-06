import { RiskScoreHero } from '../components/RiskScoreHero';
import { SemanticSignalFeed } from '../components/SemanticSignalFeed';
import { RefreshButton } from '../components/RefreshButton';
import { GitHubAnalyzer } from '../components/GitHubAnalyzer';
import { CodeDNAHelix } from '../components/CodeDNAHelix';
import { RiskRadar } from '../components/RiskRadar';
import { CommitPulseMonitor } from '../components/CommitPulseMonitor';
import { SentimentOrb } from '../components/SentimentOrb';
import type { SystemData } from '../types';
import { useMemo } from 'react';

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
  // Compute derived metrics for unique visualisations
  const derivedMetrics = useMemo(() => {
    const signals = data.signals;
    const urgent = signals.filter(s => s.status === 'Urgent').length;
    const negative = signals.filter(s => s.status === 'Negative').length;
    const neutral = signals.filter(s => s.status === 'Neutral').length;
    const total = signals.length || 1;

    // Risk radar values (0-100)
    const commitRisk = Math.min(100, Math.round((data.metrics.metadata?.commits_30d || 0) > 50 ? 40 : (data.metrics.metadata?.commits_30d || 0) * 2));
    const issueRisk = Math.min(100, Math.round(((data.metrics.metadata?.open_issues || 0) / Math.max(total, 1)) * 100));
    const sentimentRisk = Math.min(100, Math.round((negative + urgent) / total * 100));
    const activityRisk = Math.min(100, Math.round(data.metrics.failureRiskScore));
    const complexityRisk = Math.min(100, Math.round(
      (data.temporalData.reduce((s, d) => s + d.devIrregularity, 0) / Math.max(data.temporalData.length, 1))
    ));

    // Overall sentiment -1 to 1
    const sentimentScore = total > 0
      ? (neutral - urgent * 2 - negative) / total
      : 0;
    const sentimentLabel = sentimentScore > 0.3 ? 'Overwhelmingly Positive' : sentimentScore > 0 ? 'Generally Positive' : sentimentScore > -0.3 ? 'Mixed Signals' : 'Predominantly Negative';

    // Commit timestamps for pulse monitor
    const commitTimestamps = signals
      .filter(s => s.source === 'commit')
      .map(s => s.timestamp);

    return {
      commitRisk, issueRisk, sentimentRisk, activityRisk, complexityRisk,
      sentimentScore: Math.max(-1, Math.min(1, sentimentScore)),
      sentimentLabel,
      commitTimestamps,
      urgent, negative, neutral,
    };
  }, [data]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 stagger">
      {/* GitHub Analyzer - Hero Section */}
      {onAnalyzeGitHub && (
        <GitHubAnalyzer 
          onAnalyze={onAnalyzeGitHub}
          isLoading={isLoading}
          currentRepo={currentRepo}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 anim-fade-up">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">System Overview</h1>
          {currentRepo && (
            <p className="text-accent text-sm mt-1 font-medium opacity-80">
              Analyzing: {currentRepo}
            </p>
          )}
        </div>
        <RefreshButton onClick={onRefresh} isLoading={isLoading} lastUpdated={data.metrics.lastUpdated} />
      </div>

      {/* Risk Score Hero + Analysis Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5 items-start">
        <div className="lg:col-span-3">
          <RiskScoreHero
            riskScore={data.metrics.failureRiskScore}
            systemHealth={data.metrics.systemHealth}
            metadata={data.metrics.metadata}
          />
        </div>

        <div className="lg:col-span-2 space-y-5">
          {/* Analysis Summary */}
          <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.1s' }}>
            <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-accent anim-heartbeat" />
              Analysis Summary
            </h3>
            <div className="space-y-3">
              {[
                { label: 'Total Signals', value: data.signals.length, color: '#00d4ff' },
                { label: 'Urgent Issues', value: derivedMetrics.urgent, color: '#ff4d6a' },
                { label: 'Warnings', value: derivedMetrics.negative, color: '#ff8c42' },
                { label: 'Healthy', value: derivedMetrics.neutral, color: '#22c55e' },
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b border-white/[0.04] last:border-0">
                  <span className="text-gray-500 text-sm">{item.label}</span>
                  <span className="font-bold text-lg" style={{ color: item.color }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Insight Preview */}
          {data.aiInsights && (
            <div className="glass-card p-5 anim-fade-up" style={{ animationDelay: '0.2s' }}>
              <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase mb-3 flex items-center gap-2">
                <span className="text-purple">⚡</span>
                AI Insight
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed line-clamp-3">
                {data.aiInsights.title}
              </p>
              {data.aiInsights.recommendation && (
                <p className="text-gray-500 text-xs mt-3 leading-relaxed line-clamp-2 border-t border-white/[0.04] pt-3">
                  {data.aiInsights.recommendation.substring(0, 120)}...
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Unique Visualisations Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Commit Pulse Monitor */}
        <CommitPulseMonitor
          timestamps={derivedMetrics.commitTimestamps}
          risk={data.metrics.failureRiskScore}
        />

        {/* Risk Radar */}
        <RiskRadar
          commitRisk={derivedMetrics.commitRisk}
          issueRisk={derivedMetrics.issueRisk}
          sentimentRisk={derivedMetrics.sentimentRisk}
          activityRisk={derivedMetrics.activityRisk}
          complexityRisk={derivedMetrics.complexityRisk}
        />

        {/* Sentiment Orb */}
        <SentimentOrb
          sentiment={derivedMetrics.sentimentScore}
          label={derivedMetrics.sentimentLabel}
          signalCount={data.signals.length}
        />
      </div>

      {/* Code DNA Helix */}
      <CodeDNAHelix signals={data.signals} />

      {/* Signals Feed */}
      <SemanticSignalFeed signals={data.signals} />
    </div>
  );
};
