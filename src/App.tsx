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
              <div className="mb-6 glass-card p-4 flex items-center gap-3 anim-fade-up"
                style={{ borderColor: 'rgba(0,212,255,0.15)' }}>
                <div className="w-2 h-2 rounded-full bg-accent anim-heartbeat" />
                <span className="text-gray-400 text-sm">{error}</span>
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
