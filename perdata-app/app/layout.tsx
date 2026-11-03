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
      <body className="min-h-screen bg-[#FAF6EE] text-[#2A171A] font-body flex flex-col selection:bg-[#75162D] selection:text-[#F2E5C6]">
        <Navbar />
        <main className="flex-1 pt-24 pb-16">{children}</main>

        {/* Editorial Footer in Champagne Beige & Deep Wine */}
        <footer className="border-t border-[#E8DEC9] bg-[#F2E5C6]/40 py-12 px-6 text-[#6B5559]">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex flex-col gap-1">
              <span className="font-display text-2xl font-bold text-[#3B010B]">
                LexPerdata<span className="text-[#75162D]">.</span>
              </span>
              <p className="text-xs text-[#6B5559] max-w-sm leading-relaxed">
                Sistem Tanya Jawab Cerdas Hukum Perdata Material (KUHPerdata) dan Formil (HIR) dengan Perlindungan Integritas Naskah Resmi.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs text-[#6B5559]">
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
