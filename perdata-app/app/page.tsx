'use client';

import Link from 'next/link';
import {
  Scale,
  ShieldCheck,
  BookOpen,
  BarChart3,
  ArrowRight,
  ShieldAlert,
  Zap,
  CheckCircle2,
  Lock,
  Cpu,
  FileCheck,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 pt-6 flex flex-col gap-16">
      {/* Hero Section */}
      <section className="text-center flex flex-col items-center gap-6 pt-8 pb-4">
        {/* Top Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-300">
            <Scale className="w-3.5 h-3.5 text-indigo-400" />
            <span>Tugas Akhir S1 Teknologi Informasi FTEIC ITS</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Two-Tier Poisoning Defense (SHA-256 + NLI)</span>
          </div>
        </div>

        {/* Big Heading */}
        <h1 className="font-legal-title text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-white max-w-3xl leading-[1.15]">
          Kecerdasan Hukum Perdata yang{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-blue-300 to-emerald-400">
            Terverifikasi Otentik
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg text-slate-300 max-w-2xl leading-relaxed">
          Sistem Tanya Jawab Cerdas (Legal QA) berbasis Retrieval-Augmented Generation (RAG) untuk{' '}
          <strong className="text-white">KUHPerdata &amp; HIR</strong>, dilengkapi perlindungan kriptografis terhadap serangan manipulasi informasi (Knowledge Poisoning).
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-2">
          <Link
            href="/chat"
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-semibold text-sm shadow-xl shadow-indigo-600/25 transition-all hover:scale-[1.02]"
          >
            <Scale className="w-4 h-4" />
            <span>Mulai Konsultasi Hukum</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>

          <Link
            href="/database"
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-sm transition-all hover:scale-[1.02]"
          >
            <BookOpen className="w-4 h-4 text-slate-400" />
            <span>Jelajah 2.276 Pasal</span>
          </Link>

          <Link
            href="/evaluasi"
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-sm transition-all hover:scale-[1.02]"
          >
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span>Data Evaluasi &amp; Metrik</span>
          </Link>
        </div>

        {/* System Trust Stats Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full mt-6">
          <div className="p-4 rounded-2xl glass-card text-center border-slate-800">
            <p className="text-2xl font-bold font-legal-title text-indigo-400">2.276</p>
            <p className="text-xs text-slate-400 mt-1">Pasal Resmi JDIH (KUHPerdata &amp; HIR)</p>
          </div>
          <div className="p-4 rounded-2xl glass-card text-center border-slate-800">
            <p className="text-2xl font-bold font-legal-title text-emerald-400">0.0%</p>
            <p className="text-xs text-slate-400 mt-1">Attack Success Rate (ASR) Terhadap Poisoning</p>
          </div>
          <div className="p-4 rounded-2xl glass-card text-center border-slate-800">
            <p className="text-2xl font-bold font-legal-title text-blue-400">0.8333</p>
            <p className="text-xs text-slate-400 mt-1">Dense BGE-M3 Recall@Budget (C1 Scenario)</p>
          </div>
          <div className="p-4 rounded-2xl glass-card text-center border-slate-800">
            <p className="text-2xl font-bold font-legal-title text-amber-400">1.0000</p>
            <p className="text-xs text-slate-400 mt-1">Precision &amp; Recall Deteksi Manipulasi</p>
          </div>
        </div>
      </section>

      {/* Core Innovations Section */}
      <section className="flex flex-col gap-8">
        <div className="text-center">
          <h2 className="font-legal-title text-2xl sm:text-3xl font-bold text-white">
            Inovasi &amp; Kontribusi Penelitian
          </h2>
          <p className="text-sm text-slate-400 mt-2 max-w-xl mx-auto">
            Dirancang dengan fondasi ilmiah yang kokoh untuk menjawab kelemahan sistem LQA konvensional terhadap halusinasi dan serangan injeksi korpus.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FileCheck className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">C1 Single-Article Granularity</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Memisahkan setiap pasal sebagai entitas retrieval mandiri. Menghasilkan <strong className="text-indigo-300">0.0% context noise</strong> dan memungkinkan verifikasi integritas hash SHA-256 secara deterministik per pasal.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3 border-emerald-500/20">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Two-Tier Poisoning Defense</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Kombinasi <strong className="text-emerald-300">Tier-1 Kriptografis</strong> (verifikasi SHA-256 terhadap naskah JDIH) dan <strong className="text-emerald-300">Tier-2 Semantik</strong> (NLI Contradiction Filter) untuk memblokir pasal beracun sebelum mencapai LLM.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Multi-LLM Generator &amp; Grounding</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Dukungan terhadap Google Gemini 2.5 Flash, DeepSeek-R1 (Local Ollama), dan Qwen2.5. Setiap jawaban disertai kutipan pasal resmi dan audit trail integritas.
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Demonstration Teaser */}
      <section className="glass-card rounded-3xl p-8 border border-indigo-500/20 bg-gradient-to-b from-indigo-950/20 to-slate-900/60 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col gap-2 max-w-xl">
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            <Zap className="w-4 h-4" /> Fitur Khusus Sidang Tugas Akhir
          </div>
          <h3 className="font-legal-title text-2xl font-bold text-white">
            Uji Langsung Mekanisme Pertahanan secara Real-Time
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Anda dapat mendemonstrasikan perbandingan performa RAG saat menghadapi korpus yang disusupi pasal palsu (<strong className="text-rose-400">Poisoned Corpus 1% / 5%</strong>) dengan saklar pertahanan aktif vs tidak aktif.
          </p>
        </div>

        <Link
          href="/chat"
          className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shrink-0 flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
        >
          <span>Buka Simulator Uji</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </section>
    </div>
  );
}
