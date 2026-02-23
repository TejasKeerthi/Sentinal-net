import { RefreshCw } from 'lucide-react';
import clsx from 'clsx';

interface RefreshButtonProps {
  onClick: () => void;
  isLoading: boolean;
  lastUpdated: string;
}

export const RefreshButton = ({ onClick, isLoading, lastUpdated }: RefreshButtonProps) => {
  const formatLastUpdated = (iso: string) => {
    const date = new Date(iso);
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSeconds < 1) return 'just now';
    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    return date.toLocaleTimeString();
  };

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={onClick}
        disabled={isLoading}
        className={clsx(
          'flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200',
          isLoading
            ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
            : 'bg-gradient-to-r from-electric-blue to-electric-blue-dark hover:from-electric-blue hover:to-electric-blue text-darker-charcoal shadow-cyber-glow hover:shadow-cyber-intense'
        )}
      >
        <RefreshCw
          size={18}
          className={clsx('transition-transform', isLoading && 'animate-spin')}
        />
        <span>{isLoading ? 'Analyzing...' : 'Refresh Analysis'}</span>
      </button>
      <span className="text-gray-400 text-sm">
        Last update: <span className="text-electric-blue">{formatLastUpdated(lastUpdated)}</span>
      </span>
    </div>
  );
};
