import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { AmbientBackground } from './components/AmbientBackground';
import { OverviewPage, SignalsPage, TrendsPage, ReportsPage } from './pages';
import { useSystemData } from './hooks/useSystemData';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'signals' | 'trends' | 'reports'>('overview');
  const { data, isLoading, refreshData, analyzeGitHubRepo, currentRepo, error } = useSystemData();

  const renderPage = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage 
          data={data} 
          isLoading={isLoading} 
          onRefresh={refreshData}
          onAnalyzeGitHub={analyzeGitHubRepo}
          currentRepo={currentRepo}
        />;
      case 'signals':
        return <SignalsPage data={data} isLoading={isLoading} onRefresh={refreshData} />;
      case 'trends':
        return <TrendsPage data={data} isLoading={isLoading} onRefresh={refreshData} />;
      case 'reports':
        return <ReportsPage data={data} isLoading={isLoading} onRefresh={refreshData} />;
      default:
        return <OverviewPage 
          data={data} 
          isLoading={isLoading} 
          onRefresh={refreshData}
          onAnalyzeGitHub={analyzeGitHubRepo}
          currentRepo={currentRepo}
        />;
    }
  };

  return (
    <div className="relative min-h-screen bg-void text-white noise">
      {/* Ambient living background */}
      <AmbientBackground />

      <div className="relative z-10 flex min-h-screen">
        {/* Sidebar Navigation */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Main Content Area */}
        <main className="flex-1 ml-64 p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {error && (
              <div className="mb-6 glass-card p-4 anim-fade-up"
                style={{ borderColor: 'rgba(255,107,53,0.25)' }}>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full mt-1.5 shrink-0" style={{ background: '#ff6b35' }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm" style={{ color: '#ff6b35' }}>{error}</p>
                    {error.toLowerCase().includes('rate limit') && (
                      <p className="text-gray-500 text-xs mt-1.5 leading-relaxed">
                        Fix: add your token to{' '}
                        <code className="text-accent bg-white/5 px-1 py-0.5 rounded">.env</code>{' '}
                        →{' '}
                        <code className="text-accent bg-white/5 px-1 py-0.5 rounded">GITHUB_TOKEN=ghp_…</code>
                        , then restart the dev server.{' '}
                        <a
                          href="https://github.com/settings/tokens/new?description=sentinel-net&scopes=public_repo"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline hover:opacity-80 transition-opacity"
                          style={{ color: '#00d4ff' }}
                        >
                          Generate token →
                        </a>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            {renderPage()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
