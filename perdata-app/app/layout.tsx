import type { Metadata } from 'next';
import './globals.css';
import Navbar from './components/Navbar';

export const metadata: Metadata = {
  title: 'LexPerdata — Sistem Tanya Jawab Hukum Perdata & Acara Perdata Indonesia',
  description:
    'Sistem konsultasi cerdas berbasis KUHPerdata dan HIR dengan jaminan keaslian naskah hukum resmi JDIH.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="min-h-screen bg-[#faf7f2] text-[#1c1917] flex flex-col selection:bg-[#7a1827] selection:text-white">
        <Navbar />
        <main className="flex-1 pt-24 pb-16">{children}</main>

        {/* Elegant Editorial Footer */}
        <footer className="border-t border-[#e7dfd5] bg-[#f5f0ea] py-12 px-6 text-[#57534e]">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex flex-col gap-1">
              <span className="font-editorial-title text-xl font-bold text-[#1c1917]">
                LexPerdata<span className="text-[#7a1827]">.</span>
              </span>
              <p className="text-xs text-[#78716c] max-w-sm">
                Sistem Tanya Jawab Cerdas Hukum Perdata Material (KUHPerdata) dan Formil (HIR) dengan Perlindungan Integritas Naskah Resmi.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs text-[#78716c]">
              <span>2.276 Pasal Terkodifikasi</span>
              <span>•</span>
              <span>Departemen Teknologi Informasi — FTEIC ITS</span>
              <span>•</span>
              <span>NRP: 5027231075</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
