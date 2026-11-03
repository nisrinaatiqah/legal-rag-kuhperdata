'use client';

import Link from 'next/link';
import {
  BookOpen,
  MessageSquare,
  Scale,
  Search,
  ArrowRight,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

const SERVICES = [
  {
    icon: <MessageSquare className="w-6 h-6" />,
    title: 'Tanya Jawab AI Terpadu',
    desc: 'Konsultasikan persoalan perdata Anda secara menyeluruh. Asisten AI menganalisis ketentuan hukum materiil (KUHPerdata) sekaligus tata cara persidangan (HIR) dalam satu ruang diskusi.',
    href: '/chat',
    tag: 'Asisten Cerdas',
    actionText: 'Mulai Tanya Jawab',
  },
  {
    icon: <BookOpen className="w-6 h-6" />,
    title: 'Katalog Naskah Lengkap',
    desc: 'Telusuri pangkalan data otentik 1.993 pasal KUHPerdata dan 283 pasal HIR secara mandiri, lengkap dengan pencarian kata kunci dan navigasi terstruktur per bab naskah.',
    href: '/database',
    tag: 'Pustaka Resmi',
    actionText: 'Buka Katalog Naskah',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col gap-24 pb-12 font-body">
      {/* Hero Section — Minimalist & Direct */}
      <section className="relative overflow-hidden w-full min-h-[calc(100vh-7rem)] flex flex-col justify-center py-8 md:py-12">
        {/* Soft Faded Background Law Emblem Watermark */}
        <div
          aria-hidden="true"
          className="absolute right-2 sm:right-6 md:right-10 lg:right-14 top-1/2 -translate-y-1/2 w-[300px] sm:w-[380px] md:w-[460px] lg:w-[520px] max-w-[45vw] max-h-[72vh] aspect-square pointer-events-none select-none z-0 opacity-25 md:opacity-35 transition-opacity flex items-center justify-center"
        >
          <img
            src="/law-emblem.png"
            alt=""
            className="w-full h-full object-contain filter contrast-[1.05] sepia-[0.15]"
          />
        </div>

        {/* Subtle Ambient Radial Glow */}
        <div
          aria-hidden="true"
          className="absolute top-1/2 right-16 -translate-y-1/2 w-[500px] h-[500px] rounded-full pointer-events-none select-none z-0 opacity-20"
          style={{
            background: 'radial-gradient(circle, #F2D9A0 0%, transparent 70%)',
          }}
        />

        {/* Content Container */}
        <div className="max-w-6xl mx-auto px-6 relative z-10 w-full my-auto">
          <div className="max-w-2xl lg:max-w-3xl flex flex-col items-start text-left">
            <h1 className="font-bodoni text-4xl sm:text-5xl md:text-6xl lg:text-7xl leading-[1.05] tracking-tight text-[#3B010B] mb-5">
              Navigasi Perdata
              <br />
              <span className="font-bellefair text-[#75162D] italic font-normal">
                Jernih &amp; Terpercaya
              </span>
            </h1>

            <p className="text-sm sm:text-base md:text-lg text-[#6B5559] leading-relaxed mb-8 max-w-xl font-normal font-sans">
              Temukan rujukan pasal perikatan, keabsahan perjanjian, tuntutan ganti rugi, hingga tata tertib sidang perdata secara instan berbantuan AI.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/chat"
                className="btn-burgundy-primary px-6 py-3 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 shadow-sm hover:scale-[1.02] transition-transform font-sans"
              >
                <span>Mulai Konsultasi AI</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/database"
                className="px-6 py-3 rounded-xl text-xs sm:text-sm font-bold text-[#75162D] bg-white/90 border border-[#E8DEC9] hover:bg-[#F2E5C6]/40 transition-all flex items-center gap-2 font-sans shadow-xs"
              >
                <Search className="w-4 h-4" />
                <span>Katalog Naskah</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Main Services Section — 2 Unified Pathways */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="mb-8">
          <p className="text-xs font-bold uppercase tracking-widest text-[#75162D] font-montserrat mb-1.5">
            Layanan Utama
          </p>
          <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B]">
            Pusat Penelusuran Regulasi
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {SERVICES.map((item, i) => (
            <Link
              key={i}
              href={item.href}
              className="group p-8 rounded-2xl bg-white border border-[#E8DEC9] hover:border-[#75162D] hover:shadow-md transition-all flex flex-col justify-between shadow-xs"
            >
              <div>
                <div className="flex items-center justify-between mb-5">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-[#F2E5C6] text-[#75162D] group-hover:scale-105 transition-transform">
                    {item.icon}
                  </div>
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#FAF6EE] text-[#75162D] border border-[#E8DEC9] font-montserrat">
                    {item.tag}
                  </span>
                </div>
                <h3 className="font-cyntho text-xl font-bold text-[#3B010B] mb-2.5 group-hover:text-[#75162D] transition-colors">
                  {item.title}
                </h3>
                <p className="text-xs sm:text-sm text-[#6B5559] leading-relaxed font-sans mb-6">
                  {item.desc}
                </p>
              </div>

              <div className="flex items-center gap-1.5 text-xs sm:text-sm font-bold text-[#75162D] font-sans group-hover:gap-2.5 transition-all">
                <span>{item.actionText}</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Value Pillars Section */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          {/* Left Column — Heading */}
          <div className="lg:col-span-5">
            <h2 className="font-bodoni text-3xl md:text-4xl lg:text-5xl leading-tight text-[#3B010B] mb-4">
              Menjembatani Teks Hukum dengan Kebutuhan Riil.
            </h2>
            <p className="text-xs sm:text-sm text-[#6B5559] leading-relaxed font-sans">
              CiviLex AI mengurai kerumitan pasal perdata menjadi rujukan yang terang, terarah, dan berpijak pada naskah otentik.
            </p>
          </div>

          {/* Right Column — Bento Grid */}
          <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Card 1 */}
            <div className="p-7 rounded-2xl bg-white border border-[#E8DEC9] shadow-xs">
              <div className="w-10 h-10 rounded-xl bg-[#F2E5C6] text-[#75162D] flex items-center justify-center mb-4">
                <Scale className="w-5 h-5" />
              </div>
              <h3 className="font-cyntho text-base font-bold text-[#3B010B] mb-2">
                Harmonisasi Materiel &amp; Formil
              </h3>
              <p className="text-xs text-[#6B5559] leading-relaxed font-sans">
                Menghubungkan hak substantif Anda (KUHPerdata) dengan langkah penegakannya di ruang sidang (HIR).
              </p>
            </div>

            {/* Card 2 */}
            <div className="p-7 rounded-2xl bg-white border border-[#E8DEC9] shadow-xs">
              <div className="w-10 h-10 rounded-xl bg-[#F2E5C6] text-[#75162D] flex items-center justify-center mb-4">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="font-cyntho text-base font-bold text-[#3B010B] mb-2">
                Uraian Terang &amp; Runtut
              </h3>
              <p className="text-xs text-[#6B5559] leading-relaxed font-sans">
                Menyajikan intisari aturan hukum secara runtut dan mudah dipahami tanpa mengurangi bobot yuridisnya.
              </p>
            </div>

            {/* Card 3 — Wide */}
            <div className="md:col-span-2 p-7 rounded-2xl bg-white border border-[#E8DEC9] shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
              <div>
                <div className="w-10 h-10 rounded-xl bg-[#F2E5C6] text-[#75162D] flex items-center justify-center mb-4">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-cyntho text-base font-bold text-[#3B010B] mb-1.5">
                  Transparansi Nomor &amp; Petikan Pasal
                </h3>
                <p className="text-xs text-[#6B5559] leading-relaxed font-sans max-w-md">
                  Tiap simpulan selalu menyandingkan nomor pasal dan kutipan bunyi aslinya agar dapat ditinjau ulang kapan saja.
                </p>
              </div>
              <Link
                href="/chat"
                className="btn-burgundy-primary px-5 py-2.5 rounded-xl text-xs font-bold font-sans flex items-center gap-1.5 shrink-0"
              >
                <span>Eksplorasi Sekarang</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Band — Burgundy Gradient Card */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="relative overflow-hidden rounded-3xl px-8 py-14 text-center bg-gradient-to-r from-[#560B18] via-[#75162D] to-[#8C1D38] text-white shadow-md">
          <div
            className="absolute inset-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #FAF6EE 1px, transparent 1px)',
              backgroundSize: '24px 24px',
            }}
          />
          <div className="relative z-10 max-w-xl mx-auto">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-4 backdrop-blur-xs">
              <Scale className="w-6 h-6 text-[#F2D9A0]" />
            </div>
            <h2 className="font-bodoni text-2xl sm:text-3xl md:text-4xl text-white mb-3">
              Punya Persoalan Seputar Kasus Perdata?
            </h2>
            <p className="text-xs sm:text-sm text-white/80 font-sans mb-8 leading-relaxed">
              Diskusikan kronologi persoalan Anda atau cari pasal terkait untuk memperoleh analisis awal berbasis rujukan terpercaya.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <Link
                href="/chat"
                className="px-6 py-3 rounded-xl text-xs sm:text-sm font-bold bg-[#FAF6EE] text-[#560B18] hover:bg-white transition-all shadow-sm flex items-center gap-2"
              >
                <span>Mulai Konsultasi AI</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/database"
                className="px-6 py-3 rounded-xl text-xs sm:text-sm font-bold text-white bg-white/10 border border-white/20 hover:bg-white/20 transition-all flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                <span>Katalog Naskah</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
