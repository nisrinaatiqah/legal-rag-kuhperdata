'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import Link from 'next/link';
import { ArrowUpRight, CheckCircle2, ShieldCheck, Scale, X } from 'lucide-react';

const REGULATION_SCOPES = [
  {
    code: '01',
    title: 'Hukum Perikatan & Perjanjian',
    subject: 'KUHPerdata Buku III',
    description:
      'Syarat sah perjanjian (Pasal 1320), wanprestasi, tuntutan ganti rugi, dan pembatalan perikatan.',
    href: '/database?source=KUHPerdata&q=perikatan',
  },
  {
    code: '02',
    title: 'Perbuatan Melawan Hukum (PMH)',
    subject: 'KUHPerdata Pasal 1365',
    description:
      'Unsur kesalahan, kerugian materiil-imateriil, dan hubungan kausalitas gugatan perdata.',
    href: '/database?source=KUHPerdata&q=1365',
  },
  {
    code: '03',
    title: 'Kebendaan & Kewarisan',
    subject: 'KUHPerdata Buku II',
    description:
      'Hak milik, jaminan kebendaan, pembagian waris, dan hak mutlak ahli waris.',
    href: '/database?source=KUHPerdata&q=waris',
  },
  {
    code: '04',
    title: 'Hukum Acara Perdata (HIR)',
    subject: 'Reglemen Indonesia yang Diperbaharui',
    description:
      'Tata cara sidang, pendaftaran gugatan, sita jaminan, dan kekuatan alat bukti.',
    href: '/database?source=HIR',
  },
];

const POPULAR_TOPICS = [
  {
    tag: 'Pasal 1320 KUHPerdata',
    title: 'Syarat Sah Perjanjian',
    query: 'Apa 4 syarat sah perjanjian menurut Pasal 1320 KUHPerdata dan akibat hukumnya jika tidak dipenuhi?',
  },
  {
    tag: 'Pasal 1365 KUHPerdata',
    title: 'Perbuatan Melawan Hukum (PMH)',
    query: 'Apa saja 5 unsur Perbuatan Melawan Hukum (PMH) yang wajib dibuktikan dalam Pasal 1365 KUHPerdata?',
  },
  {
    tag: 'Pasal 1243 KUHPerdata',
    title: 'Wanprestasi & Ganti Rugi',
    query: 'Kapan debitur dinyatakan wanprestasi dan apa saja bentuk ganti ruginya menurut KUHPerdata?',
  },
  {
    tag: 'Pasal 1250 KUHPerdata',
    title: 'Bunga Moratoir',
    query: 'Bagaimana aturan ganti rugi bunga moratoir atas kelambatan bayar menurut Pasal 1250 KUHPerdata?',
  },
  {
    tag: 'Pasal 227 HIR',
    title: 'Sita Jaminan (Conservatoir Beslag)',
    query: 'Apa syarat dan tata cara permohonan sita jaminan (conservatoir beslag) menurut Pasal 227 HIR?',
  },
  {
    tag: 'Pasal 164 HIR',
    title: 'Alat Bukti Persidangan',
    query: 'Apa saja 5 alat bukti sah dalam sidang perdata menurut Pasal 164 HIR?',
  },
];

