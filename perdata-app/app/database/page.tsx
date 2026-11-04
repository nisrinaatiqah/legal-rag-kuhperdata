'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, ChevronLeft, ChevronRight, RefreshCw, Scale, X, Layers, ChevronDown } from 'lucide-react';
import PasalCard, { ArticleDoc } from '../components/PasalCard';
import kuhperdataBabsData from './kuhperdata_babs.json';

const KUHPERDATA_QUICK_BABS = [
  { value: '', label: 'Semua Bab (1.993)' },
  { value: 'BUKU KETIGA:BAB II', label: 'Bab II: Perjanjian & Kontrak (1320)' },
  { value: 'BUKU KETIGA:BAB III', label: 'Bab III: PMH & Ganti Rugi (1365)' },
  { value: 'BUKU KETIGA:BAB IV', label: 'Bab IV: Hapusnya Perikatan' },
  { value: 'BUKU KETIGA:BAB V', label: 'Bab V: Jual Beli' },
  { value: 'BUKU KETIGA:BAB VII', label: 'Bab VII: Sewa Menyewa' },
  { value: 'BUKU KEDUA:BAB XII', label: 'Bab XII: Waris & Kematian' },
  { value: 'BUKU KEDUA:BAB XIII', label: 'Bab XIII: Surat Wasiat' },
  { value: 'BUKU KEDUA:BAB XXI', label: 'Bab XXI: Hipotek' },
  { value: 'BUKU KEDUA:BAB XX', label: 'Bab XX: Gadai (Pand)' },
  { value: 'BUKU KEEMPAT:BAB II', label: 'Bab II: Bukti Tertulis / Akta' },
  { value: 'BUKU KESATU:BAB IV', label: 'Bab IV: Perkawinan & Harta' },
];

