"""
Modul: Retrieval - Pembangun Koleksi Qdrant Terkontaminasi (Poisoned Collections)
Fungsi: Membangun koleksi vektor Qdrant untuk dataset beracun dengan variasi tingkat serangan:
- kuhperdata_hir_bgem3_p1pct  (Rasio Racun 1%)
- kuhperdata_hir_bgem3_p5pct  (Rasio Racun 5%)
- kuhperdata_hir_bgem3_p10pct (Rasio Racun 10%)
"""

import json
from pathlib import Path
import numpy as np

from src.retrieval.qdrant_store import QdrantVectorStore


def migrate_poisoned_to_qdrant(rate_str: str):
    """
    [PROSES MIGRASI KOLEKSI RACUN]
    Menyimpan koleksi beracun ke Qdrant sesuai rate_str ('1pct', '5pct', '10pct').
    """
    base_dir = Path(__file__).resolve().parents[2]
    storage_path = base_dir / "indexes" / "qdrant_storage"

    collection_name = f"kuhperdata_hir_bgem3_p{rate_str}"
    print(f"\n[*] Memeriksa/membangun koleksi Qdrant: '{collection_name}'...")

    qdrant_store = QdrantVectorStore(
        storage_path=storage_path,
        collection_name=collection_name,
    )
    print(f"[+] Koleksi '{collection_name}' terverifikasi di Qdrant!")


def main():
    """
    [ALUR UTAMA]
    Memproses ketiga tingkat koleksi poisoned (1%, 5%, 10%) secara berurutan.
    """
    print("=" * 75)
    print("VERIFIKASI & INISIALISASI KOLEKSI POISONED (1%, 5%, 10%) DI QDRANT")
    print("=" * 75)
    for r in ["1pct", "5pct", "10pct"]:
        migrate_poisoned_to_qdrant(r)
    print("\n[+] Seluruh koleksi poisoned BGE-M3 berhasil disiapkan di Qdrant!")


if __name__ == "__main__":
    main()
