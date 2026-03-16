import { AlertTriangle, Clock, Zap } from 'lucide-react';
import { RefreshButton } from '../components/RefreshButton';
import type { SignalItem, SystemData } from '../types';

interface SignalsPageProps {
  data: SystemData;
  isLoading: boolean;
  onRefresh: () => void;
}

export const SignalsPage = ({ data, isLoading, onRefresh }: SignalsPageProps) => {
  const urgentSignals = data.signals.filter((s) => s.status === 'Urgent');
  const negativeSignals = data.signals.filter((s) => s.status === 'Negative');
  const neutralSignals = data.signals.filter((s) => s.status === 'Neutral');

  return (
    <div className="max-w-6xl mx-auto space-y-6 stagger">
      {/* Header */}
      <div className="flex items-center justify-between anim-fade-up">
        <h1 className="text-3xl font-bold text-white">Micro-Crisis Signals</h1>
        <RefreshButton onClick={onRefresh} isLoading={isLoading} lastUpdated={data.metrics.lastUpdated} />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard title="Urgent" count={urgentSignals.length} icon={<AlertTriangle size={22} />} color="#ff4d6a" delay={0} />
        <SummaryCard title="Negative" count={negativeSignals.length} icon={<Zap size={22} />} color="#ff8c42" delay={0.08} />
        <SummaryCard title="Neutral" count={neutralSignals.length} icon={<Clock size={22} />} color="#22c55e" delay={0.16} />
      </div>

      {/* Categories */}
      {urgentSignals.length > 0 && <SignalCategory title="Urgent Issues" signals={urgentSignals} color="#ff4d6a" />}
      {negativeSignals.length > 0 && <SignalCategory title="Negative Signals" signals={negativeSignals} color="#ff8c42" />}
      {neutralSignals.length > 0 && <SignalCategory title="Neutral Updates" signals={neutralSignals} color="#22c55e" />}
    </div>
  );
};

const SummaryCard = ({ title, count, icon, color, delay }: {
  title: string; count: number; icon: React.ReactNode; color: string; delay: number;
}) => (
  <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: `${delay}s` }}>
    <div className="flex items-center gap-4">
      <div className="p-2 rounded-xl glass" style={{ color, boxShadow: `0 0 16px ${color}22` }}>
        {icon}
      </div>
      <div>
        <div className="text-3xl font-bold" style={{ color }}>{count}</div>
        <div className="text-gray-500 text-sm">{title}</div>
      </div>
    </div>
  </div>
);

const SignalCategory = ({ title, signals, color }: {
  title: string; signals: SignalItem[]; color: string;
}) => (
  <div className="glass-card p-6 anim-fade-up">
    <h2 className="text-lg font-bold mb-4" style={{ color }}>{title}</h2>
    <div className="space-y-2">
      {signals.map((signal) => (
        <div key={signal.id}
          className="glass p-4 rounded-xl transition-all duration-300 hover:bg-white/[0.04]">
          <p className="text-gray-300 text-sm mb-2">{signal.message}</p>
          <div className="text-gray-600 text-xs font-mono">
            {new Date(signal.timestamp).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  </div>
);
