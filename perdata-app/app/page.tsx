'use client';

import Link from 'next/link';
import { ArrowUpRight, Scale, ShieldCheck, BookOpen, CheckCircle } from 'lucide-react';

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
    desc: 'Menganalisis unsur kesalahan, kerugian materiel-imateriel, dan hubungan kausalitas ganti rugi Pasal 1365.',
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
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[140px] md:text-[220px] font-display font-bold text-[#F2E5C6]/50 select-none pointer-events-none -z-10 tracking-widest">
          JUSTITIA
        </div>

        {/* Small Elegant Header Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#F2D9A0] bg-[#F2E5C6]/60 text-xs font-semibold text-[#560B18] mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-[#75162D]"></span>
          <span>Sistem Tanya Jawab Hukum Perdata Indonesia</span>
        </div>

        {/* Big Editorial Headline in Playfair Display */}
        <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-[#3B010B] max-w-4xl leading-[1.12]">
          MITRA HUKUM ANDA DALAM <span className="italic font-normal text-[#75162D]">SETIAP SITUASI</span>
        </h1>

        {/* Subtitle in Plus Jakarta Sans */}
        <p className="text-base sm:text-lg text-[#6B5559] max-w-2xl mt-5 font-normal leading-relaxed">
          Memberikan solusi dan analisis hukum perdata yang presisi melalui kecerdasan buatan, dengan jaminan integritas naskah resmi dari KUHPerdata dan HIR.
        </p>

        {/* Call to Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-full text-sm font-semibold tracking-wide flex items-center gap-2"
          >
            <span>Mulai Konsultasi</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>

          <Link
            href="/database"
            className="btn-champagne-outline px-7 py-3.5 rounded-full text-sm font-semibold tracking-wide flex items-center gap-2 shadow-sm"
          >
            <span>Katalog 2.276 Pasal</span>
            <ArrowUpRight className="w-4 h-4 text-[#75162D]" />
          </Link>
        </div>

        {/* Lady Justice Hero Illustration */}
        <div className="relative mt-12 w-full max-w-lg mx-auto flex items-center justify-center">
          <div className="relative w-full max-w-sm aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl border-2 border-[#F2D9A0] bg-[#FAF6EE]">
            <img
              src="/lady-justice.png"
              alt="Lady Justice — Simbol Keadilan Hukum Perdata"
              className="w-full h-full object-cover object-center filter contrast-105"
            />
          </div>
        </div>

        {/* Editorial Quote Block in Playfair Italic */}
        <div className="mt-16 max-w-2xl border-t border-[#E8DEC9] pt-8">
          <p className="font-display italic text-2xl md:text-3xl text-[#3B010B] leading-snug">
            &ldquo;Hukum perdata ditegakkan atas kepastian janji, kesucian perikatan, dan keadilan pembuktian.&rdquo;
          </p>
          <p className="text-xs text-[#6B5559] mt-3 uppercase tracking-widest font-semibold font-body">
            Prinsip Fundamental KUHPerdata &amp; HIR
          </p>
        </div>

        {/* 4 Clean Metric Counters in Playfair Display & Swatch Colors */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 w-full max-w-4xl mt-12 pt-8 border-t border-[#E8DEC9]">
          <div className="flex flex-col items-center">
            <span className="font-display text-4xl md:text-5xl font-bold text-[#75162D]">2.276</span>
            <span className="text-xs text-[#6B5559] mt-1 font-medium font-body">Pasal Terkodifikasi</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-display text-4xl md:text-5xl font-bold text-[#3B010B]">100%</span>
            <span className="text-xs text-[#6B5559] mt-1 font-medium font-body">Otentisitas Naskah JDIH</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-display text-4xl md:text-5xl font-bold text-[#75162D]">0%</span>
            <span className="text-xs text-[#6B5559] mt-1 font-medium font-body">Toleransi Manipulasi</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="font-display text-4xl md:text-5xl font-bold text-[#3B010B]">2 Kitab</span>
            <span className="text-xs text-[#6B5559] mt-1 font-medium font-body">KUHPerdata &amp; HIR</span>
          </div>
        </div>
      </section>

      {/* Competences / Bidang Hukum Section */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4 border-b border-[#E8DEC9] pb-6">
          <div>
            <span className="text-xs font-semibold tracking-widest uppercase text-[#75162D] font-body">
              Ruang Lingkup Kajian
            </span>
            <h2 className="font-display text-3xl md:text-4xl font-bold text-[#3B010B] mt-1">
              Bidang Pokok <span className="italic font-normal text-[#75162D]">Hukum Perdata</span>
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-[#6B5559] max-w-md font-body leading-relaxed">
            Dirancang khusus untuk menganalisis sengketa perdata material dan memandu langkah prosedural hukum formil di pengadilan.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {COMPETENCES.map((comp) => (
            <div
              key={comp.num}
              className="law-card law-card-hover rounded-2xl p-6 flex flex-col justify-between min-h-[220px]"
            >
              <div>
                <span className="font-display text-2xl font-bold text-[#75162D]">
                  {comp.num}
                </span>
                <h3 className="font-display text-lg font-bold text-[#3B010B] mt-2 leading-snug">
                  {comp.title}
                </h3>
                <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-body">
                  {comp.desc}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-[#FAF6EE] flex items-center justify-between font-body">
                <span className="text-[11px] font-medium text-[#6B5559]">{comp.badge}</span>
                <Link
                  href="/chat"
                  className="text-xs font-semibold text-[#75162D] hover:underline flex items-center gap-1"
                >
                  <span>Tanya</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Trust & Guarantee Banner in Sand Gold & Dark Maroon */}
      <section className="max-w-5xl mx-auto px-6 w-full">
        <div className="rounded-3xl bg-gradient-to-br from-[#F2E5C6] to-[#F2D9A0]/70 border border-[#F2D9A0] p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8 shadow-sm">
          <div className="flex flex-col gap-2 max-w-lg">
            <span className="text-xs font-bold uppercase tracking-wider text-[#560B18] font-body">
              Jaminan Integritas Informasi
            </span>
            <h3 className="font-display text-2xl md:text-3xl font-bold text-[#3B010B]">
              Setiap Jawaban Berpijak pada Naskah Asli Terverifikasi
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed mt-1 font-body">
              Sistem secara otomatis memverifikasi keaslian pasal sebelum merumuskan jawaban, memastikan pengguna terhindar dari informasi palsu atau manipulasi pasal hukum.
            </p>
          </div>

          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-full text-sm font-semibold tracking-wide shrink-0 flex items-center gap-2 shadow-lg"
          >
            <span>Mulai Konsultasi Sekarang</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
