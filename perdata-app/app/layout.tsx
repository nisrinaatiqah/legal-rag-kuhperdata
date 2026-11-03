import type { Metadata } from 'next';
import './globals.css';
import Navbar from './components/Navbar';

export const metadata: Metadata = {
  title: 'CiviLex AI — Asisten Penelusuran & Referensi Hukum Perdata Indonesia',
  description:
    'Alat bantu cerdas berbasis AI untuk penelusuran naskah resmi KUHPerdata dan HIR dari sumber terpercaya.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="min-h-screen bg-[#FAF6EE] text-[#2A171A] font-sans flex flex-col selection:bg-[#75162D] selection:text-[#F2E5C6] relative overflow-x-hidden">
        {/* Soft Ambient Radial Blur Orbs (Inspired by FloraVerse) */}
        <div className="fixed top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-[#75162D]/5 blur-[120px] pointer-events-none -z-10" />
        <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-[#F2D9A0]/25 blur-[120px] pointer-events-none -z-10" />

        <Navbar />
        <main className="flex-1 pt-28 pb-16">{children}</main>

        {/* Real-World Professional Product Footer attached directly to the bottom */}
        <footer className="w-full border-t border-[#E8DEC9] bg-[#F2E5C6]/40 py-10 px-6 text-[#6B5559] font-montserrat mt-auto">
          <div className="max-w-6xl mx-auto flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <span className="font-marcellus text-xl font-bold tracking-wide text-[#3B010B]">
                CiviLex<span className="text-[#75162D]">.AI</span>
              </span>

              <p className="text-xs text-[#6B5559] font-montserrat">
                Made by <span className="font-semibold text-[#3B010B]">Nisrina Atiqah Dwiputri Ridzki (5027231075)</span>
              </p>
            </div>

            {/* Official Legal Disclaimer Box */}
            <div className="pt-6 border-t border-[#E8DEC9]/60 text-[11px] text-[#7A6B6E] leading-relaxed">
              <p>
                <strong>Disclaimer:</strong> CiviLex AI dikembangkan sebagai sarana edukasi dan alat bantu penelusuran referensi naskah hukum resmi. Informasi dan hasil pencarian yang disajikan oleh sistem ini <u>bukan merupakan nasihat, pendapat hukum, atau pengganti jasa konsultasi hukum profesional</u> dari advokat/penasihat hukum berlisensi. Untuk penanganan perkara konkret atau keputusan hukum resmi, selalu rujuk naskah asli Lembaran Negara dan konsultasikan kepada praktisi hukum yang berwenang.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
