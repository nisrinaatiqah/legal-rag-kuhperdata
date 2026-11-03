'use client';

import {
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  Sparkles,
  BookOpen,
  Scale,
  Award,
} from 'lucide-react';

export default function EvaluasiPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col gap-10">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
          <BarChart3 className="w-4 h-4" /> Hasil Riset &amp; Verifikasi Empiris
        </div>
        <h1 className="font-legal-title text-3xl sm:text-4xl font-bold text-white">
          Dashboard Evaluasi &amp; Tolok Ukur Ilmiah
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-3xl leading-relaxed">
          Dokumentasi empiris dari 3 pilar kontribusi Tugas Akhir: Granularitas Chunking (C1 vs C2 vs C3), Model Retrieval (R1 vs R2 vs R3), dan Kerangka Pertahanan Two-Tier Knowledge Poisoning.
        </p>
      </div>

      {/* Section 1: Two-Tier Defense Metrics (Most Important!) */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h2 className="text-lg font-bold text-white">
            1. Kerangka Evaluasi Pertahanan Knowledge Poisoning (Two-Tier)
          </h2>
        </div>

        {/* Top 4 Security KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl glass-card border-emerald-500/30 bg-emerald-950/10">
            <p className="text-xs text-slate-400">Attack Success Rate (ASR)</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-emerald-400 font-mono">0.0%</span>
              <span className="text-xs line-through text-slate-500">83.3%</span>
            </div>
            <p className="text-[10px] text-emerald-400/80 mt-1">Dicegat 100% oleh defense</p>
          </div>

          <div className="p-4 rounded-2xl glass-card border-emerald-500/30 bg-emerald-950/10">
            <p className="text-xs text-slate-400">Misinformation Rate (MIR)</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-emerald-400 font-mono">0.0%</span>
              <span className="text-xs line-through text-slate-500">73.3%</span>
            </div>
            <p className="text-[10px] text-emerald-400/80 mt-1">Nol distorsi pada jawaban LLM</p>
          </div>

          <div className="p-4 rounded-2xl glass-card border-indigo-500/30 bg-indigo-950/10">
            <p className="text-xs text-slate-400">False Positive Rate (FPR)</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-indigo-400 font-mono">0.0%</span>
            </div>
            <p className="text-[10px] text-indigo-300 mt-1">Pasal sah tidak pernah terblokir</p>
          </div>

          <div className="p-4 rounded-2xl glass-card border-blue-500/30 bg-blue-950/10">
            <p className="text-xs text-slate-400">Delta Faithfulness (RAGAS)</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-blue-400 font-mono">+0.480</span>
            </div>
            <p className="text-[10px] text-blue-300 mt-1">1.0000 vs 0.5200 (tanpa defense)</p>
          </div>
        </div>

        {/* Tier 1 & Tier 2 Comparison Table */}
        <div className="glass-card rounded-2xl p-5 border border-slate-700/60 overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Tingkat Evaluasi</th>
                <th className="py-2.5 px-3">Metrik Ilmiah</th>
                <th className="py-2.5 px-3">Tanpa Pertahanan</th>
                <th className="py-2.5 px-3 text-emerald-400">Dengan Two-Tier Defense</th>
                <th className="py-2.5 px-3">Interpretasi Yudisial</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              <tr>
                <td className="py-3 px-3 font-semibold text-indigo-300" rowSpan={3}>
                  Tier 1: Evaluasi Detektor
                </td>
                <td className="py-3 px-3">Precision / Recall / F1</td>
                <td className="py-3 px-3 text-slate-500">N/A (Tidak Ada Filter)</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">1.0000 / 1.0000 / 1.0000</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">Seluruh korpus racun terdeteksi sempurna</td>
              </tr>
              <tr>
                <td className="py-3 px-3">False Positive Rate (FPR)</td>
                <td className="py-3 px-3 text-slate-500">N/A</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">0.0000 (0.0%)</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">Pasal otentik tidak pernah salah diblokir</td>
              </tr>
              <tr>
                <td className="py-3 px-3">Latency Overhead</td>
                <td className="py-3 px-3 text-slate-500">0.0 ms</td>
                <td className="py-3 px-3 font-mono text-slate-300">0.04 ms (SHA) + 85 ms (NLI)</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">Sangat ringan untuk interaksi real-time</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-blue-300" rowSpan={3}>
                  Tier 2: Keamanan Sistem RAG
                </td>
                <td className="py-3 px-3">Attack Success Rate (ASR)</td>
                <td className="py-3 px-3 text-rose-400 font-mono font-bold">83.33%</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">0.00%</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">Pasal manipulasi sukses dimentahkan total</td>
              </tr>
              <tr>
                <td className="py-3 px-3">Misinformation Injection (MIR)</td>
                <td className="py-3 px-3 text-rose-400 font-mono font-bold">73.33%</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">0.00%</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">LLM tidak pernah meracuni nasehat hukum</td>
              </tr>
              <tr>
                <td className="py-3 px-3">Generation Faithfulness</td>
                <td className="py-3 px-3 text-rose-400 font-mono">0.5200 (Drop Halusinasi)</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">1.0000 (Otentik)</td>
                <td className="py-3 px-3 text-slate-400 text-[11px]">Jawaban 100% berpijak pada hukum positif</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 2: Chunking Scenarios C1 vs C2 vs C3 */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <h2 className="text-lg font-bold text-white">
            2. Analisis Komparasi Granularitas Chunking (C1 vs C2 vs C3)
          </h2>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-700/60 overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Parameter / Metrik</th>
                <th className="py-2.5 px-3 text-indigo-400 font-bold">C1: Single Article (Usulan)</th>
                <th className="py-2.5 px-3">C2: Hierarchical / Section</th>
                <th className="py-2.5 px-3">C3: Token-based (512 tokens)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-300">Total Chunks Terbentuk</td>
                <td className="py-3 px-3 font-mono text-indigo-300 font-bold">2.276 chunks</td>
                <td className="py-3 px-3 font-mono text-slate-400">822 chunks</td>
                <td className="py-3 px-3 font-mono text-slate-400">411 chunks</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-300">Persentase Multi-Pasal</td>
                <td className="py-3 px-3 text-emerald-400 font-semibold">0.0% (Murni Mandiri)</td>
                <td className="py-3 px-3 text-amber-400">90.15% (Bercampur)</td>
                <td className="py-3 px-3 text-rose-400">97.32% (Sangat Campur)</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-300">Tingkat Context Noise</td>
                <td className="py-3 px-3 text-emerald-400 font-bold">0.0% (Zero Noise)</td>
                <td className="py-3 px-3 text-amber-400">56.4%</td>
                <td className="py-3 px-3 text-rose-400">81.4% (Noise Tinggi)</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-300">Dense BGE-M3 Recall@Budget (~500t)</td>
                <td className="py-3 px-3 text-emerald-400 font-mono font-bold">0.8333 (Unggul)</td>
                <td className="py-3 px-3 font-mono text-slate-400">0.6000</td>
                <td className="py-3 px-3 font-mono text-slate-400">0.5000</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-300">Dukungan Hash SHA-256 JDIH</td>
                <td className="py-3 px-3 text-emerald-400 font-bold">YA (1-to-1 Deterministic)</td>
                <td className="py-3 px-3 text-rose-400">TIDAK (Batas Arbitrer)</td>
                <td className="py-3 px-3 text-rose-400">TIDAK (Batas Potong Token)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 3: Retriever Comparison */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Scale className="w-4 h-4" />
          </div>
          <h2 className="text-lg font-bold text-white">
            3. Evaluasi Retriever (R1 Dense BGE-M3 vs R2 SimCSE vs R3 Hybrid)
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl glass-card border-indigo-500/30 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-sm">R1: Dense BGE-M3 (Terpilih)</span>
              <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-semibold">
                TERBAIK
              </span>
            </div>
            <div className="space-y-1.5 text-xs text-slate-300 mt-2 font-mono">
              <p>Recall@5: <strong className="text-emerald-400">0.8667</strong></p>
              <p>MRR@5: <strong className="text-emerald-400">0.8167</strong></p>
              <p>NDCG@5: <strong className="text-emerald-400">0.8351</strong></p>
            </div>
            <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
              Model multilingual 1024-dim yang sangat kuat dalam memahami doktrin hukum perdata dan padanan istilah serapan Belanda/Latin.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-card border-slate-700/60 flex flex-col gap-2">
            <span className="font-bold text-white text-sm">R3: Hybrid (BM25 + BGE-M3)</span>
            <div className="space-y-1.5 text-xs text-slate-300 mt-2 font-mono">
              <p>Recall@5: 0.8000</p>
              <p>MRR@5: 0.7444</p>
              <p>NDCG@5: 0.7672</p>
            </div>
            <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
              Kombinasi sparse BM25 mengalami degradasi karena kata serapan hukum (contoh: <em>wanprestasi, dwingend recht</em>) terdistorsi oleh stemmer leksikal.
            </p>
          </div>

          <div className="p-5 rounded-2xl glass-card border-slate-700/60 flex flex-col gap-2">
            <span className="font-bold text-white text-sm">R2: Dense SimCSE-Indo</span>
            <div className="space-y-1.5 text-xs text-slate-300 mt-2 font-mono">
              <p>Recall@5: 0.7000</p>
              <p>MRR@5: 0.6389</p>
              <p>NDCG@5: 0.6621</p>
            </div>
            <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
              Hanya dilatih pada korpus umum Wikipedia bahasa Indonesia sehingga kurang sensitif terhadap relasi hierarkis antar pasal perdata.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
