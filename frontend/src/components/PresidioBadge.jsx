import React from 'react';
import { Lock, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function PresidioBadge({ presidio }) {
  if (!presidio) return null;

  const { detected_entities = [], redacted_text, has_pii, engine } = presidio;

  return (
    <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${has_pii ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
            <Lock className="w-4 h-4" />
          </div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">Microsoft Presidio PII Shield</h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
          {engine || 'Presidio Engine'}
        </span>
      </div>

      {has_pii ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-amber-300">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Detected {detected_entities.length} sensitive entity(ies):</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {detected_entities.map((item, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded text-[11px] font-mono bg-amber-950/60 border border-amber-500/40 text-amber-200">
                {item.entity_type}: <strong className="text-white">{item.value}</strong> ({Math.round(item.confidence * 100)}% conf → {item.decision})
              </span>
            ))}
          </div>
          {redacted_text && (
            <div className="mt-2 text-xs font-mono bg-slate-900/80 p-2 rounded border border-slate-800 text-slate-300">
              <span className="text-slate-500 block text-[10px] mb-1">MASKED SAFE PROMPT:</span>
              {redacted_text}
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono">
          <ShieldCheck className="w-4 h-4" />
          <span>Zero PII detected. Prompt contains no sensitive personal data.</span>
        </div>
      )}
    </div>
  );
}
