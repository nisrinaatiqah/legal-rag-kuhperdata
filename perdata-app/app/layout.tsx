import type { Metadata } from 'next';
import './globals.css';
import Navbar from './components/Navbar';

export const metadata: Metadata = {
  title: 'CiviLex AI — Asisten Penelusuran & Referensi Hukum Perdata Indonesia',
  description:
    'Alat bantu cerdas berbasis AI untuk penelusuran naskah resmi KUHPerdata dan HIR dengan jaminan keaslian data JDIH.',
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

        {/* Real-World Professional Product Footer with Prominent Legal Disclaimer */}
        <footer className="border-t border-[#E8DEC9] bg-[#F2E5C6]/40 py-12 px-6 text-[#6B5559]">
          <div className="max-w-6xl mx-auto flex flex-col gap-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex flex-col gap-1.5">
                <span className="font-serif text-xl font-normal tracking-wide text-[#3B010B]">
                  CiviLex<span className="text-[#75162D] font-bold">.AI</span>
                </span>
                <p className="text-xs text-[#6B5559] max-w-sm leading-relaxed font-sans">
                  Platform Asistensi Penelusuran dan Analisis Naskah Resmi KUHPerdata dan HIR Berbasis Kecerdasan Buatan.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs text-[#6B5559]">
                <span>2.276 Pasal Terkodifikasi</span>
                <span>•</span>
                <span>Naskah Resmi JDIH</span>
                <span>•</span>
                <span>© 2026 CiviLex AI • Hak Cipta Dilindungi</span>
              </div>
            </div>

            {/* Official Legal Disclaimer Box */}
            <div className="pt-6 border-t border-[#E8DEC9]/60 text-[11px] text-[#7A6B6E] leading-relaxed">
              <p>
                <strong>Penafian Hukum (Disclaimer):</strong> CiviLex AI dikembangkan sebagai sarana edukasi dan alat bantu penelusuran referensi naskah hukum resmi. Informasi dan hasil pencarian yang disajikan oleh sistem ini <u>bukan merupakan nasihat, pendapat hukum, atau pengganti jasa konsultasi hukum profesional</u> dari advokat/penasihat hukum berlisensi. Untuk penanganan perkara konkret atau keputusan hukum resmi, selalu rujuk naskah asli Lembaran Negara dan konsultasikan kepada praktisi hukum yang berwenang.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
