'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Scale, X, Layers, Filter } from 'lucide-react';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

const SOURCE_OPTIONS = [
  { label: 'Semua Koleksi Database', value: '', desc: 'KUHPerdata & HIR Terpadu' },
  { label: 'KUHPerdata (1.993)', value: 'KUHPerdata', desc: 'Hukum Perdata Materiel' },
  { label: 'HIR — Acara Perdata (283)', value: 'HIR', desc: 'Hukum Acara Formil di Pengadilan' },
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

const UNIFIED_QUICK_CATEGORIES = [
  { label: 'Semua Subjek Database', source: '', category: '' },
  { label: 'Perikatan & Perjanjian', source: 'KUHPerdata', category: 'BUKU KETIGA' },
  { label: 'Kebendaan & Waris', source: 'KUHPerdata', category: 'BUKU KEDUA' },
  { label: 'Sita Jaminan & Eksekusi', source: 'HIR', category: 'Bagian 5' },
  { label: 'Alat Bukti Persidangan', source: 'HIR', category: 'Bagian 2' },
  { label: 'Orang & Keluarga', source: 'KUHPerdata', category: 'BUKU KESATU' },
  { label: 'Pembuktian Materiel', source: 'KUHPerdata', category: 'BUKU KEEMPAT' },
  { label: 'Pemeriksaan Gugatan', source: 'HIR', category: 'Bagian 1' },
];

function DatabaseContent() {
  const searchParams = useSearchParams();
  const initialSource = searchParams.get('source') || '';
  const initialQuery = searchParams.get('q') || '';
  const initialCategory = searchParams.get('category') || '';

  const [articles, setArticles] = useState<ArticleDoc[]>([]);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [selectedSource, setSelectedSource] = useState(initialSource);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [page, setPage] = useState(0);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(false);

  // Sync if query params change
  useEffect(() => {
    const s = searchParams.get('source');
    const q = searchParams.get('q');
    const c = searchParams.get('category');
    if (s !== null) setSelectedSource(s);
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
    setSelectedSource('');
    setSelectedCategory('');
    setSearchQuery('');
    setPage(0);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="max-w-6xl mx-auto px-6 flex flex-col gap-8 pb-12 font-body">
      {/* Header with Marcellus & Italiana Typography */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-montserrat">
          Pangkalan Data Naskah Resmi
        </span>
        <h1 className="font-marcellus text-3xl sm:text-4xl md:text-5xl font-normal tracking-wide text-[#3B010B]">
          Database{' '}
          <span className="font-italiana text-[#75162D] normal-case text-4xl sm:text-5xl md:text-6xl block sm:inline">
            KUHPerdata &amp; HIR
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-2xl font-montserrat font-medium mt-1 leading-relaxed">
          Pustaka terpadu naskah resmi Lembaran Negara dan JDIH Nasional. Saring pasal berdasarkan klasifikasi buku materiel maupun tahapan hukum acara persidangan.
        </p>
      </div>

      {/* Primary Level Filter: Search & Source Tabs */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        {/* Search Input: Floraverse Rounded-Full Style */}
        <form onSubmit={handleSearchSubmit} className="relative w-full lg:max-w-md">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari nomor pasal atau kata kunci (contoh: 1320, ganti rugi, waris)..."
            className="w-full pl-10 pr-4 py-3 rounded-full bg-white/95 border border-[#E8DEC9] text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] shadow-xs font-montserrat"
          />
          <Search className="w-4 h-4 text-[#6B5559] absolute left-3.5 top-3.5" />
        </form>

        {/* Source Filter Tabs: Clean Segmented Pill Switcher */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0 font-montserrat">
          {SOURCE_OPTIONS.map((opt) => {
            const isSelected = selectedSource === opt.value;
            return (
              <button
                key={opt.value}
                onClick={() => {
                  setSelectedSource(opt.value);
                  setSelectedCategory(''); // Reset sub-kategori saat ganti sumber
                  setPage(0);
                }}
                className={`px-4 py-2.5 rounded-full text-xs font-bold tracking-wide transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-[#75162D] text-[#F2E5C6] shadow-sm'
                    : 'bg-white/90 text-[#560B18] hover:bg-[#F2E5C6]/50 border border-[#E8DEC9]'
                }`}
              >
                <span>{opt.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Secondary Level Filter: Granular Sub-Category Chips */}
      <div className="bg-white/80 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl p-4 sm:p-5 flex flex-col gap-3 shadow-xs font-montserrat">
        <div className="flex items-center justify-between gap-2 border-b border-[#FAF6EE] pb-2.5">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#75162D]">
            <Layers className="w-3.5 h-3.5" />
            <span>
              {selectedSource === 'KUHPerdata'
                ? 'Kategori 4 Buku KUHPerdata (Hukum Materiel)'
                : selectedSource === 'HIR'
                ? 'Kategori Bagian HIR (Hukum Acara Persidangan)'
                : 'Klasifikasi Subjek Regulasi Populer'}
            </span>
          </div>

          {(selectedSource || selectedCategory || searchQuery) && (
            <button
              onClick={resetAllFilters}
              className="text-[11px] font-semibold text-[#8C7A7C] hover:text-[#75162D] flex items-center gap-1 transition-colors"
              title="Reset Semua Filter"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reset Filter</span>
            </button>
          )}
        </div>

        {/* Category Chips Container */}
        <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-none">
          {selectedSource === 'KUHPerdata' ? (
            KUHPERDATA_CATEGORIES.map((cat) => {
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
          ) : selectedSource === 'HIR' ? (
            HIR_CATEGORIES.map((cat) => {
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
          ) : (
            UNIFIED_QUICK_CATEGORIES.map((cat, idx) => {
              const isSelected = selectedSource === cat.source && selectedCategory === cat.category;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setSelectedSource(cat.source);
                    setSelectedCategory(cat.category);
                    setPage(0);
                  }}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide transition-all whitespace-nowrap flex items-center gap-2 ${
                    isSelected
                      ? 'bg-[#560B18] text-[#F2E5C6] shadow-xs'
                      : 'bg-[#FAF6EE] text-[#560B18] hover:bg-[#F2E5C6] border border-[#E8DEC9]'
                  }`}
                >
                  <span>{cat.label}</span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Counter & Active Scope Info */}
      <div className="flex flex-wrap items-center justify-between text-xs text-[#6B5559] px-1 font-montserrat gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span>Menampilkan {articles.length} dari <strong className="text-[#3B010B]">{total}</strong> ketentuan ditemukan</span>
          {selectedSource && (
            <span className="px-2.5 py-0.5 rounded-full bg-[#F2E5C6] text-[#560B18] text-[10px] font-bold uppercase">
              Sumber: {selectedSource}
            </span>
          )}
          {selectedCategory && (
            <span className="px-2.5 py-0.5 rounded-full bg-[#75162D] text-[#F2E5C6] text-[10px] font-bold">
              Kategori: {selectedCategory}
            </span>
          )}
        </div>

        {(selectedSource || selectedCategory || searchQuery) && (
          <button
            onClick={resetAllFilters}
            className="text-[11px] font-semibold text-[#75162D] hover:underline"
          >
            Hapus Semua Filter
          </button>
        )}
      </div>

      {/* Grid of Articles */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-[#6B5559] font-montserrat">
          <RefreshCw className="w-5 h-5 animate-spin text-[#75162D]" />
          <p className="text-xs font-medium">Memuat naskah resmi terverifikasi...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-16 text-center bg-white/95 border border-[#E8DEC9] rounded-2xl p-8 shadow-xs font-montserrat">
          <Scale className="w-8 h-8 text-[#8C7A7C] mx-auto mb-2" />
          <p className="text-sm font-bold text-[#3B010B]">Tidak ada pasal yang cocok</p>
          <p className="text-xs text-[#6B5559] mt-1">Coba sesuaikan kata kunci atau pilih kategori buku/bagian lainnya.</p>
          <button
            onClick={resetAllFilters}
            className="mt-4 px-4 py-2 rounded-full bg-[#75162D] text-[#FAF6EE] text-xs font-bold font-montserrat hover:bg-[#560B18] transition-colors"
          >
            Tampilkan Seluruh Database
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

      {/* Clean Floraverse-Style Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-[#E8DEC9] text-xs font-montserrat">
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
        <div className="max-w-6xl mx-auto px-6 py-20 flex justify-center text-xs text-[#6B5559] font-montserrat">
          Memuat katalog naskah...
        </div>
      }
    >
      <DatabaseContent />
    </Suspense>
  );
}
