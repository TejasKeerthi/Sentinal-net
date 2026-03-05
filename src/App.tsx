import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
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
    <div className="flex min-h-screen bg-darker-charcoal text-white">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 ml-64 p-8 overflow-auto">
        <div className="max-w-7xl mx-auto">
          {error && (
            <div className="mb-4 p-3 bg-cyber-card border border-cyan-500 border-opacity-20 rounded-xl text-gray-400 text-sm max-w-6xl mx-auto flex items-center gap-2">
              <span className="text-electric-blue text-base">ℹ</span>
              {error}
            </div>
          )}
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;
