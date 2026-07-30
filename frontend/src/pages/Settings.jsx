import React, { useState, useEffect } from 'react';
import { Settings, ShieldAlert, Cpu, AlertTriangle, CheckCircle2, Lock, Sliders, RefreshCw } from 'lucide-react';
import { DemoAPI } from '../services/api';

export default function SettingsPage({ integrity, onRefreshIntegrity }) {
  const [demoTools, setDemoTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusMsg, setStatusMsg] = useState(null);
  const [simulatedSafeMode, setSimulatedSafeMode] = useState(false);

  useEffect(() => {
    fetchDemoTools();
  }, []);

  const fetchDemoTools = async () => {
    setLoading(true);
    try {
      const res = await DemoAPI.getTools();
      setDemoTools(res.data || []);
    } catch (e) {
      console.warn('Failed to fetch demo tools:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTool = async (toolKey, currentlyAllowed) => {
    const newTargetState = !currentlyAllowed;
    setStatusMsg(`Updating policy for '${toolKey}' to ${newTargetState ? 'ENABLED' : 'DISABLED'}...`);
    try {
      const res = await DemoAPI.toggleTool(toolKey, newTargetState);
      setStatusMsg(`Policy reloaded! Audit record created, version bumped, and SHA256 integrity verified.`);
      fetchDemoTools();
      onRefreshIntegrity && onRefreshIntegrity();
    } catch (e) {
      setStatusMsg(`Failed to update tool state: ${e.message}`);
    }
  };

  const handleToggleSafeMode = async (enabled) => {
    setSimulatedSafeMode(enabled);
    try {
      await DemoAPI.toggleSafeMode(enabled);
      setStatusMsg(`Safe Mode simulation set to ${enabled ? 'ACTIVE' : 'INACTIVE'}.`);
      onRefreshIntegrity && onRefreshIntegrity();
    } catch (e) {
      setStatusMsg(`Safe mode toggle error: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-600/10 border border-blue-500/20 text-blue-400 rounded-xl">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white">Developer Settings & Policy Tool Demonstration</h1>
            <p className="text-xs text-slate-400">Live tool permission toggles, dynamic policy reloading, and Safe Mode simulation</p>
          </div>
        </div>
        <button
          onClick={fetchDemoTools}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold border border-slate-800 transition-all flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4 text-slate-400" />
          Reload Tools
        </button>
      </div>

      {statusMsg && (
        <div className="p-4 rounded-xl bg-blue-950/80 border border-blue-500/40 text-blue-300 text-xs font-mono">
          {statusMsg}
        </div>
      )}

      {/* Dedicated Tool Demonstration Section */}
      <div className="glass-panel-glow p-6 rounded-2xl border border-blue-500/30 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <span className="text-xs font-mono font-bold text-blue-400 uppercase tracking-widest block">POLICY DEMONSTRATION SUITE</span>
            <h3 className="text-lg font-bold text-white mt-1">Live Tool Governance Controls</h3>
          </div>
          <span className="text-xs text-slate-400 font-mono bg-slate-900 px-3 py-1 rounded border border-slate-800">
            No Manual YAML Edit Needed
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Toggle blocked/dangerous tools below. When enabled, the backend updates the agent policy, reloads governance rules, creates an audit record, increments a new governance version, and rechecks SHA256 integrity automatically.
        </p>

        <div className="grid md:grid-cols-2 gap-6 pt-2">
          {demoTools.map((tool) => {
            const isAllowed = tool.allowed;
            return (
              <div key={tool.key} className="glass-card p-5 rounded-xl border border-slate-800 flex flex-col justify-between gap-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-slate-400 uppercase font-semibold">{tool.agent_id}</span>
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                      isAllowed ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'
                    }`}>
                      {isAllowed ? 'ALLOWED IN POLICY' : 'BLOCKED BY POLICY'}
                    </span>
                  </div>
                  <h4 className="font-extrabold text-base text-white">{tool.name}</h4>
                  <p className="text-xs text-slate-400 mt-1 font-mono">{tool.description}</p>
                  <div className="mt-3 text-[11px] font-mono text-slate-500">
                    <span>Scope: <strong className="text-slate-300">{tool.scope}</strong></span>
                  </div>
                </div>

                <button
                  onClick={() => handleToggleTool(tool.key, isAllowed)}
                  className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                    isAllowed
                      ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/20'
                      : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                  }`}
                >
                  <Sliders className="w-4 h-4" />
                  {isAllowed ? 'Disable / Block Tool' : 'Enable / Allow Tool'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Safe Mode Simulation Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-red-600/10 border border-red-500/20 text-red-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Safe Mode & Code Tampering Simulator</h3>
              <p className="text-xs text-slate-400">Simulate code integrity hash mismatch to test Safe Mode lockdown</p>
            </div>
          </div>

          <button
            onClick={() => handleToggleSafeMode(!simulatedSafeMode)}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              simulatedSafeMode
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                : 'bg-red-600 hover:bg-red-500 text-white'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            {simulatedSafeMode ? 'Deactivate Safe Mode Simulation' : 'Simulate Safe Mode Lockdown'}
          </button>
        </div>
      </div>

    </div>
  );
}
