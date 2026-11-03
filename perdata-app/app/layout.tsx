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
      <body className="min-h-screen bg-[#FAF6EE] text-[#2A171A] font-sans flex flex-col selection:bg-[#75162D] selection:text-[#F2E5C6] relative overflow-x-hidden">
        {/* Soft Ambient Radial Blur Orbs (Inspired by FloraVerse) */}
        <div className="fixed top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-[#75162D]/5 blur-[120px] pointer-events-none -z-10" />
        <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-[#F2D9A0]/25 blur-[120px] pointer-events-none -z-10" />

        <Navbar />
        <main className="flex-1 pt-28 pb-16">{children}</main>

        {/* FloraVerse-Style Modern Floating Footer Card & Giant Watermark */}
        <footer className="w-full px-4 md:px-8 pb-4 pt-10 flex flex-col items-center font-montserrat overflow-hidden">
          <div className="w-full max-w-6xl bg-white/90 backdrop-blur-md border border-[#E8DEC9] rounded-2xl shadow-sm px-6 md:px-10 py-8 flex flex-col gap-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex flex-col gap-1.5">
                <span className="font-cyntho text-xl font-bold tracking-tight text-[#3B010B]">
                  CiviLex<span className="text-[#75162D]">.AI</span>
                </span>
                <p className="text-xs text-[#6B5559] max-w-sm leading-relaxed font-montserrat">
                  Platform Asistensi Penelusuran dan Analisis Naskah Resmi KUHPerdata dan HIR Berbasis Kecerdasan Buatan.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs font-semibold text-[#6B5559]">
                <span className="px-3 py-1 rounded-full bg-[#F2E5C6]/60 text-[#560B18]">2.276 Ketentuan</span>
                <span className="px-3 py-1 rounded-full bg-[#F2E5C6]/60 text-[#560B18]">Naskah Resmi JDIH</span>
                <span className="text-[#8C7A7C]">© 2026 CiviLex AI</span>
              </div>
            </div>

            {/* Official Legal Disclaimer Box */}
            <div className="pt-4 border-t border-[#E8DEC9] text-[11px] text-[#7A6B6E] leading-relaxed">
              <p>
                <strong>Penafian Hukum (Disclaimer):</strong> CiviLex AI dikembangkan sebagai sarana edukasi dan alat bantu penelusuran referensi naskah hukum resmi. Informasi dan hasil pencarian yang disajikan oleh sistem ini <u>bukan merupakan nasihat, pendapat hukum, atau pengganti jasa konsultasi hukum profesional</u> dari advokat/penasihat hukum berlisensi. Untuk keputusan hukum konkret, selalu rujuk naskah resmi Lembaran Negara dan konsultasikan pada praktisi hukum berwenang.
              </p>
            </div>
          </div>

          {/* FloraVerse-Style Giant Ghost Typography Watermark at the Bottom */}
          <div className="relative w-full max-w-6xl select-none pointer-events-none mt-6 overflow-hidden" aria-hidden="true">
            <span
              className="block text-center font-cyntho font-bold tracking-tight text-[#3B010B]/5 leading-none"
              style={{ fontSize: 'clamp(3.5rem, 13vw, 9.5rem)' }}
            >
              CIVILEX AI
            </span>
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[#FAF6EE] to-transparent" />
          </div>
        </footer>
      </body>
    </html>
  );
}
