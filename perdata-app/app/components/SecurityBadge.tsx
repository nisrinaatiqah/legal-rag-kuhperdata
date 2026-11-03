'use client';

import { ShieldCheck, ShieldAlert, AlertTriangle, Lock, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export interface BlockedPasal {
  pasal: string;
  source: string;
  content: string;
  composite_risk_score: number;
  reason: string;
  source_status?: string;
  semantic_status?: string;
}

export interface DefenseStatusProps {
  is_defense_active: boolean;
  total_retrieved: number;
  cleared_count: number;
  blocked_count: number;
  status_badge: string; // 'VERIFIED_AUTHENTIC' | 'BLOCKED_POISON' | 'DANGER_PENETRATED'
  status_message: string;
  blocked_pasals?: BlockedPasal[];
}

export default function SecurityBadge({ defense }: { defense: DefenseStatusProps }) {
  const [showBlockedDetails, setShowBlockedDetails] = useState(false);

  if (!defense) return null;

  const isAuthentic = defense.status_badge === 'VERIFIED_AUTHENTIC';
  const isBlocked = defense.status_badge === 'BLOCKED_POISON';
  const isDanger = defense.status_badge === 'DANGER_PENETRATED';

  return (
    <div className="w-full my-4">
      {/* Main Alert Banner */}
      <div
        className={`rounded-2xl p-4 border transition-all ${
          isAuthentic
            ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200 shadow-lg shadow-emerald-950/20'
            : isBlocked
            ? 'bg-amber-950/30 border-amber-500/40 text-amber-200 shadow-lg shadow-amber-950/20'
            : 'bg-rose-950/40 border-rose-500/50 text-rose-200 shadow-lg shadow-rose-950/30 animate-pulse'
        }`}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div
              className={`p-2.5 rounded-xl shrink-0 ${
                isAuthentic
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : isBlocked
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}
            >
              {isAuthentic && <ShieldCheck className="w-6 h-6" />}
              {isBlocked && <ShieldAlert className="w-6 h-6" />}
              {isDanger && <AlertTriangle className="w-6 h-6" />}
            </div>

            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-bold text-sm tracking-wide uppercase">
                  {isAuthentic && 'Otentisitas Terverifikasi (100% SHA-256 Valid)'}
                  {isBlocked && 'Peringatan: Knowledge Poisoning Terdeteksi & Dikarantina!'}
                  {isDanger && 'Peringatan Bahaya: Pertahanan Dinonaktifkan (Pasal Beracun Lolos)'}
                </span>

                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300">
                  {defense.cleared_count}/{defense.total_retrieved} Dokumen Sah
                </span>
              </div>

              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                {defense.status_message}
              </p>
            </div>
          </div>

          {/* Toggle Blocked Details Button */}
          {defense.blocked_count > 0 && defense.blocked_pasals && (
            <button
              onClick={() => setShowBlockedDetails(!showBlockedDetails)}
              className="text-xs px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 flex items-center gap-1.5 shrink-0 transition-colors"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>{showBlockedDetails ? 'Tutup Rincian' : `Lihat ${defense.blocked_count} Pasal Dicegat`}</span>
              {showBlockedDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Detailed Blocked Chunks Drawer */}
        {showBlockedDetails && defense.blocked_pasals && (
          <div className="mt-4 pt-4 border-t border-amber-500/20 flex flex-col gap-3">
            <p className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-amber-400" />
              Audit Log Pasal yang Dicegat oleh Two-Tier Defense:
            </p>
            {defense.blocked_pasals.map((bp, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-900/90 border border-rose-500/30 text-xs flex flex-col gap-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-rose-300">
                    {bp.source} Pasal {bp.pasal}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-mono border border-rose-500/30">
                    Skor Risiko: {bp.composite_risk_score.toFixed(3)} (Threshold &gt; 0.50)
                  </span>
                </div>
                <p className="text-slate-300 italic line-clamp-2">&quot;{bp.content}&quot;</p>
                <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-1">
                  <span>
                    Integritas Sumber:{' '}
                    <strong className="text-rose-400">{bp.source_status || 'Hash Mismatch'}</strong>
                  </span>
                  <span>•</span>
                  <span>
                    Validasi NLI:{' '}
                    <strong className="text-amber-400">{bp.semantic_status || 'Contradiction'}</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
