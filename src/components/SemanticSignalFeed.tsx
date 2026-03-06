import { AlertTriangle, AlertCircle, CheckCircle2, Clock, Zap, Brain, Tag } from 'lucide-react';
import type { SignalItem } from '../types';
import clsx from 'clsx';

interface SemanticSignalFeedProps {
  signals: SignalItem[];
}

export const SemanticSignalFeed = ({ signals }: SemanticSignalFeedProps) => {
  const getStatusConfig = (status: SignalItem['status']) => {
    switch (status) {
      case 'Urgent':
        return { icon: AlertTriangle, color: '#ff4d6a', glow: 'rgba(255,77,106,0.1)' };
      case 'Negative':
        return { icon: AlertCircle, color: '#ff8c42', glow: 'rgba(255,140,66,0.08)' };
      case 'Neutral':
        return { icon: CheckCircle2, color: '#22c55e', glow: 'rgba(34,197,94,0.08)' };
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
    if (diffMinutes < 1) return 'just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const sourceColors: Record<SignalItem['source'], { color: string; label: string }> = {
    commit: { color: '#00d4ff', label: 'Commit' },
    issue: { color: '#a855f7', label: 'Issue' },
    alert: { color: '#ff4d6a', label: 'Alert' },
  };

  const getRiskColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical': return '#ff4d6a';
      case 'high': return '#ff8c42';
      case 'medium': return '#fbbf24';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  return (
    <div className="glass-card p-6 anim-fade-up" style={{ animationDelay: '0.2s' }}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-3">
          <div className="p-2 rounded-xl glass" style={{ boxShadow: '0 0 16px rgba(0,212,255,0.12)' }}>
            <Brain size={22} className="text-accent" />
          </div>
          Semantic Signal Feed
        </h2>
        <span className="px-3 py-1 rounded-full text-[11px] font-semibold glass text-accent"
          style={{ borderColor: 'rgba(0,212,255,0.15)' }}>
          {signals.length} signals
        </span>
      </div>

      <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1 stagger"
        style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(0,212,255,0.2) transparent' }}>
        {signals.length === 0 ? (
          <div className="text-center py-16 text-gray-600">
            <Brain size={40} className="mx-auto mb-3 opacity-20" />
            <p className="text-sm">No signals detected</p>
          </div>
        ) : (
          signals.map((signal, index) => {
            const sc = getStatusConfig(signal.status);
            const StatusIcon = sc.icon;
            const src = sourceColors[signal.source];
            const nlp = signal.nlp;

            return (
              <div
                key={signal.id}
                className="glass p-4 rounded-xl transition-all duration-300 hover:bg-white/[0.04] group cursor-pointer anim-fade-up"
                style={{
                  animationDelay: `${index * 0.04}s`,
                  borderColor: 'rgba(255,255,255,0.04)',
                }}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-0.5 transition-all duration-300 group-hover:scale-110" style={{ color: sc.color }}>
                    <StatusIcon size={20} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-300 text-sm leading-relaxed mb-2 group-hover:text-white transition-colors break-words">
                      {signal.message}
                    </p>

                    {/* NLP Metadata */}
                    {nlp && (
                      <div className="mb-2.5 p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
                        <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                          <div className="flex items-center gap-1">
                            <span className="text-gray-500">Intent:</span>
                            <span className="text-accent font-semibold">{nlp.intent.replace('_', ' ')}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-500">Sentiment:</span>
                            <span className="font-semibold" style={{
                              color: nlp.sentiment === 'positive' ? '#22c55e' : nlp.sentiment === 'negative' ? '#ff4d6a' : '#6b7280'
                            }}>{nlp.sentiment}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-500">Risk:</span>
                            <span className="font-semibold" style={{ color: getRiskColor(nlp.risk_level) }}>{nlp.risk_level}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-500">Urgency:</span>
                            <span className={nlp.has_urgency ? 'text-danger font-semibold' : 'text-gray-600'}>
                              {nlp.has_urgency ? 'High' : 'Normal'}
                            </span>
                          </div>
                        </div>
                        
                        {nlp.keywords && nlp.keywords.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-white/[0.04] flex items-center gap-1.5 flex-wrap">
                            <Tag size={10} className="text-gray-600" />
                            {nlp.keywords.slice(0, 3).map((keyword, i) => (
                              <span key={i} className="px-1.5 py-0.5 rounded text-[10px] bg-accent/10 text-accent/80">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold"
                        style={{
                          color: sc.color,
                          backgroundColor: `${sc.color}0d`,
                          border: `1px solid ${sc.color}22`,
                        }}>
                        {signal.status}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-medium flex items-center gap-1"
                        style={{
                          color: src.color,
                          backgroundColor: `${src.color}0d`,
                          border: `1px solid ${src.color}22`,
                        }}>
                        <Zap size={9} />
                        {src.label}
                      </span>
                      
                      {nlp?.is_bug && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-danger/10 text-danger border border-danger/20 flex items-center gap-1">
                          <AlertTriangle size={9} />
                          Bug
                        </span>
                      )}
                      
                      <div className="flex items-center gap-1 text-gray-600 text-[10px] ml-auto">
                        <Clock size={11} />
                        <span>{formatTime(signal.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
