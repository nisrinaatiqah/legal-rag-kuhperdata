import type { Metadata } from 'next';
import './globals.css';
import Navbar from './components/Navbar';

export const metadata: Metadata = {
  title: 'LexPerdata AI — Sistem Tanya Jawab Hukum Perdata & Pertahanan Knowledge Poisoning',
  description:
    'Sistem Legal Question Answering Hukum Perdata & Acara Perdata Indonesia (KUHPerdata & HIR) Berbasis RAG dengan Mekanisme Pertahanan Two-Tier Knowledge Poisoning (SHA-256 + NLI).',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-indigo-600 selection:text-white">
        <Navbar />
        <main className="flex-1 pt-24 pb-16">{children}</main>
        
        {/* Footer */}
        <footer className="border-t border-slate-800/80 bg-slate-950/60 py-8 px-6 text-center text-xs text-slate-400">
          <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-left">
              <p className="font-semibold text-slate-200">LexPerdata AI — Sistem LQA Hukum Perdata & Acara Perdata</p>
              <p className="text-[11px] text-slate-400">
                Tugas Akhir Sarjana — Departemen Teknologi Informasi, FTEIC, Institut Teknologi Sepuluh Nopember (ITS)
              </p>
            </div>
            <div className="flex items-center gap-4 text-[11px] text-slate-400">
              <span>NRP: 5027231075</span>
              <span>•</span>
              <span>Two-Tier Defense Framework</span>
              <span>•</span>
              <span>KUHPerdata (1.993) & HIR (283)</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
