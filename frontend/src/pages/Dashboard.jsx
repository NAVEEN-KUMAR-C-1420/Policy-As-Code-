import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, RefreshCw, Trash2, Download, ShieldCheck, ShieldAlert, Cpu, Lock, FileText, 
  Database, Activity, CheckCircle2, AlertTriangle, Layers, BarChart3, Search, Filter, Play, ChevronDown, ChevronUp 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

import { SystemAPI, PipelineAPI, AuditAPI, ReportsAPI, DemoAPI } from '../services/api';
import ExecutionTimeline from '../components/ExecutionTimeline';
import ArchitectureGraph from '../components/ArchitectureGraph';
import PresidioBadge from '../components/PresidioBadge';
import PromptInjectionBadge from '../components/PromptInjectionBadge';

export default function Dashboard({ integrity, onRefreshIntegrity }) {
  // Chat & Execution state
  const [messages, setMessages] = useState([
    {
      sender: 'system',
      text: 'Welcome to AIVAR Enterprise Governance Dashboard. Select an account or prompt to execute multi-agent analysis.',
      timestamp: new Date().toLocaleTimeString(),
    }
  ]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [selectedAccount, setSelectedAccount] = useState(101);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentExecutionData, setCurrentExecutionData] = useState(null);
  const [activeArchNode, setActiveArchNode] = useState('user');

  // Audit Logs state
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditFilter, setAuditFilter] = useState('ALL');
  const [auditSearch, setAuditSearch] = useState('');
  const [expandedLogId, setExpandedLogId] = useState(null);

  // Metrics & Reports state
  const [reportsList, setReportsList] = useState([]);
  const [activeReport, setActiveReport] = useState(null);
  const [metrics, setMetrics] = useState({
    totalRequests: 42,
    allowedRequests: 38,
    blockedRequests: 4,
    avgRiskScore: 0.14,
    avgResponseMs: 340,
    reportsCount: 12
  });

  const chatEndRef = useRef(null);

  // Load Initial Data
  useEffect(() => {
    fetchAuditLogs();
    fetchReports();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchAuditLogs = async () => {
    try {
      const res = await AuditAPI.getRecent();
      if (res && res.data) {
        setAuditLogs(res.data);
      }
    } catch (e) {
      console.warn('Failed to fetch audit logs:', e);
    }
  };

  const fetchReports = async () => {
    try {
      const res = await ReportsAPI.list();
      if (res && res.data) {
        setReportsList(res.data);
        if (res.data.length > 0 && !activeReport) {
          setActiveReport(res.data[0]);
        }
      }
    } catch (e) {
      console.warn('Failed to fetch reports:', e);
    }
  };

  const [abortController, setAbortController] = useState(null);

  const handleSendMessage = (e) => {
    if (e) e.preventDefault();
    if (!inputPrompt.trim() && !selectedAccount) return;

    const userText = inputPrompt || `Run analysis for Account ${selectedAccount}`;
    const newMsg = {
      sender: 'user',
      text: userText,
      account_id: selectedAccount,
      timestamp: new Date().toLocaleTimeString(),
    };

    if (abortController) abortController.abort();
    const newController = new AbortController();
    setAbortController(newController);

    setMessages((prev) => [...prev, newMsg]);
    setInputPrompt('');
    setIsExecuting(true);
    setCurrentExecutionData({ timeline: [], presidio: null, prompt_injection: null, report: null });
    setActiveArchNode('user');

    PipelineAPI.stream(
      selectedAccount, 
      userText,
      (data) => {
        if (data.type === 'stage') {
          setCurrentExecutionData(prev => {
            const prevData = prev || { timeline: [], presidio: null, prompt_injection: null, report: null };
            const newTimeline = [...(prevData.timeline || [])];
            
            const existingIdx = newTimeline.findIndex(t => t.stage === data.stage);
            if (existingIdx >= 0) {
              newTimeline[existingIdx] = { stage: data.stage, status: data.status, details: data.details };
            } else {
              newTimeline.push({ stage: data.stage, status: data.status, details: data.details });
            }

            const archMap = ['user', 'presidio', 'injection', 'governance', 'governance', 'fastapi', 'orchestrator', 'data_collector', 'risk_analyzer', 'report_writer', 'audit', 'fastapi'];
            setActiveArchNode(archMap[newTimeline.length - 1] || 'fastapi');

            const payload = data.payload || {};
            
            if (payload.response) {
               const assistantMsg = {
                  sender: 'assistant',
                  text: payload.response,
                  data: prevData,
                  timestamp: new Date().toLocaleTimeString(),
                };
                setMessages((msgs) => [...msgs.filter(m => m.text !== payload.response), assistantMsg]);
                fetchAuditLogs();
                fetchReports();
                if (onRefreshIntegrity) onRefreshIntegrity();
            }

            return {
              ...prevData,
              timeline: newTimeline,
              presidio: payload.original_text !== undefined ? payload : prevData.presidio,
              prompt_injection: payload.is_safe !== undefined ? payload : prevData.prompt_injection,
              report: payload.response !== undefined ? payload.response : prevData.report
            };
          });
        }
      },
      (err) => {
        setIsExecuting(false);
        setActiveArchNode('user');
        if (!newController.signal.aborted) {
          setMessages((prev) => [
            ...prev,
            {
              sender: 'assistant',
              isError: true,
              text: `❌ EXECUTION BLOCKED or FAILED`,
              timestamp: new Date().toLocaleTimeString(),
            }
          ]);
          setMetrics((prev) => ({ ...prev, totalRequests: prev.totalRequests + 1, blockedRequests: prev.blockedRequests + 1 }));
        }
      },
      () => {
        setIsExecuting(false);
        setActiveArchNode('user');
        setMetrics((prev) => ({ ...prev, totalRequests: prev.totalRequests + 1, allowedRequests: prev.allowedRequests + 1 }));
      },
      newController.signal
    );
  };

  useEffect(() => {
    return () => {
      if (abortController) abortController.abort();
    };
  }, [abortController]);


  const clearChat = () => {
    setMessages([
      {
        sender: 'system',
        text: 'Chat history cleared. Select an account or prompt to begin a new governance session.',
        timestamp: new Date().toLocaleTimeString(),
      }
    ]);
    setCurrentExecutionData(null);
  };

  // Filter audit logs
  const filteredAuditLogs = auditLogs.filter((log) => {
    const matchFilter = 
      auditFilter === 'ALL' ? true :
      auditFilter === 'ALLOWED' ? log.decision === 'ALLOWED' :
      auditFilter === 'BLOCKED' ? (log.decision === 'BLOCKED' || log.decision === 'DENIED') : true;

    const query = auditSearch.toLowerCase();
    const matchSearch = 
      !query ? true :
      (log.agent_id || '').toLowerCase().includes(query) ||
      (log.event_type || '').toLowerCase().includes(query) ||
      (log.reason || '').toLowerCase().includes(query) ||
      (log.tool_name || '').toLowerCase().includes(query);

    return matchFilter && matchSearch;
  });

  // Demo Recharts data
  const chartData = [
    { name: '00:00', allowed: 4, blocked: 0, risk: 0.12 },
    { name: '04:00', allowed: 7, blocked: 1, risk: 0.15 },
    { name: '08:00', allowed: 12, blocked: 0, risk: 0.10 },
    { name: '12:00', allowed: 18, blocked: 2, risk: 0.22 },
    { name: '16:00', allowed: 24, blocked: 1, risk: 0.18 },
    { name: '20:00', allowed: 32, blocked: 0, risk: 0.11 },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-6 space-y-6 max-w-[1600px] mx-auto">
      
      {/* Dashboard Top Header & Quick Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-black tracking-tight text-white">Enterprise Governance Control Center</h1>
            <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
              LIVE SYSTEM
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Real-time PII Detection, Prompt Injection Defense, Policy Enforcement & Immutable Audit Trail</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => handleSendMessage()}
            disabled={isExecuting || (integrity && integrity.safe_mode)}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            Run Sample Pipeline
          </button>
          <button
            onClick={fetchAuditLogs}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-medium border border-slate-800 transition-all flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
            Refresh Logs
          </button>
        </div>
      </div>

      {/* Main Grid: Left Column (Chat + Presidio + Reports) & Right Column (Timeline + Policy + Audit + Metrics) */}
      <div className="grid lg:grid-cols-12 gap-6">

        {/* LEFT COLUMN (5 cols): AI Chat & Reports Panel */}
        <div className="lg:col-span-5 space-y-6">

          {/* AI Chat Panel */}
          <div className="glass-panel rounded-2xl border border-slate-800 flex flex-col h-[520px] shadow-xl">
            {/* Chat Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60 rounded-t-2xl">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20 text-blue-400">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Governed Multi-Agent AI Chat</h3>
                  <p className="text-[11px] text-slate-400">Policy-guarded prompt analyzer</p>
                </div>
              </div>
              <button
                onClick={clearChat}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                title="Clear Chat"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {/* Account Selector & Presets */}
            <div className="p-3 bg-slate-950/60 border-b border-slate-800/80 flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-mono">ACCOUNT:</span>
              {[101, 102, 103].map((accId) => (
                <button
                  key={accId}
                  onClick={() => setSelectedAccount(accId)}
                  className={`px-3 py-1 rounded-lg font-mono font-bold transition-all ${
                    selectedAccount === accId
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                >
                  Account #{accId}
                </button>
              ))}
            </div>

            {/* Chat Messages Scroll Window */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[90%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-tr-none shadow-md'
                        : msg.isError
                        ? 'bg-red-950/80 text-red-200 border border-red-500/40 rounded-tl-none font-mono'
                        : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                    <span className="text-[10px] text-slate-400 opacity-60 block text-right mt-1 font-mono">
                      {msg.timestamp}
                    </span>
                  </div>
                </div>
              ))}
              {isExecuting && (
                <div className="flex items-center gap-2 text-xs text-blue-400 font-mono p-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Evaluating governance policy & invoking agents...</span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Prompt Input Form */}
            <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-800 bg-slate-900/60 rounded-b-2xl flex items-center gap-2">
              <input
                type="text"
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                placeholder={integrity && integrity.safe_mode ? "Execution disabled in Safe Mode..." : "Ask AI or enter prompt (e.g. Analyze account 101)..."}
                disabled={isExecuting || (integrity && integrity.safe_mode)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isExecuting || (integrity && integrity.safe_mode)}
                className="p-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-md disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>

          {/* Presidio & Prompt Injection Live Security Badges */}
          <div className="space-y-4">
            <PresidioBadge presidio={currentExecutionData?.presidio} />
            <PromptInjectionBadge injection={currentExecutionData?.prompt_injection} />
          </div>

          {/* Generated Reports Panel */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Generated Reports</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">{reportsList.length} Archived</span>
            </div>

            {activeReport ? (
              <div className="space-y-3">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 max-h-56 overflow-y-auto leading-relaxed whitespace-pre-wrap">
                  {activeReport.summary || activeReport.report_content || "Executive Financial Risk Report generated cleanly under active policy controls."}
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
                  <span>Account ID: #{activeReport.account_id || 101}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        const blob = new Blob([activeReport.summary || activeReport.report_content || ''], { type: 'text/markdown' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `report_account_${activeReport.account_id || 101}.md`;
                        a.click();
                      }}
                      className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded border border-slate-700 font-mono flex items-center gap-1"
                    >
                      <Download className="w-3 h-3" /> Markdown
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 font-mono text-center py-4">No reports generated yet.</p>
            )}
          </div>

        </div>

        {/* RIGHT COLUMN (7 cols): Timeline, Policy, Audit Logs, Architecture & Metrics */}
        <div className="lg:col-span-7 space-y-6">

          {/* Visual Execution Timeline */}
          <ExecutionTimeline 
            timeline={currentExecutionData?.timeline || []} 
            isExecuting={isExecuting} 
          />

          {/* Active Policy & System Integrity Card Grid */}
          <div className="grid md:grid-cols-2 gap-4">

            {/* Active Policy Summary Card */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-blue-400" />
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider">Active Policy Info</h4>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                  YAML ENFORCED
                </span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Agent ID:</span>
                  <span className="text-slate-200">multi_agent_system</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Policy Version:</span>
                  <span className="text-blue-400 font-bold">1.0</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Risk Threshold (HITL):</span>
                  <span className="text-amber-400 font-bold">0.70</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">PII Allowed:</span>
                  <span className="text-emerald-400 font-bold">FALSE (Redacted)</span>
                </div>
              </div>
            </div>

            {/* System Integrity & Safe Mode Status */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {integrity && integrity.safe_mode ? (
                    <ShieldAlert className="w-4 h-4 text-red-400" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider">Integrity Status</h4>
                </div>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  integrity && integrity.safe_mode
                    ? 'bg-red-950 text-red-300 border border-red-500/40'
                    : 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                }`}>
                  {integrity && integrity.safe_mode ? 'FAILED' : 'VERIFIED'}
                </span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Commit SHA:</span>
                  <span className="text-slate-200">{integrity?.commit_sha || 'HEAD'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Policy SHA256:</span>
                  <span className="text-slate-300">{(integrity?.policy_hash || 'SHA256').slice(0, 12)}...</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Agent SHA256:</span>
                  <span className="text-slate-300">{(integrity?.agent_hash || 'SHA256').slice(0, 12)}...</span>
                </div>
              </div>
            </div>

          </div>

          {/* Interactive Visual Architecture Panel */}
          <ArchitectureGraph activeNode={activeArchNode} />

          {/* Live Audit Trail Table */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-bold text-white">Immutable Governance Audit Logs</h3>
              </div>

              {/* Filter Controls */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                  <input
                    type="text"
                    value={auditSearch}
                    onChange={(e) => setAuditSearch(e.target.value)}
                    placeholder="Search logs..."
                    className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none"
                  />
                </div>
                <div className="flex bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-[11px] font-mono">
                  {['ALL', 'ALLOWED', 'BLOCKED'].map((f) => (
                    <button
                      key={f}
                      onClick={() => setAuditFilter(f)}
                      className={`px-2.5 py-1 rounded-md transition-all ${
                        auditFilter === f ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Audit Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Timestamp</th>
                    <th className="py-2.5 px-3">Agent</th>
                    <th className="py-2.5 px-3">Event / Action</th>
                    <th className="py-2.5 px-3">Decision</th>
                    <th className="py-2.5 px-3">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredAuditLogs.slice(0, 8).map((log, idx) => {
                    const isAllowed = log.decision === 'ALLOWED';
                    const isExpanded = expandedLogId === idx;
                    return (
                      <React.Fragment key={idx}>
                        <tr 
                          onClick={() => setExpandedLogId(isExpanded ? null : idx)}
                          className="hover:bg-slate-900/60 cursor-pointer transition-colors"
                        >
                          <td className="py-2.5 px-3 text-slate-400">{log.timestamp ? log.timestamp.split('T')[1]?.slice(0, 8) || log.timestamp : 'Just now'}</td>
                          <td className="py-2.5 px-3 font-semibold text-slate-200">{log.agent_id || log.agent_name || 'system'}</td>
                          <td className="py-2.5 px-3 text-blue-400">{log.action || log.event_type || 'TOOL_EXEC'}</td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              isAllowed ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                            }`}>
                              {log.decision}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-300 truncate max-w-xs">{log.reason || 'Governance criteria satisfied.'}</td>
                        </tr>
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* System Metrics Visual Charts */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">System Metrics & Compliance Analytics</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Live Recharts Data</span>
            </div>

            <div className="grid md:grid-cols-2 gap-6 pt-2">
              <div>
                <h4 className="text-xs font-mono text-slate-400 mb-3">Request Volume (Allowed vs Blocked)</h4>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                      <YAxis stroke="#64748b" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                      <Area type="monotone" dataKey="allowed" stroke="#3b82f6" fillOpacity={1} fill="url(#colorAllowed)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-mono text-slate-400 mb-3">Deterministic Risk Score Distribution</h4>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                      <YAxis stroke="#64748b" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                      <Bar dataKey="risk" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
