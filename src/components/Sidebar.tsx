import { BarChart3, TrendingUp, AlertTriangle, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface SidebarProps {
  activeTab: 'overview' | 'signals' | 'trends' | 'reports';
  onTabChange: (tab: 'overview' | 'signals' | 'trends' | 'reports') => void;
}

export const Sidebar = ({ activeTab, onTabChange }: SidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems = [
    { id: 'overview' as const, label: 'Overview', icon: LayoutDashboard },
    { id: 'signals' as const, label: 'Micro-Crisis Signals', icon: AlertTriangle },
    { id: 'trends' as const, label: 'Temporal Trends', icon: TrendingUp },
    { id: 'reports' as const, label: 'Risk Reports', icon: BarChart3 },
  ];

  return (
    <div
      className={clsx(
        'fixed left-0 top-0 h-full bg-darker-charcoal border-r border-electric-blue transition-all duration-300 z-50',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="p-6 border-b border-cyber-gray flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-electric-blue to-warning-orange rounded-lg flex items-center justify-center">
              <span className="text-darker-charcoal font-bold text-sm">SN</span>
            </div>
            <span className="text-electric-blue font-bold text-sm">SENTINEL-NET</span>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-cyber-gray-light rounded transition-colors"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={clsx(
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
              activeTab === id
                ? 'bg-cyber-gray-light border-l-2 border-electric-blue text-electric-blue'
                : 'text-gray-400 hover:text-electric-blue hover:bg-cyber-gray'
            )}
            title={isCollapsed ? label : undefined}
          >
            <Icon size={20} />
            {!isCollapsed && <span className="text-sm font-medium">{label}</span>}
          </button>
        ))}
      </nav>

      {/* Footer Status */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-cyber-gray bg-darker-charcoal">
          <div className="text-xs text-gray-500">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>System Active</span>
            </div>
            <div className="text-gray-600">Last update: now</div>
          </div>
        </div>
      )}
    </div>
  );
};
