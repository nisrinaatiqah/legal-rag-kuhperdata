'use client';

import Link from 'next/link';
import { ArrowUpRight, Search, FileText, CheckCircle2, ShieldCheck, Scale } from 'lucide-react';
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

const POPULAR_TOPICS = [
  {
    tag: 'Pasal 1320 KUHPerdata',
    title: 'Syarat Sah Perjanjian',
    query: 'Apa 4 syarat sahnya perjanjian menurut Pasal 1320 KUHPerdata dan akibat hukum bila tidak dipenuhi?',
  },
  {
    tag: 'Pasal 1365 KUHPerdata',
    title: 'Perbuatan Melawan Hukum (PMH)',
    query: 'Bagaimana unsur-unsur Perbuatan Melawan Hukum (PMH) menurut Pasal 1365 KUHPerdata?',
  },
  {
    tag: 'Pasal 1243 KUHPerdata',
    title: 'Gugatan Wanprestasi & Ganti Rugi',
    query: 'Kapan debitur dinyatakan wanprestasi dan apa saja bentuk ganti rugi menurut Pasal 1243 KUHPerdata?',
  },
  {
    tag: 'Pasal 1250 KUHPerdata',
    title: 'Bunga Moratoir (Kelalaian Uang)',
    query: 'Bagaimana ketentuan ganti rugi bunga moratoir atas kelalaian pembayaran uang menurut KUHPerdata?',
  },
  {
    tag: 'Pasal 227 HIR',
    title: 'Sita Jaminan (Conservatoir Beslag)',
    query: 'Bagaimana tata cara dan syarat permohonan sita jaminan (conservatoir beslag) menurut HIR?',
  },
  {
    tag: 'Pasal 164 HIR',
    title: 'Kekuatan Alat Bukti Persidangan',
    query: 'Apa saja 5 alat bukti sah dalam hukum acara perdata menurut Pasal 164 HIR?',
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
      {/* Editorial Hero Section with Faded Law Emblem Background (Inspired by fe-kuhp-kuhap-chatbot) */}
      <section className="relative overflow-hidden w-full pt-4 pb-8">
        {/* Soft Faded Background Law Emblem Watermark */}
        <div
          aria-hidden="true"
          className="absolute right-0 md:right-8 lg:right-20 top-1/2 -translate-y-1/2 w-[340px] sm:w-[460px] lg:w-[560px] h-[340px] sm:h-[460px] lg:h-[560px] pointer-events-none select-none z-0 opacity-15 md:opacity-20 transition-opacity"
          style={{
            backgroundImage: "url('/law-emblem.png')",
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
            backgroundSize: 'contain',
            filter: 'contrast(1.1) sepia(0.2)',
          }}
        />

        {/* Subtle Ambient Radial Glow */}
        <div
          aria-hidden="true"
          className="absolute top-1/2 right-16 -translate-y-1/2 w-[500px] h-[500px] rounded-full pointer-events-none select-none z-0 opacity-20"
          style={{
            background: 'radial-gradient(circle, #F2D9A0 0%, transparent 70%)',
          }}
        />

        {/* Content Container */}
        <div className="max-w-6xl mx-auto px-6 relative z-10 w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
            {/* Left Column (60%): Headline, Context, & Action */}
            <div className="lg:col-span-7 flex flex-col items-start text-left">
            {/* Minimalist Section Eyebrow */}
            <div className="flex items-center gap-3 mb-6">
              <span className="w-6 h-[2px] bg-[#75162D] rounded-full"></span>
              <span className="text-[11px] font-bold tracking-widest uppercase font-montserrat text-[#75162D]">
                Platform Penelusuran Regulasi Perdata
              </span>
            </div>

            {/* Asymmetric Typography Headline in Marcellus + Italiana */}
            <h1 className="font-marcellus text-3xl sm:text-5xl md:text-6xl lg:text-[3.75rem] font-normal tracking-wide text-[#3B010B] leading-[1.1]">
              Penelusuran Cerdas{' '}
              <span className="font-italiana text-[#75162D] block mt-1 normal-case text-4xl sm:text-6xl md:text-7xl">
                Hukum Perdata Indonesia
              </span>
            </h1>

            {/* Lead Copy */}
            <p className="text-sm sm:text-base text-[#6B5559] mt-6 leading-relaxed max-w-xl font-medium font-montserrat">
              Asisten berbasis kecerdasan buatan untuk membantu penelusuran naskah resmi KUHPerdata dan HIR secara terstruktur, cepat, dan terverifikasi dari sumber pangkalan data JDIH Nasional.
            </p>

            {/* Actions: Floraverse Rounded-Full Pill Buttons */}
            <div className="flex flex-wrap items-center gap-6 mt-8 pt-2">
              <Link
                href="/chat"
                className="btn-burgundy-primary px-7 py-3.5 rounded-full text-xs font-bold tracking-wide uppercase font-montserrat flex items-center gap-2 shadow-md hover:scale-[1.02] transition-transform"
              >
                <span>Mulai Penelusuran</span>
                <ArrowUpRight className="w-4 h-4" />
              </Link>

              <Link
                href="/database"
                className="text-xs font-bold tracking-wide uppercase font-montserrat text-[#3B010B] hover:text-[#75162D] transition-colors border-b-2 border-[#3B010B] pb-0.5 flex items-center gap-1"
              >
                <span>Katalog 2.276 Ketentuan</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-[#75162D]" />
              </Link>
            </div>

            {/* Editorial Principle Quote in Italiana */}
            <div className="mt-12 pt-6 border-t border-[#E8DEC9] w-full">
              <p className="font-italiana text-2xl md:text-3xl text-[#3B010B] leading-snug">
                &ldquo;Hukum perdata ditegakkan atas kepastian janji, kesucian perikatan, dan keadilan pembuktian.&rdquo;
              </p>
              <p className="text-[10px] text-[#6B5559] mt-2 uppercase tracking-widest font-bold font-montserrat">
                Prinsip Fundamental KUHPerdata &amp; HIR
              </p>
            </div>
          </div>

          {/* Right Column (40%): Structured Regulatory Index Box (Floraverse Rounded-2xl Style) */}
          <div className="lg:col-span-5 w-full">
            <div className="bg-[#FFFFFF]/95 backdrop-blur-md border border-[#E8DEC9] p-7 rounded-2xl shadow-sm flex flex-col gap-6">
              <div className="border-b border-[#E8DEC9] pb-4 flex items-center justify-between">
                <span className="font-cyntho text-xs font-bold tracking-widest uppercase text-[#3B010B]">
                  Pustaka Peraturan Resmi
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-3 py-1 bg-[#F2E5C6] text-[#560B18] rounded-full font-montserrat">
                  Terkodifikasi
                </span>
              </div>

              {/* Scope Breakdown */}
              <div className="flex flex-col divide-y divide-[#FAF6EE] text-xs font-montserrat">
                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-[#3B010B]">KUHPerdata (BW)</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Buku I s/d Buku IV (Hukum Materiel)</p>
                  </div>
                  <span className="font-cyntho text-[#75162D] font-bold text-sm shrink-0">
                    1.993 Pasal
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-[#3B010B]">HIR (Reglemen Indonesia)</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Hukum Acara Perdata di Persidangan</p>
                  </div>
                  <span className="font-cyntho text-[#75162D] font-bold text-sm shrink-0">
                    283 Pasal
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-[#3B010B]">Standar Verifikasi</p>
                    <p className="text-[#6B5559] text-[11px] mt-0.5">Integritas Naskah Asli JDIH</p>
                  </div>
                  <span className="text-[#15803d] font-bold text-xs shrink-0 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 100% Valid
                  </span>
                </div>
              </div>

              {/* Direct Query Search Input inside Box */}
              <form onSubmit={handleQuickSearch} className="mt-2 pt-4 border-t border-[#E8DEC9] flex flex-col gap-2">
                <label className="text-[11px] font-bold text-[#6B5559] uppercase tracking-wider font-montserrat">
                  Pencarian Langsung Naskah:
                </label>
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={quickQuery}
                    onChange={(e) => setQuickQuery(e.target.value)}
                    placeholder="Contoh: Pasal 1320, ganti rugi, sita jaminan..."
                    className="w-full pl-3 pr-10 py-2.5 bg-[#FAF6EE] border border-[#E8DEC9] text-xs text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] rounded-full font-montserrat"
                  />
                  <button
                    type="submit"
                    className="absolute right-2.5 p-1.5 text-[#75162D] hover:text-[#3B010B]"
                    title="Cari"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

      {/* Structured Competences Section (Floraverse Rounded-2xl Connected Panels) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        {/* Section Header */}
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Kompilasi Ruang Lingkup
            </span>
            <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B] mt-1">
              Empat Pilar Pengaturan Perdata
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-montserrat font-medium">
            Klasifikasi naskah hukum resmi yang telah terindeks dan dapat ditelusuri melalui sistem.
          </p>
        </div>

        {/* 4 Connected Panels with Hairline Vertical Dividers (Floraverse Rounded-2xl Style) */}
        <div className="bg-[#FFFFFF]/95 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-[#E8DEC9] overflow-hidden shadow-xs">
          {REGULATION_SCOPES.map((scope) => (
            <div key={scope.code} className="p-6 flex flex-col justify-between min-h-[240px]">
              <div>
                <div className="flex items-baseline justify-between">
                  <span className="font-cyntho text-2xl font-bold text-[#75162D]">
                    {scope.code}
                  </span>
                  <span className="text-[10px] font-bold text-[#8C7A7C] uppercase tracking-wider font-montserrat">
                    {scope.subject}
                  </span>
                </div>

                <h3 className="font-cyntho text-base font-bold tracking-tight text-[#3B010B] mt-3 leading-snug">
                  {scope.title}
                </h3>

                <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-montserrat">
                  {scope.description}
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center justify-between text-xs font-montserrat">
                <Link
                  href={`/database?q=${encodeURIComponent(scope.title.split(' ')[1] || 'perdata')}`}
                  className="text-xs font-bold text-[#75162D] hover:underline flex items-center gap-1"
                >
                  <span>Lihat Ketentuan</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Editorial Information: Standar Keaslian & Integritas Penelusuran (Floraverse 3-Column Division) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Standar &amp; Informasi Sistem
            </span>
            <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B] mt-1">
              Transparansi &amp; Integritas Penelusuran
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-montserrat font-medium">
            Bagaimana CiviLex AI menjaga keaslian setiap pasal dan menyajikan rujukan hukum secara terpercaya.
          </p>
        </div>

        <div className="bg-[#FFFFFF]/95 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-[#E8DEC9] overflow-hidden shadow-xs">
          {/* Pillar 1 */}
          <div className="p-7 flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-full bg-[#F2E5C6] text-[#75162D] flex items-center justify-center font-cyntho text-sm font-bold mb-4">
                01
              </div>
              <h3 className="font-cyntho text-lg font-bold tracking-tight text-[#3B010B]">
                2.276 Ketentuan Terkodifikasi
              </h3>
              <p className="text-xs text-[#6B5559] mt-3 leading-relaxed font-montserrat">
                Memproses naskah resmi KUHPerdata (Buku I–IV) dan HIR secara granular per ketentuan pasal mandiri dari sumber primer JDIH Nasional guna mengeliminasi informasi bising (*zero context noise*).
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#15803d] font-montserrat">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Sumber Terkodifikasi Otentik</span>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-7 flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-full bg-[#F2E5C6] text-[#75162D] flex items-center justify-center font-cyntho text-sm font-bold mb-4">
                02
              </div>
              <h3 className="font-cyntho text-lg font-bold tracking-tight text-[#3B010B]">
                Verifikasi Sidik Jari Kriptografis
              </h3>
              <p className="text-xs text-[#6B5559] mt-3 leading-relaxed font-montserrat">
                Setiap pasal divalidasi terhadap sidik jari hash kriptografis resmi sebelum dianalisis, mencegah penyusupan kutipan palsu, pasal kedaluwarsa, atau manipulasi redaksi undang-undang.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#75162D] font-montserrat">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Proteksi Naskah Berlapis</span>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="p-7 flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-full bg-[#F2E5C6] text-[#75162D] flex items-center justify-center font-cyntho text-sm font-bold mb-4">
                03
              </div>
              <h3 className="font-cyntho text-lg font-bold tracking-tight text-[#3B010B]">
                Rujukan Semantik Presisi
              </h3>
              <p className="text-xs text-[#6B5559] mt-3 leading-relaxed font-montserrat">
                Pengguna dapat memasukkan kronologi atau pertanyaan sehari-hari; AI mencocokkan substansi hukum dengan pasal yang relevan dan menyertakan kutipan naskah aslinya secara utuh.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#560B18] font-montserrat">
              <Scale className="w-3.5 h-3.5" />
              <span>Analisis Berbasis Hukum Positif</span>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Civil Legal Topics (Floraverse Rounded-2xl Cards) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Topik Regulasi Populer
            </span>
            <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B] mt-1">
              Pertanyaan yang Kerap Ditelusuri
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-montserrat font-medium">
            Pilih topik berikut untuk langsung membuka penelusuran naskah dan analisis ketentuan hukumnya.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {POPULAR_TOPICS.map((topic, idx) => (
            <Link
              key={idx}
              href={`/chat?q=${encodeURIComponent(topic.query)}`}
              className="group p-5 bg-white/90 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl hover:border-[#75162D] hover:shadow-md transition-all flex flex-col justify-between gap-3 shadow-xs"
            >
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#75162D] font-montserrat">
                  {topic.tag}
                </span>
                <h4 className="font-cyntho text-sm font-bold text-[#3B010B] mt-1 group-hover:text-[#75162D] transition-colors">
                  {topic.title}
                </h4>
                <p className="text-xs text-[#6B5559] mt-1 leading-relaxed font-montserrat line-clamp-2 font-medium">
                  {topic.query}
                </p>
              </div>
              <div className="flex items-center gap-1 text-[11px] font-bold text-[#75162D] pt-2 border-t border-[#FAF6EE] font-montserrat">
                <span>Tinjau Naskah Pasal</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Authentic Swiss/Editorial Statement Section (Floraverse Rounded-2xl Style) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="bg-[#F2E5C6]/50 backdrop-blur-sm border border-[#E8DEC9] p-8 md:p-12 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-8 shadow-xs">
          <div className="flex flex-col gap-2 max-w-2xl">
            <span className="text-[11px] font-bold uppercase tracking-widest text-[#75162D] font-montserrat">
              Integritas &amp; Verifikasi Data
            </span>
            <h3 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B]">
              Kepastian Rujukan Berdasarkan Naskah Resmi
            </h3>
            <p className="text-xs sm:text-sm text-[#560B18] leading-relaxed mt-1 font-montserrat font-medium">
              Setiap rujukan pasal yang ditampilkan ditautkan langsung dengan naskah otentik dari JDIH Nasional guna mencegah kesalahan sitasi, distorsi redaksi, maupun kutipan yang tidak berlaku.
            </p>
          </div>

          <Link
            href="/chat"
            className="btn-burgundy-primary px-8 py-3.5 rounded-full text-xs font-bold tracking-wide uppercase font-montserrat shrink-0 flex items-center gap-2 shadow-md hover:scale-[1.02] transition-transform"
          >
            <span>Mulai Penelusuran Naskah</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
