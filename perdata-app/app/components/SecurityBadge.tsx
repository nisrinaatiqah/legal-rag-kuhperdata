'use client';

import { ShieldCheck, ShieldAlert, AlertTriangle, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export interface BlockedPasal {
  pasal: string;
  source: string;
  content: string;
  composite_risk_score?: number;
  reason?: string;
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
  const [showBlocked, setShowBlocked] = useState(false);

  if (!defense) return null;

  const isAuthentic = defense.status_badge === 'VERIFIED_AUTHENTIC';
  const isBlocked = defense.status_badge === 'BLOCKED_POISON';
  const isDanger = defense.status_badge === 'DANGER_PENETRATED';

  return (
    <div className="w-full my-3">
      {isAuthentic && (
        <div className="rounded-xl px-4 py-2.5 bg-[#f0fdf4] border border-[#bbf7d0] text-[#166534] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#16a34a] shrink-0" />
            <span className="font-semibold">Naskah Resmi Terverifikasi</span>
            <span className="text-[#15803d] hidden sm:inline">• Bebas dari manipulasi informasi</span>
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#dcfce7] text-[#15803d]">
            JDIH Valid
          </span>
        </div>
      )}

      {isBlocked && (
        <div className="rounded-xl p-4 bg-[#fef2f2] border border-[#fecaca] text-[#991b1b] flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-[#dc2626] shrink-0" />
              <span className="font-bold text-xs sm:text-sm">
                Manipulasi Terdeteksi &amp; Berhasil Dicegat
              </span>
            </div>
            {defense.blocked_count > 0 && defense.blocked_pasals && (
              <button
                onClick={() => setShowBlocked(!showBlocked)}
                className="text-[11px] font-semibold text-[#991b1b] hover:underline flex items-center gap-1"
              >
                <span>{showBlocked ? 'Tutup' : `Lihat ${defense.blocked_count} Pasal Dicegat`}</span>
                {showBlocked ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
          </div>

          <p className="text-xs text-[#7f1d1d] leading-relaxed">
            Sistem mendeteksi adanya ketidaksesuaian naskah dengan rujukan resmi. Seluruh dokumen yang terindikasi palsu telah dikeluarkan dari hasil penelusuran AI.
          </p>

          {showBlocked && defense.blocked_pasals && (
            <div className="mt-2 pt-2 border-t border-[#fecaca] space-y-2">
              {defense.blocked_pasals.map((bp, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-white border border-[#fca5a5] text-xs">
                  <span className="font-bold text-[#b91c1c]">
                    {bp.source} Pasal {bp.pasal}
                  </span>
                  <p className="text-[#7f1d1d] italic mt-0.5">&ldquo;{bp.content}&rdquo;</p>
                  <span className="text-[10px] text-[#dc2626] font-semibold block mt-1">
                    Status: Dicegat &amp; Ditolak dari Konteks AI
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {isDanger && (
        <div className="rounded-xl px-4 py-3 bg-[#fffbeb] border border-[#fde68a] text-[#92400e] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#d97706] shrink-0" />
            <span className="font-semibold">Mode Tanpa Pertahanan Aktif</span>
            <span className="text-[#b45309] hidden sm:inline">(Pengujian Kerentanan Serangan)</span>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#fef3c7] text-[#b45309]">
            Simulasi Demo
          </span>
        </div>
      )}
    </div>
  );
}
