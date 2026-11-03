'use client';

import { useState, useRef, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  ArrowUpRight,
  Scale,
  RefreshCw,
  FileText,
  Sliders,
  Sparkles,
} from 'lucide-react';
import SecurityBadge, { DefenseStatusProps } from '../components/SecurityBadge';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  defenseStatus?: DefenseStatusProps;
  retrievedPasals?: ArticleDoc[];
  scopeUsed?: string;
}

const SUGGESTED_QUERIES = [
  {
    tag: 'KUHPerdata Buku III',
    title: 'Syarat Sah Perjanjian (1320)',
    query: 'Apa 4 syarat sah perjanjian menurut Pasal 1320 KUHPerdata dan akibat hukum bila tidak terpenuhi?',
  },
  {
    tag: 'KUHPerdata Pasal 1365',
    title: 'Perbuatan Melawan Hukum (PMH)',
    query: 'Apa saja 5 unsur Perbuatan Melawan Hukum (PMH) menurut Pasal 1365 KUHPerdata?',
  },
  {
    tag: 'HIR Pasal 227',
    title: 'Sita Jaminan (Beslag)',
    query: 'Bagaimana syarat dan tata cara permohonan sita jaminan menurut Pasal 227 HIR?',
  },
  {
    tag: 'HIR Pasal 164',
    title: 'Alat Bukti Persidangan',
    query: 'Apa saja 5 alat bukti yang sah dalam persidangan perdata menurut Pasal 164 HIR?',
  },
];

function ChatContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Essential Anti-Poisoning Defense & Scenario
  const [enableDefense, setEnableDefense] = useState(true);
  const [corpusScenario, setCorpusScenario] = useState('kuhperdata_hir_bgem3');
  const [showDemoOptions, setShowDemoOptions] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasAutoQueried = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Auto-run if query param is passed from homepage or database
  useEffect(() => {
    if (initialQuery && !hasAutoQueried.current) {
      hasAutoQueried.current = true;
      handleSubmit(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = async (queryText: string) => {
    const text = queryText.trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      scopeUsed: 'KUHPerdata & HIR',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const payload = {
        query: text,
        collection: corpusScenario,
        enable_defense: enableDefense,
        llm_model: 'gemini',
        source_filter: null, // Terpadu: mencakup KUHPerdata & HIR sekaligus
        top_k: 5,
      };

      let res = await fetch('/api/py/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        res = await fetch('http://127.0.0.1:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        throw new Error('Gagal menghubungi backend CiviLex AI');
      }

      const data = await res.json();
      handleServerSuccess(data);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          'Mohon maaf, terjadi kendala koneksi dengan server backend CiviLex AI. Pastikan server.py telah berjalan di latar belakang.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleServerSuccess = (data: any) => {
    const assistantMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: data.answer,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      defenseStatus: data.defense_status,
      retrievedPasals: data.retrieved_pasals,
      scopeUsed: 'KUHPerdata & HIR',
    };
    setMessages((prev) => [...prev, assistantMsg]);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-6 pb-12 font-body">
      {/* Centered Testing Controls: Korpus (Poison/Non-Poison) & Proteksi (ON/OFF) */}
      <div className="flex flex-wrap items-center justify-center gap-3 pt-1 pb-1">
        {/* Korpus: Non-Poison vs Poison */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[#E8DEC9] shadow-2xs text-xs font-sans">
          <span className="text-[11px] text-[#6B5559] font-medium">Korpus:</span>
          <div className="flex items-center bg-[#FAF6EE] p-0.5 rounded-full border border-[#E8DEC9]">
            <button
              type="button"
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3')}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                corpusScenario === 'kuhperdata_hir_bgem3'
                  ? 'bg-[#75162D] text-[#FAF6EE] shadow-2xs'
                  : 'text-[#6B5559] hover:text-[#3B010B]'
              }`}
            >
              Non-Poison
            </button>
            <button
              type="button"
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3_p1pct')}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                corpusScenario === 'kuhperdata_hir_bgem3_p1pct'
                  ? 'bg-[#c2410c] text-white shadow-2xs'
                  : 'text-[#6B5559] hover:text-[#3B010B]'
              }`}
            >
              Poison (1%)
            </button>
          </div>
        </div>

        {/* Proteksi: ON vs OFF */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[#E8DEC9] shadow-2xs text-xs font-sans">
          <span className="text-[11px] text-[#6B5559] font-medium">Proteksi:</span>
          <div className="flex items-center bg-[#FAF6EE] p-0.5 rounded-full border border-[#E8DEC9]">
            <button
              type="button"
              onClick={() => setEnableDefense(true)}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                enableDefense
                  ? 'bg-[#15803d] text-white shadow-2xs'
                  : 'text-[#6B5559] hover:text-[#3B010B]'
              }`}
            >
              ON
            </button>
            <button
              type="button"
              onClick={() => setEnableDefense(false)}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold transition-all ${
                !enableDefense
                  ? 'bg-[#b91c1c] text-white shadow-2xs'
                  : 'text-[#6B5559] hover:text-[#3B010B]'
              }`}
            >
              OFF
            </button>
          </div>
        </div>
      </div>

      {/* Conversation Thread */}
      <div className="min-h-[360px] flex flex-col gap-6 font-sans">
        {messages.length === 0 && (
          <div className="my-auto py-8 text-center flex flex-col items-center max-w-xl mx-auto">
            <div className="w-11 h-11 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] mb-3 shadow-xs">
              <Scale className="w-5 h-5" />
            </div>
            <h2 className="font-bodoni text-xl sm:text-2xl font-medium tracking-tight text-[#3B010B]">
              Konsultasi Hukum Perdata
            </h2>
            <p className="text-xs text-[#6B5559] mt-1 mb-6 font-sans">
              Pilih contoh pertanyaan di bawah atau ketik langsung pertanyaan Anda:
            </p>

            {/* Suggested Question Pills (Clean & compact 2-col) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(q.query)}
                  className="p-3.5 rounded-xl bg-white border border-[#E8DEC9] text-xs text-[#2A171A] transition-all shadow-2xs hover:border-[#75162D] hover:shadow-xs flex items-center justify-between gap-3 group text-left"
                >
                  <div className="min-w-0">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#75162D] block font-sans">
                      {q.tag}
                    </span>
                    <span className="text-xs font-semibold text-[#3B010B] group-hover:text-[#75162D] transition-colors line-clamp-1 font-sans">
                      {q.title}
                    </span>
                  </div>
                  <ArrowUpRight className="w-4 h-4 text-[#75162D] shrink-0 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message Items */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col gap-1.5 ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            <div className="flex items-center gap-2 px-1 text-[11px] text-[#6B5559] font-medium">
              <span>{msg.role === 'user' ? 'Pertanyaan Anda' : 'Analisis CiviLex AI'}</span>
              <span>•</span>
              <span>{msg.timestamp}</span>
              {msg.scopeUsed && (
                <>
                  <span>•</span>
                  <span className="px-2 py-0.5 rounded-full bg-[#F2E5C6] text-[#560B18] text-[10px] font-bold">
                    {msg.scopeUsed === 'KUHPerdata' ? 'KUHPerdata' : msg.scopeUsed === 'HIR' ? 'HIR' : 'KUHPerdata & HIR'}
                  </span>
                </>
              )}
            </div>

            <div
              className={`rounded-2xl p-6 leading-relaxed max-w-2xl border ${
                msg.role === 'user'
                  ? 'bg-[#3B010B] text-[#FAF6EE] border-[#3B010B] shadow-sm'
                  : 'bg-[#FFFFFF] text-[#2A171A] border-[#E8DEC9] shadow-sm'
              }`}
            >
              {/* Security Defense Badge */}
              {msg.defenseStatus && <SecurityBadge defense={msg.defenseStatus} />}

              {/* Main Answer Content */}
              <div className="whitespace-pre-wrap text-xs sm:text-sm leading-relaxed space-y-3 font-normal">
                {msg.content}
              </div>

              {/* Cited Official Articles */}
              {msg.retrievedPasals && msg.retrievedPasals.length > 0 && (
                <div className="mt-6 pt-5 border-t border-[#E8DEC9] flex flex-col gap-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-[#75162D] flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    Pasal Rujukan Resmi ({msg.retrievedPasals.length} Pasal Terverifikasi):
                  </span>

                  <div className="space-y-3">
                    {msg.retrievedPasals.map((art, idx) => (
                      <PasalCard key={idx} article={art} index={idx} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Spinner */}
        {loading && (
          <div className="flex items-center gap-3 p-4 rounded-2xl bg-white border border-[#E8DEC9] max-w-xs shadow-sm">
            <RefreshCw className="w-4 h-4 text-[#75162D] animate-spin" />
            <span className="text-xs font-medium text-[#6B5559]">
              Sedang menelaah naskah resmi KUHPerdata &amp; HIR...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Floating Query Input */}
      <div className="sticky bottom-6 z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(input);
          }}
          className="relative flex items-center rounded-full bg-white/95 backdrop-blur-md border border-[#E8DEC9] shadow-lg shadow-[#75162D]/5 p-2 focus-within:border-[#75162D] transition-all"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ketik pertanyaan pasal atau persoalan perdata..."
            className="w-full px-5 py-2.5 text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none bg-transparent font-sans"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-burgundy-primary px-6 py-2.5 rounded-full disabled:opacity-40 shrink-0 ml-1 text-xs font-bold font-sans flex items-center gap-1.5 shadow-sm hover:scale-[1.02] transition-transform"
            title="Kirim Pertanyaan"
          >
            <span>Kirim</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-6 py-20 flex justify-center text-xs text-[#6B5559] font-sans">
          Memuat ruang konsultasi naskah...
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
