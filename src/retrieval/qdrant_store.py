"""
Modul: Retrieval - Qdrant Vector Store Manager
Fungsi: Mengelola penyimpanan dan pencarian vektor embedding dense (BGE-M3 / SimCSE).
Mendukung koneksi ganda secara transparan:
1. Qdrant Cloud (jika QDRANT_URL dan QDRANT_API_KEY disetel di file .env).
2. Qdrant Local Embedded (fallback ke disk lokal tanpa memerlukan Docker).
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np


class QdrantVectorStore:
    """Kelas pengelola database vektor Qdrant (Cloud & Lokal Terintegrasi)."""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        collection_name: str = "kuhperdata_hir_bgem3",
        use_cloud: Optional[bool] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        [PROSES 1: INISIALISASI & KONEKSI DATABASE]
        Memeriksa ketersediaan kredensial Qdrant Cloud. Jika valid, hubungkan ke Cloud Cluster.
        Jika tidak tersedia atau gagal, otomatis beralih ke Qdrant lokal disk storage.
        """
        import os
        from qdrant_client import QdrantClient
        from dotenv import load_dotenv

        load_dotenv()

        base_dir = Path(__file__).resolve().parents[2]
        if storage_path is None:
            storage_path = base_dir / "indexes" / "qdrant_storage"

        self.storage_path = Path(storage_path)
        self.collection_name = collection_name
        self.is_cloud = False

        cloud_url = url or os.getenv("QDRANT_URL")
        cloud_key = api_key or os.getenv("QDRANT_API_KEY")

        # Coba koneksi Qdrant Cloud terlebih dahulu
        should_try_cloud = use_cloud if use_cloud is not None else bool(cloud_url and cloud_key)

        if should_try_cloud and cloud_url and cloud_key:
            try:
                print(f"[*] Menghubungkan ke Qdrant Cloud: {cloud_url[:45]}... (koleksi: {self.collection_name})")
                self.client = QdrantClient(url=cloud_url, api_key=cloud_key, timeout=60)
                # Validasi koneksi dengan memeriksa keberadaan koleksi
                self.client.get_collection(self.collection_name)
                self.is_cloud = True
                print(f"[+] Berhasil terhubung ke Qdrant Cloud untuk koleksi '{self.collection_name}'!")
                return
            except Exception as e:
                print(f"[!] Gagal terhubung ke Qdrant Cloud ({e}). Beralih otomatis ke Qdrant lokal...")

        # Fallback ke penyimpanan lokal jika Cloud tidak aktif
        self.storage_path.mkdir(parents=True, exist_ok=True)
        print(f"[*] Inisialisasi Qdrant lokal pada direktori: {self.storage_path}...")
        try:
            self.client = QdrantClient(path=str(self.storage_path))
        except Exception as e:
            # Mengatasi kendala concurrency lock jika ada proses lain yang membuka file yang sama
            print(f"[!] Qdrant lock detected ({e}). Menggunakan temporary read replica...")
            import tempfile, shutil
            temp_dir = Path(tempfile.mkdtemp(prefix="qdrant_replica_"))
            for item in self.storage_path.iterdir():
                if item.is_file() and not item.name.endswith(".lock"):
                    shutil.copy2(item, temp_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, temp_dir / item.name, ignore=shutil.ignore_patterns("*.lock"))
            self.client = QdrantClient(path=str(temp_dir))

    def build(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]], batch_size: int = 64) -> None:
        """
        [PROSES 2: PEMBUATAN KOLEKSI & INJEKSI VEKTOR]
        Membuat koleksi baru dengan metrik kemiripan Cosine Distance dan mengunggah
        vektor beserta payload metadata (nama dokumen, bab, nomor pasal, isi teks) secara bertahap (batch).
        """
        from qdrant_client.models import VectorParams, Distance, PointStruct

        dim = embeddings.shape[1]
        print(f"[*] Membuat/memperbarui koleksi Qdrant '{self.collection_name}' (dimensi={dim}, metric=COSINE)...")

        # Buat ulang koleksi agar bersih dari data lama
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        total_points = len(metadata)
        print(f"[*] Menyimpan {total_points} vektor pasal ke Qdrant...")

        for i in range(0, total_points, batch_size):
            batch_end = min(i + batch_size, total_points)
            points = []
            for idx in range(i, batch_end):
                vec = embeddings[idx].tolist()
                payload = dict(metadata[idx])
                points.append(PointStruct(id=idx, vector=vec, payload=payload))

            self.client.upsert(collection_name=self.collection_name, points=points)

        print(f"[+] Selesai! Koleksi '{self.collection_name}' berhasil disimpan.")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        [PROSES 3: PENCARIAN VEKTOR (SIMILARITY SEARCH)]
        Mencari top-K artikel yang paling mirip secara semantik dengan vektor kueri pengguna
        berdasarkan skor Cosine Similarity (rentang 0.0 sampai 1.0).
        """
        if query_vector.ndim == 2:
            query_vector = query_vector[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=top_k,
        )

        formatted_hits = []
        for rank, hit in enumerate(results.points, start=1):
            record = dict(hit.payload or {})
            record["rank"] = rank
            record["score"] = float(hit.score)
            formatted_hits.append(record)

        return formatted_hits
