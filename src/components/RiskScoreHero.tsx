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
  const displayScore = Math.round(Math.max(0, Math.min(100, riskScore)));

  const healthConfig = {
    Critical: { color: '#ff4d6a', glow: 'rgba(255,77,106,0.3)', label: 'Critical Risk', ring: 'danger' },
    Warning: { color: '#ff8c42', glow: 'rgba(255,140,66,0.3)', label: 'Elevated Risk', ring: 'warn' },
    Nominal: { color: '#22c55e', glow: 'rgba(34,197,94,0.3)', label: 'Low Risk', ring: 'success' },
  }[systemHealth];

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;

  return (
    <div className="glass-card p-8 anim-fade-up relative overflow-hidden">
      {/* Ambient glow in background */}
      <div className="absolute -top-20 -right-20 w-60 h-60 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: healthConfig.glow }} />

      {/* Header */}
      <div className="flex items-start justify-between mb-8 relative">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1 flex items-center gap-3">
            <div className="p-2 rounded-xl glass" style={{
              boxShadow: `0 0 20px ${healthConfig.glow}`,
            }}>
              <Shield size={24} className="text-accent" />
            </div>
            Software Failure Risk Score
          </h2>
          <p className="text-gray-500 text-sm ml-14">ML-powered real-time system reliability assessment</p>
        </div>
        <div
          className={clsx(
            'px-4 py-2 rounded-full text-xs font-bold tracking-wide border',
            systemHealth === 'Critical' && 'anim-heartbeat'
          )}
          style={{
            color: healthConfig.color,
            borderColor: `${healthConfig.color}33`,
            backgroundColor: `${healthConfig.color}0d`,
            boxShadow: `0 0 16px ${healthConfig.glow}`,
          }}
        >
          {systemHealth}
        </div>
      </div>

      <div className="flex items-center justify-center gap-10 flex-wrap">
        {/* Circular Progress — glass morphism gauge */}
        <div className="relative w-52 h-52 flex-shrink-0">
          {/* Outer pulse ring */}
          <div className="absolute inset-0 rounded-full" style={{
            border: `2px solid ${healthConfig.color}15`,
            animation: 'pulseRing 3s ease-out infinite',
          }} />

          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            {/* Track */}
            <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3" />
            {/* Progress */}
            <circle
              cx="50" cy="50" r="45" fill="none"
              stroke={healthConfig.color}
              strokeWidth="4"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
              style={{ filter: `drop-shadow(0 0 10px ${healthConfig.glow})` }}
            />
          </svg>

          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="font-black text-5xl" style={{
              color: healthConfig.color,
              textShadow: `0 0 30px ${healthConfig.glow}`,
            }}>
              {displayScore}
            </div>
            <div className="text-gray-500 text-[10px] mt-0.5 font-semibold tracking-widest uppercase">Risk %</div>
            <div className="text-[11px] font-bold mt-1" style={{ color: healthConfig.color }}>
              {healthConfig.label}
            </div>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="flex-1 min-w-[280px]">
          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="Commits (30d)" value={metadata?.commits_30d?.toString() || '--'}
              icon={<TrendingUp size={15} />} color="#00d4ff" delay={0.1} />
            <MetricCard label="Contributors" value={metadata?.contributors_30d?.toString() || '--'}
              icon={<Zap size={15} />} color="#a855f7" delay={0.2} />
            <MetricCard label="Open Issues" value={metadata?.open_issues?.toString() || '--'}
              icon={<AlertCircle size={15} />} color="#ff8c42" delay={0.3} />
            <MetricCard label="Last Update" value="Now"
              icon={<Clock size={15} />} color="#22c55e" delay={0.4} />
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-8 pt-5 border-t border-white/[0.04]">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="relative">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: healthConfig.color }} />
            <div className="absolute inset-0 w-2 h-2 rounded-full animate-ping opacity-30" style={{ backgroundColor: healthConfig.color }} />
          </div>
          <span>System under active ML monitoring &bull; {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Bottom gradient accent */}
      <div className="mt-4 h-px"
        style={{ background: `linear-gradient(90deg, ${healthConfig.color}44, #a855f744, transparent)` }} />
    </div>
  );
};

interface MetricCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  color: string;
  delay: number;
}

const MetricCard = ({ label, value, icon, color, delay }: MetricCardProps) => (
  <div
    className="glass p-4 rounded-xl transition-all duration-300 hover:bg-white/[0.04] hover-lift anim-fade-up"
    style={{ animationDelay: `${delay}s` }}
  >
    <div className="text-gray-500 text-[11px] mb-2 flex items-center gap-1.5 font-medium">
      <span style={{ color }}>{icon}</span>
      {label}
    </div>
    <div className="text-xl font-bold" style={{ color }}>
      {value}
    </div>
  </div>
);
