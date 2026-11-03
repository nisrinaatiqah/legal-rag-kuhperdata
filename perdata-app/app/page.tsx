'use client';

import Link from 'next/link';
import Image from 'next/image';
import { ArrowUpRight, ArrowDown, Scale, ShieldCheck, BookOpen, CheckCircle } from 'lucide-react';

const COMPETENCES = [
  {
    num: '01',
    title: 'Hukum Perikatan & Perjanjian',
    desc: 'Membedah syarat sahnya perjanjian (Pasal 1320), wanprestasi, akibat kelalaian debitur, hingga pembatalan sepihak.',
    badge: 'Buku III KUHPerdata',
  },
  {
    num: '02',
    title: 'Perbuatan Melawan Hukum (PMH)',
    desc: 'Menganalisis unsur kesalahan, kerugian materiel-imateriel, dan hubungan kausalitas berdasarkan Pasal 1365.',
    badge: 'Pasal 1365 KUHPerdata',
  },
  {
    num: '03',
    title: 'Hukum Kebendaan & Kewarisan',
    desc: 'Ketentuan kepemilikan hak kebendaan, hak tanggungan, pembagian harta peninggalan, dan perlindungan ahli waris.',
    badge: 'Buku II KUHPerdata',
  },
  {
    num: '04',
    title: 'Hukum Acara Perdata (HIR)',
    desc: 'Pedoman beracara di persidangan: tata cara pengajuan gugatan, sita jaminan (conservatoir beslag), dan kekuatan alat bukti.',
    badge: 'Reglemen Indonesia (HIR)',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col gap-24 pb-12">
      {/* Hero Section */}
      <section className="relative max-w-6xl mx-auto px-6 pt-6 flex flex-col items-center text-center">
        {/* Subtle Watermark Behind Hero */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[140px] md:text-[220px] font-editorial-display font-bold text-[#e8dfd2]/35 select-none pointer-events-none -z-10 tracking-widest">
          JUSTITIA
        </div>

        {/* Small Elegant Header Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#dcd2c4] bg-[#f5efe6] text-xs font-medium text-[#7a1827] mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-[#7a1827]"></span>
          <span>Sistem Tanya Jawab Hukum Perdata Indonesia</span>
        </div>

        {/* Big Editorial Headline */}
        <h1 className="font-editorial-title text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-[#1c1917] max-w-4xl leading-[1.12]">
          MITRA HUKUM ANDA DALAM SETIAP SITUASI
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg text-[#57534e] max-w-2xl mt-5 font-normal leading-relaxed">
          Memberikan solusi dan analisis hukum perdata yang presisi melalui kecerdasan buatan, dengan jaminan integritas naskah resmi dari KUHPerdata dan HIR.
        </p>

        {/* Call to Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
          <Link
            href="/chat"
            className="btn-burgundy px-8 py-3.5 rounded-full text-sm font-semibold tracking-wide flex items-center gap-2 shadow-lg shadow-[#7a1827]/15"
          >
            <span>Mulai Konsultasi</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>

          <Link
            href="/database"
            className="px-7 py-3.5 rounded-full text-sm font-semibold tracking-wide text-[#1c1917] bg-white border border-[#dcd2c4] hover:bg-[#f5efe6] transition-all flex items-center gap-2 shadow-sm"
          >
            <span>Katalog 2.276 Pasal</span>
            <ArrowUpRight className="w-4 h-4 text-[#78716c]" />
          </Link>
        </div>

        {/* Lady Justice Hero Illustration (Reference Image Style) */}
        <div className="relative mt-12 w-full max-w-lg mx-auto flex items-center justify-center">
          <div className="relative w-full max-w-sm aspect-[4/3] rounded-2xl overflow-hidden shadow-xl border border-[#e2d7c9] bg-[#f3ede3]">
            <img
              src="/lady-justice.png"
              alt="Lady Justice — Simbol Keadilan Hukum Perdata"
              className="w-full h-full object-cover object-center filter contrast-105"
            />
          </div>
        </div>

        {/* Editorial Quote Block (Image 1 Style) */}
        <div className="mt-16 max-w-2xl border-t border-[#e7dfd5] pt-8">
          <p className="font-editorial-title text-xl md:text-2xl text-[#1c1917] leading-snug">
            &ldquo;Hukum perdata ditegakkan atas kepastian janji, kesucian perikatan, dan keadilan pembuktian.&rdquo;
          </p>
          <p className="text-xs text-[#8a847c] mt-2 uppercase tracking-widest font-medium">
            Prinsip Fundamental KUHPerdata &amp; HIR
          </p>
        </div>

        {/* 4 Clean Metric Counters (Image 1 & Image 5 Style) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 w-full max-w-4xl mt-12 pt-8 border-t border-[#e7dfd5]">
          <div className="flex flex-col items-center">
            <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#7a1827]">2.276</span>
            <span className="text-xs text-[#57534e] mt-1 font-medium">Pasal Resmi Terkodifikasi</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#1c1917]">100%</span>
            <span className="text-xs text-[#57534e] mt-1 font-medium">Otentisitas Naskah JDIH</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#7a1827]">0%</span>
            <span className="text-xs text-[#57534e] mt-1 font-medium">Toleransi Manipulasi</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-editorial-display text-4xl md:text-5xl font-bold text-[#1c1917]">2 Kitab</span>
            <span className="text-xs text-[#57534e] mt-1 font-medium">KUHPerdata &amp; HIR</span>
          </div>
        </div>
      </section>

      {/* Competences / Bidang Hukum Section (Image 3 Style) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4 border-b border-[#e7dfd5] pb-6">
          <div>
            <span className="text-xs font-semibold tracking-widest uppercase text-[#7a1827]">
              Ruang Lingkup Kajian
            </span>
            <h2 className="font-editorial-title text-3xl md:text-4xl font-bold text-[#1c1917] mt-1">
              Bidang Pokok Hukum Perdata
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-[#78716c] max-w-md">
            Dirancang khusus untuk menganalisis sengketa perdata material dan memandu langkah prosedural hukum formil di pengadilan.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {COMPETENCES.map((comp) => (
            <div
              key={comp.num}
              className="editorial-card editorial-card-hover rounded-2xl p-6 flex flex-col justify-between min-h-[220px]"
            >
              <div>
                <span className="font-editorial-display text-2xl font-bold text-[#7a1827]">
                  {comp.num}
                </span>
                <h3 className="font-editorial-title text-base font-bold text-[#1c1917] mt-2 leading-snug">
                  {comp.title}
                </h3>
                <p className="text-xs text-[#57534e] mt-2.5 leading-relaxed">
                  {comp.desc}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-[#f0ebe1] flex items-center justify-between">
                <span className="text-[11px] font-medium text-[#8a847c]">{comp.badge}</span>
                <Link
                  href="/chat"
                  className="text-xs font-semibold text-[#7a1827] hover:underline flex items-center gap-1"
                >
                  <span>Tanya</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Trust & Guarantee Banner */}
      <section className="max-w-5xl mx-auto px-6 w-full">
        <div className="rounded-3xl bg-[#f4eee5] border border-[#e2d7c9] p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex flex-col gap-2 max-w-lg">
            <span className="text-xs font-bold uppercase tracking-wider text-[#7a1827]">
              Jaminan Integritas Informasi
            </span>
            <h3 className="font-editorial-title text-2xl md:text-3xl font-bold text-[#1c1917]">
              Setiap Jawaban Berpijak pada Naskah Asli Terverifikasi
            </h3>
            <p className="text-xs sm:text-sm text-[#57534e] leading-relaxed mt-1">
              Sistem secara otomatis memverifikasi keaslian pasal sebelum merumuskan jawaban, memastikan pengguna terhindar dari informasi palsu atau manipulasi pasal hukum.
            </p>
          </div>

          <Link
            href="/chat"
            className="btn-burgundy px-8 py-3.5 rounded-full text-sm font-semibold tracking-wide shrink-0 flex items-center gap-2 shadow-lg"
          >
            <span>Mulai Konsultasi Sekarang</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
