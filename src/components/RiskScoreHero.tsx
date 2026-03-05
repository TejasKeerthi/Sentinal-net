import { AlertCircle, TrendingUp, Zap, Clock, Shield } from 'lucide-react';
import clsx from 'clsx';

interface RiskScoreHeroProps {
  riskScore: number;
  systemHealth: 'Critical' | 'Warning' | 'Nominal';
  metadata?: {
    commits_30d?: number;
    contributors_30d?: number;
    open_issues?: number;
  };
}

export const RiskScoreHero = ({ riskScore, systemHealth, metadata }: RiskScoreHeroProps) => {
  const getHealthColor = () => {
    switch (systemHealth) {
      case 'Critical':
        return { 
          bg: 'from-red-900 to-red-700', 
          text: 'text-red-400', 
          badge: 'bg-red-900 text-red-300',
          glowColor: 'rgba(239, 68, 68, 0.3)'
        };
      case 'Warning':
        return { 
          bg: 'from-warning-orange to-orange-700', 
          text: 'text-warning-orange', 
          badge: 'bg-orange-900 text-warning-orange',
          glowColor: 'rgba(255, 107, 53, 0.3)'
        };
      case 'Nominal':
        return { 
          bg: 'from-green-900 to-green-700', 
          text: 'text-green-400', 
          badge: 'bg-green-900 text-green-300',
          glowColor: 'rgba(74, 222, 128, 0.3)'
        };
    }
  };

  const colors = getHealthColor();
  // Clamp and round risk score to a clean integer 0-100
  const displayScore = Math.round(Math.max(0, Math.min(100, riskScore)));
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;

  const riskStatus = displayScore > 75 ? 'Critical Risk' : displayScore > 50 ? 'Elevated Risk' : 'Low Risk';

  return (
    <div 
      className="bg-gradient-to-br from-cyber-card to-darker-charcoal p-8 rounded-xl border border-cyber-gray-light shadow-cyber-glow hover-lift card-enter"
      style={{
        animation: 'fadeIn 0.7s ease-out'
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
            <Shield size={32} className="text-electric-blue neon-text" />
            Software Failure Risk Score
          </h2>
          <p className="text-gray-400 text-sm">ML-powered real-time system reliability assessment</p>
        </div>
        <div className={clsx(
          'px-4 py-2 rounded-full text-sm font-bold transition-all duration-300',
          colors.badge,
          systemHealth === 'Critical' && 'animate-pulse'
        )}>
          <span className="inline-block">{systemHealth}</span>
        </div>
      </div>

      <div className="flex items-center justify-center gap-8 flex-wrap">
        {/* Circular Progress with Animation */}
        <div className="relative w-48 h-48 flex-shrink-0">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            {/* Outer glow circle */}
            <circle
              cx="50"
              cy="50"
              r="48"
              fill="none"
              stroke={colors.glowColor}
              strokeWidth="1.5"
              opacity="0.3"
            />
            {/* Background circle */}
            <circle cx="50" cy="50" r="45" fill="none" stroke="#2a2a3e" strokeWidth="2" />
            {/* Progress circle with animation */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={colors.text.split('-')[1] === 'orange' ? '#ff6b35' : colors.text === 'text-red-400' ? '#ef4444' : '#22c55e'}
              strokeWidth="4"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
              style={{
                filter: `drop-shadow(0 0 8px ${colors.glowColor})`
              }}
            />
          </svg>

          {/* Center content with animation */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div 
              className={`font-black ${colors.text} ${displayScore === 100 ? 'text-3xl' : 'text-5xl'}`}
              style={{
                animation: 'fadeIn 0.8s ease-out 0.3s backwards',
                textShadow: `0 0 20px ${colors.glowColor}`,
                letterSpacing: '-0.02em'
              }}
            >
              {displayScore}
            </div>
            <div className="text-gray-400 text-xs mt-1 font-semibold tracking-wide">Risk %</div>
            <div className={`text-xs font-bold mt-1 ${colors.text}`}>
              {riskStatus}
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="flex-1 min-w-[280px]">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                label="Commits (30d)"
                value={metadata?.commits_30d?.toString() || '--'}
                unit=""
                trend={metadata?.commits_30d ? (metadata.commits_30d > 20 ? 'up' : 'neutral') : 'neutral'}
                icon={<TrendingUp size={16} />}
                delay={0.1}
              />
              <MetricCard
                label="Contributors"
                value={metadata?.contributors_30d?.toString() || '--'}
                unit=""
                trend="neutral"
                icon={<Zap size={16} />}
                delay={0.2}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <MetricCard 
                label="Open Issues" 
                value={metadata?.open_issues?.toString() || '--'} 
                unit="" 
                trend={metadata?.open_issues ? (metadata.open_issues > 10 ? 'up' : 'neutral') : 'neutral'}
                icon={<AlertCircle size={16} />}
                delay={0.3}
              />
              <MetricCard 
                label="Last Update" 
                value="Now" 
                unit="" 
                trend="neutral"
                icon={<Clock size={16} />}
                delay={0.4}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-8 pt-6 border-t border-cyber-gray">
        <div className="flex items-center gap-2 text-sm text-gray-400 transition-colors duration-300 hover:text-gray-300">
          <div className={clsx(
            'w-2 h-2 rounded-full',
            systemHealth === 'Critical' ? 'bg-red-500 animate-pulse' :
            systemHealth === 'Warning' ? 'bg-yellow-500 animate-pulse' :
            'bg-green-500 animate-pulse'
          )}></div>
          <span>System under active ML monitoring • {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Decorative gradient line */}
      <div className="mt-4 h-0.5 bg-gradient-to-r from-electric-blue via-warning-orange to-transparent opacity-30"></div>
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string;
  unit: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  delay?: number;
}

const MetricCard = ({ label, value, unit, trend = 'neutral', icon, delay = 0 }: MetricCardProps) => {
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
        return 'bg-orange-900 bg-opacity-20 border-orange-700';
      case 'down':
        return 'bg-green-900 bg-opacity-20 border-green-700';
      default:
        return 'bg-cyber-gray-light border-cyber-gray';
    }
  };

  return (
    <div 
      className={`p-4 rounded-lg border transition-all duration-300 hover:scale-105 hover-lift ${getTrendBg()}`}
      style={{
        animation: `slideInRight 0.6s ease-out backwards`,
        animationDelay: `${delay}s`
      }}
    >
      <div className="text-gray-500 text-xs mb-2 flex items-center gap-1">
        {icon && <span className={getTrendColor()}>{icon}</span>}
        {label}
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${getTrendColor()}`}>
          {value}
        </span>
        {unit && <span className="text-xs text-gray-500 font-medium">{unit}</span>}
      </div>
    </div>
  );
};
