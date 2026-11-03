'use client';

import { ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function EvaluasiPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 flex flex-col gap-12 pb-12 font-body">
      {/* Editorial Header in DM Serif Display & DM Sans */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-semibold tracking-widest uppercase text-[#75162D] font-sans">
          Standar Transparansi
        </span>
        <h1 className="font-serif text-2xl md:text-3xl font-normal tracking-tight text-[#3B010B]">
          Keandalan &amp;{' '}
          <span className="italic text-[#75162D] text-3xl md:text-4xl">
            Integritas Sistem
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-xl font-sans">
          Standar pengujian independen untuk memastikan setiap rujukan hukum yang disajikan otentik, akurat, dan terlindungi dari manipulasi data.
        </p>
      </div>

      {/* 3 Primary Stat Cards in DM Serif Display & Swatch Colors */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="law-card rounded-sm p-6 text-center">
          <span className="font-serif text-4xl md:text-5xl font-bold text-[#75162D]">
            100%
          </span>
          <h3 className="font-serif text-sm font-bold tracking-tight text-[#3B010B] mt-2">
            Akurasi Deteksi Manipulasi
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-sans">
            Seluruh upaya penyusupan atau manipulasi pasal berhasil dideteksi tanpa kesalahan.
          </p>
        </div>

        <div className="law-card rounded-sm p-6 text-center">
          <span className="font-serif text-4xl md:text-5xl font-bold text-[#3B010B]">
            0.0%
          </span>
          <h3 className="font-serif text-sm font-bold tracking-tight text-[#3B010B] mt-2">
            Kebocoran Serangan (ASR)
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-sans">
            Pasal beracun tidak pernah berhasil menembus hasil penelusuran yang disajikan AI.
          </p>
        </div>

        <div className="law-card rounded-sm p-6 text-center">
          <span className="font-serif text-4xl md:text-5xl font-bold text-[#75162D]">
            0.0%
          </span>
          <h3 className="font-serif text-sm font-bold tracking-tight text-[#3B010B] mt-2">
            Tingkat Salah Blokir (FPR)
          </h3>
          <p className="text-xs text-[#6B5559] mt-1.5 leading-relaxed font-sans">
            Pasal resmi yang sah tidak pernah terblokir, menjamin kelengkapan analisis hukum.
          </p>
        </div>
      </div>

      {/* 3 Core Pillars */}
      <div className="flex flex-col gap-6">
        <h2 className="font-serif text-xl md:text-2xl font-normal tracking-tight text-[#3B010B]">
          3 Pilar{' '}
          <span className="italic text-[#75162D] text-2xl md:text-3xl">
            Integritas Informasi
          </span>
        </h2>

        {/* Pillar 1 */}
        <div className="law-card rounded-sm p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-sm bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-serif text-sm">
            I
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-serif text-base font-bold tracking-tight text-[#3B010B]">
              Granularitas Pasal Mandiri
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-sans">
              Sistem memproses setiap ketentuan pasal sebagai satu entitas hukum utuh dan mandiri. Pendekatan ini menghasilkan <strong>nol informasi bising (zero context noise)</strong> dan memastikan kutipan yang diambil selalu spesifik pada pokok perkara.
            </p>
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="law-card rounded-sm p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-sm bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-serif text-sm">
            II
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-serif text-base font-bold tracking-tight text-[#3B010B]">
              Verifikasi Integritas Berlapis
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-sans">
              Menggabungkan verifikasi sidik jari kriptografis terhadap pangkalan data resmi JDIH Nasional dengan validasi semantik. Jika terdapat naskah yang dimanipulasi, mekanisme pertahanan akan langsung mengarantina dokumen tersebut sebelum mencapai modul penelusuran.
            </p>
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="law-card rounded-sm p-6 flex flex-col md:flex-row items-start gap-5">
          <div className="w-10 h-10 rounded-sm bg-[#F2E5C6] border border-[#F2D9A0] flex items-center justify-center text-[#75162D] shrink-0 font-bold font-serif text-sm">
            III
          </div>
          <div className="flex flex-col gap-1.5">
            <h3 className="font-serif text-base font-bold tracking-tight text-[#3B010B]">
              Kepatuhan 100% pada Hukum Positif
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed font-sans">
              Jawaban yang dirumuskan sepenuhnya berpijak pada ketentuan naskah resmi KUHPerdata dan HIR, mengeliminasi risiko halusinasi informasi hukum.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Bottom in Sand Gold & Burgundy */}
      <div className="rounded-sm bg-gradient-to-br from-[#F2E5C6] to-[#F2D9A0]/70 border border-[#F2D9A0] p-8 text-center flex flex-col items-center gap-3">
        <h3 className="font-serif text-xl md:text-2xl font-normal tracking-tight text-[#3B010B]">
          Mulai Eksplorasi Informasi Hukum
        </h3>
        <p className="text-xs sm:text-sm text-[#560B18] max-w-md font-sans">
          Ajukan pertanyaan pasal hukum perdata material maupun formil dan temukan rujukan pasal terverifikasi berbasis naskah resmi JDIH.
        </p>
        <Link
          href="/chat"
          className="btn-burgundy-primary px-7 py-3 rounded-sm text-xs font-semibold tracking-wider uppercase font-sans flex items-center gap-2 mt-2"
        >
          <span>Buka Modul Tanya Jawab</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
