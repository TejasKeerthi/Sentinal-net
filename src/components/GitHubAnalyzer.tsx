import { Github, Search } from 'lucide-react';
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
    <div className="bg-gradient-to-br from-cyber-card to-darker-charcoal rounded-xl border border-cyan-500 border-opacity-20 p-6 mb-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-electric-blue bg-opacity-10 rounded-lg">
          <Github size={24} className="text-electric-blue" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Analyze GitHub Repository</h2>
          <p className="text-gray-400 text-sm">Real-time analysis of actual projects</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Input Section */}
        <div className="flex gap-2">
          <input
            type="text"
            value={repoInput}
            onChange={(e) => setRepoInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="owner/repo (e.g., torvalds/linux)"
            className="flex-1 px-4 py-2 bg-darker-charcoal border border-cyber-gray rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-electric-blue transition-colors"
          />
          <button
            onClick={handleAnalyze}
            disabled={isLoading || !repoInput.trim()}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all',
              isLoading || !repoInput.trim()
                ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
                : 'bg-electric-blue text-darker-charcoal hover:bg-electric-blue-dark shadow-cyber-glow'
            )}
          >
            <Search size={18} />
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* Current Repo Display */}
        {currentRepo && (
          <div className="p-3 bg-green-900 bg-opacity-20 border border-green-700 border-opacity-30 rounded-lg">
            <p className="text-green-300 text-sm">
              <span className="font-semibold">Currently analyzing:</span> {currentRepo}
            </p>
          </div>
        )}

        {/* Examples */}
        <div>
          <p className="text-gray-500 text-xs mb-2">Popular projects:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {examples.map((example) => (
              <button
                key={example}
                onClick={() => {
                  setRepoInput(example);
                  onAnalyze(example);
                }}
                disabled={isLoading}
                className="text-xs px-2 py-1 bg-cyber-gray-light border border-cyber-gray rounded hover:border-electric-blue hover:text-electric-blue transition-all disabled:opacity-50"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="p-3 bg-blue-900 bg-opacity-10 border border-blue-700 border-opacity-20 rounded-lg">
          <p className="text-gray-300 text-xs">
            💡 <span className="font-semibold">Tip:</span> Enter any public GitHub repository. The API will analyze commits, issues, and pull requests to calculate reliability metrics.
          </p>
        </div>
      </div>
    </div>
  );
};
