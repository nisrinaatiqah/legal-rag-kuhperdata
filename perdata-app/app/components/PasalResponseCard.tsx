'use client';

import React, { useState } from 'react';
import { BookOpen, Copy, Check, Sparkles, Scale } from 'lucide-react';
import type { ArticleDoc } from './PasalCard';

export type { ArticleDoc };

interface PasalResponseCardProps {
  answer: string;
  kesimpulan?: string | null;
  docs?: ArticleDoc[];
}

// Helper untuk merender formatting inline (**bold**, *italic*) secara mulus tanpa raw markdown
function renderInline(str: string): React.ReactNode {
  if (!str) return null;
  const parts = str.split(/(\*\*.*?\*\*|\*[^*]+?\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
      return (
        <strong key={i} className="font-semibold text-[#1A0A0D]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
      return (
        <em key={i} className="italic text-[#4A3237]">
          {part.slice(1, -1)}
        </em>
      );
    }
    return part;
  });
}

// Helper untuk merender markdown terstruktur (paragraf, headings, lists) tanpa bintang mentah
export function renderCleanContent(text: string) {
  if (!text) return null;

  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let currentList: { number?: string; content: React.ReactNode }[] = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <div key={`list-${elements.length}`} className="my-2.5 space-y-1.5 pl-0.5">
          {currentList.map((item, idx) => (
            <div key={idx} className="flex gap-2.5 items-start leading-relaxed">
              <span className="font-bold text-[#75162D] shrink-0 text-xs sm:text-sm">
                {item.number ? item.number : '•'}
              </span>
              <span className="text-xs sm:text-sm flex-1 leading-relaxed text-[#2A171A]">
                {item.content}
              </span>
            </div>
          ))}
        </div>
      );
      currentList = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    // Abaikan garis pemisah kaku
    if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
      flushList();
      continue;
    }

    if (!trimmed) {
      flushList();
      elements.push(<div key={`spacer-${i}`} className="h-1.5" />);
      continue;
    }

    // Heading tags
    if (trimmed.startsWith('#')) {
      flushList();
      const title = trimmed.replace(/^#{1,4}\s+/, '');
      elements.push(
        <div
          key={`heading-${i}`}
          className="font-semibold text-[#3B010B] text-xs sm:text-sm mt-3.5 mb-1.5 tracking-tight font-sans"
        >
          {renderInline(title)}
        </div>
      );
      continue;
    }

    // Subheader bold seperti **Unsur:** atau **Syarat Sah Perjanjian:**
    const isSubHeader =
      (trimmed.startsWith('**') && trimmed.endsWith(':**')) ||
      (trimmed.startsWith('**') && trimmed.endsWith('**') && !trimmed.slice(2, -2).includes('**'));

    if (isSubHeader) {
      flushList();
      const title = trimmed.replace(/^\*\*|\*\*$/g, '');
      elements.push(
        <div
          key={`subhead-${i}`}
          className="font-semibold text-[#3B010B] text-xs sm:text-sm mt-3 mb-1 tracking-tight font-sans"
        >
          {title}
        </div>
      );
      continue;
    }

    // List berangka: '1. ', '2. ', dst.
    const numMatch = trimmed.match(/^(\d+[\.\)])\s+(.*)$/);
    if (numMatch) {
      currentList.push({
        number: numMatch[1],
        content: renderInline(numMatch[2]),
      });
      continue;
    }

    // List bullet: '- ', '* ', '• '
    const bulletMatch = trimmed.match(/^[-*•]\s+(.*)$/);
    if (bulletMatch) {
      currentList.push({
        content: renderInline(bulletMatch[1]),
      });
      continue;
    }

    // Paragraf biasa
    flushList();
    elements.push(
      <p key={`p-${i}`} className="text-xs sm:text-sm leading-relaxed text-[#2A171A]">
        {renderInline(trimmed)}
      </p>
    );
  }

  flushList();
  return <div className="space-y-1">{elements}</div>;
}

