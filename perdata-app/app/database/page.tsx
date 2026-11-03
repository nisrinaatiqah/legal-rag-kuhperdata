'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Scale, X, Layers } from 'lucide-react';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

const SOURCE_OPTIONS = [
  {
    id: 'KUHPerdata' as const,
    label: 'KUHPerdata',
    badge: 'Hukum Materiel',
    count: '1.993 Ketentuan',
    desc: 'Buku I s/d IV — Orang, Benda, Perikatan, & Pembuktian',
  },
  {
    id: 'HIR' as const,
    label: 'HIR — Acara Perdata',
    badge: 'Hukum Formil',
    count: '283 Ketentuan',
    desc: 'Bagian 1 s/d 6 — Sidang, Sita Jaminan, & Pembuktian',
  },
];

const KUHPERDATA_CATEGORIES = [
  { label: 'Semua Buku (1.993)', value: '', count: '1.993' },
  { label: 'Buku I: Orang & Keluarga', value: 'BUKU KESATU', count: '547', desc: 'Subjek Hukum, Perkawinan, Status Sipil' },
  { label: 'Buku II: Kebendaan & Waris', value: 'BUKU KEDUA', count: '741', desc: 'Hak Milik, Jaminan Kebendaan, Kewarisan' },
  { label: 'Buku III: Perikatan & Perjanjian', value: 'BUKU KETIGA', count: '709', desc: 'Syarat Sah Perjanjian (1320), Wanprestasi, PMH (1365)' },
  { label: 'Buku IV: Pembuktian & Daluwarsa', value: 'BUKU KEEMPAT', count: '130', desc: 'Alat Bukti Materiel, Kedaluwarsa Hak' },
];

const HIR_CATEGORIES = [
  { label: 'Semua Bagian (283)', value: '', count: '283' },
  { label: 'Bagian 1: Pemeriksaan & Gugatan', value: 'Bagian 1', count: '51', desc: 'Surat Gugatan, Pemanggilan, Sidang Perdamaian' },
  { label: 'Bagian 2: Alat Bukti Persidangan', value: 'Bagian 2', count: '15', desc: '5 Alat Bukti Sah di Persidangan (Pasal 164 HIR)' },
  { label: 'Bagian 3: Musyawarah & Putusan', value: 'Bagian 3', count: '10', desc: 'Putusan Hakim, Putusan Verstek, Kontradiktoir' },
  { label: 'Bagian 4: Upaya Hukum Banding', value: 'Bagian 4', count: '9', desc: 'Pernyataan Banding ke Pengadilan Tinggi' },
  { label: 'Bagian 5: Eksekusi & Sita Jaminan', value: 'Bagian 5', count: '35', desc: 'Conservatoir Beslag (227), Revindicatoir, Lelang' },
  { label: 'Bagian 6 & Bab XV: Acara Istimewa', value: 'Bagian 6', count: '30', desc: 'Perkara Khusus dan Berbagai Peraturan' },
];

