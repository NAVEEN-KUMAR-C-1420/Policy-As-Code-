import React from 'react';
import { ShieldAlert, AlertTriangle, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function SafeModeBanner({ integrity, onResolve }) {
  if (!integrity || !integrity.safe_mode) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: 'auto', opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        className="bg-red-950/90 border-b-2 border-red-500/80 px-6 py-4 shadow-2xl backdrop-blur-md relative z-50"
      >
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-red-900/60 rounded-xl border border-red-500/40 text-red-400 animate-pulse">
              <ShieldAlert className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h3 className="font-extrabold text-red-100 text-lg tracking-wide uppercase">
                  SYSTEM INTEGRITY FAILED — SAFE MODE ACTIVE
                </h3>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-red-900/80 text-red-200 border border-red-500/40">
                  EXECUTION DISABLED
                </span>
              </div>
              <p className="text-red-300 text-sm mt-1 leading-relaxed">
                <strong className="text-white">Reason:</strong> {integrity.reason || 'SHA256 Hash Mismatch detected in governed codebase.'}
              </p>
              <div className="flex flex-wrap gap-4 mt-2 text-xs font-mono text-red-200/90">
                <span>Commit: <strong className="text-white">{integrity.commit_sha || 'HEAD'}</strong></span>
                <span>Version: <strong className="text-white">v{integrity.deployment_version || 1}</strong></span>
                <span>Expected: <strong className="text-emerald-400 font-mono">{(integrity.expected_policy_hash || integrity.expected_hash || 'SHA256').slice(0, 10)}...</strong></span>
                <span>Current: <strong className="text-rose-400 font-mono">{(integrity.policy_hash || 'SHA256').slice(0, 10)}...</strong></span>
              </div>
            </div>
          </div>
          {onResolve && (
            <button
              onClick={onResolve}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-semibold text-xs transition-all shadow-lg flex items-center gap-2 shrink-0 border border-red-400/50"
            >
              <RefreshCw className="w-4 h-4 animate-spin-slow" />
              Re-check Integrity / Resolve
            </button>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
