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
    <div className="bg-gradient-to-br from-cyber-card via-darker-charcoal to-cyber-card rounded-2xl border border-cyan-500 border-opacity-20 p-8 shadow-cyber-glow relative overflow-hidden">    
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-5 pointer-events-none" style={{
        backgroundImage: 'radial-gradient(circle at 20% 50%, #00d4ff 1px, transparent 1px), radial-gradient(circle at 80% 50%, #00d4ff 1px, transparent 1px)',
        backgroundSize: '40px 40px'
      }}></div>

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-electric-blue bg-opacity-15 rounded-xl border border-electric-blue border-opacity-20">
            <Github size={28} className="text-electric-blue" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Analyze GitHub Repository</h2>
            <p className="text-gray-400 text-sm mt-0.5">Real-time NLP analysis of commits, issues, and pull requests</p>
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
                className="w-full px-5 py-3 bg-darker-charcoal border border-cyber-gray-light rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-electric-blue focus:ring-1 focus:ring-electric-blue focus:ring-opacity-30 transition-all text-base"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={isLoading || !repoInput.trim()}
              className={clsx(
                'flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 text-base min-w-[140px] justify-center',
                isLoading || !repoInput.trim()
                  ? 'bg-gray-600 text-gray-300 cursor-not-allowed opacity-60'
                  : 'bg-electric-blue text-darker-charcoal hover:bg-electric-blue-dark shadow-cyber-glow hover:shadow-cyber-intense'
              )}
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
            <div className="p-3 bg-green-900 bg-opacity-15 border border-green-700 border-opacity-30 rounded-xl flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <p className="text-green-300 text-sm">
                <span className="font-semibold">Currently analyzing:</span> {currentRepo}
              </p>
            </div>
          )}

          {/* Examples Row */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-gray-500 text-xs font-medium uppercase tracking-wider">Popular:</span>
            {examples.map((example) => (
              <button
                key={example}
                onClick={() => {
                  setRepoInput(example);
                  onAnalyze(example);
                }}
                disabled={isLoading}
                className="text-xs px-3 py-1.5 bg-cyber-gray-light bg-opacity-50 border border-cyber-gray rounded-lg hover:border-electric-blue hover:text-electric-blue hover:bg-electric-blue hover:bg-opacity-10 transition-all disabled:opacity-50 text-gray-300"
              >
                {example}
              </button>
            ))}
          </div>

          {/* Info Tip */}
          <div className="p-3 bg-blue-900 bg-opacity-10 border border-blue-700 border-opacity-15 rounded-xl">
            <p className="text-gray-400 text-xs leading-relaxed">
              <span className="text-electric-blue font-semibold">Tip:</span>{' '}
              {window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? 'Enter any public GitHub repository. The system will analyze commits, issues, and pull requests using NLP to calculate accurate reliability metrics and risk scores.'
                : 'This is a live demo. To enable real-time GitHub analysis, clone the repo and run the Python backend locally. See the README for setup instructions.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
