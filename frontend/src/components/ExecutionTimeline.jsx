import React, { useState } from 'react';
import { CheckCircle2, Clock, AlertCircle, ChevronDown, ChevronRight, Shield, ShieldAlert, Cpu, FileText, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ExecutionTimeline({ timeline = [], isExecuting = false }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  const defaultStages = [
    { stage: "Prompt Ingestion", status: "Completed", details: "User prompt received and tokenized." },
    { stage: "Presidio PII Detection", status: "Completed", details: "Scanned for sensitive entities (Names, Emails, Cards, Addresses)." },
    { stage: "Prompt Injection Shield", status: "Completed", details: "Passed zero injection patterns check." },
    { stage: "Code Integrity Validation", status: "Completed", details: "Runtime SHA256 matches active version." },
    { stage: "Policy Validation", status: "Completed", details: "Verified against policy ruleset." },
    { stage: "Governance Version Check", "status": "Completed", details: "Active version verified." },
    { stage: "Data Collector Agent", status: "Completed", details: "Fetched transactions & market news." },
    { stage: "Risk Analyzer Agent", status: "Completed", details: "Calculated outflow/balance risk ratio." },
    { stage: "Report Writer Agent", status: "Completed", details: "Generated executive markdown report." },
    { stage: "Audit Logging", status: "Completed", details: "Wrote decision entry to immutable log." },
    { stage: "Supabase Storage", status: "Completed", details: "Persisted report record." },
    { stage: "Response Delivery", status: "Completed", details: "Payload rendered to client." }
  ];

  const stagesToDisplay = timeline.length > 0 ? timeline : defaultStages;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Completed':
        return <span className="flex items-center gap-1 text-emerald-400 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20"><CheckCircle2 className="w-3.5 h-3.5" /> Completed</span>;
      case 'Running':
        return <span className="flex items-center gap-1 text-blue-400 text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 animate-pulse"><Clock className="w-3.5 h-3.5 animate-spin" /> Running</span>;
      case 'Failed':
      case 'Blocked':
        return <span className="flex items-center gap-1 text-red-400 text-xs font-semibold px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20"><AlertCircle className="w-3.5 h-3.5" /> Failed</span>;
      case 'Warning':
        return <span className="flex items-center gap-1 text-amber-400 text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20"><AlertCircle className="w-3.5 h-3.5" /> Warning</span>;
      default:
        return <span className="flex items-center gap-1 text-slate-500 text-xs font-medium px-2 py-0.5 rounded bg-slate-800"><Clock className="w-3.5 h-3.5" /> Pending</span>;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-wide">Execution Timeline & Stage Pipeline</h3>
            <p className="text-xs text-slate-400">Step-by-step audit visualization of prompt processing</p>
          </div>
        </div>
        {isExecuting && (
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 animate-pulse">
            Processing Live Pipeline...
          </span>
        )}
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-blue-500 before:via-indigo-500 before:to-emerald-500">
        {stagesToDisplay.map((item, idx) => {
          const isExpanded = expandedIndex === idx;
          const isCompleted = item.status === 'Completed';

          return (
            <div key={idx} className="relative group">
              {/* Point Node Indicator */}
              <div className={`absolute -left-9 top-1.5 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                isCompleted 
                  ? 'bg-emerald-950 border-emerald-500 text-emerald-400 shadow-md shadow-emerald-500/20' 
                  : item.status === 'Running'
                  ? 'bg-blue-950 border-blue-500 text-blue-400 animate-pulse'
                  : item.status === 'Failed' || item.status === 'Blocked'
                  ? 'bg-red-950 border-red-500 text-red-400'
                  : 'bg-slate-900 border-slate-700 text-slate-500'
              }`}>
                {isCompleted ? <CheckCircle2 className="w-3.5 h-3.5" /> : <div className="w-1.5 h-1.5 rounded-full bg-current" />}
              </div>

              {/* Stage Card */}
              <div 
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className={`glass-card rounded-xl p-3.5 border transition-all cursor-pointer ${
                  isExpanded ? 'border-blue-500/40 bg-slate-800/60 shadow-lg' : 'border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/40'
                }`}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-500 font-bold">STAGE {idx + 1}</span>
                    <span className="text-sm font-semibold text-slate-200">{item.stage}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {getStatusBadge(item.status)}
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
                  </div>
                </div>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-300 font-mono"
                    >
                      <p className="text-slate-300 leading-relaxed font-sans">{item.details}</p>
                      <div className="mt-2 flex items-center gap-4 text-[11px] text-slate-400">
                        <span>Timestamp: {new Date().toLocaleTimeString()}</span>
                        <span>Stage ID: stage_{idx + 1}</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
