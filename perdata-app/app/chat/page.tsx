'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Send,
  Scale,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Bot,
  User,
  Sparkles,
  RefreshCw,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
  FileText,
  SlidersHorizontal,
} from 'lucide-react';
import SecurityBadge, { DefenseStatusProps } from '../components/SecurityBadge';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  llmUsed?: string;
  defenseStatus?: DefenseStatusProps;
  retrievedPasals?: ArticleDoc[];
}

const SUGGESTED_QUERIES = [
  {
    title: 'Syarat Sah Perjanjian (Ps. 1320)',
    query: 'Apa saja 4 syarat sahnya suatu perjanjian menurut Pasal 1320 KUHPerdata dan konsekuensi hukumnya?',
  },
  {
    title: 'Perbuatan Melawan Hukum (Ps. 1365)',
    query: 'Jelaskan unsur-unsur Perbuatan Melawan Hukum (PMH) berdasarkan Pasal 1365 KUHPerdata beserta ganti ruginya!',
  },
  {
    title: 'Sita Jaminan HIR (Hukum Acara)',
    query: 'Bagaimana prosedur dan syarat permohonan sita jaminan (conservatoir beslag) menurut ketentuan HIR?',
  },
  {
    title: 'Pembatalan Akibat Wanprestasi (Ps. 1266)',
    query: 'Apakah pembatalan perjanjian akibat wanprestasi harus selalu dimintakan ke Pengadilan menurut Pasal 1266?',
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  // Settings
  const [selectedModel, setSelectedModel] = useState('gemini');
  const [selectedCollection, setSelectedCollection] = useState('kuhperdata_hir_bgem3');
  const [enableDefense, setEnableDefense] = useState(true);
  const [topK, setTopK] = useState(5);
  const [showSettings, setShowSettings] = useState(false);

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
    setActiveStep(1);

    try {
      // Step simulation for transparency
      setTimeout(() => setActiveStep(2), 700);
      setTimeout(() => setActiveStep(3), 1500);

      // Endpoint: backend FastAPI
      const res = await fetch('/api/py/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          collection: selectedCollection,
          enable_defense: enableDefense,
          llm_model: selectedModel,
          top_k: topK,
        }),
      });

      if (!res.ok) {
        // Fallback directly to localhost:8000 if rewrite is not active in dev
        const fallbackRes = await fetch('http://127.0.0.1:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: text,
            collection: selectedCollection,
            enable_defense: enableDefense,
            llm_model: selectedModel,
            top_k: topK,
          }),
        });

        if (!fallbackRes.ok) {
          throw new Error(`Server API Error: ${fallbackRes.statusText}`);
        }
        const data = await fallbackRes.json();
        handleServerSuccess(data);
        return;
      }

      const data = await res.json();
      handleServerSuccess(data);
    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Terjadi kendala saat menghubungi server backend (${err.message || 'Connection refused'}). Pastikan backend server.py berjalan di port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      setActiveStep(0);
    }
  };

  const handleServerSuccess = (data: any) => {
    const assistantMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: data.answer,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      llmUsed: data.llm_used,
      defenseStatus: data.defense_status,
      retrievedPasals: data.retrieved_pasals,
    };
    setMessages((prev) => [...prev, assistantMsg]);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col gap-6">
      {/* Top Controls / Experiment Settings Bar */}
      <div className="rounded-2xl glass-card p-4 border border-slate-700/60 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-white">Konsultasi Hukum Perdata &amp; Acara</h2>
              <p className="text-[11px] text-slate-400">
                KUHPerdata &amp; HIR • BAAI/bge-m3 • Two-Tier Defense
              </p>
            </div>
          </div>

          {/* Quick Defense Switch */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700/80">
              <span className="text-xs text-slate-300 font-medium">Pertahanan SHA-256 + NLI:</span>
              <button
                onClick={() => setEnableDefense(!enableDefense)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                  enableDefense
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                    : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                }`}
              >
                {enableDefense ? (
                  <>
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>AKTIF</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>NONAKTIF</span>
                  </>
                )}
              </button>
            </div>

            {/* Toggle Experiment Settings */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              title="Konfigurasi Model & Koleksi"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Collapsible Experiment Parameters Panel */}
        {showSettings && (
          <div className="mt-4 pt-4 border-t border-slate-700/60 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            {/* LLM Model */}
            <div className="flex flex-col gap-1.5">
              <label className="text-slate-400 font-medium flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                Generator LLM:
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="gemini">Google Gemini 2.5 Flash (Cloud)</option>
                <option value="deepseek-r1">DeepSeek-R1-8B (Ollama Local)</option>
                <option value="qwen">Qwen2.5-7B (Ollama Local)</option>
                <option value="deepseek-cloud">DeepSeek-V3 (Cloud API)</option>
              </select>
            </div>

            {/* Collection / Poison Scenario */}
            <div className="flex flex-col gap-1.5">
              <label className="text-slate-400 font-medium flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                Korpus Qdrant / Skenario Injeksi:
              </label>
              <select
                value={selectedCollection}
                onChange={(e) => setSelectedCollection(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="kuhperdata_hir_bgem3">Koleksi Bersih (Baseline JDIH)</option>
                <option value="kuhperdata_hir_bgem3_p1pct">Injeksi Manipulasi 1% (P-1%)</option>
                <option value="kuhperdata_hir_bgem3_p5pct">Injeksi Manipulasi 5% (P-5%)</option>
              </select>
            </div>

            {/* Top-K */}
            <div className="flex flex-col gap-1.5">
              <label className="text-slate-400 font-medium flex items-center justify-between">
                <span>Top-K Dokumen Ditarik:</span>
                <span className="font-mono text-indigo-400">{topK} pasal</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                className="w-full accent-indigo-500 mt-2"
              />
            </div>
          </div>
        )}
      </div>

      {/* Messages Feed Area */}
      <div className="min-h-[420px] flex flex-col gap-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center text-center my-auto py-12 px-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 shadow-xl shadow-indigo-950/40">
              <Scale className="w-7 h-7" />
            </div>
            <h3 className="font-legal-title text-xl font-bold text-white">
              Pusat Tanya Jawab Hukum Perdata Indonesia
            </h3>
            <p className="text-xs text-slate-400 max-w-md mt-1.5 leading-relaxed">
              Tanyakan ketentuan perdata material (KUHPerdata) maupun formil (HIR). Sistem akan mencari pasal rujukan resmi dan memverifikasi integritasnya sebelum menyusun jawaban.
            </p>

            {/* Suggested Question Chips */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl mt-8">
              {SUGGESTED_QUERIES.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSubmit(sq.query)}
                  className="p-3.5 rounded-xl glass-card text-left hover:border-indigo-500/40 transition-all text-xs group"
                >
                  <p className="font-semibold text-slate-200 group-hover:text-indigo-300">
                    {sq.title}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{sq.query}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Render Conversation List */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col gap-2 ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            {/* Author Label */}
            <div className="flex items-center gap-2 px-1 text-[11px] text-slate-400">
              {msg.role === 'user' ? (
                <>
                  <span>Pengguna</span>
                  <User className="w-3.5 h-3.5" />
                </>
              ) : (
                <>
                  <Bot className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="font-medium text-slate-300">LexPerdata AI</span>
                  {msg.llmUsed && (
                    <span className="px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px]">
                      {msg.llmUsed}
                    </span>
                  )}
                </>
              )}
              <span>•</span>
              <span>{msg.timestamp}</span>
            </div>

            {/* Bubble */}
            <div
              className={`rounded-2xl p-5 max-w-3xl leading-relaxed text-xs sm:text-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-lg shadow-indigo-600/15'
                  : 'glass-card border border-slate-700/60 text-slate-200 shadow-xl'
              }`}
            >
              {/* If Assistant, show Security Badge First */}
              {msg.defenseStatus && <SecurityBadge defense={msg.defenseStatus} />}

              {/* Main Content Body */}
              <div className="whitespace-pre-wrap leading-relaxed space-y-2">{msg.content}</div>

              {/* Retrieved Articles Shelf */}
              {msg.retrievedPasals && msg.retrievedPasals.length > 0 && (
                <div className="mt-6 pt-5 border-t border-slate-700/60 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-indigo-400" />
                      Pasal Rujukan Resmi ({msg.retrievedPasals.length} Divalidasi):
                    </p>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {msg.retrievedPasals.map((art, idx) => (
                      <PasalCard key={idx} article={art} index={idx} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading / Multi-step Reasoning Indicator */}
        {loading && (
          <div className="flex flex-col items-start gap-2 max-w-md">
            <div className="flex items-center gap-2 px-1 text-[11px] text-slate-400">
              <Bot className="w-3.5 h-3.5 text-indigo-400" />
              <span>LexPerdata AI sedang menganalisis kueri hukum...</span>
            </div>
            <div className="rounded-2xl glass-card p-4 border border-indigo-500/30 flex flex-col gap-2.5 w-full">
              <div className="flex items-center gap-2.5 text-xs">
                <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                <span className="font-semibold text-slate-200">
                  {activeStep === 1 && 'Menarik pasal relevan dengan BAAI/bge-m3...'}
                  {activeStep === 2 && 'Memeriksa integritas SHA-256 & filter semantik NLI...'}
                  {activeStep === 3 && 'Menyusun sintesis pertimbangan hukum...'}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${(activeStep / 3) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box Bar */}
      <div className="sticky bottom-4 z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(input);
          }}
          className="relative flex items-center shadow-2xl shadow-black/80 rounded-2xl glass-card border border-slate-700/80 focus-within:border-indigo-500/80 transition-all p-1.5"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(input);
              }
            }}
            placeholder="Ketik pertanyaan hukum perdata atau hukum acara (contoh: Pasal 1320, ganti rugi wanprestasi, sita jaminan)..."
            rows={1}
            className="w-full px-4 py-3 bg-transparent text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none max-h-32"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white transition-all shrink-0 ml-1"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-500 mt-2">
          LexPerdata AI menyajikan analisis hukum terverifikasi. Untuk keputusan yudisial resmi, selalu rujuk naskah putusan pengadilan &amp; JDIH.
        </p>
      </div>
    </div>
  );
}
