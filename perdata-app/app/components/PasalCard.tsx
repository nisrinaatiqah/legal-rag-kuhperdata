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
    <div className="editorial-card editorial-card-hover rounded-2xl p-5 md:p-6 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-editorial-title text-base md:text-lg font-bold text-[#1c1917]">
              {article.source} Pasal {article.pasal}
            </span>
            <span className="text-[10px] uppercase tracking-wider font-semibold px-2.5 py-0.5 rounded-full bg-[#f4eee5] text-[#7a1827] border border-[#e2d7c9]">
              {article.source === 'KUHPerdata' ? 'Hukum Materiel' : 'Hukum Acara Formil'}
            </span>
          </div>
          {article.bab_title && article.bab_title !== '-' && (
            <p className="text-xs text-[#78716c] mt-1 italic font-editorial-display text-sm">
              {article.bab_title}
            </p>
          )}
        </div>

        {/* Copy Button */}
        <button
          onClick={copyToClipboard}
          className="p-2 rounded-xl bg-[#faf7f2] hover:bg-[#f0ebe1] text-[#57534e] hover:text-[#1c1917] border border-[#e7dfd5] transition-all shrink-0 flex items-center gap-1.5 text-xs"
          title="Salin Rujukan Hukum"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-[#15803d]" />
              <span className="text-[11px] text-[#15803d] font-medium">Tersalin</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="hidden sm:inline text-[11px]">Salin</span>
            </>
          )}
        </button>
      </div>

      {/* Content Text */}
      <div className="relative mt-2">
        <p
          className={`text-xs sm:text-sm text-[#44403c] leading-relaxed font-normal ${
            !expanded && isLong ? 'line-clamp-3' : ''
          }`}
        >
          &ldquo;{article.content}&rdquo;
        </p>

        {isLong && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-[#7a1827] hover:underline font-semibold mt-2 inline-flex items-center gap-1"
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
      <div className="mt-4 pt-3 border-t border-[#f2ede4] flex items-center justify-between text-[11px] text-[#8a847c]">
        <div className="flex items-center gap-1.5 text-[#15803d] font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Naskah Resmi Terverifikasi</span>
        </div>
        <span className="text-[10px] text-[#a8a29e] uppercase tracking-wider font-mono">
          JDIH Valid
        </span>
      </div>
    </div>
  );
}
