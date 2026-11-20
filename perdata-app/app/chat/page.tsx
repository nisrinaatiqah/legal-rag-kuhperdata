'use client';

import { useState, useRef, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  ArrowUpRight,
  RefreshCw,
  FlaskConical,
  ShieldCheck,
  ShieldAlert,
  ChevronDown,
  Check,
} from 'lucide-react';
import type { DefenseStatusProps } from '../components/SecurityBadge';
import type { ArticleDoc } from '../components/PasalCard';
import PasalResponseCard from '../components/PasalResponseCard';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  kesimpulan?: string | null;
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
  const [greeting, setGreeting] = useState('Selamat Datang');

  // Time-based greeting in Indonesian
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 4 && hour < 11) setGreeting('Selamat Pagi');
    else if (hour >= 11 && hour < 15) setGreeting('Selamat Siang');
    else if (hour >= 15 && hour < 18) setGreeting('Selamat Sore');
    else setGreeting('Selamat Malam');
  }, []);

  // Essential Anti-Poisoning Defense & Scenario
  const [enableDefense, setEnableDefense] = useState(true);
  const [corpusScenario, setCorpusScenario] = useState('kuhperdata_hir_bgem3');
  const [showDemoOptions, setShowDemoOptions] = useState(false);
  const [showCorpusMenu, setShowCorpusMenu] = useState(false);
  const [showDefenseMenu, setShowDefenseMenu] = useState(false);

  const corpusMenuRef = useRef<HTMLDivElement>(null);
  const defenseMenuRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasAutoQueried = useRef(false);
  const isInitialMount = useRef(true);

  // Close menus when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (corpusMenuRef.current && !corpusMenuRef.current.contains(event.target as Node)) {
        setShowCorpusMenu(false);
      }
      if (defenseMenuRef.current && !defenseMenuRef.current.contains(event.target as Node)) {
        setShowDefenseMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const corpusOptions = [
    {
      id: 'kuhperdata_hir_bgem3',
      label: 'Non-Poison',
      badge: '0% Poison',
      desc: 'Naskah resmi otentik (2.276 pasal KUHPerdata & HIR)',
    },
    {
      id: 'kuhperdata_hir_bgem3_p1pct',
      label: 'Poison 1%',
      badge: '1% Poison',
      desc: 'Simulasi manipulasi minor (~23 pasal beracun)',
    },
    {
      id: 'kuhperdata_hir_bgem3_p5pct',
      label: 'Poison 5%',
      badge: '5% Poison',
      desc: 'Simulasi manipulasi moderat (~114 pasal beracun)',
    },
    {
      id: 'kuhperdata_hir_bgem3_p10pct',
      label: 'Poison 10%',
      badge: '10% Poison',
      desc: 'Simulasi manipulasi masif (~228 pasal beracun)',
    },
  ];

  const currentCorpus =
    corpusOptions.find((c) => c.id === corpusScenario) || corpusOptions[0];

  // Ensure view starts precisely at the top on initial load
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  }, []);

  // ChatGPT-style auto-follow scroll: follows prompt and generated answers smoothly
  const scrollToFlow = (behavior: ScrollBehavior = 'smooth') => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior,
        block: 'end',
      });
    }
  };

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    if (messages.length > 0 || loading) {
      const timer = setTimeout(() => {
        scrollToFlow('smooth');
      }, 120);
      return () => clearTimeout(timer);
    }
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

      const backendUrl = (
        process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'
      ).replace(/\/+$/, '');

      let res = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok && backendUrl !== 'http://127.0.0.1:8000') {
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
    let cleanAnswer = data.answer || '';
    let extractedKesimpulan = data.kesimpulan || null;
    if (!extractedKesimpulan && cleanAnswer.includes('=== KESIMPULAN ===')) {
      const parts = cleanAnswer.split('=== KESIMPULAN ===');
      cleanAnswer = parts[0].trim();
      extractedKesimpulan = parts[1].trim();
    }

    const assistantMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: cleanAnswer,
      kesimpulan: extractedKesimpulan,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      defenseStatus: data.defense_status,
      retrievedPasals: data.retrieved_pasals,
      scopeUsed: 'KUHPerdata & HIR',
    };
    setMessages((prev) => [...prev, assistantMsg]);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-6 pb-12 font-body">
      {/* Conversation Thread */}
      <div className="min-h-[360px] flex flex-col gap-6 font-sans">
        {messages.length === 0 && (
          <div className="my-auto py-8 text-center flex flex-col items-center max-w-xl mx-auto font-sans">
            {/* Welcoming Headline */}
            <h2
              className="font-bodoni text-3xl sm:text-4xl md:text-5xl font-medium tracking-tight text-[#3B010B] leading-tight animate-fade-up"
              style={{ animationDelay: '0.05s' }}
            >
              {greeting}
            </h2>

            {/* Subtitle / Opening Sentence */}
            <p
              className="text-xs sm:text-sm text-[#6B5559] mt-2 mb-8 max-w-lg leading-relaxed font-normal animate-fade-up"
              style={{ animationDelay: '0.15s' }}
            >
              Tanyakan apa saja yang ingin Anda ketahui seputar ketentuan KUHPerdata dan HIR.
            </p>

            {/* Suggested Question Pills with Smooth Staggered Fade Entrance */}
            <div
              className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left animate-fade-up"
              style={{ animationDelay: '0.25s' }}
            >
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(q.query)}
                  className="p-3.5 rounded-xl bg-white border border-[#E8DEC9] text-xs text-[#2A171A] transition-all shadow-2xs hover:border-[#75162D] hover:shadow-xs flex items-center justify-between gap-3 group text-left cursor-pointer"
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
            className={`flex flex-col gap-1.5 scroll-mt-32 ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            {/* Timestamp Only */}
            <div className="px-1 text-[11px] text-[#8C7A7E] font-medium">
              <span>{msg.timestamp}</span>
            </div>

            <div
              className={`rounded-2xl p-6 leading-relaxed border animate-fade-up ${
                msg.role === 'user'
                  ? 'bg-[#3B010B] text-[#FAF6EE] border-[#3B010B] shadow-sm max-w-xl ml-auto'
                  : 'bg-[#FFFFFF] text-[#2A171A] border-[#E8DEC9] shadow-sm max-w-2xl w-full'
              }`}
            >
              {msg.role === 'user' ? (
                <div className="whitespace-pre-wrap text-xs sm:text-sm">{msg.content}</div>
              ) : (
                <PasalResponseCard
                  answer={msg.content}
                  kesimpulan={msg.kesimpulan}
                  docs={msg.retrievedPasals}
                />
              )}
            </div>
          </div>
        ))}

        {/* Loading Spinner */}
        {loading && (
          <div className="flex items-center gap-3 p-4 rounded-2xl bg-white border border-[#E8DEC9] max-w-xs shadow-sm animate-fade-up">
            <RefreshCw className="w-4 h-4 text-[#75162D] animate-spin" />
            <span className="text-xs font-medium text-[#6B5559]">
              Sedang menelaah naskah resmi KUHPerdata &amp; HIR...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Ample bottom spacer so cards and articles are never covered by sticky input */}
      <div className="h-16 pointer-events-none" />

      {/* Floating Query Input with Integrated Controls (Antigravity Style) */}
      <div className="sticky bottom-6 z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(input);
          }}
          className="relative flex flex-col rounded-2xl bg-white/95 backdrop-blur-md border border-[#E8DEC9] shadow-lg shadow-[#75162D]/5 p-2.5 focus-within:border-[#75162D] focus-within:ring-2 focus-within:ring-[#75162D]/10 transition-all"
        >
          {/* Text Input / Textarea */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(input);
              }
            }}
            placeholder="Ketik pertanyaan pasal atau persoalan perdata... (Enter untuk kirim, Shift+Enter untuk baris baru)"
            rows={1}
            className="w-full px-3 py-1.5 text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none bg-transparent font-sans resize-none min-h-[38px] max-h-32"
          />

          {/* Bottom Toolbar Row: Poisoning & Defense Buttons (Antigravity Style) */}
          <div className="flex items-center justify-between pt-2 border-t border-[#F2ECE1] mt-1 gap-2">
            <div className="flex items-center gap-1.5 flex-wrap">
              {/* Tombol Tingkat Poisoning */}
              <div className="relative" ref={corpusMenuRef}>
                <button
                  type="button"
                  onClick={() => {
                    setShowCorpusMenu(!showCorpusMenu);
                    setShowDefenseMenu(false);
                  }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold border transition-all ${
                    corpusScenario === 'kuhperdata_hir_bgem3'
                      ? 'bg-[#FAF6EE] text-[#4A3236] border-[#E8DEC9] hover:bg-[#F2EADB]'
                      : 'bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100'
                  }`}
                  title="Pilih tingkat manipulasi korpus (Knowledge Poisoning)"
                >
                  <FlaskConical className="w-3.5 h-3.5 text-[#75162D]" />
                  <span>Korpus: {currentCorpus.label}</span>
                  <ChevronDown className="w-3 h-3 text-[#8C7A7C]" />
                </button>

                {/* Dropdown Menu Korpus (Floating Above) */}
                {showCorpusMenu && (
                  <div className="absolute bottom-full mb-2 left-0 w-72 bg-white border border-[#E8DEC9] rounded-xl shadow-2xl p-1.5 z-50 flex flex-col gap-1">
                    <div className="px-3 py-1.5 text-[10px] font-bold text-[#8C7A7C] uppercase tracking-wider border-b border-[#F2ECE1]">
                      Tingkat Knowledge Poisoning
                    </div>
                    {corpusOptions.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => {
                          setCorpusScenario(opt.id);
                          setShowCorpusMenu(false);
                        }}
                        className={`flex flex-col text-left px-3 py-2 rounded-lg transition-all ${
                          corpusScenario === opt.id
                            ? 'bg-[#FAF6EE] border border-[#E8DEC9]'
                            : 'hover:bg-[#FAF6EE]/60'
                        }`}
                      >
                        <div className="flex items-center justify-between w-full">
                          <span className="font-semibold text-xs text-[#2A171A] flex items-center gap-1.5">
                            {opt.label}
                          </span>
                          {corpusScenario === opt.id && (
                            <Check className="w-3.5 h-3.5 text-[#75162D]" />
                          )}
                        </div>
                        <span className="text-[10px] text-[#8C7A7C] mt-0.5">{opt.desc}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Tombol Mode Pertahanan (Proteksi) */}
              <div className="relative" ref={defenseMenuRef}>
                <button
                  type="button"
                  onClick={() => {
                    setShowDefenseMenu(!showDefenseMenu);
                    setShowCorpusMenu(false);
                  }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold border transition-all ${
                    enableDefense
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
                      : 'bg-rose-50 text-rose-800 border-rose-300 hover:bg-rose-100'
                  }`}
                  title="Pilih status proteksi SHA-256 + NLI"
                >
                  {enableDefense ? (
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                  )}
                  <span>{enableDefense ? 'Proteksi: ON' : 'Proteksi: OFF'}</span>
                  <ChevronDown className="w-3 h-3 text-[#8C7A7C]" />
                </button>

                {/* Dropdown Menu Proteksi (Floating Above) */}
                {showDefenseMenu && (
                  <div className="absolute bottom-full mb-2 left-0 sm:left-auto sm:right-0 w-64 bg-white border border-[#E8DEC9] rounded-xl shadow-2xl p-1.5 z-50 flex flex-col gap-1">
                    <div className="px-3 py-1.5 text-[10px] font-bold text-[#8C7A7C] uppercase tracking-wider border-b border-[#F2ECE1]">
                      Mode Pertahanan RAG
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setEnableDefense(true);
                        setShowDefenseMenu(false);
                      }}
                      className={`flex flex-col text-left px-3 py-2 rounded-lg transition-all ${
                        enableDefense
                          ? 'bg-[#FAF6EE] border border-[#E8DEC9]'
                          : 'hover:bg-[#FAF6EE]/60'
                      }`}
                    >
                      <div className="flex items-center justify-between w-full">
                        <span className="font-semibold text-xs text-emerald-700 flex items-center gap-1.5">
                          <ShieldCheck className="w-3.5 h-3.5" /> Proteksi Aktif (ON)
                        </span>
                        {enableDefense && <Check className="w-3.5 h-3.5 text-emerald-700" />}
                      </div>
                      <span className="text-[10px] text-[#8C7A7C] mt-0.5">
                        Mencegat pasal manipulasi via verifikasi SHA-256 & evaluasi NLI
                      </span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setEnableDefense(false);
                        setShowDefenseMenu(false);
                      }}
                      className={`flex flex-col text-left px-3 py-2 rounded-lg transition-all ${
                        !enableDefense
                          ? 'bg-[#FAF6EE] border border-[#E8DEC9]'
                          : 'hover:bg-[#FAF6EE]/60'
                      }`}
                    >
                      <div className="flex items-center justify-between w-full">
                        <span className="font-semibold text-xs text-rose-700 flex items-center gap-1.5">
                          <ShieldAlert className="w-3.5 h-3.5" /> Proteksi Nonaktif (OFF)
                        </span>
                        {!enableDefense && <Check className="w-3.5 h-3.5 text-rose-700" />}
                      </div>
                      <span className="text-[10px] text-[#8C7A7C] mt-0.5">
                        Simulasi tanpa saringan pertahanan (menguji kerentanan RAG)
                      </span>
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Tombol Kirim */}
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn-burgundy-primary px-4 py-1.5 rounded-xl disabled:opacity-40 shrink-0 text-xs font-bold font-sans flex items-center gap-1.5 shadow-sm hover:scale-[1.02] transition-transform"
              title="Kirim Pertanyaan (Enter)"
            >
              <span>Kirim</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
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
