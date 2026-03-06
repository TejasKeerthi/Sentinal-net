import { TrendingUp, BarChart3, PieChart, Download } from 'lucide-react';
import { RefreshButton } from '../components/RefreshButton';
import type { SystemData } from '../types';

interface ReportsPageProps {
  data: SystemData;
  isLoading: boolean;
  onRefresh: () => void;
}

export const ReportsPage = ({ data, isLoading, onRefresh }: ReportsPageProps) => {
  const handleExportJSON = () => {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sentinel-report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    const csv =
      'Timestamp,Risk Score,System Health\n' +
      `${data.metrics.lastUpdated},${data.metrics.failureRiskScore},${data.metrics.systemHealth}`;
    const dataBlob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sentinel-metrics-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const urgent = data.signals.filter((s) => s.status === 'Urgent').length;
  const negative = data.signals.filter((s) => s.status === 'Negative').length;
  const neutral = data.signals.filter((s) => s.status === 'Neutral').length;
  const total = data.signals.length;

  // Dynamic recommendations based on actual data
  const getRecommendations = () => {
    const recs: string[] = [];
    if (urgent > 0) recs.push(`${urgent} urgent signal${urgent > 1 ? 's' : ''} detected — investigate flagged commits and issues immediately`);
    if (negative > 0) recs.push(`${negative} negative signal${negative > 1 ? 's' : ''} found — review recent code changes for regressions`);
    if (data.metrics.failureRiskScore > 60) recs.push('Risk score exceeds 60% — consider pausing feature development for stability sprint');
    if (data.metrics.failureRiskScore > 30 && data.metrics.failureRiskScore <= 60) recs.push('Moderate risk level — monitor trends closely and address high-priority issues');
    if (total === 0) recs.push('No signals analyzed yet — enter a GitHub repository to begin analysis');
    if (recs.length === 0) recs.push('System health is nominal — continue regular development practices');
    return recs;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 stagger">
      {/* Header */}
      <div className="flex items-center justify-between anim-fade-up">
        <h1 className="text-3xl font-bold text-white">Risk Reports</h1>
        <RefreshButton onClick={onRefresh} isLoading={isLoading} lastUpdated={data.metrics.lastUpdated} />
      </div>

      {/* Export */}
      <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.08s' }}>
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Download size={18} className="text-accent" />
          Export Reports
        </h2>
        <div className="flex gap-3 flex-wrap">
          <button onClick={handleExportJSON}
            className="flex items-center gap-2 px-4 py-2.5 glass rounded-xl text-accent text-sm font-medium transition-all duration-300 hover:bg-white/[0.04]"
            style={{ borderColor: 'rgba(0,212,255,0.15)' }}>
            <BarChart3 size={16} /> Export JSON
          </button>
          <button onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2.5 glass rounded-xl text-warn text-sm font-medium transition-all duration-300 hover:bg-white/[0.04]"
            style={{ borderColor: 'rgba(255,140,66,0.15)' }}>
            <PieChart size={16} /> Export CSV
          </button>
        </div>
      </div>

      {/* Report Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Current Status */}
        <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.16s' }}>
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-warn" />
            Current Status
          </h2>
          <div className="space-y-3">
            {[
              { label: 'Failure Risk Score', value: `${data.metrics.failureRiskScore}%`, color: data.metrics.failureRiskScore > 60 ? '#ff4d6a' : data.metrics.failureRiskScore > 30 ? '#ff8c42' : '#22c55e' },
              { label: 'System Health', value: data.metrics.systemHealth, color: data.metrics.systemHealth === 'Nominal' ? '#22c55e' : data.metrics.systemHealth === 'Warning' ? '#ff8c42' : '#ff4d6a' },
              { label: 'Total Signals', value: `${total}`, color: '#00d4ff' },
              { label: 'Critical Issues', value: `${urgent}`, color: '#ff4d6a' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 glass rounded-xl">
                <span className="text-gray-500 text-sm">{item.label}</span>
                <span className="font-bold" style={{ color: item.color }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Signal Distribution */}
        <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.24s' }}>
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <PieChart size={18} className="text-purple" />
            Signal Distribution
          </h2>
          <div className="space-y-4">
            {[
              { label: 'Urgent', value: urgent, color: '#ff4d6a' },
              { label: 'Negative', value: negative, color: '#ff8c42' },
              { label: 'Neutral', value: neutral, color: '#22c55e' },
            ].map((item, i) => {
              const pct = total > 0 ? (item.value / total) * 100 : 0;
              return (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-gray-400 text-sm">{item.label}</span>
                    <span className="text-white text-sm font-semibold">{item.value}/{total} ({pct.toFixed(0)}%)</span>
                  </div>
                  <div className="w-full h-2 bg-white/[0.04] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${pct}%`, backgroundColor: item.color, boxShadow: `0 0 10px ${item.color}44` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.32s', borderColor: 'rgba(0,212,255,0.08)' }}>
        <h2 className="text-lg font-bold text-accent mb-4">Automated Recommendations</h2>
        <ul className="space-y-2">
          {getRecommendations().map((rec, i) => (
            <li key={i} className="flex items-start gap-3 text-gray-400 text-sm">
              <span className="text-accent mt-0.5">→</span>
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
