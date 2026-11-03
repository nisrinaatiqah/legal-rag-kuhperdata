'use client';

import { useState, useEffect } from 'react';
import { Search, BookOpen, Filter, Hash, ChevronLeft, ChevronRight, RefreshCw, Scale } from 'lucide-react';
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
  const [limit] = useState(15);
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
        // Fallback directly to localhost:8000
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
    <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <BookOpen className="w-4 h-4" /> Basis Data Kodifikasi Hukum Nasional
        </div>
        <h1 className="font-legal-title text-3xl font-bold text-white">
          Katalog 2.276 Pasal Resmi KUHPerdata &amp; HIR
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
          Seluruh naskah diekstraksi dari Lembaran Negara dan JDIH resmi, dipartisi dengan skenario C1 (Single-Article Granularity) dan dilengkapi nilai SHA-256 terverifikasi.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-card rounded-2xl p-4 border border-slate-700/60 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:max-w-md">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari nomor pasal atau kata kunci (contoh: 1320, ganti rugi, waris)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        </form>

        {/* Source Filter Tabs */}
        <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          {SOURCE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => {
                setSelectedSource(opt.value);
                setPage(0);
              }}
              className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                selectedSource === opt.value
                  ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/50 shadow-sm'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats and Count */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>
          Menampilkan {articles.length} dari <strong className="text-white">{total}</strong> pasal ditemukan
        </span>
        <span className="font-mono text-[11px] text-emerald-400 flex items-center gap-1">
          <Hash className="w-3.5 h-3.5" /> 100% SHA-256 JDIH Valid
        </span>
      </div>

      {/* Articles Grid List */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-400">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
          <p className="text-xs">Memuat data pasal resmi...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-20 glass-card rounded-2xl text-center text-slate-400 p-8">
          <Scale className="w-10 h-10 text-slate-500 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-200">Tidak ada pasal yang cocok</p>
          <p className="text-xs text-slate-500 mt-1">Coba gunakan kata kunci atau nomor pasal lain.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3.5">
          {articles.map((art, idx) => (
            <PasalCard key={`${art.source}-${art.pasal}-${idx}`} article={art} index={page * limit + idx} />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-slate-800 text-slate-200 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Sebelumnya</span>
          </button>

          <span className="text-slate-400 font-mono text-[11px]">
            Halaman {page + 1} dari {totalPages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1 || loading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-slate-800 text-slate-200 transition-colors"
          >
            <span>Selanjutnya</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
