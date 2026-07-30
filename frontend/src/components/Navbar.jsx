import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, History, Activity, Settings, ShieldAlert, Cpu, Terminal } from 'lucide-react';

export default function Navbar({ integrity }) {
  const location = useLocation();

  const isSafeMode = integrity && integrity.safe_mode;

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Playground', path: '/playground', icon: Terminal },
    { name: 'Versions', path: '/versions', icon: History },
    { name: 'Health', path: '/health', icon: Activity },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <nav className="glass-panel sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-blue-400 group-hover:rotate-12 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white">AIVAR</span>
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                GOVERNANCE v1.0
              </span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-wider uppercase font-medium">Enterprise Multi-Agent Platform</p>
          </div>
        </Link>

        {/* Navigation Items */}
        <div className="flex items-center gap-1 md:gap-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-inner'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span className="hidden sm:inline">{link.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Integrity Status Pill */}
        <div className="flex items-center gap-3">
          {isSafeMode ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-950/80 border border-red-500/50 text-red-300 text-xs font-medium animate-pulse">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <span className="font-mono font-bold">SAFE MODE ACTIVE</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs font-medium shadow-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="font-mono">INTEGRITY VERIFIED</span>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
