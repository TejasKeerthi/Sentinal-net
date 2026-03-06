import { BarChart3, TrendingUp, AlertTriangle, LayoutDashboard, ChevronLeft, ChevronRight } from 'lucide-react';
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
        'fixed left-0 top-0 h-full glass-strong z-50 transition-all duration-500 ease-out',
        isCollapsed ? 'w-20' : 'w-64'
      )}
      style={{
        borderRight: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Ambient gradient at top */}
      <div className="absolute top-0 left-0 right-0 h-32 pointer-events-none"
        style={{ background: 'linear-gradient(180deg, rgba(0,212,255,0.04) 0%, transparent 100%)' }} />

      {/* Header */}
      <div className="relative p-6 border-b border-white/[0.06] flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-3 anim-fade-in">
            <div className="relative w-9 h-9 rounded-xl flex items-center justify-center overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #00d4ff 0%, #a855f7 50%, #ff8c42 100%)',
                boxShadow: '0 0 20px rgba(0,212,255,0.3)',
              }}>
              <span className="text-white font-black text-xs tracking-wider">SN</span>
            </div>
            <div>
              <span className="gradient-text font-black text-sm tracking-wide">SENTINEL-NET</span>
              <div className="text-[9px] text-gray-500 font-medium tracking-widest uppercase">NLP Analytics</div>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="w-9 h-9 mx-auto rounded-xl flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, #00d4ff 0%, #a855f7 50%, #ff8c42 100%)',
              boxShadow: '0 0 20px rgba(0,212,255,0.3)',
            }}>
            <span className="text-white font-black text-xs">SN</span>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={clsx(
            'p-1.5 rounded-lg transition-all duration-300 hover:bg-white/[0.06] text-gray-500 hover:text-accent',
            isCollapsed && 'mx-auto mt-3'
          )}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-3 space-y-1 mt-2">
        {navItems.map(({ id, label, icon: Icon }) => {
          const isActive = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              className={clsx(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative group',
                isActive
                  ? 'text-white'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/[0.03]'
              )}
              title={isCollapsed ? label : undefined}
            >
              {/* Active indicator glow */}
              {isActive && (
                <div className="absolute inset-0 rounded-xl"
                  style={{
                    background: 'linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(168,85,247,0.04) 100%)',
                    border: '1px solid rgba(0,212,255,0.15)',
                    boxShadow: '0 0 20px rgba(0,212,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05)',
                  }}
                />
              )}
              {/* Active left bar */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-full"
                  style={{
                    background: 'linear-gradient(180deg, #00d4ff, #a855f7)',
                    boxShadow: '0 0 12px rgba(0,212,255,0.5)',
                  }}
                />
              )}
              <Icon size={20} className={clsx(
                'relative z-10 transition-all duration-300',
                isActive ? 'text-accent' : 'group-hover:text-accent/70'
              )} />
              {!isCollapsed && (
                <span className={clsx(
                  'text-sm font-medium relative z-10 transition-all duration-300',
                  isActive && 'gradient-text-subtle font-semibold'
                )}>{label}</span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Status */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/[0.04]">
          <div className="text-xs text-gray-600">
            <div className="flex items-center gap-2 mb-2">
              <div className="relative">
                <div className="w-2 h-2 bg-success rounded-full" />
                <div className="absolute inset-0 w-2 h-2 bg-success rounded-full animate-ping opacity-40" />
              </div>
              <span className="text-gray-400">System Active</span>
            </div>
            <div className="text-gray-600 font-mono text-[10px]">v2.0 — Liquid Glass</div>
          </div>
        </div>
      )}
    </div>
  );
};
