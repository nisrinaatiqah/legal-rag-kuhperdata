'use client';

import { useState, useRef, useEffect } from 'react';
import {
  ArrowUpRight,
  Scale,
  ShieldCheck,
  ShieldAlert,
  Bot,
  User,
  RefreshCw,
  FileText,
  Sliders,
  AlertCircle,
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
}

const SUGGESTED_QUERIES = [
  'Apa 4 syarat sahnya perjanjian menurut Pasal 1320 KUHPerdata?',
  'Bagaimana unsur Perbuatan Melawan Hukum (PMH) Pasal 1365 KUHPerdata?',
  'Bagaimana prosedur sita jaminan (conservatoir beslag) menurut HIR?',
  'Apakah pembatalan perjanjian akibat wanprestasi harus melalui Pengadilan?',
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Clean, essential controls only
  const [enableDefense, setEnableDefense] = useState(true);
  const [corpusScenario, setCorpusScenario] = useState('kuhperdata_hir_bgem3');
  const [showDemoOptions, setShowDemoOptions] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (queryText: string) => {
    const text = queryText.trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/py/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          collection: corpusScenario,
          enable_defense: enableDefense,
          llm_model: 'gemini',
          top_k: 5,
        }),
      });

      if (!res.ok) {
        const fallbackRes = await fetch('http://127.0.0.1:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: text,
            collection: corpusScenario,
            enable_defense: enableDefense,
            llm_model: 'gemini',
            top_k: 5,
          }),
        });

        if (!fallbackRes.ok) {
          throw new Error('Gagal menghubungi backend');
        }
        const data = await fallbackRes.json();
        handleServerSuccess(data);
        return;
      }

      const data = await res.json();
      handleServerSuccess(data);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          'Mohon maaf, terjadi kendala koneksi dengan server backend. Pastikan server.py telah berjalan di latar belakang.',
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
    };
    setMessages((prev) => [...prev, assistantMsg]);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-8 pb-12 font-body">
      {/* Editorial Page Header in Cinzel & Cormorant */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#E8DEC9] pb-6">
        <div>
          <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-cinzel">
            Asistensi Penelusuran Naskah
          </span>
          <h1 className="font-cinzel text-2xl md:text-3xl font-bold tracking-wider text-[#3B010B] mt-1">
            Tanya Jawab{' '}
            <span className="font-cormorant italic font-normal text-[#75162D] text-3xl md:text-4xl normal-case">
              KUHPerdata &amp; HIR
            </span>
          </h1>
        </div>

        {/* Essential Defense Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-white border border-[#E8DEC9] shadow-sm text-xs font-medium text-[#2A171A]">
            <span>Proteksi Naskah Asli:</span>
            <button
              onClick={() => setEnableDefense(!enableDefense)}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                enableDefense
                  ? 'bg-[#15803d] text-white shadow-sm'
                  : 'bg-[#75162D] text-[#F2E5C6]'
              }`}
            >
              {enableDefense ? 'Aktif' : 'Nonaktif'}
            </button>
          </div>

          <button
            onClick={() => setShowDemoOptions(!showDemoOptions)}
            className="p-2 rounded-full bg-white border border-[#E8DEC9] text-[#6B5559] hover:text-[#3B010B] transition-colors"
            title="Mode Basis Data"
          >
            <Sliders className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Hidden Collapsible Options */}
      {showDemoOptions && (
        <div className="p-4 rounded-2xl bg-[#F2E5C6]/50 border border-[#F2D9A0] text-xs flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="text-[#560B18] font-semibold">Mode Pangkalan Data:</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3')}
              className={`px-3 py-1.5 rounded-full font-medium ${
                corpusScenario === 'kuhperdata_hir_bgem3'
                  ? 'bg-[#75162D] text-white'
                  : 'bg-white text-[#560B18] border border-[#E8DEC9]'
              }`}
            >
              Standar Resmi JDIH
            </button>
            <button
              onClick={() => setCorpusScenario('kuhperdata_hir_bgem3_p1pct')}
              className={`px-3 py-1.5 rounded-full font-medium ${
                corpusScenario === 'kuhperdata_hir_bgem3_p1pct'
                  ? 'bg-[#75162D] text-white'
                  : 'bg-white text-[#560B18] border border-[#E8DEC9]'
              }`}
            >
              Simulasi Uji Integritas (1%)
            </button>
          </div>
        </div>
      )}

      {/* Conversation Thread */}
      <div className="min-h-[380px] flex flex-col gap-6">
        {messages.length === 0 && (
          <div className="my-auto py-12 text-center flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] mb-4">
              <Scale className="w-6 h-6" />
            </div>
            <h2 className="font-cinzel text-xl md:text-2xl font-bold tracking-wider text-[#3B010B]">
              Mulai Penelusuran{' '}
              <span className="font-cormorant italic font-normal text-[#75162D] text-2xl md:text-3xl normal-case">
                Ketentuan Hukum
              </span>
            </h2>
            <p className="text-xs sm:text-sm text-[#6B5559] max-w-md mt-1.5 leading-relaxed">
              Ajukan pertanyaan mengenai bunyi pasal perjanjian, ketentuan wanprestasi, pasal perbuatan melawan hukum, maupun aturan beracara di persidangan.
            </p>

            {/* Clean Suggested Question Pills */}
            <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-2.5 max-w-2xl mt-8">
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(q)}
                  className="px-4 py-2.5 rounded-full bg-white hover:bg-[#F2E5C6]/60 border border-[#E8DEC9] text-xs font-medium text-[#2A171A] transition-all text-left shadow-sm hover:border-[#F2D9A0]"
                >
                  {q}
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
            <span className="text-[11px] text-[#6B5559] px-1 font-medium">
              {msg.role === 'user' ? 'Pertanyaan Anda' : 'Hasil Penelusuran Civil AI'} • {msg.timestamp}
            </span>

            <div
              className={`rounded-2xl p-6 leading-relaxed max-w-2xl ${
                msg.role === 'user'
                  ? 'bg-[#3B010B] text-[#FAF6EE] shadow-md'
                  : 'law-card text-[#2A171A]'
              }`}
            >
              {/* Security Badge */}
              {msg.defenseStatus && <SecurityBadge defense={msg.defenseStatus} />}

              {/* Main Text Answer */}
              <div className="whitespace-pre-wrap text-xs sm:text-sm leading-relaxed space-y-2.5">
                {msg.content}
              </div>

              {/* Cited Articles Shelf */}
              {msg.retrievedPasals && msg.retrievedPasals.length > 0 && (
                <div className="mt-6 pt-5 border-t border-[#E8DEC9] flex flex-col gap-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-[#75162D] flex items-center gap-1.5 font-cinzel">
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
              Sedang menelaah pasal rujukan resmi...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Question Input Bar */}
      <div className="sticky bottom-6 z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(input);
          }}
          className="relative flex items-center rounded-full bg-white border border-[#E8DEC9] shadow-xl shadow-black/5 p-1.5 focus-within:border-[#75162D] transition-all"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tuliskan pertanyaan pasal perdata atau hukum acara..."
            className="w-full px-5 py-3 text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none bg-transparent"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-burgundy-primary p-3 rounded-full disabled:opacity-40 shrink-0 ml-1"
            title="Kirim Pertanyaan"
          >
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </form>

        {/* Explicit Legal Disclaimer */}
        <p className="text-[10px] text-center text-[#8C7A7C] mt-2 font-normal leading-relaxed">
          Civil.AI menyajikan kutipan naskah resmi KUHPerdata &amp; HIR untuk tujuan edukasi dan referensi hukum. Sistem ini bukan nasihat hukum atau pengganti konsultasi profesional dengan advokat berlisensi.
        </p>
      </div>
    </div>
  );
}
