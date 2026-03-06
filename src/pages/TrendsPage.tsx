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
  const stats = (() => {
    if (data.temporalData.length === 0) {
      return { currentTrend: 'Stable', changePercent: '0%', peakRisk: '0%', stabilityIndex: '5.0/10' };
    }
    const bg = data.temporalData.map(d => d.bugGrowth);
    const di = data.temporalData.map(d => d.devIrregularity);
    const first = bg[0];
    const last = bg[bg.length - 1];
    const trend = last > first ? 'Increasing' : last < first ? 'Decreasing' : 'Stable';
    const change = ((last - first) / Math.max(first, 1)) * 100;
    const peak = Math.round((Math.max(...bg) / 100) * 100);
    const avgDev = di.reduce((a, b) => a + b, 0) / di.length;
    const stability = Math.max(0, Math.min(10, 10 - (avgDev / 10)));
    return {
      currentTrend: trend,
      changePercent: `${change > 0 ? '+' : ''}${Math.round(change)}%`,
      peakRisk: `${peak}%`,
      stabilityIndex: `${stability.toFixed(1)}/10`,
    };
  })();

  const statItems = [
    { label: 'Current Trend', value: stats.currentTrend, color: '#ff8c42' },
    { label: '24h Change', value: stats.changePercent, color: '#00d4ff' },
    { label: 'Peak Risk', value: stats.peakRisk, color: '#ff4d6a' },
    { label: 'Stability', value: stats.stabilityIndex, color: '#22c55e' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 stagger">
      <div className="flex items-center justify-between flex-wrap gap-4 anim-fade-up">
        <h1 className="text-3xl font-bold text-white">Temporal Trends & Analysis</h1>
        <RefreshButton onClick={onRefresh} isLoading={isLoading} lastUpdated={data.metrics.lastUpdated} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <TemporalChart data={data.temporalData} />
        </div>
        <div>
          <AIInsightsPanel insight={data.aiInsights} />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {statItems.map((s, i) => (
          <div key={i} className="glass-card p-5 anim-fade-up" style={{ animationDelay: `${i * 0.08}s` }}>
            <div className="text-gray-500 text-xs font-medium mb-2">{s.label}</div>
            <div className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
