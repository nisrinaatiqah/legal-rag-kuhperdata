"""
Modul: Ingestion - Inspeksi PDF Hukum (KUHPerdata & HIR)
Fungsi: Memeriksa kualitas ekstraksi teks pada file PDF mentah tanpa mengubah isi file aslinya.
Digunakan sebelum ekstraksi penuh untuk memastikan tidak ada halaman yang kosong/rusak.
"""
from __future__ import annotations

import re
from pathlib import Path
import pymupdf

# [KONFIGURASI DIREKTORI]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "raw_trusted"


def inspect_pdf(pdf_path: Path) -> None:
    """
    [PROSES 1] Membuka dan menganalisis struktur teks dari satu file PDF.
    - Menghitung jumlah halaman dan karakter.
    - Mendeteksi halaman yang minim teks (misal halaman kosong atau hasil scan buruk).
    - Menghitung perkiraan penyebutan kata 'Pasal' untuk estimasi awal.
    """
    print("\n" + "=" * 88)
    print(f"FILE: {pdf_path.name}")
    try:
        # Membuka dokumen PDF menggunakan pustaka PyMuPDF (fitz)
        with pymupdf.open(pdf_path) as document:
            page_texts = [page.get_text("text") or "" for page in document]
    except Exception as exc:
        print(f"ERROR: tidak bisa membuka PDF: {exc}")
        return

    # Menghitung statistik teks
    total_chars = sum(len(text.strip()) for text in page_texts)
    # Deteksi halaman yang karakternya sangat sedikit (<40 karakter)
    low_text_pages = [i + 1 for i, text in enumerate(page_texts) if len(text.strip()) < 40]
    full_text = "\n".join(page_texts)
    
    # Menghitung penyebutan pola 'Pasal <angka>' sebagai indikator kasar kelengkapan
    pasal_mentions = len(re.findall(r"(?i)\bpasal\s+\d+", full_text))
    # Menghitung baris yang berdiri sendiri khusus sebagai judul pasal
    standalone_heading_candidates = len(
        re.findall(r"(?im)^\s*pasal\s+\d+[a-z]?\s*\.?\s*$", full_text)
    )

    # Menampilkan ringkasan statistik ke terminal
    print(f"Pages                    : {len(page_texts)}")
    print(f"Extracted characters     : {total_chars:,}")
    print(f"Pages with <40 chars     : {low_text_pages[:30]}" + (" ..." if len(low_text_pages) > 30 else ""))
    print(f"Mentions matching 'Pasal N': {pasal_mentions}")
    print(f"Standalone heading candidates: {standalone_heading_candidates}")
    
    # Menampilkan pratinjau cuplikan teks halaman pertama yang tidak kosong
    print("\nPREVIEW (halaman pertama yang berisi teks, maks 1.200 karakter):")
    first_text = next((text.strip() for text in page_texts if text.strip()), "")
    print(first_text[:1200] if first_text else "[Tidak ada teks yang berhasil diekstrak]")


def main() -> None:
    """
    [PROSES UTAMA] Memindai folder data/raw_trusted/ dan menginspeksi setiap PDF.
    """
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise SystemExit(
            f"Belum ada PDF di {PDF_DIR}. Salin PDF KUHPerdata dan HIR ke folder tersebut, lalu jalankan ulang."
        )

    # Iterasi setiap file PDF dan jalankan fungsi inspeksi
    for pdf_path in pdf_files:
        inspect_pdf(pdf_path)

    print("\nINSPEKSI SELESAI. Baca preview dan halaman yang minim teks sebelum menjalankan ekstraksi penuh.")


if __name__ == "__main__":
    main()
