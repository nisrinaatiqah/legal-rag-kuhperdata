'use client';

import { useState } from 'react';
import { Copy, Check, Hash, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';

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
  const [expanded, setExpanded] = useState(true);

  const copyToClipboard = () => {
    const textToCopy = `${article.source} Pasal ${article.pasal}:\n"${article.content}"`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isLong = article.content.length > 280;

  return (
    <div className="rounded-2xl glass-card p-5 border border-slate-700/60 transition-all hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-950/20">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs shrink-0">
            {index !== undefined ? index + 1 : <BookOpen className="w-4 h-4" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white">
                {article.source} Pasal {article.pasal}
              </span>
              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                  article.source === 'KUHPerdata'
                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                }`}
              >
                {article.source === 'KUHPerdata' ? 'Hukum Materiel' : 'Hukum Acara'}
              </span>
            </div>
            {article.bab_title && article.bab_title !== '-' && (
              <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{article.bab_title}</p>
            )}
          </div>
        </div>

        {/* Action & Metric Score */}
        <div className="flex items-center gap-2">
          {article.score !== undefined && article.score > 0 && (
            <span className="text-[11px] font-mono px-2 py-1 rounded-lg bg-slate-800 border border-slate-700 text-indigo-300">
              Sim: {article.score.toFixed(4)}
            </span>
          )}
          <button
            onClick={copyToClipboard}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors"
            title="Salin Rujukan Hukum"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Content Body */}
      <div className="relative">
        <p
          className={`text-xs text-slate-200 leading-relaxed font-normal ${
            !expanded && isLong ? 'line-clamp-3' : ''
          }`}
        >
          &quot;{article.content}&quot;
        </p>

        {isLong && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[11px] text-indigo-400 hover:text-indigo-300 mt-1 flex items-center gap-1 font-medium"
          >
            {expanded ? (
              <>
                <ChevronUp className="w-3 h-3" /> Ringkas
              </>
            ) : (
              <>
                <ChevronDown className="w-3 h-3" /> Tampilkan Lengkap
              </>
            )}
          </button>
        )}
      </div>

      {/* Footer Metadata: SHA-256 Checksum */}
      {article.sha256 && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
          <div className="flex items-center gap-1.5 font-mono truncate max-w-[80%]">
            <Hash className="w-3 h-3 text-emerald-400 shrink-0" />
            <span className="text-slate-500">SHA-256:</span>
            <span className="text-slate-400 truncate">{article.sha256}</span>
          </div>
          <span className="text-emerald-400 font-medium shrink-0 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Valid JDIH
          </span>
        </div>
      )}
    </div>
  );
}
