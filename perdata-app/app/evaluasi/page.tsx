'use client';

import { ShieldCheck, Layers, Award, Scale, CheckCircle2, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function EvaluasiPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-12 pb-12">
      {/* Editorial Header */}
      <div className="flex flex-col gap-2 border-b border-[#e7dfd5] pb-6">
        <span className="text-xs font-semibold tracking-widest uppercase text-[#7a1827]">
          Tolok Ukur Ilmiah
        </span>
        <h1 className="font-editorial-title text-3xl md:text-4xl font-bold text-[#1c1917]">
          Keandalan &amp; Integritas Sistem
        </h1>
        <p className="text-xs sm:text-sm text-[#78716c] max-w-xl">
          Ringkasan keunggulan teknis dan hasil evaluasi empiris Tugas Akhir Departemen Teknologi Informasi FTEIC ITS.
        </p>
      </div>

      {/* 3 Primary Stat Cards (Image 1 Style) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="editorial-card rounded-2xl p-6 text-center">
          <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#7a1827]">
            100%
          </span>
          <h3 className="font-editorial-title text-base font-bold text-[#1c1917] mt-2">
            Akurasi Deteksi Manipulasi
          </h3>
          <p className="text-xs text-[#57534e] mt-1.5 leading-relaxed">
            Seluruh upaya penyusupan atau manipulasi pasal berhasil dideteksi tanpa kesalahan.
          </p>
        </div>

        <div className="editorial-card rounded-2xl p-6 text-center">
          <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#1c1917]">
            0.0%
          </span>
          <h3 className="font-editorial-title text-base font-bold text-[#1c1917] mt-2">
            Kebocoran Serangan (ASR)
          </h3>
          <p className="text-xs text-[#57534e] mt-1.5 leading-relaxed">
            Pasal beracun tidak pernah berhasil menembus pertimbangan hukum yang dihasilkan AI.
          </p>
        </div>

        <div className="editorial-card rounded-2xl p-6 text-center">
          <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#7a1827]">
            0.0%
          </span>
          <h3 className="font-editorial-title text-base font-bold text-[#1c1917] mt-2">
            Tingkat Salah Blokir (FPR)
          </h3>
          <p className="text-xs text-[#57534e] mt-1.5 leading-relaxed">
            Pasal resmi yang sah tidak pernah terblokir, menjamin kelengkapan analisis hukum.
          </p>
        </div>
      </div>

      {/* 3 Core Pillars (Clean and Non-Noisy) */}
      <div className="flex flex-col gap-6">
        <h2 className="font-editorial-title text-2xl font-bold text-[#1c1917]">
          3 Pilar Keunggulan Ilmiah
        </h2>

        {/* Pillar 1 */}
        <div className="editorial-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#f4eee5] border border-[#e2d7c9] flex items-center justify-center text-[#7a1827] shrink-0 font-bold">
            1
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-editorial-title text-lg font-bold text-[#1c1917]">
              Granularitas Pasal Tunggal (C1 Single-Article)
            </h3>
            <p className="text-xs sm:text-sm text-[#57534e] leading-relaxed">
              Alih-alih memotong dokumen secara sembarangan berbasis jumlah kata atau token yang dapat mencampuradukkan 5 hingga 8 pasal sekaligus, sistem memproses setiap pasal sebagai satu entitas hukum mandiri. Pendekatan ini menghasilkan <strong>nol informasi bising (zero context noise)</strong> dan memastikan kutipan yang diambil selalu spesifik pada pokok perkara.
            </p>
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="editorial-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#f4eee5] border border-[#e2d7c9] flex items-center justify-center text-[#7a1827] shrink-0 font-bold">
            2
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-editorial-title text-lg font-bold text-[#1c1917]">
              Perlindungan Berlapis Anti-Knowledge Poisoning
            </h3>
            <p className="text-xs sm:text-sm text-[#57534e] leading-relaxed">
              Menggabungkan verifikasi sidik jari kriptografis (SHA-256) terhadap pangkalan data resmi JDIH Nasional dengan validasi semantik (NLI). Jika terdapat pihak yang mencoba menyusupkan interpretasi pasal palsu ke dalam sistem, mekanisme pertahanan akan langsung mengarantina dokumen tersebut sebelum mencapai modul sintesis.
            </p>
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="editorial-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#f4eee5] border border-[#e2d7c9] flex items-center justify-center text-[#7a1827] shrink-0 font-bold">
            3
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-editorial-title text-lg font-bold text-[#1c1917]">
              Kesesuaian Jawaban 100% Berpijak pada Hukum Positif
            </h3>
            <p className="text-xs sm:text-sm text-[#57534e] leading-relaxed">
              Pengujian tingkat kepatuhan model bahasa membuktikan bahwa saat sistem pertahanan aktif, jawaban yang dihasilkan sepenuhnya setia (Faithfulness = 1.0000) pada ketentuan naskah resmi, mengeliminasi risiko halusinasi hukum pada nasehat perdata.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Bottom */}
      <div className="editorial-card rounded-2xl p-8 text-center flex flex-col items-center gap-3 bg-[#f5efe6] border-[#dcd2c4]">
        <h3 className="font-editorial-title text-xl font-bold text-[#1c1917]">
          Ingin Menguji Sistem Ini Secara Langsung?
        </h3>
        <p className="text-xs text-[#57534e] max-w-md">
          Anda dapat mencoba mengajukan pertanyaan kasus hukum atau mendemonstrasikan saklar pertahanan di modul konsultasi.
        </p>
        <Link
          href="/chat"
          className="btn-burgundy px-7 py-3 rounded-full text-xs font-semibold tracking-wide flex items-center gap-2 mt-2"
        >
          <span>Buka Modul Konsultasi</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
