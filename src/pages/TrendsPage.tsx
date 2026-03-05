import { TemporalChart } from '../components/TemporalChart';
import { AIInsightsPanel } from '../components/AIInsightsPanel';
import { RefreshButton } from '../components/RefreshButton';
import type { SystemData } from '../types';

interface TrendsPageProps {
  data: SystemData;
  isLoading: boolean;
  onRefresh: () => void;
}

export const TrendsPage = ({ data, isLoading, onRefresh }: TrendsPageProps) => {
  // Calculate statistics from real temporal data
  const calculateStats = () => {
    if (data.temporalData.length === 0) {
      return {
        currentTrend: 'Stable',
        changePercent: '0%',
        peakRisk: '0%',
        stabilityIndex: '5.0/10',
      };
    }

    const bugGrowthValues = data.temporalData.map(d => d.bugGrowth);
    const devIrregularityValues = data.temporalData.map(d => d.devIrregularity);
    
    // Current trend
    const first = bugGrowthValues[0];
    const last = bugGrowthValues[bugGrowthValues.length - 1];
    const trend = last > first ? 'Increasing' : last < first ? 'Decreasing' : 'Stable';
    
    // 24h change percentage
    const changePercent = ((last - first) / Math.max(first, 1)) * 100;
    
    // Peak risk
    const maxBugGrowth = Math.max(...bugGrowthValues);
    const peakRisk = Math.round((maxBugGrowth / 100) * 100);
    
    // Stability index (0-10 based on deviation)
    const avgDeviation = devIrregularityValues.reduce((a, b) => a + b, 0) / devIrregularityValues.length;
    const stabilityIndex = Math.max(0, Math.min(10, 10 - (avgDeviation / 10)));
    
    return {
      currentTrend: trend,
      changePercent: `${changePercent > 0 ? '+' : ''}${Math.round(changePercent)}%`,
      peakRisk: `${peakRisk}%`,
      stabilityIndex: `${stabilityIndex.toFixed(1)}/10`,
    };
  };

  const stats = calculateStats();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-4xl font-bold text-white">Temporal Trends & Analysis</h1>
        <RefreshButton
          onClick={onRefresh}
          isLoading={isLoading}
          lastUpdated={data.metrics.lastUpdated}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart - Spans 2 columns on large screens */}
        <div className="lg:col-span-2">
          <TemporalChart data={data.temporalData} />
        </div>

        {/* AI Insights - Spans 1 column */}
        <div>
          <AIInsightsPanel insight={data.aiInsights} />
        </div>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Current Trend" value={stats.currentTrend} color="warning-orange" />
        <StatCard label="24h Change" value={stats.changePercent} color="warning-orange" />
        <StatCard label="Peak Risk" value={stats.peakRisk} color="warning-orange" />
        <StatCard label="Stability Index" value={stats.stabilityIndex} color="warning-orange" />
      </div>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string;
  color: 'electric-blue' | 'warning-orange' | 'green-400';
}

const StatCard = ({ label, value, color }: StatCardProps) => {
  const colorClass: Record<string, string> = {
    'electric-blue': 'text-electric-blue',
    'warning-orange': 'text-warning-orange',
    'green-400': 'text-green-400',
  };

  return (
    <div className="bg-cyber-card border border-cyber-gray-light rounded-lg p-4">
      <div className="text-gray-500 text-sm mb-2">{label}</div>
      <div className={`text-2xl font-bold ${colorClass[color]}`}>{value}</div>
    </div>
  );
};