function DatabaseContent() {
  const searchParams = useSearchParams();
  const rawSource = searchParams.get('source');
  const initialSource: 'KUHPerdata' | 'HIR' = rawSource === 'HIR' ? 'HIR' : 'KUHPerdata';
  const initialQuery = searchParams.get('q') || '';
  const initialCategory = searchParams.get('category') || '';

  const [articles, setArticles] = useState<ArticleDoc[]>([]);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [selectedSource, setSelectedSource] = useState<'KUHPerdata' | 'HIR'>(initialSource);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [page, setPage] = useState(0);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(false);

  // Sync if query params change
  useEffect(() => {
    const s = searchParams.get('source');
    const q = searchParams.get('q');
    const c = searchParams.get('category');
    if (s === 'HIR') setSelectedSource('HIR');
    else if (s === 'KUHPerdata') setSelectedSource('KUHPerdata');
    if (q !== null) setSearchQuery(q);
    if (c !== null) setSelectedCategory(c);
  }, [searchParams]);

  const fetchArticles = async (q: string, source: string, category: string, pageNum: number) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.append('q', q.trim());
      if (source) params.append('source', source);
      if (category) params.append('category', category);
      params.append('limit', limit.toString());
      params.append('offset', (pageNum * limit).toString());

      let res = await fetch(`/api/py/database?${params.toString()}`);
      if (!res.ok) {
        res = await fetch(`http://127.0.0.1:8000/api/database?${params.toString()}`);
      }

      if (res.ok) {
        const data = await res.json();
        setArticles(data.articles || []);
        setTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Error fetching database:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles(searchQuery, selectedSource, selectedCategory, page);
  }, [page, selectedSource, selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    fetchArticles(searchQuery, selectedSource, selectedCategory, 0);
  };

  const resetAllFilters = () => {
    setSelectedCategory('');
    setSearchQuery('');
    setPage(0);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="max-w-6xl mx-auto px-6 flex flex-col gap-8 pb-12 font-sans">
      {/* Header in High-Fashion Didone Style (Bodoni Moda - Opsi B) */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-sans">
          Pangkalan Data Naskah Resmi
        </span>
        <h1 className="font-bodoni text-3xl sm:text-4xl md:text-5xl font-medium tracking-normal text-[#3B010B]">
          Katalog Ketentuan{' '}
          <span className="text-[#75162D] italic normal-case text-3xl sm:text-4xl md:text-5xl block sm:inline">
            KUHPerdata &amp; HIR
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-2xl font-sans font-normal mt-1 leading-relaxed">
          Pustaka naskah resmi Lembaran Negara dan JDIH Nasional. Telusuri ketentuan hukum materiil (<strong>KUHPerdata</strong>) atau hukum acara perdata di pengadilan (<strong>HIR</strong>) berdasarkan sistematika buku dan bagian secara terstruktur.
        </p>
      </div>

      {/* Primary Category Switcher: Directly Divided into KUHPerdata vs HIR (No "Semua Koleksi") */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        {/* Source Toggle Tabs */}
        <div className="inline-flex p-1.5 bg-white/95 backdrop-blur-md border border-[#E8DEC9] rounded-2xl shadow-xs font-sans">
          {SOURCE_OPTIONS.map((opt) => {
            const isSelected = selectedSource === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => {
                  setSelectedSource(opt.id);
                  setSelectedCategory(''); // Reset subkategori saat berganti undang-undang
                  setPage(0);
                }}
                className={`px-5 sm:px-7 py-3 rounded-xl transition-all flex items-center gap-3 text-left ${
                  isSelected
                    ? 'bg-[#75162D] text-[#FAF6EE] shadow-sm'
                    : 'text-[#6B5559] hover:text-[#3B010B] hover:bg-[#F2E5C6]/40'
                }`}
              >
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs sm:text-sm">{opt.label}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                        isSelected
                          ? 'bg-[#560B18] text-[#F2E5C6]'
                          : 'bg-[#E8DEC9]/70 text-[#6B5559]'
                      }`}
                    >
                      {opt.count}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] uppercase tracking-wider font-semibold mt-0.5 ${
                      isSelected ? 'text-[#F2D9A0]' : 'text-[#8C7A7C]'
                    }`}
                  >
                    {opt.badge}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Search Input Specific to Active Law */}
        <form onSubmit={handleSearchSubmit} className="relative w-full lg:max-w-md">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              selectedSource === 'HIR'
                ? 'Cari di HIR... (contoh: 164 alat bukti, 227 sita)'
                : 'Cari di KUHPerdata... (contoh: 1320, 1365, waris)'
            }
            className="w-full pl-10 pr-4 py-3.5 rounded-full bg-white/95 border border-[#E8DEC9] text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] shadow-xs font-sans transition-all focus:ring-2 focus:ring-[#75162D]/10"
          />
          <Search className="w-4 h-4 text-[#6B5559] absolute left-3.5 top-4" />
        </form>
      </div>

      {/* Sub-Category Chips for the Selected Law */}
      <div className="bg-white/80 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl p-4 sm:p-5 flex flex-col gap-3 shadow-xs font-sans">
        <div className="flex items-center justify-between gap-2 border-b border-[#FAF6EE] pb-2.5">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#75162D]">
            <Layers className="w-3.5 h-3.5" />
            <span>
              {selectedSource === 'KUHPerdata'
                ? 'Struktur 4 Buku KUHPerdata (Hukum Materiel)'
                : 'Struktur Bagian HIR (Hukum Acara Persidangan)'}
            </span>
          </div>

          {(selectedCategory || searchQuery) && (
            <button
              onClick={resetAllFilters}
              className="text-[11px] font-semibold text-[#8C7A7C] hover:text-[#75162D] flex items-center gap-1 transition-colors"
              title="Reset Filter"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reset Filter</span>
            </button>
          )}
        </div>

        {/* Category Chips Container */}
        <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-none">
          {selectedSource === 'KUHPerdata'
            ? KUHPERDATA_CATEGORIES.map((cat) => {
                const isSelected = selectedCategory === cat.value;
                return (
                  <button
                    key={cat.value}
                    onClick={() => {
                      setSelectedCategory(cat.value);
                      setPage(0);
                    }}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide transition-all whitespace-nowrap flex items-center gap-2 ${
                      isSelected
                        ? 'bg-[#560B18] text-[#F2E5C6] shadow-xs'
                        : 'bg-[#FAF6EE] text-[#560B18] hover:bg-[#F2E5C6] border border-[#E8DEC9]'
                    }`}
                    title={cat.desc || cat.label}
                  >
                    <span>{cat.label}</span>
                  </button>
                );
              })
            : HIR_CATEGORIES.map((cat) => {
                const isSelected = selectedCategory === cat.value;
                return (
                  <button
                    key={cat.value}
                    onClick={() => {
                      setSelectedCategory(cat.value);
                      setPage(0);
                    }}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide transition-all whitespace-nowrap flex items-center gap-2 ${
                      isSelected
                        ? 'bg-[#560B18] text-[#F2E5C6] shadow-xs'
                        : 'bg-[#FAF6EE] text-[#560B18] hover:bg-[#F2E5C6] border border-[#E8DEC9]'
                    }`}
                    title={cat.desc || cat.label}
                  >
                    <span>{cat.label}</span>
                  </button>
                );
              })}
        </div>
      </div>

      {/* Counter & Active Scope Info */}
      <div className="flex flex-wrap items-center justify-between text-xs text-[#6B5559] px-1 font-sans gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span>Menampilkan {articles.length} dari <strong className="text-[#3B010B]">{total}</strong> ketentuan ditemukan</span>
          <span className="px-2.5 py-0.5 rounded-full bg-[#F2E5C6] text-[#560B18] text-[10px] font-bold uppercase">
            Sumber: {selectedSource}
          </span>
          {selectedCategory && (
            <span className="px-2.5 py-0.5 rounded-full bg-[#75162D] text-[#F2E5C6] text-[10px] font-bold">
              {selectedCategory}
            </span>
          )}
        </div>

        {(selectedCategory || searchQuery) && (
          <button
            onClick={resetAllFilters}
            className="text-[11px] font-semibold text-[#75162D] hover:underline"
          >
            Hapus Filter
          </button>
        )}
      </div>

      {/* Grid of Articles */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-[#6B5559] font-sans">
          <RefreshCw className="w-5 h-5 animate-spin text-[#75162D]" />
          <p className="text-xs font-medium">Memuat naskah resmi {selectedSource}...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-16 text-center bg-white/95 border border-[#E8DEC9] rounded-2xl p-8 shadow-xs font-sans">
          <Scale className="w-8 h-8 text-[#8C7A7C] mx-auto mb-2" />
          <p className="text-sm font-bold text-[#3B010B]">Tidak ada pasal yang cocok di {selectedSource}</p>
          <p className="text-xs text-[#6B5559] mt-1">Coba sesuaikan kata kunci atau pilih kategori buku/bagian lainnya.</p>
          <button
            onClick={resetAllFilters}
            className="mt-4 px-5 py-2.5 rounded-full bg-[#75162D] text-[#FAF6EE] text-xs font-bold font-sans hover:bg-[#560B18] transition-colors"
          >
            Tampilkan Seluruh {selectedSource === 'HIR' ? 'HIR (283 Ketentuan)' : 'KUHPerdata (1.993 Ketentuan)'}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {articles.map((art, idx) => (
            <PasalCard
              key={`${art.source}-${art.pasal}-${idx}`}
              article={art}
              index={page * limit + idx}
            />
          ))}
        </div>
      )}

      {/* Clean Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-[#E8DEC9] text-xs font-sans">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white hover:bg-[#F2E5C6]/50 disabled:opacity-30 border border-[#E8DEC9] text-[#560B18] transition-all font-bold shadow-xs"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Sebelumnya</span>
          </button>

          <span className="text-[#6B5559] font-medium">
            Halaman <strong className="text-[#3B010B]">{page + 1}</strong> dari {totalPages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1 || loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white hover:bg-[#F2E5C6]/50 disabled:opacity-30 border border-[#E8DEC9] text-[#560B18] transition-all font-bold shadow-xs"
          >
            <span>Selanjutnya</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

export default function DatabasePage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-6xl mx-auto px-6 py-20 flex justify-center text-xs text-[#6B5559] font-sans">
          Memuat katalog naskah...
        </div>
      }
    >
      <DatabaseContent />
    </Suspense>
  );
}
