import { AlertCircle } from 'lucide-react';
import clsx from 'clsx';

interface RiskScoreHeroProps {
  riskScore: number;
  systemHealth: 'Critical' | 'Warning' | 'Nominal';
}

export const RiskScoreHero = ({ riskScore, systemHealth }: RiskScoreHeroProps) => {
  const getHealthColor = () => {
    switch (systemHealth) {
      case 'Critical':
        return { bg: 'from-red-900 to-red-700', text: 'text-red-400', badge: 'bg-red-900 text-red-300' };
      case 'Warning':
        return { bg: 'from-warning-orange to-orange-700', text: 'text-warning-orange', badge: 'bg-orange-900 text-warning-orange' };
      case 'Nominal':
        return { bg: 'from-green-900 to-green-700', text: 'text-green-400', badge: 'bg-green-900 text-green-300' };
    }
  };

  const colors = getHealthColor();
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (riskScore / 100) * circumference;

  return (
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal p-8 rounded-xl border border-cyber-gray-light shadow-cyber-glow">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Software Failure Risk Score</h2>
          <p className="text-gray-400 text-sm">Real-time system reliability assessment</p>
        </div>
        <div className={clsx('px-3 py-1 rounded-full text-sm font-semibold', colors.badge)}>
          {systemHealth}
        </div>
      </div>

      <div className="flex items-center justify-between">
        {/* Circular Progress */}
        <div className="relative w-40 h-40 flex-shrink-0">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            {/* Background circle */}
            <circle cx="50" cy="50" r="45" fill="none" stroke="#2a2a3e" strokeWidth="2" />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={colors.text.split('-')[1] === 'orange' ? '#ff6b35' : colors.text === 'text-red-400' ? '#ef4444' : '#22c55e'}
              strokeWidth="3"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
            {/* Glow effect */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={colors.text.split('-')[1] === 'orange' ? '#ff6b35' : colors.text === 'text-red-400' ? '#ef4444' : '#22c55e'}
              strokeWidth="1"
              opacity="0.2"
              filter="blur(2)"
            />
          </svg>

          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-4xl font-bold ${colors.text}`}>{riskScore}</div>
            <div className="text-gray-400 text-xs mt-1">Risk %</div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="flex-1 ml-12">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                label="Bug Growth"
                value="45"
                unit="+%"
                trend="up"
                icon={<AlertCircle size={16} />}
              />
              <MetricCard
                label="Dev Irregularity"
                value="35"
                unit="%"
                trend="up"
                icon={<AlertCircle size={16} />}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <MetricCard label="Critical Issues" value="3" unit="" trend="neutral" />
              <MetricCard label="Last Update" value="Now" unit="" trend="neutral" />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-8 pt-6 border-t border-cyber-gray">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
          <span>System under active monitoring • {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string;
  unit: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
}

const MetricCard = ({ label, value, unit, trend = 'neutral', icon }: MetricCardProps) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-warning-orange';
      case 'down':
        return 'text-green-400';
      default:
        return 'text-electric-blue';
    }
  };

  const getTrendBg = () => {
    switch (trend) {
      case 'up':
        return 'bg-orange-900 bg-opacity-30';
      case 'down':
        return 'bg-green-900 bg-opacity-30';
      default:
        return 'bg-cyber-gray-light';
    }
  };

  return (
    <div className={`p-3 rounded-lg ${getTrendBg()} border border-cyber-gray`}>
      <div className="text-gray-500 text-xs mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className={`text-xl font-bold ${getTrendColor()}`}>
          {value}
        </span>
        {unit && <span className="text-xs text-gray-500">{unit}</span>}
      </div>
      {icon && <div className="mt-1 text-gray-600">{icon}</div>}
    </div>
  );
};