export default function HomePage() {
  const [showChoiceModal, setShowChoiceModal] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setShowChoiceModal(false);
    };
    if (showChoiceModal) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [showChoiceModal]);

  return (
    <div className="flex flex-col gap-24 pb-20 font-body">
      {/* Editorial Hero Section with Faded Law Emblem Background */}
      <section className="relative overflow-hidden w-full min-h-[calc(100vh-7rem)] flex flex-col justify-center py-8 md:py-12">
        {/* Law Emblem Hero Image - Gede & Alami */}
        <div
          aria-hidden="true"
          className="absolute right-0 sm:right-4 md:right-8 lg:right-12 top-1/2 -translate-y-1/2 w-[340px] sm:w-[440px] md:w-[540px] lg:w-[620px] max-w-[50vw] max-h-[85vh] pointer-events-none select-none z-0 flex items-center justify-center"
        >
          <img
            src="/law-emblem.png"
            alt=""
            className="w-full h-full object-contain animate-float-slow"
          />
        </div>

        {/* Content Container */}
        <div className="max-w-6xl mx-auto px-6 relative z-10 w-full my-auto">
          <div className="max-w-2xl lg:max-w-3xl flex flex-col items-start text-left">
            {/* Hybrid B + D: Bodoni Moda (High Didone) + Bellefair (Slender Aristocratic) */}
            <h1 className="font-bodoni text-3xl sm:text-4xl md:text-5xl lg:text-[3.85rem] font-medium tracking-tight text-[#3B010B] leading-[1.08]">
              <span className="block animate-fade-up" style={{ animationDelay: '0.05s' }}>
                Penelusuran Cerdas
              </span>
              <span
                className="font-bellefair text-[#75162D] block mt-1.5 italic font-normal text-3xl sm:text-4xl md:text-5xl lg:text-[4.25rem] tracking-wide animate-fade-up"
                style={{ animationDelay: '0.2s' }}
              >
                Hukum Perdata Indonesia
              </span>
            </h1>

            {/* Lead Copy — Ringkas & dari Sumber Terpercaya */}
            <p
              className="text-xs sm:text-sm md:text-base text-[#6B5559] mt-4 leading-relaxed max-w-xl font-normal font-sans animate-fade-up"
              style={{ animationDelay: '0.35s' }}
            >
              Asisten AI untuk penelusuran naskah resmi KUHPerdata dan HIR secara cepat, terstruktur, dan terverifikasi dari sumber terpercaya.
            </p>

            {/* Primary Action Buttons in Hero */}
            <div
              className="flex flex-wrap items-center gap-3 mt-8 animate-fade-up"
              style={{ animationDelay: '0.5s' }}
            >
              <Link
                href="/chat"
                className="btn-burgundy-primary px-6 py-3 rounded-full text-xs font-bold tracking-wider uppercase flex items-center gap-2 shadow-sm hover:scale-[1.02] transition-transform font-sans"
              >
                <span>Mulai Penelusuran</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
              <button
                type="button"
                onClick={() => setShowChoiceModal(true)}
                className="px-6 py-3 rounded-full text-xs font-bold tracking-wider uppercase text-[#75162D] hover:bg-[#F2E5C6]/40 border border-[#E8DEC9] transition-all flex items-center gap-1.5 font-sans cursor-pointer hover:border-[#75162D]"
              >
                <span>Cari Pasal</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Structured Competences Section (4 Connected Panels) */}
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
            Klasifikasi naskah hukum yang terindeks dan dapat ditelusuri langsung.
          </p>
        </div>

        {/* 4 Connected Panels */}
        <div className="bg-[#FFFFFF]/95 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-[#E8DEC9] overflow-hidden shadow-xs">
          {REGULATION_SCOPES.map((scope) => (
            <div key={scope.code} className="p-6 flex flex-col justify-between min-h-[220px]">
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

                <p className="text-xs text-[#6B5559] mt-2 leading-relaxed font-sans">
                  {scope.description}
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center justify-between text-xs font-montserrat">
                <Link
                  href={scope.href}
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

      {/* Editorial Information: Standar Keaslian & Integritas Penelusuran (3 Connected Panels) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Standar Sistem
            </span>
            <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B] mt-1">
              Transparansi &amp; Integritas Penelusuran
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-montserrat font-medium">
            Cara CiviLex AI menjaga keaslian pasal dan menyajikan rujukan hukum terpercaya.
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
                Database Terkodifikasi
              </h3>
              <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-sans">
                Memproses naskah resmi KUHPerdata (Buku I–IV) dan HIR per pasal dari sumber terpercaya tanpa distorsi konteks.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#15803d] font-montserrat">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Naskah Terpercaya</span>
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
              <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-sans">
                Tiap pasal divalidasi dengan hash kriptografis untuk mencegah kutipan palsu atau manipulasi isi pasal.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#75162D] font-montserrat">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Proteksi Berlapis</span>
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
              <p className="text-xs text-[#6B5559] mt-2.5 leading-relaxed font-sans">
                Ajukan pertanyaan dengan bahasa sehari-hari; AI mencocokkan substansi hukum dan menyertakan kutipan naskah aslinya.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[#FAF6EE] flex items-center gap-2 text-xs font-bold text-[#560B18] font-montserrat">
              <Scale className="w-3.5 h-3.5" />
              <span>Kutipan Otentik</span>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Civil Legal Topics (6 Cards) */}
      <section className="max-w-6xl mx-auto px-6 w-full">
        <div className="border-b border-[#E8DEC9] pb-4 mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
              Topik Populer
            </span>
            <h2 className="font-cyntho text-2xl md:text-3xl font-bold tracking-tight text-[#3B010B] mt-1">
              Pertanyaan yang Kerap Ditelusuri
            </h2>
          </div>
          <p className="text-xs text-[#6B5559] max-w-md font-montserrat font-medium">
            Pilih pertanyaan di bawah untuk langsung membuka analisis pasalnya.
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
                <p className="text-xs text-[#6B5559] mt-1 leading-relaxed font-sans line-clamp-2">
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

      {/* Choice Modal for KUHPerdata vs HIR — Portaled directly to document.body */}
      {mounted &&
        showChoiceModal &&
        createPortal(
          <div
            role="dialog"
            aria-modal="true"
            className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-[#2A171A]/50 backdrop-blur-sm"
            onClick={() => setShowChoiceModal(false)}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="bg-[#FAF6EE] border border-[#E8DEC9] rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl relative font-sans"
            >
              <button
                type="button"
                onClick={() => setShowChoiceModal(false)}
                className="absolute top-5 right-5 text-[#8C7A7C] hover:text-[#3B010B] p-2 rounded-full hover:bg-[#F2E5C6]/50 transition-colors cursor-pointer"
                title="Tutup"
              >
                <X className="w-5 h-5" />
              </button>

              <h3 className="font-bodoni text-2xl sm:text-3xl font-bold text-[#3B010B]">
                Cari Pasal
              </h3>
              <p className="text-xs sm:text-sm text-[#6B5559] mt-1 mb-6 font-normal">
                Pilih naskah yang ingin ditelusuri:
              </p>

              <div className="flex flex-col gap-3">
                <Link
                  href="/database?source=KUHPerdata"
                  onClick={() => setShowChoiceModal(false)}
                  className="flex items-center justify-between p-4 sm:p-5 rounded-2xl bg-white border border-[#E8DEC9] hover:border-[#75162D] hover:shadow-md transition-all group cursor-pointer"
                >
                  <div className="flex flex-col text-left">
                    <span className="font-bodoni text-lg sm:text-xl font-bold text-[#3B010B] group-hover:text-[#75162D] transition-colors">
                      KUHPerdata
                    </span>
                    <span className="text-xs text-[#6B5559] mt-0.5">
                      Hukum Perdata Materiel
                    </span>
                  </div>
                  <div className="w-9 h-9 rounded-full bg-[#FAF6EE] group-hover:bg-[#75162D] flex items-center justify-center text-[#75162D] group-hover:text-[#FAF6EE] transition-colors shrink-0">
                    <ArrowUpRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </div>
                </Link>

                <Link
                  href="/database?source=HIR"
                  onClick={() => setShowChoiceModal(false)}
                  className="flex items-center justify-between p-4 sm:p-5 rounded-2xl bg-white border border-[#E8DEC9] hover:border-[#75162D] hover:shadow-md transition-all group cursor-pointer"
                >
                  <div className="flex flex-col text-left">
                    <span className="font-bodoni text-lg sm:text-xl font-bold text-[#3B010B] group-hover:text-[#75162D] transition-colors">
                      HIR
                    </span>
                    <span className="text-xs text-[#6B5559] mt-0.5">
                      Hukum Acara Formil
                    </span>
                  </div>
                  <div className="w-9 h-9 rounded-full bg-[#FAF6EE] group-hover:bg-[#75162D] flex items-center justify-center text-[#75162D] group-hover:text-[#FAF6EE] transition-colors shrink-0">
                    <ArrowUpRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </div>
                </Link>
              </div>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
}
