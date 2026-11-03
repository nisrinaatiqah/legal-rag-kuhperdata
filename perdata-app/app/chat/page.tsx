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
    title: 'Syarat Sah Perjanjian & Akibat Batal',
    query: 'Apa 4 syarat sahnya perjanjian menurut Pasal 1320 KUHPerdata dan apa akibat hukumnya jika syarat subjektif atau objektif tidak terpenuhi?',
  },
  {
    tag: 'KUHPerdata Pasal 1365',
    title: 'Gugatan Perbuatan Melawan Hukum (PMH)',
    query: 'Apa saja 5 unsur Perbuatan Melawan Hukum (PMH) menurut Pasal 1365 KUHPerdata yang wajib dibuktikan oleh penggugat?',
  },
  {
    tag: 'HIR Pasal 227',
    title: 'Sita Jaminan (Conservatoir Beslag)',
    query: 'Bagaimana tata cara dan syarat permohonan sita jaminan (conservatoir beslag) menurut Pasal 227 HIR agar aset tergugat tidak dipindahtangankan?',
  },
  {
    tag: 'HIR Pasal 164',
    title: 'Hierarki 5 Alat Bukti Persidangan',
    query: 'Sebutkan dan jelaskan kekuatan pembuktian 5 alat bukti yang sah dalam persidangan perdata menurut Pasal 164 HIR!',
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
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-8 pb-12 font-body">
      {/* Header with Marcellus & Italiana Typography */}
      <div className="flex flex-col gap-4 border-b border-[#E8DEC9] pb-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Asistensi Penelusuran Cerdas
            </span>
            <h1 className="font-marcellus text-3xl sm:text-4xl font-normal tracking-wide text-[#3B010B] mt-1">
              Konsultasi Naskah{' '}
              <span className="font-italiana text-[#75162D] normal-case text-4xl sm:text-5xl block sm:inline">
                KUHPerdata &amp; HIR
              </span>
            </h1>
            <p className="text-xs sm:text-sm text-[#6B5559] mt-1 font-montserrat font-medium max-w-xl">
              Satu asisten terpadu untuk menelaah hukum materiel (perjanjian &amp; ganti rugi) sekaligus hukum formil persidangan (sita jaminan &amp; pembuktian).
            </p>
          </div>

          {/* Essential Defense Toggle */}
          <div className="flex items-center gap-2.5 shrink-0">
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/95 border border-[#E8DEC9] shadow-xs text-xs font-semibold text-[#2A171A] font-montserrat">
              <span className="text-[11px] text-[#6B5559]">Proteksi SHA-256 + NLI:</span>
              <button
                onClick={() => setEnableDefense(!enableDefense)}
                className={`px-3 py-0.5 rounded-full text-[11px] font-bold transition-all ${
                  enableDefense
                    ? 'bg-[#15803d] text-white shadow-xs'
                    : 'bg-[#75162D] text-[#F2E5C6]'
                }`}
              >
                {enableDefense ? 'Aktif' : 'Nonaktif'}
              </button>
            </div>

            <button
              onClick={() => setShowDemoOptions(!showDemoOptions)}
              className="p-2 rounded-full bg-white/95 border border-[#E8DEC9] text-[#6B5559] hover:text-[#3B010B] transition-colors shadow-xs"
              title="Pengaturan Korpus Pengujian"
            >
              <Sliders className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Hidden Collapsible Options for Evaluation / Attack Simulation */}
      {showDemoOptions && (
        <div className="p-4 rounded-2xl bg-[#F2E5C6]/50 border border-[#F2D9A0] text-xs flex flex-col sm:flex-row items-center justify-between gap-3 font-montserrat shadow-xs">
          <span className="text-[#560B18] font-semibold">Korpus Pengujian (Knowledge Poisoning Test):</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                corpusScenario === 'kuhperdata_hir_bgem3'
                  ? 'bg-[#75162D] text-white shadow-xs'
                  : 'bg-white text-[#560B18] border border-[#E8DEC9]'
              }`}
            >
              Korpus Asli JDIH (Clean)
            </button>
            <button
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3_p1pct')}
              className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                corpusScenario === 'kuhperdata_hir_bgem3_p1pct'
                  ? 'bg-[#75162D] text-white shadow-xs'
                  : 'bg-white text-[#560B18] border border-[#E8DEC9]'
              }`}
            >
              Simulasi Serangan Racun (1% Poisoned)
            </button>
          </div>
        </div>
      )}

      {/* Conversation Thread */}
      <div className="min-h-[380px] flex flex-col gap-6 font-montserrat">
        {messages.length === 0 && (
          <div className="my-auto py-10 text-center flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] mb-4 shadow-xs">
              <Scale className="w-6 h-6" />
            </div>
            <h2 className="font-marcellus text-2xl md:text-3xl font-normal tracking-wide text-[#3B010B]">
              Mulai Penelusuran{' '}
              <span className="font-italiana text-[#75162D] normal-case text-3xl md:text-4xl">
                Ketentuan Hukum
              </span>
            </h2>
            <p className="text-xs sm:text-sm text-[#6B5559] max-w-md mt-2 leading-relaxed font-medium">
              Ajukan kronologi sengketa, syarat perjanjian, dasar ganti rugi wanprestasi/PMH, maupun tata cara sita jaminan dan alat bukti di persidangan.
            </p>

            {/* Suggested Question Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mt-8 w-full text-left">
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(q.query)}
                  className="p-4 rounded-2xl bg-white/95 hover:bg-white border border-[#E8DEC9] text-xs text-[#2A171A] transition-all shadow-xs hover:border-[#75162D] hover:shadow-md flex flex-col justify-between gap-2 group text-left"
                >
                  <div>
                    <span className="text-[10px] font-bold tracking-wider uppercase text-[#75162D]">
                      {q.tag}
                    </span>
                    <h4 className="font-bold text-[#3B010B] mt-0.5 group-hover:text-[#75162D] transition-colors">
                      {q.title}
                    </h4>
                    <p className="text-[11px] text-[#6B5559] mt-1 line-clamp-2 leading-relaxed">
                      {q.query}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-bold text-[#75162D] pt-2 border-t border-[#FAF6EE]">
                    <span>Ajukan Pertanyaan Ini</span>
                    <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </div>
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
            placeholder="Tanyakan persoalan hukum perdata (KUHPerdata & HIR dianalisis bersamaan)..."
            className="w-full px-5 py-2.5 text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none bg-transparent font-montserrat"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-burgundy-primary px-6 py-2.5 rounded-full disabled:opacity-40 shrink-0 ml-1 text-xs font-bold font-montserrat flex items-center gap-1.5 shadow-sm hover:scale-[1.02] transition-transform"
            title="Kirim Pertanyaan"
          >
            <span>Kirim</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Legal Disclaimer Pill */}
        <p className="text-[10px] text-center text-[#8C7A7C] mt-2 font-normal leading-relaxed font-montserrat">
          CiviLex AI menyajikan kutipan naskah otentik KUHPerdata &amp; HIR untuk tujuan edukasi dan asistensi penelitian hukum. Bukan merupakan nasihat atau konsultasi hukum berlisensi.
        </p>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-6 py-20 flex justify-center text-xs text-[#6B5559] font-montserrat">
          Memuat ruang konsultasi naskah...
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
