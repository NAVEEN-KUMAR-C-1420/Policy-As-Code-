import React from 'react';
import { Shield, Cpu, Lock } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 py-8 px-6 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20 text-blue-400">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-200 font-semibold">AIVAR Financial Multi-Agent Governance</span>
            <p className="text-xs text-slate-500">Enterprise AI Compliance & Policy Enforcement Platform</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-emerald-400" />
            <span>Presidio PII Shield Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span>Deterministic Risk Engine</span>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          © 2026 AIVAR Innovations. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
