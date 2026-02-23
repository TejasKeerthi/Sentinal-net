import { AlertTriangle, Clock, Zap } from 'lucide-react';
import { RefreshButton } from '../components/RefreshButton';
import type { SystemData } from '../types';

interface SignalsPageProps {
  data: SystemData;
  isLoading: boolean;
  onRefresh: () => void;
}

export const SignalsPage = ({ data, isLoading, onRefresh }: SignalsPageProps) => {
  // Separate signals by status
  const urgentSignals = data.signals.filter((s) => s.status === 'Urgent');
  const negativeSignals = data.signals.filter((s) => s.status === 'Negative');
  const neutralSignals = data.signals.filter((s) => s.status === 'Neutral');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold text-white">Micro-Crisis Signals</h1>
        <RefreshButton
          onClick={onRefresh}
          isLoading={isLoading}
          lastUpdated={data.metrics.lastUpdated}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SignalSummaryCard
          title="Urgent"
          count={urgentSignals.length}
          icon={<AlertTriangle size={24} />}
          color="red"
        />
        <SignalSummaryCard
          title="Negative"
          count={negativeSignals.length}
          icon={<Zap size={24} />}
          color="orange"
        />
        <SignalSummaryCard
          title="Neutral"
          count={neutralSignals.length}
          icon={<Clock size={24} />}
          color="green"
        />
      </div>

      {/* Signals by Category */}
      {urgentSignals.length > 0 && (
        <SignalCategory
          title="Urgent Issues"
          signals={urgentSignals}
          color="red"
        />
      )}
      {negativeSignals.length > 0 && (
        <SignalCategory
          title="Negative Signals"
          signals={negativeSignals}
          color="orange"
        />
      )}
      {neutralSignals.length > 0 && (
        <SignalCategory
          title="Neutral Updates"
          signals={neutralSignals}
          color="green"
        />
      )}
    </div>
  );
};

interface SignalSummaryCardProps {
  title: string;
  count: number;
  icon: React.ReactNode;
  color: 'red' | 'orange' | 'green';
}

const SignalSummaryCard = ({ title, count, icon, color }: SignalSummaryCardProps) => {
  const colorClass: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    red: {
      bg: 'bg-red-900 bg-opacity-20',
      border: 'border-red-700',
      text: 'text-red-300',
      icon: 'text-red-400',
    },
    orange: {
      bg: 'bg-orange-900 bg-opacity-20',
      border: 'border-orange-700',
      text: 'text-orange-300',
      icon: 'text-warning-orange',
    },
    green: {
      bg: 'bg-green-900 bg-opacity-20',
      border: 'border-green-700',
      text: 'text-green-300',
      icon: 'text-green-400',
    },
  };

  const config = colorClass[color];

  return (
    <div className={`${config.bg} border ${config.border} rounded-lg p-6`}>
      <div className="flex items-center gap-4">
        <div className={config.icon}>{icon}</div>
        <div>
          <div className={`text-3xl font-bold ${config.text}`}>{count}</div>
          <div className="text-gray-500 text-sm">{title}</div>
        </div>
      </div>
    </div>
  );
};

interface SignalCategoryProps {
  title: string;
  signals: any[];
  color: 'red' | 'orange' | 'green';
}

const SignalCategory = ({ title, signals, color }: SignalCategoryProps) => {
  const colorClass: Record<string, { header: string }> = {
    red: { header: 'text-red-400' },
    orange: { header: 'text-warning-orange' },
    green: { header: 'text-green-400' },
  };

  return (
    <div className="bg-cyber-card border border-cyber-gray-light rounded-lg p-6">
      <h2 className={`text-xl font-bold mb-4 ${colorClass[color].header}`}>{title}</h2>
      <div className="space-y-3">
        {signals.map((signal) => (
          <div
            key={signal.id}
            className="p-4 bg-darker-charcoal border border-cyber-gray rounded-lg hover:border-electric-blue transition-colors"
          >
            <p className="text-gray-300 mb-2">{signal.message}</p>
            <div className="text-gray-500 text-xs">
              {new Date(signal.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
