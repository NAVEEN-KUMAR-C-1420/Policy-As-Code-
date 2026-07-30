import React from 'react';
import { ShieldCheck, ShieldAlert, AlertOctagon } from 'lucide-react';

export default function PromptInjectionBadge({ injection }) {
  if (!injection) return null;

  const { status = 'Safe', matched_rules = [] } = injection;

  const getBadgeStyle = () => {
    switch (status) {
      case 'Blocked':
        return {
          bg: 'bg-red-950/80 border-red-500/50 text-red-300',
          icon: <AlertOctagon className="w-4 h-4 text-red-400 animate-bounce" />,
          label: 'PROMPT INJECTION BLOCKED'
        };
      case 'Warning':
        return {
          bg: 'bg-amber-950/80 border-amber-500/50 text-amber-300',
          icon: <ShieldAlert className="w-4 h-4 text-amber-400" />,
          label: 'INJECTION THREAT WARNING'
        };
      default:
        return {
          bg: 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300',
          icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
          label: 'PROMPT SHIELD SAFE'
        };
    }
  };

  const style = getBadgeStyle();

  return (
    <div className={`glass-card rounded-xl p-4 border space-y-2 ${style.bg}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {style.icon}
          <h4 className="text-xs font-bold uppercase tracking-wider">{style.label}</h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900/60 font-semibold">
          STATUS: {status.toUpperCase()}
        </span>
      </div>

      {matched_rules.length > 0 ? (
        <div className="space-y-1">
          <p className="text-xs font-mono font-medium">Detected Threat Patterns:</p>
          <ul className="space-y-1">
            {matched_rules.map((rule, idx) => (
              <li key={idx} className="text-[11px] font-mono text-red-300 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                <span>{rule.reason} (Severity: {rule.severity})</span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-xs text-emerald-300/90 font-mono">
          No system overrides, prompt leaks, or jailbreak patterns detected.
        </p>
      )}
    </div>
  );
}
