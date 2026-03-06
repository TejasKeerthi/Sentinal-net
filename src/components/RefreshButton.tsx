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
          'flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all duration-300 text-sm',
          isLoading
            ? 'glass text-gray-500 cursor-not-allowed'
            : 'text-void hover-lift'
        )}
        style={!isLoading ? {
          background: 'linear-gradient(135deg, #00d4ff, #38bdf8)',
          boxShadow: '0 0 20px rgba(0,212,255,0.25)',
        } : undefined}
      >
        <RefreshCw
          size={16}
          className={clsx('transition-transform', isLoading && 'animate-spin')}
        />
        <span>{isLoading ? 'Analyzing...' : 'Refresh'}</span>
      </button>
      <span className="text-gray-500 text-xs font-mono">
        {formatLastUpdated(lastUpdated)}
      </span>
    </div>
  );
};
