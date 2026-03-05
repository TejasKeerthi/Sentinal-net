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
        return {
          icon: AlertTriangle,
          bgColor: 'bg-red-900 bg-opacity-20',
          borderColor: 'border-red-700',
          badgeBg: 'bg-red-900 bg-opacity-50',
          badgeText: 'text-red-300',
          iconColor: 'text-red-400',
          hoverEffect: 'hover:bg-red-900 hover:bg-opacity-30',
        };
      case 'Negative':
        return {
          icon: AlertCircle,
          bgColor: 'bg-warning-orange bg-opacity-10',
          borderColor: 'border-warning-orange border-opacity-30',
          badgeBg: 'bg-orange-900 bg-opacity-50',
          badgeText: 'text-warning-orange',
          iconColor: 'text-warning-orange',
          hoverEffect: 'hover:bg-orange-900 hover:bg-opacity-20',
        };
      case 'Neutral':
        return {
          icon: CheckCircle2,
          bgColor: 'bg-green-900 bg-opacity-10',
          borderColor: 'border-green-700 border-opacity-30',
          badgeBg: 'bg-green-900 bg-opacity-50',
          badgeText: 'text-green-300',
          iconColor: 'text-green-400',
          hoverEffect: 'hover:bg-green-900 hover:bg-opacity-20',
        };
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

  const getSourceBadge = (source: SignalItem['source']) => {
    const config: Record<SignalItem['source'], { bg: string; text: string; label: string; icon: any }> = {
      commit: { bg: 'bg-electric-blue bg-opacity-20', text: 'text-electric-blue', label: 'Commit', icon: Zap },
      issue: { bg: 'bg-purple-900 bg-opacity-20', text: 'text-purple-300', label: 'Issue', icon: AlertCircle },
      alert: { bg: 'bg-red-900 bg-opacity-20', text: 'text-red-300', label: 'Alert', icon: AlertTriangle },
    };
    return config[source];
  };

  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'text-red-400';
      case 'high':
        return 'text-warning-orange';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-cyber-gray-light p-6 cyber-border-glow">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Brain size={28} className="text-electric-blue neon-text" />
          Semantic Signal Feed
        </h2>
        <span className="px-3 py-1 rounded-full bg-electric-blue bg-opacity-20 text-electric-blue text-xs font-semibold">
          {signals.length} signals
        </span>
      </div>

      <div className="space-y-3 max-h-[700px] overflow-y-auto scrollbar-hide">
        {signals.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Brain size={48} className="mx-auto mb-4 opacity-30" />
            <p className="text-sm">No signals detected</p>
          </div>
        ) : (
          signals.map((signal, index) => {
            const statusConfig = getStatusConfig(signal.status);
            const StatusIcon = statusConfig.icon;
            const sourceBadge = getSourceBadge(signal.source);
            const SourceIcon = sourceBadge.icon;
            const nlp = signal.nlp;

            return (
              <div
                key={signal.id}
                className={clsx(
                  'p-4 rounded-lg border transition-all duration-300 hover:border-electric-blue hover:shadow-cyber-glow group cursor-pointer',
                  'hover-lift stable-layout',
                  statusConfig.bgColor,
                  statusConfig.borderColor,
                  statusConfig.hoverEffect
                )}
                style={{
                  animation: `slideInLeft 0.5s ease-out backwards`,
                  animationDelay: `${index * 0.05}s`,
                }}
              >
                <div className="flex items-start gap-4">
                  {/* Icon with glow */}
                  <div className={clsx('flex-shrink-0 mt-1 transition-all duration-300', statusConfig.iconColor)}>
                    <StatusIcon size={24} className="group-hover:scale-110" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Message */}
                    <p className="text-gray-200 text-sm leading-relaxed mb-3 group-hover:text-white transition-colors break-words">
                      {signal.message}
                    </p>

                    {/* NLP Metadata */}
                    {nlp && (
                      <div className="mb-3 p-3 rounded bg-black bg-opacity-20 border border-cyber-gray-light border-opacity-50">
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="flex items-center gap-1">
                            <span className="text-gray-400">Intent:</span>
                            <span className="text-electric-blue font-semibold">
                              {nlp.intent.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-400">Sentiment:</span>
                            <span className={clsx(
                              'font-semibold',
                              nlp.sentiment === 'positive' ? 'text-green-400' :
                              nlp.sentiment === 'negative' ? 'text-red-400' :
                              'text-gray-400'
                            )}>
                              {nlp.sentiment}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-400">Risk:</span>
                            <span className={clsx('font-semibold', getRiskLevelColor(nlp.risk_level))}>
                              {nlp.risk_level}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-gray-400">Urgency:</span>
                            <span className={nlp.has_urgency ? 'text-red-400 font-semibold' : 'text-gray-500'}>
                              {nlp.has_urgency ? 'High' : 'Normal'}
                            </span>
                          </div>
                        </div>
                        
                        {/* Keywords */}
                        {nlp.keywords && nlp.keywords.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-cyber-gray-light border-opacity-30">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-gray-500 text-xs">Keywords:</span>
                              {nlp.keywords.slice(0, 3).map((keyword, i) => (
                                <span
                                  key={i}
                                  className="px-2 py-0.5 rounded text-xs bg-electric-blue bg-opacity-15 text-electric-blue"
                                >
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Metadata Badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={clsx(
                          'px-2 py-1 rounded-sm text-xs font-semibold transition-all duration-200',
                          statusConfig.badgeBg,
                          statusConfig.badgeText
                        )}
                      >
                        {signal.status}
                      </span>
                      <span
                        className={clsx(
                          'px-2 py-1 rounded-sm text-xs font-medium flex items-center gap-1 transition-all duration-200',
                          sourceBadge.bg,
                          sourceBadge.text
                        )}
                      >
                        <SourceIcon size={12} />
                        {sourceBadge.label}
                      </span>
                      
                      {/* Bug indicator */}
                      {nlp?.is_bug && (
                        <span className="px-2 py-1 rounded-sm text-xs font-semibold bg-red-900 bg-opacity-40 text-red-300 flex items-center gap-1">
                          <AlertTriangle size={12} />
                          Bug
                        </span>
                      )}
                      
                      <div className="flex items-center gap-1 text-gray-500 text-xs ml-auto transition-all duration-200 group-hover:text-gray-300">
                        <Clock size={14} />
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

      {/* Custom Scrollbar Styles */}
      <style>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }

        /* Smooth scrollbar for signal feed */
        .max-h-\\[700px\\]::-webkit-scrollbar {
          width: 6px;
        }
        
        .max-h-\\[700px\\]::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .max-h-\\[700px\\]::-webkit-scrollbar-thumb {
          background: rgba(0, 212, 255, 0.3);
          border-radius: 3px;
          transition: background 0.2s;
        }
        
        .max-h-\\[700px\\]::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 212, 255, 0.6);
        }
      `}</style>
    </div>
  );
};
