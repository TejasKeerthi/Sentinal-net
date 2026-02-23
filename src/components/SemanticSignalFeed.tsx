import { AlertTriangle, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
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
        };
      case 'Negative':
        return {
          icon: AlertCircle,
          bgColor: 'bg-warning-orange bg-opacity-10',
          borderColor: 'border-warning-orange border-opacity-30',
          badgeBg: 'bg-orange-900 bg-opacity-50',
          badgeText: 'text-warning-orange',
          iconColor: 'text-warning-orange',
        };
      case 'Neutral':
        return {
          icon: CheckCircle2,
          bgColor: 'bg-green-900 bg-opacity-10',
          borderColor: 'border-green-700 border-opacity-30',
          badgeBg: 'bg-green-900 bg-opacity-50',
          badgeText: 'text-green-300',
          iconColor: 'text-green-400',
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
    const config: Record<SignalItem['source'], { bg: string; text: string; label: string }> = {
      commit: { bg: 'bg-electric-blue bg-opacity-20', text: 'text-electric-blue', label: 'Commit' },
      issue: { bg: 'bg-purple-900 bg-opacity-20', text: 'text-purple-300', label: 'Issue' },
      alert: { bg: 'bg-red-900 bg-opacity-20', text: 'text-red-300', label: 'Alert' },
    };
    return config[source];
  };

  return (
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-cyber-gray-light p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Semantic Signal Feed</h2>

      <div className="space-y-3 max-h-[600px] overflow-y-auto scrollbar-hide">
        {signals.map((signal) => {
          const statusConfig = getStatusConfig(signal.status);
          const StatusIcon = statusConfig.icon;
          const sourceBadge = getSourceBadge(signal.source);

          return (
            <div
              key={signal.id}
              className={clsx(
                'p-4 rounded-lg border transition-all duration-200 hover:border-electric-blue hover:shadow-cyber-glow group cursor-pointer',
                statusConfig.bgColor,
                statusConfig.borderColor
              )}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className={`flex-shrink-0 mt-1 ${statusConfig.iconColor}`}>
                  <StatusIcon size={20} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Message */}
                  <p className="text-gray-200 text-sm leading-relaxed mb-2 group-hover:text-white transition-colors">
                    {signal.message}
                  </p>

                  {/* Metadata */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={clsx(
                        'px-2 py-1 rounded-sm text-xs font-semibold',
                        statusConfig.badgeBg,
                        statusConfig.badgeText
                      )}
                    >
                      {signal.status}
                    </span>
                    <span
                      className={clsx(
                        'px-2 py-1 rounded-sm text-xs font-medium',
                        sourceBadge.bg,
                        sourceBadge.text
                      )}
                    >
                      {sourceBadge.label}
                    </span>
                    <div className="flex items-center gap-1 text-gray-500 text-xs ml-auto">
                      <Clock size={14} />
                      <span>{formatTime(signal.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {signals.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-sm">No signals detected</div>
        </div>
      )}

      {/* Custom Scrollbar Styles */}
      <style>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};
