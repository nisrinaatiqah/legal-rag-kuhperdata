'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Scale } from 'lucide-react';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

const SOURCE_OPTIONS = [
  { label: 'Semua Koleksi (2.276)', value: '', desc: 'KUHPerdata & HIR' },
  { label: 'KUHPerdata (1.993)', value: 'KUHPerdata', desc: 'Hukum Materiel' },
  { label: 'HIR — Acara Perdata (283)', value: 'HIR', desc: 'Hukum Formil Persidangan' },
];

function DatabaseContent() {
  const searchParams = useSearchParams();
  const initialSource = searchParams.get('source') || '';
  const initialQuery = searchParams.get('q') || '';

  const [articles, setArticles] = useState<ArticleDoc[]>([]);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [selectedSource, setSelectedSource] = useState(initialSource);
  const [page, setPage] = useState(0);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(false);

  // Sync if query params change
  useEffect(() => {
    const s = searchParams.get('source');
    const q = searchParams.get('q');
    if (s !== null) setSelectedSource(s);
    if (q !== null) setSearchQuery(q);
  }, [searchParams]);

  const fetchArticles = async (q: string, source: string, pageNum: number) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.append('q', q.trim());
      if (source) params.append('source', source);
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
    fetchArticles(searchQuery, selectedSource, page);
  }, [page, selectedSource]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    fetchArticles(searchQuery, selectedSource, 0);
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
          Katalog 2.276 Ketentuan{' '}
          <span className="font-italiana text-[#75162D] normal-case text-4xl sm:text-5xl md:text-6xl block sm:inline">
            KUHPerdata &amp; HIR
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-2xl font-montserrat font-medium mt-1 leading-relaxed">
          Pustaka terpadu naskah resmi Lembaran Negara dan JDIH Nasional. Telusuri seluruh ketentuan hukum materiel maupun hukum acara secara terstruktur dalam satu pangkalan data.
        </p>
      </div>

      {/* Clean Structured Search and Tab Filter Controls */}
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

      {/* Counter & Active Scope Info */}
      <div className="flex items-center justify-between text-xs text-[#6B5559] px-1 font-montserrat">
        <div>
          Menampilkan {articles.length} dari <strong className="text-[#3B010B]">{total}</strong> ketentuan ditemukan
          {selectedSource && (
            <span className="ml-2 px-2.5 py-0.5 rounded-full bg-[#F2E5C6] text-[#560B18] text-[10px] font-bold uppercase">
              Filter: {selectedSource}
            </span>
          )}
        </div>
        {selectedSource && (
          <button
            onClick={() => {
              setSelectedSource('');
              setPage(0);
            }}
            className="text-[11px] font-semibold text-[#75162D] hover:underline"
          >
            Tampilkan Semua Regulasi
          </button>
        )}
      </div>

      {/* Grid of Articles */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-[#6B5559] font-montserrat">
          <RefreshCw className="w-5 h-5 animate-spin text-[#75162D]" />
          <p className="text-xs font-medium">Memuat naskah resmi...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-16 text-center bg-white/95 border border-[#E8DEC9] rounded-2xl p-8 shadow-xs font-montserrat">
          <Scale className="w-8 h-8 text-[#8C7A7C] mx-auto mb-2" />
          <p className="text-sm font-bold text-[#3B010B]">Tidak ada pasal yang cocok</p>
          <p className="text-xs text-[#6B5559] mt-1">Coba gunakan kata kunci atau nomor pasal lain.</p>
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
