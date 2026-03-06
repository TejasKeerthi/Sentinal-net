import { Github, Search, Loader2 } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface GitHubAnalyzerProps {
  onAnalyze: (repo: string) => void;
  isLoading: boolean;
  currentRepo?: string | null;
}

export const GitHubAnalyzer = ({ onAnalyze, isLoading, currentRepo }: GitHubAnalyzerProps) => {
  const [repoInput, setRepoInput] = useState(currentRepo || '');

  const handleAnalyze = () => {
    if (repoInput.trim()) {
      onAnalyze(repoInput.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const examples = [
    'torvalds/linux',
    'facebook/react',
    'kubernetes/kubernetes',
    'golang/go',
  ];

  return (
    <div className="glass-card p-8 anim-fade-up relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute -top-20 -left-20 w-60 h-60 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #00d4ff, transparent 70%)' }} />
      <div className="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #a855f7, transparent 70%)' }} />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 rounded-xl glass"
            style={{ boxShadow: '0 0 20px rgba(0,212,255,0.15)' }}>
            <Github size={26} className="text-accent" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Analyze GitHub Repository</h2>
            <p className="text-gray-500 text-sm mt-0.5">Real-time NLP analysis of commits, issues, and pull requests</p>
          </div>
        </div>

        <div className="space-y-5">
          {/* Input Section */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={repoInput}
                onChange={(e) => setRepoInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="owner/repo (e.g., TejasKeerthi/ART-VAULT)"
                className="w-full px-5 py-3.5 glass rounded-xl text-white placeholder-gray-600 text-base transition-all duration-300 focus:border-accent/30"
                style={{ border: '1px solid rgba(255,255,255,0.06)' }}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={isLoading || !repoInput.trim()}
              className={clsx(
                'flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold transition-all duration-300 text-base min-w-[140px] justify-center',
                isLoading || !repoInput.trim()
                  ? 'glass text-gray-500 cursor-not-allowed opacity-50'
                  : 'text-void hover-lift'
              )}
              style={!(isLoading || !repoInput.trim()) ? {
                background: 'linear-gradient(135deg, #00d4ff, #38bdf8)',
                boxShadow: '0 0 24px rgba(0,212,255,0.3)',
              } : undefined}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search size={18} />
                  Analyze
                </>
              )}
            </button>
          </div>

          {/* Current Repo Display */}
          {currentRepo && !isLoading && (
            <div className="glass p-3 rounded-xl flex items-center gap-2"
              style={{ borderColor: 'rgba(34,197,94,0.15)' }}>
              <div className="relative">
                <div className="w-2 h-2 bg-success rounded-full" />
                <div className="absolute inset-0 w-2 h-2 bg-success rounded-full animate-ping opacity-40" />
              </div>
              <p className="text-gray-300 text-sm">
                <span className="font-semibold text-success">Currently analyzing:</span> {currentRepo}
              </p>
            </div>
          )}

          {/* Examples Row */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-gray-600 text-xs font-medium uppercase tracking-wider">Popular:</span>
            {examples.map((example) => (
              <button
                key={example}
                onClick={() => {
                  setRepoInput(example);
                  onAnalyze(example);
                }}
                disabled={isLoading}
                className="text-xs px-3 py-1.5 glass rounded-lg hover:border-accent/20 hover:text-accent transition-all disabled:opacity-40 text-gray-400"
              >
                {example}
              </button>
            ))}
          </div>

          {/* Info Tip */}
          <div className="glass p-3 rounded-xl" style={{ borderColor: 'rgba(0,212,255,0.08)' }}>
            <p className="text-gray-500 text-xs leading-relaxed">
              <span className="text-accent font-semibold">Tip:</span>{' '}
              Enter any public GitHub repository. The system will analyze commits, issues, and pull requests using NLP to calculate accurate reliability metrics and risk scores — all in your browser, no backend needed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
