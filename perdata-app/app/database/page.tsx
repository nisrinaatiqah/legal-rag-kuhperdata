'use client';

import { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Scale } from 'lucide-react';
import PasalCard, { ArticleDoc } from '../components/PasalCard';

const SOURCE_OPTIONS = [
  { label: 'Semua Koleksi (2.276)', value: '' },
  { label: 'KUHPerdata (1.993)', value: 'KUHPerdata' },
  { label: 'HIR — Acara Perdata (283)', value: 'HIR' },
];

export default function DatabasePage() {
  const [articles, setArticles] = useState<ArticleDoc[]>([]);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [page, setPage] = useState(0);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(false);

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
    <div className="max-w-5xl mx-auto px-6 flex flex-col gap-8 pb-12 font-body">
      {/* Editorial Header in Cinzel & Cormorant */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-cinzel">
          Basis Data Kodifikasi
        </span>
        <h1 className="font-cinzel text-2xl md:text-3xl font-bold tracking-wider text-[#3B010B]">
          Katalog 2.276 Pasal{' '}
          <span className="font-cormorant italic font-normal text-[#75162D] text-3xl md:text-4xl normal-case">
            KUHPerdata &amp; HIR
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-xl">
          Naskah resmi dari Lembaran Negara dan JDIH Nasional, terverifikasi utuh dan bebas dari distorsi data.
        </p>
      </div>

      {/* Clean Search and Filter Controls */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:max-w-md">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari nomor pasal atau kata kunci (contoh: 1320, ganti rugi, waris)..."
            className="w-full pl-11 pr-5 py-3 rounded-full bg-white border border-[#E8DEC9] text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] shadow-sm font-body"
          />
          <Search className="w-4 h-4 text-[#6B5559] absolute left-4 top-3.5" />
        </form>

        {/* Source Pills in Cinzel */}
        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          {SOURCE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => {
                setSelectedSource(opt.value);
                setPage(0);
              }}
              className={`px-4 py-2 rounded-full text-xs font-semibold tracking-wider font-cinzel transition-all whitespace-nowrap ${
                selectedSource === opt.value
                  ? 'bg-[#75162D] text-[#F2E5C6] shadow-sm'
                  : 'bg-white text-[#560B18] hover:bg-[#F2E5C6]/50 border border-[#E8DEC9]'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Counter */}
      <div className="text-xs text-[#6B5559] px-1 font-medium font-body">
        Menampilkan {articles.length} dari <strong className="text-[#3B010B]">{total}</strong> pasal ditemukan
      </div>

      {/* Grid of Articles */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-[#6B5559]">
          <RefreshCw className="w-5 h-5 animate-spin text-[#75162D]" />
          <p className="text-xs font-medium">Memuat naskah resmi...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-16 text-center law-card rounded-2xl p-8">
          <Scale className="w-8 h-8 text-[#8C7A7C] mx-auto mb-2" />
          <p className="text-sm font-semibold text-[#3B010B] font-cinzel">Tidak ada pasal yang cocok</p>
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

      {/* Clean Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-[#E8DEC9] text-xs">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white hover:bg-[#F2E5C6]/50 disabled:opacity-30 border border-[#E8DEC9] text-[#560B18] transition-all font-cinzel font-semibold"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Sebelumnya</span>
          </button>

          <span className="text-[#6B5559] font-medium font-body">
            Halaman {page + 1} dari {totalPages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1 || loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white hover:bg-[#F2E5C6]/50 disabled:opacity-30 border border-[#E8DEC9] text-[#560B18] transition-all font-cinzel font-semibold"
          >
            <span>Selanjutnya</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
