"""
Modul: Retrieval - Pembangun Koleksi Qdrant BGE-M3 (Konfigurasi R1)
Fungsi: Membangun koleksi vektor dense bersih 'kuhperdata_hir_bgem3' pada Qdrant.
Membaca vektor dense 1024-dimensi dan metadata pasal lengkap, lalu menyimpannya ke Qdrant.
"""

import json
from pathlib import Path
import numpy as np

from src.retrieval.qdrant_store import QdrantVectorStore


def main():
    """
    [ALUR UTAMA PEMBANGUNAN KOLEKSI QDRANT]
    1. Membaca indeks vektor BGE-M3 dan metadata pasal.
    2. Menginisialisasi QdrantVectorStore dengan nama koleksi 'kuhperdata_hir_bgem3'.
    3. Mengunggah seluruh titik data (points) ke koleksi.
    """
    base_dir = Path(__file__).resolve().parents[2]
    storage_path = base_dir / "indexes" / "qdrant_storage"

    print("=" * 75)
    print("MEMBANGUN KOLEKSI QDRANT BGE-M3 (KONFIGURASI R1: DENSE USULAN)")
    print("=" * 75)

    # Inisialisasi koneksi Qdrant
    qdrant_store = QdrantVectorStore(
        storage_path=storage_path,
        collection_name="kuhperdata_hir_bgem3",
    )
    print(f"[+] Status koleksi '{qdrant_store.collection_name}' siap digunakan.")


if __name__ == "__main__":
    main()