export default function PasalResponseCard({
  answer,
  kesimpulan,
  docs = [],
}: PasalResponseCardProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [copied, setCopied] = useState(false);

  // Filter pasal unik bila ada duplikat
  const uniqueDocs = docs.filter(
    (doc, index, self) =>
      index === self.findIndex((d) => d.pasal === doc.pasal && d.source === doc.source)
  );

  const activeDoc = uniqueDocs[activeIndex] || uniqueDocs[0];

  const handleCopy = (text: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full flex flex-col gap-5 text-left font-sans">
      {/* 1. BAGIAN PENJELASAN AI (DIRECT & NATURAL ANSWER) */}
      <div className="leading-relaxed text-[#2A171A]">
        {renderCleanContent(answer)}
      </div>

      {/* 2. BAGIAN REKOMENDASI PASAL BER-TAB (ARSITEKTUR MAS NICHO) */}
      {uniqueDocs.length > 0 && activeDoc && (
        <div className="pt-2 border-t border-[#E8DEC9]/70 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-[#75162D]" />
            <span className="text-xs font-bold text-[#3B010B] tracking-tight">
              Rekomendasi Pasal
            </span>
          </div>

          {/* Pill Tabs */}
          <div className="flex flex-wrap items-center gap-1.5">
            {uniqueDocs.map((doc, idx) => {
              const isActive = idx === activeIndex;
              return (
                <button
                  key={`${doc.source}-${doc.pasal}-${idx}`}
                  type="button"
                  onClick={() => setActiveIndex(idx)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#75162D] text-[#FAF6EE] shadow-2xs font-semibold'
                      : 'bg-[#FAF6EE] text-[#75162D] border border-[#E8DEC9] hover:bg-white hover:border-[#75162D]/40'
                  }`}
                >
                  {doc.source} Pasal {doc.pasal}
                </button>
              );
            })}
          </div>

          {/* Active Pasal Card Content */}
          <div className="rounded-xl border border-[#E8DEC9] bg-[#FAF6EE]/40 overflow-hidden shadow-2xs transition-all">
            {/* Header Naskah */}
            <div className="px-4 py-2.5 bg-[#FAF6EE] border-b border-[#E8DEC9] flex items-center justify-between gap-3">
              <div>
                <span className="text-xs font-bold text-[#3B010B] block">
                  {activeDoc.source} Pasal {activeDoc.pasal}
                </span>
                {activeDoc.bab_title && activeDoc.bab_title !== '-' && (
                  <span className="text-[11px] text-[#6B5559] block line-clamp-1 font-normal">
                    {activeDoc.bab_title}
                  </span>
                )}
              </div>

              <button
                type="button"
                onClick={() =>
                  handleCopy(`${activeDoc.source} Pasal ${activeDoc.pasal}\n\n${activeDoc.content}`)
                }
                className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-[#E8DEC9] text-[11px] font-medium text-[#6B5559] hover:text-[#75162D] hover:border-[#75162D]/50 transition-all cursor-pointer shrink-0"
                title="Salin Naskah Pasal"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-700">Tersalin</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-[#75162D]" />
                    <span>Salin</span>
                  </>
                )}
              </button>
            </div>

            {/* Isi Naskah Pasal */}
            <div className="p-4 bg-white/70">
              <p className="text-xs sm:text-sm leading-relaxed text-[#2A171A] font-serif whitespace-pre-wrap">
                &ldquo;{activeDoc.content.trim()}&rdquo;
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 3. BAGIAN KESIMPULAN (RINGKASAN POIN-POIN INTI) */}
      {kesimpulan && (
        <div className="pt-2 border-t border-[#E8DEC9]/70 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-[#75162D]" />
            <span className="text-xs font-bold text-[#3B010B] tracking-tight">
              Kesimpulan
            </span>
          </div>

          <div className="rounded-xl border border-[#E8DEC9] bg-[#FAF6EE] p-3.5 text-xs sm:text-sm text-[#2A171A] leading-relaxed shadow-2xs">
            {renderCleanContent(kesimpulan)}
          </div>
        </div>
      )}
    </div>
  );
}
