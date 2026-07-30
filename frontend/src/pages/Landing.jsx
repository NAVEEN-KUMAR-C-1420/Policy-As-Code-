import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Cpu, ArrowRight, Layers, Lock, History, Database, FileText, CheckCircle2, Activity, Server, Zap, User } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">

      {/* Hero Section */}
      <header className="relative pt-24 pb-20 px-6 overflow-hidden border-b border-slate-800/80">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/30 via-slate-950 to-slate-950 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto text-center relative z-10">
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono font-semibold mb-8 shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            ENTERPRISE MULTI-AGENT AI GOVERNANCE SYSTEM
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-5xl mx-auto leading-tight"
          >
            Deterministic Compliance & Safety for <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">Financial AI Agents</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-6 text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto font-normal leading-relaxed"
          >
            AIVAR delivers real-time PII redaction, prompt injection defense, SHA256 code integrity, policy enforcement, and immutable audit trails for autonomous financial workflows.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-4"
          >
            <Link
              to="/dashboard"
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-xl shadow-blue-500/20 transition-all transform hover:-translate-y-0.5 flex items-center gap-3 text-sm tracking-wide"
            >
              <span>Launch Enterprise Dashboard</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#architecture"
              className="px-8 py-4 glass-card hover:bg-slate-800/60 text-slate-200 font-semibold rounded-xl border border-slate-700/60 transition-all text-sm"
            >
              Explore Architecture
            </a>
          </motion.div>

          {/* Quick Metrics Banner */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto glass-panel p-6 rounded-2xl border border-slate-800"
          >
            <div>
              <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">100%</span>
              <p className="text-xs text-slate-400 mt-1">Deterministic Policy Check</p>
            </div>
            <div>
              <span className="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-mono">0ms</span>
              <p className="text-xs text-slate-400 mt-1">PII Masking Latency</p>
            </div>
            <div>
              <span className="text-2xl sm:text-3xl font-extrabold text-blue-400 font-mono">SHA256</span>
              <p className="text-xs text-slate-400 mt-1">Code Integrity Hash</p>
            </div>
            <div>
              <span className="text-2xl sm:text-3xl font-extrabold text-cyan-400 font-mono">1-Click</span>
              <p className="text-xs text-slate-400 mt-1">Governance Rollback</p>
            </div>
          </motion.div>
        </div>
      </header>

      {/* Governance Highlights */}
      <section className="py-20 px-6 max-w-7xl mx-auto w-full">
        <div className="text-center mb-16">
          <span className="text-xs font-mono text-blue-400 font-semibold uppercase tracking-widest">Enterprise Shield</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">Core Governance Pillars</h2>
          <p className="text-slate-400 text-sm mt-2 max-w-2xl mx-auto">Multi-layered security & verification enforcing zero-trust execution for AI agents.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-blue-500/40 transition-all group">
            <div className="p-3 bg-blue-600/10 border border-blue-500/20 text-blue-400 rounded-xl w-fit mb-4 group-hover:scale-110 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Presidio PII Redaction</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Automatically detects and masks names, email addresses, phone numbers, credit card data, and IP addresses before agent execution.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-indigo-500/40 transition-all group">
            <div className="p-3 bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 rounded-xl w-fit mb-4 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Prompt Injection Guard</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Filters System Override attempts, Jailbreak personas, and instruction injection attacks prior to passing prompts to LLM loaders.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all group">
            <div className="p-3 bg-cyan-600/10 border border-cyan-500/20 text-cyan-400 rounded-xl w-fit mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">SHA256 Code Integrity</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Computes real-time hashes of agent code, configs, and policy YAMLs. Instantly enters Safe Mode if unversioned changes occur.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture Overview Section */}
      <section id="architecture" className="py-20 px-6 bg-slate-900/40 border-y border-slate-800/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs font-mono text-indigo-400 font-semibold uppercase tracking-widest">Pipeline Pipeline</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">End-to-End Governance Architecture</h2>
            <p className="text-slate-400 text-sm mt-2 max-w-2xl mx-auto">Seamless flow from user prompt through security shields, agent routers, and database audit persistence.</p>
          </div>

          <div className="glass-panel p-8 rounded-2xl border border-slate-800 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 text-center">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <User className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">User Request</span>
                <span className="text-[10px] text-slate-500 font-mono">React UI</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <Lock className="w-6 h-6 text-amber-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">Presidio PII</span>
                <span className="text-[10px] text-slate-500 font-mono">Masking</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <ShieldCheck className="w-6 h-6 text-indigo-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">Policy Engine</span>
                <span className="text-[10px] text-slate-500 font-mono">YAML Rules</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <Cpu className="w-6 h-6 text-cyan-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">Agent Router</span>
                <span className="text-[10px] text-slate-500 font-mono">3 Agents</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <FileText className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">Audit Trail</span>
                <span className="text-[10px] text-slate-500 font-mono">Immutable</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <Database className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                <span className="text-xs font-bold text-white block">Supabase / DB</span>
                <span className="text-[10px] text-slate-500 font-mono">Postgres / SQLite</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Grid */}
      <section className="py-20 px-6 max-w-7xl mx-auto w-full">
        <div className="text-center mb-16">
          <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-widest">Technology Stack</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">Enterprise Stack Integration</h2>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { title: "FastAPI", desc: "Python REST Backend", icon: Server },
            { title: "React + Vite", desc: "Enterprise Dashboard", icon: Zap },
            { title: "Tailwind CSS", desc: "Modern UI System", icon: Layers },
            { title: "LangChain", desc: "Agent Framework", icon: Cpu },
            { title: "Presidio", desc: "Microsoft PII Engine", icon: Lock },
            { title: "Supabase", desc: "PostgreSQL & Audit", icon: Database }
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="glass-card p-4 rounded-xl border border-slate-800 text-center">
                <Icon className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                <h4 className="font-bold text-sm text-white">{item.title}</h4>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full mb-12">
        <div className="glass-panel-glow p-10 rounded-3xl text-center border border-blue-500/30 relative overflow-hidden">
          <h2 className="text-3xl font-extrabold text-white mb-4">Ready to Evaluate Enterprise AI Governance?</h2>
          <p className="text-slate-300 text-sm max-w-xl mx-auto mb-8">
            Access the live interactive governance dashboard to run financial agents, inspect PII masks, test prompt injection shields, and simulate policy rollbacks.
          </p>
          <Link
            to="/dashboard"
            className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-xl shadow-blue-500/25 transition-all inline-flex items-center gap-2 text-sm"
          >
            <span>Enter Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

    </div>
  );
}
