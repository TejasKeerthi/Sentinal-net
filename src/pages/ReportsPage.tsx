import { TrendingUp, BarChart3, PieChart } from 'lucide-react';
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

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold text-white">Risk Reports</h1>
        <RefreshButton
          onClick={onRefresh}
          isLoading={isLoading}
          lastUpdated={data.metrics.lastUpdated}
        />
      </div>

      {/* Export Actions */}
      <div className="bg-cyber-card border border-cyber-gray-light rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Export Reports</h2>
        <div className="flex gap-4 flex-wrap">
          <button
            onClick={handleExportJSON}
            className="flex items-center gap-2 px-4 py-2 bg-electric-blue bg-opacity-20 border border-electric-blue border-opacity-50 text-electric-blue rounded-lg hover:bg-opacity-30 transition-all"
          >
            <BarChart3 size={18} />
            Export as JSON
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-warning-orange bg-opacity-20 border border-warning-orange border-opacity-50 text-warning-orange rounded-lg hover:bg-opacity-30 transition-all"
          >
            <PieChart size={18} />
            Export as CSV
          </button>
        </div>
      </div>

      {/* Report Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Status Report */}
        <div className="bg-cyber-card border border-cyber-gray-light rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={20} />
            Current Status Report
          </h2>
          <div className="space-y-4">
            <ReportLine
              label="Failure Risk Score"
              value={`${data.metrics.failureRiskScore}%`}
              status="warning"
            />
            <ReportLine
              label="System Health"
              value={data.metrics.systemHealth}
              status={data.metrics.systemHealth === 'Nominal' ? 'good' : 'warning'}
            />
            <ReportLine
              label="Total Signals"
              value={data.signals.length}
              status="neutral"
            />
            <ReportLine
              label="Critical Issues"
              value={data.signals.filter((s) => s.status === 'Urgent').length}
              status="critical"
            />
          </div>
        </div>

        {/* Analysis Summary */}
        <div className="bg-cyber-card border border-cyber-gray-light rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <PieChart size={20} />
            Signal Distribution
          </h2>
          <div className="space-y-4">
            {(() => {
              const urgent = data.signals.filter((s) => s.status === 'Urgent').length;
              const negative = data.signals.filter((s) => s.status === 'Negative').length;
              const neutral = data.signals.filter((s) => s.status === 'Neutral').length;
              const total = data.signals.length;

              return (
                <>
                  <ProgressBar
                    label="Urgent"
                    value={urgent}
                    total={total}
                    color="bg-red-600"
                  />
                  <ProgressBar
                    label="Negative"
                    value={negative}
                    total={total}
                    color="bg-warning-orange"
                  />
                  <ProgressBar
                    label="Neutral"
                    value={neutral}
                    total={total}
                    color="bg-green-600"
                  />
                </>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-gradient-to-r from-blue-900 from-opacity-20 to-transparent border border-blue-700 border-opacity-30 rounded-lg p-6">
        <h2 className="text-xl font-bold text-blue-300 mb-4">Automated Recommendations</h2>
        <ul className="space-y-2 text-gray-300">
          <li className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">→</span>
            <span>Immediate investigation required for WebSocket memory leak identified in recent commits</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">→</span>
            <span>Authentication module regression affecting 12% of user sessions - rollback or hotfix recommended</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">→</span>
            <span>Implement circuit breaker pattern for traffic spike mitigation</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">→</span>
            <span>Schedule emergency code review session for development irregularity normalization</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

interface ReportLineProps {
  label: string;
  value: string | number;
  status: 'good' | 'warning' | 'critical' | 'neutral';
}

const ReportLine = ({ label, value, status }: ReportLineProps) => {
  const statusColor: Record<string, string> = {
    good: 'text-green-400',
    warning: 'text-warning-orange',
    critical: 'text-red-400',
    neutral: 'text-electric-blue',
  };

  return (
    <div className="flex items-center justify-between p-3 bg-darker-charcoal rounded-lg">
      <span className="text-gray-400">{label}</span>
      <span className={`font-bold ${statusColor[status]}`}>{value}</span>
    </div>
  );
};

interface ProgressBarProps {
  label: string;
  value: number;
  total: number;
  color: string;
}

const ProgressBar = ({ label, value, total, color }: ProgressBarProps) => {
  const percentage = total > 0 ? (value / total) * 100 : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{label}</span>
        <span className="text-white font-semibold">
          {value}/{total} ({percentage.toFixed(0)}%)
        </span>
      </div>
      <div className="w-full bg-darker-charcoal rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};
