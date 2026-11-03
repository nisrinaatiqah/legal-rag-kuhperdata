'use client';

import Link from 'next/link';
import { ArrowUpRight, Search, FileText, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const REGULATION_SCOPES = [
  {
    code: '01',
    title: 'Hukum Perikatan & Perjanjian',
    subject: 'KUHPerdata Buku III',
    description:
      'Penelusuran syarat sah perjanjian (Pasal 1320), wanprestasi, ganti rugi kelalaian, dan pembatalan perikatan timbal balik.',
  },
  {
    code: '02',
    title: 'Perbuatan Melawan Hukum (PMH)',
    subject: 'KUHPerdata Pasal 1365',
    description:
      'Analisis unsur kesalahan, kerugian materiel-imateriel, dan hubungan kausalitas dalam gugatan ganti rugi perdata.',
  },
  {
    code: '03',
    title: 'Kebendaan & Kewarisan',
    subject: 'KUHPerdata Buku II',
    description:
      'Ketentuan hak milik, hak jaminan kebendaan, pembagian harta peninggalan, dan perlindungan hak mutlak ahli waris.',
  },
  {
    code: '04',
    title: 'Hukum Acara Perdata (HIR)',
    subject: 'Reglemen Indonesia yang Diperbaharui',
    description:
      'Pedoman beracara di pengadilan: tata cara pendaftaran gugatan, sita jaminan (conservatoir beslag), dan kekuatan alat bukti.',
  },
];

export default function HomePage() {
  const router = useRouter();
  const [quickQuery, setQuickQuery] = useState('');

  const handleQuickSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickQuery.trim()) {
      router.push(`/chat?q=${encodeURIComponent(quickQuery.trim())}`);
    } else {
      router.push('/chat');
    }
  };

  return (
    <div className="flex flex-col gap-24 pb-20 font-body">
      {/* Editorial Hero Section (Asymmetric 2-Column Grid - Inspired by Image 2 & 3) */}
      <section className="max-w-6xl mx-auto px-6 pt-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Left Column (60%): Headline, Context, & Action */}
          <div className="lg:col-span-7 flex flex-col items-start text-left">
            {/* Minimalist Section Eyebrow */}
            <div className="flex items-center gap-3 mb-6">
              <span className="w-6 h-[1.5px] bg-[#75162D]"></span>
              <span className="text-[11px] font-semibold tracking-widest uppercase font-sans text-[#75162D]">
                Platform Penelusuran Regulasi Perdata
              </span>
            </div>

            {/* Asymmetric Typography Headline */}
            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl lg:text-[3.25rem] font-normal tracking-tight text-[#3B010B] leading-[1.2]">
              Penelusuran Cerdas{' '}
              <span className="italic text-[#75162D] block normal-case text-4xl sm:text-5xl md:text-6xl mt-1">
                hukum perdata indonesia.
              </span>
            </h1>

            {/* Lead Copy */}
            <p className="text-sm sm:text-base text-[#6B5559] mt-6 leading-relaxed max-w-xl font-normal font-sans">
              Asisten berbasis kecerdasan buatan untuk membantu penelusuran naskah resmi KUHPerdata dan HIR secara terstruktur, cepat, dan terverifikasi dari sumber pangkalan data JDIH Nasional.
            </p>

            {/* Actions: Solid Burgundy Rectangular Button + Underlined Link */}
            <div className="flex flex-wrap items-center gap-6 mt-8 pt-2">
              <Link
                href="/chat"
                className="btn-burgundy-primary px-7 py-3.5 rounded-sm text-xs font-semibold tracking-wider uppercase font-sans flex items-center gap-2"
              >
                <span>Mulai Penelusuran</span>
                <ArrowUpRight className="w-4 h-4" />
              </Link>

              <Link
                href="/database"
                className="text-xs font-semibold tracking-wider uppercase font-sans text-[#3B010B] hover:text-[#75162D] transition-colors border-b border-[#3B010B] pb-0.5 flex items-center gap-1"
              >
                <span>Katalog 2.276 Ketentuan</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-[#75162D]" />
              </Link>
            </div>

            {/* Editorial Principle Quote */}
            <div className="mt-12 pt-6 border-t border-[#E8DEC9] w-full">
              <p className="font-serif italic text-xl md:text-2xl text-[#3B010B] leading-snug">
                &ldquo;Hukum perdata ditegakkan atas kepastian janji, kesucian perikatan, dan keadilan pembuktian.&rdquo;
              </p>
              <p className="text-[10px] text-[#6B5559] mt-2 uppercase tracking-widest font-semibold font-sans">
                Prinsip Fundamental KUHPerdata &amp; HIR
              </p>
            </div>
          </div>

          {/* Right Column (40%): Structured Regulatory Index Box (Inspired by Image 2 & 5) */}
          <div className="lg:col-span-5 w-full">
            <div className="bg-[#FFFFFF] border border-[#E8DEC9] p-7 rounded-sm shadow-sm flex flex-col gap-6">
              <div className="border-b border-[#E8DEC9] pb-4 flex items-center justify-between">
                <span className="font-sans text-xs font-bold tracking-widest uppercase text-[#3B010B]">
                  Pustaka Peraturan Resmi
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-[#F2E5C6] text-[#560B18] rounded-sm font-sans">
                  Terkodifikasi
                </span>
              </div>

              {/* Scope Breakdown */}
              <div className="flex flex-col divide-y divide-[#FAF6EE] text-xs font-sans">
                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-[#3B010B]">KUHPerdata (BW)</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Buku I s/d Buku IV (Hukum Materiel)</p>
                  </div>
                  <span className="font-serif text-[#75162D] font-bold text-sm shrink-0">
                    1.993 Pasal
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-[#3B010B]">HIR (Reglemen Indonesia)</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Hukum Acara Perdata di Persidangan</p>
                  </div>
                  <span className="font-serif text-[#75162D] font-bold text-sm shrink-0">
                    283 Pasal
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-[#3B010B]">Standar Verifikasi</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Integritas Naskah Asli JDIH</p>
                  </div>
                  <span className="text-[#15803d] font-semibold text-xs shrink-0 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 100% Valid
                  </span>
                </div>
              </div>

              {/* Direct Query Search Input inside Box */}
              <form onSubmit={handleQuickSearch} className="mt-2 pt-4 border-t border-[#E8DEC9] flex flex-col gap-2">
                <label className="text-[11px] font-semibold text-[#6B5559] uppercase tracking-wider font-sans">
                  Pencarian Langsung Naskah:
                </label>
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={quickQuery}
                    onChange={(e) => setQuickQuery(e.target.value)}
                    placeholder="Contoh: Pasal 1320, ganti rugi, sita jaminan..."
                    className="w-full pl-3 pr-10 py-2.5 bg-[#FAF6EE] border border-[#E8DEC9] text-xs text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] rounded-sm font-body"
                  />
                  <button
                    type="submit"
                    className="absolute right-2 p-1.5 text-[#75162D] hover:text-[#3B010B]"
                    title="Cari"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Structured Competences Section (Enclosed 4-Column Division - Inspired by Image 3 & 5) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        {/* Section Header */}
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-semibold tracking-widest uppercase text-[#75162D] font-sans">
              Kompilasi Ruang Lingkup
            </span>
            <h2 className="font-serif text-2xl md:text-3xl font-normal tracking-tight text-[#3B010B] mt-1">
              Empat Pilar Pengaturan Perdata
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-sans">
            Klasifikasi naskah hukum resmi yang telah terindeks dan dapat ditelusuri melalui sistem.
          </p>
        </div>

        {/* 4 Connected Panels with Hairline Vertical Dividers (NOT Floating Cards!) */}
        <div className="bg-[#FFFFFF] border border-[#E8DEC9] rounded-sm grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-[#E8DEC9]">
          {REGULATION_SCOPES.map((scope) => (
            <div key={scope.code} className="p-6 flex flex-col justify-between min-h-[240px]">
              <div>
                <div className="flex items-baseline justify-between">
                  <span className="font-serif text-2xl font-bold text-[#75162D]">
                    {scope.code}
                  </span>
                  <span className="text-[10px] font-semibold text-[#8C7A7C] uppercase tracking-wider font-sans">
                    {scope.subject}
                  </span>
                </div>

                <h3 className="font-serif text-base font-bold tracking-tight text-[#3B010B] mt-3 leading-snug">
                  {scope.title}
                </h3>

                <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-sans">
                  {scope.description}
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center justify-between text-xs font-sans">
                <Link
                  href={`/database?q=${encodeURIComponent(scope.title.split(' ')[1] || 'perdata')}`}
                  className="text-xs font-semibold text-[#75162D] hover:underline flex items-center gap-1"
                >
                  <span>Lihat Ketentuan</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Authentic Swiss/Editorial Statement Section (Inspired by Image 1 & 5) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="bg-[#F2E5C6]/45 border border-[#E8DEC9] p-8 md:p-12 rounded-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
          <div className="flex flex-col gap-2 max-w-2xl">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-[#75162D] font-sans">
              Integritas &amp; Verifikasi Data
            </span>
            <h3 className="font-serif text-2xl md:text-3xl font-normal tracking-tight text-[#3B010B]">
              Kepastian Rujukan Berdasarkan Naskah Resmi
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed mt-1 font-sans">
              Setiap rujukan pasal yang ditampilkan ditautkan langsung dengan naskah otentik dari JDIH Nasional guna mencegah kesalahan sitasi, distorsi redaksi, maupun kutipan yang tidak berlaku.
            </p>
          </div>

          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-sm text-xs font-semibold tracking-wider uppercase font-sans shrink-0 flex items-center gap-2"
          >
            <span>Mulai Penelusuran Naskah</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
