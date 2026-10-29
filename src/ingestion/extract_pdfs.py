"""
Modul: Ingestion - Ekstraksi Teks PDF per Halaman ke JSONL
Fungsi: Membaca dokumen PDF resmi (KUHPerdata dan HIR) halaman per halaman,
menghitung hash kriptografi SHA-256 untuk integritas file sumber,
dan menyimpannya ke format JSONL mentah di folder data/extracted/.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pymupdf

# [KONFIGURASI DIREKTORI & PATH]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "raw_trusted"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted"


def safe_stem(name: str) -> str:
    """
    [UTILITAS] Mengubah nama file menjadi format yang aman untuk penamaan file (slug).
    Contoh: 'KUHPerdata (BW).pdf' -> 'kuhperdata_bw'
    """
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", Path(name).stem).strip("_").lower()


def sha256_file(path: Path) -> str:
    """
    [UTILITAS KRIPTOGRAFI] Menghitung checksum SHA-256 dari file PDF mentah.
    Hash ini dicatat sebagai bukti verifikasi sumber bahwa teks berasal dari file asli tanpa modifikasi.
    """
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    """
    [PROSES UTAMA EKSTRAKSI]
    1. Memindai seluruh file PDF di data/raw_trusted/.
    2. Menghitung sidik jari SHA-256 PDF asli.
    3. Mengekstrak teks tiap halaman secara berurutan.
    4. Menyimpan record JSONL berisi nomor halaman dan teks lengkapnya.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise SystemExit(f"Belum ada file PDF di {PDF_DIR}")

    for pdf_path in pdf_files:
        source_hash = sha256_file(pdf_path)
        output_path = OUTPUT_DIR / f"{safe_stem(pdf_path.name)}.jsonl"
        row_count = 0
        total_chars = 0

        # Membuka PDF dan menulis hasil ekstraksi halaman ke file .jsonl
        with pymupdf.open(pdf_path) as document, output_path.open("w", encoding="utf-8") as out:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text") or ""
                record = {
                    "source_file": pdf_path.name,
                    "source_pdf_sha256": source_hash,
                    "page_number": page_number,
                    "text": text,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                row_count += 1
                total_chars += len(text.strip())

        print(f"OK: {pdf_path.name} -> {output_path.relative_to(PROJECT_ROOT)}")
        print(f"    pages={row_count}, extracted_chars={total_chars:,}, source_sha256={source_hash}")

    print("\nEkstraksi selesai. Periksa hasil di data/extracted sebelum membuat chunk pasal.")


if __name__ == "__main__":
    main()
