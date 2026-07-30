import React from 'react';
import { Cpu, ShieldCheck, Database, Server, User, Terminal, Layers, FileCode2, CheckCircle2, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ArchitectureGraph({ activeNode = 'user' }) {
  const nodes = [
    { id: "user", label: "User / Evaluator", icon: User, type: "client" },
    { id: "react", label: "React Frontend", icon: Terminal, type: "frontend" },
    { id: "fastapi", label: "FastAPI REST Layer", icon: Server, type: "api" },
    { id: "presidio", label: "Presidio PII Shield", icon: Lock, type: "security" },
    { id: "injection", "label": "Prompt Injection Guard", icon: ShieldCheck, type: "security" },
    { id: "integrity", label: "Code Integrity SHA256", icon: FileCode2, type: "middleware" },
    { id: "governance", label: "Governance Middleware", icon: ShieldCheck, type: "middleware" },
    { id: "policy", label: "Policy Engine", icon: Layers, type: "governance" },
    { id: "version", label: "Version Control", icon: CheckCircle2, type: "governance" },
    { id: "orchestrator", label: "Agent Router", icon: Cpu, type: "core" },
    { id: "data_collector", label: "Data Collector", icon: Cpu, type: "agent" },
    { id: "risk_analyzer", label: "Risk Analyzer", icon: Cpu, type: "agent" },
    { id: "report_writer", label: "Report Writer", icon: Cpu, type: "agent" },
    { id: "audit", label: "Audit Logger", icon: FileCode2, type: "logging" },
    { id: "supabase", label: "Supabase / SQLite", icon: Database, type: "database" }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-wide">Visual System Architecture & Data Flow</h3>
            <p className="text-xs text-slate-400">Live active node highlighting across governance & agent pipeline</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Interactive Topology</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {nodes.map((node, index) => {
          const Icon = node.icon;
          const isActive = activeNode === node.id || activeNode === 'all';

          return (
            <motion.div
              key={node.id}
              whileHover={{ scale: 1.03 }}
              className={`p-3 rounded-xl border transition-all flex flex-col items-center justify-center text-center relative ${
                isActive
                  ? 'bg-blue-900/30 border-blue-500/80 shadow-lg shadow-blue-500/20 text-white animate-pulse-glow'
                  : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className={`p-2.5 rounded-lg mb-2 ${
                isActive ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold leading-snug">{node.label}</span>
              <span className="text-[10px] font-mono text-slate-500 uppercase mt-1">{node.type}</span>
              <span className="absolute top-1.5 right-2 text-[9px] font-mono text-slate-600">0{index + 1}</span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
