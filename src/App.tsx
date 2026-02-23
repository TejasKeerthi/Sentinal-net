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
        {error && (
          <div className="mb-4 p-4 bg-warning-orange bg-opacity-10 border border-warning-orange border-opacity-50 rounded-lg text-warning-orange">
            <strong>Connection Status:</strong> {error}
          </div>
        )}
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