const HIR_CATEGORIES = [
  { label: 'Semua Bagian (283 Ketentuan)', value: '', count: '283' },
  { label: 'Bagian 1: Pemeriksaan & Gugatan (Pasal 118–161)', value: 'Bagian 1', count: '51' },
  { label: 'Bagian 2: 5 Alat Bukti Persidangan (Pasal 162–185)', value: 'Bagian 2', count: '15' },
  { label: 'Bagian 3: Musyawarah & Putusan (Pasal 186–194)', value: 'Bagian 3', count: '10' },
  { label: 'Bagian 4: Upaya Banding (Pasal 195–205)', value: 'Bagian 4', count: '9' },
  { label: 'Bagian 5: Eksekusi & Sita Jaminan (Pasal 206–240)', value: 'Bagian 5', count: '35' },
  { label: 'Bagian 6: Perkara Istimewa (Pasal 241–245)', value: 'Bagian 6', count: '14' },
  { label: 'Bab XV: Berbagai Peraturan (Pasal 372–394)', value: 'BAB XV', count: '16' },
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

  const getCategoryLabel = (catVal: string) => {
    if (!catVal) return '';
    if (selectedSource === 'KUHPerdata') {
      const found = (kuhperdataBabsData as any[]).find((b) => b.value === catVal);
      return found ? found.label : catVal;
    } else {
      const found = HIR_CATEGORIES.find((b) => b.value === catVal);
      return found ? found.label : catVal;
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="max-w-6xl mx-auto px-6 flex flex-col gap-8 pb-12 font-sans">
      {/* Header in Hybrid B + D Style (Bodoni Moda + Bellefair) */}
      <div className="flex flex-col gap-2 border-b border-[#E8DEC9] pb-6">
        <span className="text-[11px] font-bold tracking-widest uppercase text-[#75162D] font-sans">
          Pangkalan Data Naskah Resmi
        </span>
        <h1 className="font-bodoni text-3xl sm:text-4xl md:text-5xl font-medium tracking-normal text-[#3B010B]">
          Database Ketentuan{' '}
          <span className="font-bellefair text-[#75162D] italic normal-case text-3xl sm:text-4xl md:text-5xl block sm:inline tracking-wide">
            {selectedSource === 'HIR' ? 'HIR' : 'KUHPerdata'}
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-[#6B5559] max-w-2xl font-sans font-normal mt-1 leading-relaxed">
          {selectedSource === 'HIR'
            ? 'Pustaka 283 ketentuan hukum acara perdata dari sumber terpercaya. Telusuri tata cara sidang, sita jaminan, dan pembuktian.'
            : 'Pustaka 1.993 pasal hukum perdata materiil dari sumber terpercaya. Telusuri ketentuan orang, kebendaan, perikatan, dan pembuktian.'}
        </p>
      </div>

      {/* Search Input Specific to Active Law */}
      <form onSubmit={handleSearchSubmit} className="relative w-full">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={
            selectedSource === 'HIR'
              ? 'Cari di ketentuan HIR... (contoh: 164 alat bukti, 227 sita jaminan, putusan)'
              : 'Cari di ketentuan KUHPerdata... (contoh: 1320 syarat sah, 1365 PMH, waris)'
          }
          className="w-full pl-11 pr-4 py-3.5 rounded-full bg-white/95 border border-[#E8DEC9] text-xs sm:text-sm text-[#2A171A] placeholder-[#8C7A7C] focus:outline-none focus:border-[#75162D] shadow-xs font-sans transition-all focus:ring-2 focus:ring-[#75162D]/10"
        />
        <Search className="w-4 h-4 text-[#6B5559] absolute left-4 top-4" />
      </form>

      {/* Scope Navigation / Bab Filter */}
      <div className="bg-white/80 backdrop-blur-sm border border-[#E8DEC9] rounded-2xl p-4 sm:p-5 flex flex-col gap-3.5 shadow-xs font-sans">
        <div className="flex items-center justify-between gap-2 border-b border-[#FAF6EE] pb-2.5">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#75162D]">
            <Layers className="w-3.5 h-3.5" />
            <span>
              {selectedSource === 'KUHPerdata'
                ? 'Filter Bab KUHPerdata (Hukum Materiel)'
                : 'Filter Bagian HIR (Hukum Acara Formil)'}
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

        {/* Dropdown Bab Selector: Covers All 63 Babs of KUHPerdata or All HIR Sections */}
        <div className="relative w-full">
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(0);
            }}
            className="w-full appearance-none px-4 py-2.5 pr-10 rounded-xl bg-white border border-[#E8DEC9] text-xs sm:text-sm font-semibold text-[#3B010B] focus:outline-none focus:border-[#75162D] shadow-2xs cursor-pointer hover:border-[#75162D]/60 transition-colors"
          >
            <option value="">
              {selectedSource === 'KUHPerdata'
                ? '— Pilih Bab Spesifik (Semua 63 Bab / 1.993 Pasal) —'
                : '— Pilih Bagian HIR (Semua Bagian / 283 Ketentuan) —'}
            </option>
            {selectedSource === 'KUHPerdata' ? (
              <>
                <optgroup label="Buku I: Tentang Orang & Keluarga (18 Bab)">
                  {(kuhperdataBabsData as any[])
                    .filter((b) => b.buku === 'BUKU KESATU')
                    .map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.label}
                      </option>
                    ))}
                </optgroup>
                <optgroup label="Buku II: Tentang Kebendaan & Waris (21 Bab)">
                  {(kuhperdataBabsData as any[])
                    .filter((b) => b.buku === 'BUKU KEDUA')
                    .map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.label}
                      </option>
                    ))}
                </optgroup>
                <optgroup label="Buku III: Tentang Perikatan & Kontrak (18 Bab)">
                  {(kuhperdataBabsData as any[])
                    .filter((b) => b.buku === 'BUKU KETIGA')
                    .map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.label}
                      </option>
                    ))}
                </optgroup>
                <optgroup label="Buku IV: Tentang Pembuktian & Daluwarsa (6 Bab)">
                  {(kuhperdataBabsData as any[])
                    .filter((b) => b.buku === 'BUKU KEEMPAT')
                    .map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.label}
                      </option>
                    ))}
                </optgroup>
              </>
            ) : (
              HIR_CATEGORIES.filter((h) => h.value !== '').map((h) => (
                <option key={h.value} value={h.value}>
                  {h.label}
                </option>
              ))
            )}
          </select>
          <ChevronDown className="w-4 h-4 text-[#75162D] absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Quick Bab Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none">
          <span className="text-[10px] font-bold text-[#8C7A7C] uppercase tracking-wider shrink-0 mr-1 font-sans">
            Akses Cepat:
          </span>
          {(selectedSource === 'KUHPerdata' ? KUHPERDATA_QUICK_BABS : HIR_CATEGORIES).map((cat) => {
            const isSelected = selectedCategory === cat.value;
            return (
              <button
                key={cat.value}
                onClick={() => {
                  setSelectedCategory(cat.value);
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold tracking-normal transition-all whitespace-nowrap shrink-0 ${
                  isSelected
                    ? 'bg-[#560B18] text-[#F2E5C6] shadow-xs ring-1 ring-[#560B18]'
                    : 'bg-[#FAF6EE] text-[#560B18] hover:bg-[#F2E5C6] border border-[#E8DEC9]'
                }`}
              >
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Active Bab Indicator */}
        {selectedCategory && (
          <div className="flex items-center gap-2 pt-2 border-t border-[#FAF6EE]">
            <span className="text-[11px] text-[#6B5559] font-medium">Bab Aktif:</span>
            <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#75162D] text-[#F2E5C6] text-xs font-bold shadow-2xs">
              <span>{getCategoryLabel(selectedCategory)}</span>
              <button
                onClick={() => setSelectedCategory('')}
                className="hover:text-white transition-colors"
                title="Hapus Filter Bab"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          </div>
        )}
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
              {getCategoryLabel(selectedCategory)}
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
          Memuat database naskah...
        </div>
      }
    >
      <DatabaseContent />
    </Suspense>
  );
}
