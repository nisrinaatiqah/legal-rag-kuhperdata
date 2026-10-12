"""Inspect selectable text in PDF files without modifying the source PDFs."""
from __future__ import annotations

import re
from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "raw_trusted"


def inspect_pdf(pdf_path: Path) -> None:
    print("\n" + "=" * 88)
    print(f"FILE: {pdf_path.name}")
    try:
        with pymupdf.open(pdf_path) as document:
            page_texts = [page.get_text("text") or "" for page in document]
    except Exception as exc:
        print(f"ERROR: tidak bisa membuka PDF: {exc}")
        return

    total_chars = sum(len(text.strip()) for text in page_texts)
    low_text_pages = [i + 1 for i, text in enumerate(page_texts) if len(text.strip()) < 40]
    full_text = "\n".join(page_texts)
    # Ini hanya hitungan indikatif untuk inspeksi, bukan parser chunk final.
    pasal_mentions = len(re.findall(r"(?i)\bpasal\s+\d+", full_text))
    standalone_heading_candidates = len(
        re.findall(r"(?im)^\s*pasal\s+\d+[a-z]?\s*\.?\s*$", full_text)
    )

    print(f"Pages                    : {len(page_texts)}")
    print(f"Extracted characters     : {total_chars:,}")
    print(f"Pages with <40 chars     : {low_text_pages[:30]}" + (" ..." if len(low_text_pages) > 30 else ""))
    print(f"Mentions matching 'Pasal N': {pasal_mentions}")
    print(f"Standalone heading candidates: {standalone_heading_candidates}")
    print("\nPREVIEW (first non-empty page, max 1,200 characters):")
    first_text = next((text.strip() for text in page_texts if text.strip()), "")
    print(first_text[:1200] if first_text else "[Tidak ada teks yang berhasil diekstrak]")


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise SystemExit(
            f"Belum ada PDF di {PDF_DIR}. Salin PDF KUHPerdata dan HIR ke folder tersebut, lalu jalankan ulang."
        )

    for pdf_path in pdf_files:
        inspect_pdf(pdf_path)

    print("\nINSPEKSI SELESAI. Baca preview dan halaman yang minim teks sebelum menjalankan ekstraksi penuh.")


if __name__ == "__main__":
    main()
