'use client';

import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

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
    <div className="flex flex-col gap-20 pb-16 font-body">
      {/* Clean Hero Section — The Roman Jurist Style */}
      <section className="max-w-4xl mx-auto px-6 pt-10 flex flex-col items-center text-center">
        {/* Small Roman Header Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#F2D9A0] bg-[#F2E5C6]/60 text-[11px] font-bold tracking-widest uppercase font-cinzel text-[#560B18] mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-[#75162D]"></span>
          <span>Sistem Tanya Jawab Hukum Perdata Indonesia</span>
        </div>

        {/* Big Roman Jurist Headline: Cinzel + Cormorant Garamond */}
        <h1 className="font-cinzel text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-wider text-[#3B010B] max-w-4xl leading-[1.25]">
          MITRA HUKUM ANDA DALAM{' '}
          <span className="font-cormorant italic font-normal text-[#75162D] text-4xl sm:text-5xl md:text-6xl lg:text-7xl block sm:inline normal-case">
            setiap situasi
          </span>
        </h1>

        {/* Subtitle in Inter */}
        <p className="text-sm sm:text-base text-[#6B5559] max-w-2xl mt-6 font-normal leading-relaxed">
          Memberikan solusi dan analisis hukum perdata yang presisi melalui kecerdasan buatan, dengan jaminan integritas naskah resmi dari KUHPerdata dan HIR.
        </p>

        {/* Call to Actions in Swatch Colors */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-full text-xs font-semibold tracking-wider uppercase font-cinzel flex items-center gap-2"
          >
            <span>Mulai Konsultasi</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>

          <Link
            href="/database"
            className="btn-champagne-outline px-7 py-3.5 rounded-full text-xs font-semibold tracking-wider uppercase font-cinzel flex items-center gap-2 shadow-sm"
          >
            <span>Katalog 2.276 Pasal</span>
            <ArrowUpRight className="w-4 h-4 text-[#75162D]" />
          </Link>
        </div>

        {/* Editorial Quote Block in Cormorant Garamond Italic */}
        <div className="mt-16 max-w-2xl border-t border-[#E8DEC9] pt-8">
          <p className="font-cormorant italic text-2xl md:text-3xl text-[#3B010B] leading-snug">
            &ldquo;Hukum perdata ditegakkan atas kepastian janji, kesucian perikatan, dan keadilan pembuktian.&rdquo;
          </p>
          <p className="text-[11px] text-[#6B5559] mt-3 uppercase tracking-widest font-bold font-cinzel">
            Prinsip Fundamental KUHPerdata &amp; HIR
          </p>
        </div>
      </section>

      {/* Competences / Bidang Pokok Hukum Perdata (4 Clean Cards) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4 border-b border-[#E8DEC9] pb-6">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-cinzel">
              Ruang Lingkup Kajian
            </span>
            <h2 className="font-cinzel text-2xl md:text-3xl font-bold tracking-wider text-[#3B010B] mt-1">
              Bidang Pokok{' '}
              <span className="font-cormorant italic font-normal text-[#75162D] text-3xl md:text-4xl normal-case">
                Hukum Perdata
              </span>
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-[#6B5559] max-w-md leading-relaxed">
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
                <span className="font-cinzel text-2xl font-bold text-[#75162D]">
                  {comp.num}
                </span>
                <h3 className="font-cinzel text-sm font-bold tracking-wide text-[#3B010B] mt-2 leading-snug">
                  {comp.title}
                </h3>
                <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-body">
                  {comp.desc}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-[#FAF6EE] flex items-center justify-between text-xs">
                <span className="text-[11px] font-medium text-[#6B5559]">{comp.badge}</span>
                <Link
                  href="/chat"
                  className="text-xs font-semibold text-[#75162D] hover:underline flex items-center gap-1 font-cinzel"
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
            <span className="text-[11px] font-bold uppercase tracking-widest text-[#560B18] font-cinzel">
              Jaminan Integritas Informasi
            </span>
            <h3 className="font-cinzel text-xl md:text-2xl font-bold tracking-wider text-[#3B010B]">
              Setiap Jawaban Berpijak pada Naskah Asli Terverifikasi
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed mt-1">
              Sistem secara otomatis memverifikasi keaslian pasal sebelum merumuskan jawaban, memastikan pengguna terhindar dari informasi palsu atau manipulasi pasal hukum.
            </p>
          </div>

          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-full text-xs font-semibold tracking-wider uppercase font-cinzel shrink-0 flex items-center gap-2 shadow-lg"
          >
            <span>Mulai Konsultasi Sekarang</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
