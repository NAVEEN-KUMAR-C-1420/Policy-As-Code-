import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, RotateCcw, GitCommit, CheckCircle2, RefreshCw } from 'lucide-react';
import { GlobalVersionsAPI } from '../services/api';

export default function Versions({ onRefreshIntegrity }) {
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rollbackMsg, setRollbackMsg] = useState(null);

  useEffect(() => {
    fetchVersionHistory();
  }, []);

  const fetchVersionHistory = async () => {
    setLoading(true);
    try {
      const [verList, currVer] = await Promise.all([
        GlobalVersionsAPI.list(),
        GlobalVersionsAPI.getCurrent()
      ]);
      setVersions(verList.data || []);
      setCurrentVersion(currVer.data || null);
    } catch (e) {
      console.warn('Failed to load version history:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (versionNum) => {
    try {
      setRollbackMsg(`Rolling back to Version v${versionNum}...`);
      await GlobalVersionsAPI.rollback(versionNum);
      setRollbackMsg(`Successfully rolled back to Version v${versionNum}.`);
      fetchVersionHistory();
      onRefreshIntegrity && onRefreshIntegrity();
    } catch (e) {
      setRollbackMsg(`Rollback failed: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-600/10 border border-blue-500/20 text-blue-400 rounded-xl">
            <History className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white">Governance Version Management</h1>
            <p className="text-xs text-slate-400">Track and rollback system governance states, policy YAMLs, and agent configs</p>
          </div>
        </div>
        <button
          onClick={fetchVersionHistory}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold border border-slate-800 transition-all flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4 text-slate-400" />
          Refresh
        </button>
      </div>

      {rollbackMsg && (
        <div className="p-4 rounded-xl bg-blue-950/80 border border-blue-500/40 text-blue-300 text-xs font-mono">
          {rollbackMsg}
        </div>
      )}

      {/* Current Version Card */}
      {currentVersion && (
        <div className="glass-panel-glow p-6 rounded-2xl border border-blue-500/30 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-blue-400 uppercase tracking-widest">ACTIVE GOVERNANCE STATE</span>
            <span className="px-3 py-1 rounded-full text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" /> ACTIVE
            </span>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <span className="text-xs text-slate-400 block font-mono">VERSION NUMBER</span>
              <span className="text-2xl font-black text-white font-mono">v{currentVersion.version_number}</span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block font-mono">GIT COMMIT SHA</span>
              <span className="text-sm font-bold text-slate-200 font-mono flex items-center gap-1.5 mt-1">
                <GitCommit className="w-4 h-4 text-blue-400" /> {currentVersion.git_commit_sha || 'local_head'}
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block font-mono">POLICY SHA256</span>
              <span className="text-xs font-bold text-slate-300 font-mono block mt-1">
                {(currentVersion.policy_hash || 'SHA256').slice(0, 16)}...
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-400 block font-mono">GOVERNANCE HASH</span>
              <span className="text-xs font-bold text-slate-300 font-mono block mt-1">
                {(currentVersion.governance_hash || 'SHA256').slice(0, 16)}...
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Version History Table */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white">Governance State History</h3>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {versions.map((ver) => {
              const isActive = ver.is_active || (currentVersion && currentVersion.version_number === ver.version_number);
              const changedTools = ver.metadata?.changed_tools || [];
              const changedPolicies = ver.metadata?.changed_policies || [];
              
              const truncateHash = (hash) => hash ? `${hash.slice(0, 4)}...${hash.slice(-4)}` : 'N/A';
              const handleCopy = (text) => navigator.clipboard.writeText(text);

              return (
                <div key={ver.version_number} className={`relative p-5 rounded-2xl border transition-all ${isActive ? 'bg-blue-900/10 border-blue-500/30' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`}>
                  {isActive && (
                    <div className="absolute -top-3 -right-3 px-3 py-1 bg-blue-600 text-white text-[10px] font-bold rounded-full border-4 border-slate-950 shadow-lg flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> ACTIVE
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-xl font-black text-white">v{ver.version_number}</h4>
                    <div className="text-right">
                      <span className="text-[10px] text-slate-500 uppercase block mb-1">Commit</span>
                      <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">{ver.git_commit_sha || 'head'}</span>
                    </div>
                  </div>

                  <p className="text-sm text-slate-300 mb-4 h-10 overflow-hidden text-ellipsis line-clamp-2">
                    {ver.change_summary || 'System startup detected changes'}
                  </p>

                  <div className="space-y-2 mb-4 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between group">
                      <span className="text-[10px] text-slate-500 uppercase">Policy Hash</span>
                      <div className="flex items-center gap-2">
                         <span className="text-xs font-mono text-slate-300" title={ver.policy_hash}>
                           {truncateHash(ver.policy_hash)}
                         </span>
                         <button onClick={() => handleCopy(ver.policy_hash)} className="text-slate-500 hover:text-white transition-colors" title="Copy Full Hash">
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                         </button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between group">
                      <span className="text-[10px] text-slate-500 uppercase">Gov Hash</span>
                      <div className="flex items-center gap-2">
                         <span className="text-xs font-mono text-slate-300" title={ver.governance_hash}>
                           {truncateHash(ver.governance_hash)}
                         </span>
                         <button onClick={() => handleCopy(ver.governance_hash)} className="text-slate-500 hover:text-white transition-colors" title="Copy Full Hash">
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                         </button>
                      </div>
                    </div>
                  </div>

                  <div className="mb-4 min-h-[60px]">
                    <span className="text-[10px] text-slate-500 uppercase block mb-2">Diff Summary</span>
                    {(changedTools.length > 0 || changedPolicies.length > 0) ? (
                      <div className="space-y-1.5">
                        {changedTools.map((t, idx) => (
                          <div key={idx} className="text-[10px] text-slate-300 flex items-center gap-2">
                            <span className={`w-1.5 h-1.5 rounded-full ${t.status === 'enabled' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                            <span className="truncate">{t.name}</span>
                          </div>
                        ))}
                        {changedPolicies.map((p, idx) => (
                          <div key={idx} className="text-[10px] text-slate-400 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                            <span className="truncate">{p}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-[10px] text-slate-600 italic">No significant diffs recorded</span>
                    )}
                  </div>

                  {!isActive && (
                    <button
                      onClick={() => handleRollback(ver.version_number)}
                      className="w-full py-2.5 bg-slate-950 hover:bg-slate-900 text-blue-400 hover:text-blue-300 rounded-xl border border-slate-800 font-mono text-xs transition-all flex items-center justify-center gap-2"
                    >
                      <RotateCcw className="w-4 h-4" /> Rollback to v{ver.version_number}
                    </button>
                  )}
                  {isActive && (
                     <div className="w-full py-2.5 bg-blue-900/10 text-blue-400/50 rounded-xl border border-blue-500/10 font-mono text-xs flex items-center justify-center gap-2 cursor-not-allowed">
                      Current Active State
                    </div>
                  )}
                </div>
              );
            })}
          </div>
      </div>

    </div>
  );
}
