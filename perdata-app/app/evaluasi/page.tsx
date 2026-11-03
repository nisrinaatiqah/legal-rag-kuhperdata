'use client';

import { ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function EvaluasiPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-12 pb-12 font-body">
      {/* Editorial Header in Cinzel & Cormorant */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-cinzel">
          Tolok Ukur Ilmiah
        </span>
        <h1 className="font-cinzel text-2xl md:text-3xl font-bold tracking-wider text-[#3B010B]">
          Keandalan &amp;{' '}
          <span className="font-cormorant italic font-normal text-[#75162D] text-3xl md:text-4xl normal-case">
            Integritas Sistem
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-xl">
          Ringkasan keunggulan teknis dan hasil evaluasi empiris Tugas Akhir Departemen Teknologi Informasi FTEIC ITS.
        </p>
      </div>

      {/* 3 Primary Stat Cards in Cinzel & Swatch Colors */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="law-card rounded-2xl p-6 text-center">
          <span className="font-cinzel text-4xl md:text-5xl font-bold text-[#75162D]">
            100%
          </span>
          <h3 className="font-cinzel text-sm font-bold tracking-wide text-[#3B010B] mt-2">
            Akurasi Deteksi Manipulasi
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-body">
            Seluruh upaya penyusupan atau manipulasi pasal berhasil dideteksi tanpa kesalahan.
          </p>
        </div>

        <div className="law-card rounded-2xl p-6 text-center">
          <span className="font-cinzel text-4xl md:text-5xl font-bold text-[#3B010B]">
            0.0%
          </span>
          <h3 className="font-cinzel text-sm font-bold tracking-wide text-[#3B010B] mt-2">
            Kebocoran Serangan (ASR)
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-body">
            Pasal beracun tidak pernah berhasil menembus pertimbangan hukum yang dihasilkan AI.
          </p>
        </div>

        <div className="law-card rounded-2xl p-6 text-center">
          <span className="font-cinzel text-4xl md:text-5xl font-bold text-[#75162D]">
            0.0%
          </span>
          <h3 className="font-cinzel text-sm font-bold tracking-wide text-[#3B010B] mt-2">
            Tingkat Salah Blokir (FPR)
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-body">
            Pasal resmi yang sah tidak pernah terblokir, menjamin kelengkapan analisis hukum.
          </p>
        </div>
      </div>

      {/* 3 Core Pillars */}
      <div className="flex flex-col gap-6">
        <h2 className="font-cinzel text-xl md:text-2xl font-bold tracking-wide text-[#3B010B]">
          3 Pilar{' '}
          <span className="font-cormorant italic font-normal text-[#75162D] text-2xl md:text-3xl normal-case">
            Keunggulan Ilmiah
          </span>
        </h2>

        {/* Pillar 1 */}
        <div className="law-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-cinzel text-sm">
            I
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-cinzel text-base font-bold tracking-wide text-[#3B010B]">
              Granularitas Pasal Tunggal (C1 Single-Article)
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-body">
              Alih-alih memotong dokumen secara sembarangan berbasis jumlah kata atau token yang dapat mencampuradukkan 5 hingga 8 pasal sekaligus, sistem memproses setiap pasal sebagai satu entitas hukum mandiri. Pendekatan ini menghasilkan <strong>nol informasi bising (zero context noise)</strong> dan memastikan kutipan yang diambil selalu spesifik pada pokok perkara.
            </p>
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="law-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-cinzel text-sm">
            II
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-cinzel text-base font-bold tracking-wide text-[#3B010B]">
              Perlindungan Berlapis Anti-Knowledge Poisoning
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-body">
              Menggabungkan verifikasi sidik jari kriptografis (SHA-256) terhadap pangkalan data resmi JDIH Nasional dengan validasi semantik (NLI). Jika terdapat pihak yang mencoba menyusupkan interpretasi pasal palsu ke dalam sistem, mekanisme pertahanan akan langsung mengarantina dokumen tersebut sebelum mencapai modul sintesis.
            </p>
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="law-card rounded-2xl p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-full bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-cinzel text-sm">
            III
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-cinzel text-base font-bold tracking-wide text-[#3B010B]">
              Kesesuaian Jawaban 100% Berpijak pada Hukum Positif
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-body">
              Pengujian tingkat kepatuhan model bahasa membuktikan bahwa saat sistem pertahanan aktif, jawaban yang dihasilkan sepenuhnya setia (Faithfulness = 1.0000) pada ketentuan naskah resmi, mengeliminasi risiko halusinasi hukum pada nasehat perdata.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Bottom in Sand Gold & Burgundy */}
      <div className="rounded-3xl bg-gradient-to-br from-[#F2E5C6] to-[#F2D9A0]/70 border border-[#F2D9A0] p-8 text-center flex flex-col items-center gap-3">
        <h3 className="font-cinzel text-xl md:text-2xl font-bold tracking-wider text-[#3B010B]">
          Ingin Menguji Sistem Ini Secara Langsung?
        </h3>
        <p className="text-xs sm:text-sm text-[#560B18] max-w-md font-body">
          Anda dapat mencoba mengajukan pertanyaan kasus hukum atau mendemonstrasikan saklar pertahanan di modul konsultasi.
        </p>
        <Link
          href="/chat"
          className="btn-burgundy-primary px-7 py-3 rounded-full text-xs font-semibold tracking-wider uppercase font-cinzel flex items-center gap-2 mt-2"
        >
          <span>Buka Modul Konsultasi</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
