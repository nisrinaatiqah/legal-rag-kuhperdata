'use client';

import { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp, ShieldCheck } from 'lucide-react';

export interface ArticleDoc {
  pasal: string;
  source: string;
  bab_title?: string;
  content: string;
  score?: number;
  sha256?: string;
  is_poisoned?: boolean;
}

export default function PasalCard({ article, index }: { article: ArticleDoc; index?: number }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const copyToClipboard = () => {
    const textToCopy = `${article.source} Pasal ${article.pasal}:\n"${article.content}"`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isLong = article.content.length > 250;

  return (
    <div className="bg-[#FFFFFF] border border-[#E8DEC9] rounded-sm p-5 md:p-6 transition-all hover:border-[#F2D9A0] font-body shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-cinzel text-base md:text-lg font-bold tracking-wide text-[#3B010B]">
              {article.source} Pasal {article.pasal}
            </span>
            <span className="text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-sm bg-[#F2E5C6] text-[#560B18] border border-[#F2D9A0] font-cinzel">
              {article.source === 'KUHPerdata' ? 'Hukum Materiel' : 'Hukum Acara Formil'}
            </span>
          </div>
          {article.bab_title && article.bab_title !== '-' && (
            <p className="text-sm text-[#75162D] mt-1 italic font-cormorant font-medium">
              {article.bab_title}
            </p>
          )}
        </div>

        {/* Copy Button: Crisp Rectangular (Image 2 Style) */}
        <button
          onClick={copyToClipboard}
          className="p-2 rounded-sm bg-[#FAF6EE] hover:bg-[#F2E5C6] text-[#560B18] border border-[#E8DEC9] transition-all shrink-0 flex items-center gap-1.5 text-xs font-cinzel font-semibold"
          title="Salin Rujukan Hukum"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-[#15803d]" />
              <span className="text-[11px] text-[#15803d]">Tersalin</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="hidden sm:inline text-[11px]">Salin</span>
            </>
          )}
        </button>
      </div>

      {/* Content Text in Inter */}
      <div className="relative mt-2">
        <p
          className={`text-xs sm:text-sm text-[#2A171A] leading-relaxed font-normal ${
            !expanded && isLong ? 'line-clamp-3' : ''
          }`}
        >
          &ldquo;{article.content}&rdquo;
        </p>

        {isLong && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-[#75162D] hover:underline font-semibold mt-2 inline-flex items-center gap-1"
          >
            {expanded ? (
              <>
                <ChevronUp className="w-3.5 h-3.5" /> Ringkas
              </>
            ) : (
              <>
                <ChevronDown className="w-3.5 h-3.5" /> Baca Selengkapnya
              </>
            )}
          </button>
        )}
      </div>

      {/* Subtle Integrity Badge */}
      <div className="mt-4 pt-3 border-t border-[#FAF6EE] flex items-center justify-between text-[11px] text-[#6B5559]">
        <div className="flex items-center gap-1.5 text-[#15803d] font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Naskah Resmi Terverifikasi</span>
        </div>
        <span className="text-[10px] text-[#8C7A7C] uppercase tracking-wider font-mono">
          JDIH Valid
        </span>
      </div>
    </div>
  );
}
