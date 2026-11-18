"""
Modul: Retrieval - Qdrant Cloud BM25 Sparse Retriever
Fungsi: Melakukan pencarian leksikal berbasis kata kunci menggunakan Sparse Vectors BM25
yang tersimpan terpusat di Qdrant Cloud pada koleksi 'kuhperdata_hir_bm25'.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

from src.retrieval.build_bm25 import legal_tokenize

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class QdrantBM25Retriever:
    """
    Kelas Retriever untuk pencarian kata kunci BM25 berbasis Qdrant Cloud.
    Memiliki interface kompatibel dengan BM25Retriever lokal.
    """

    def __init__(
        self,
        collection_name: str = "kuhperdata_hir_bm25",
        vocab_path: Optional[Path] = None,
        client: Optional[QdrantClient] = None,
    ):
        self.collection_name = collection_name
        if vocab_path is None:
            vocab_path = BASE_DIR / "indexes" / "bm25" / "qdrant_bm25_vocab.json"
        self.vocab_path = Path(vocab_path)

        # Muat kosakata & IDF
        with open(self.vocab_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.vocab_to_id = meta["vocab_to_id"]

        # Hubungkan ke Qdrant
        if client:
            self.client = client
        else:
            cloud_url = os.getenv("QDRANT_URL")
            cloud_key = os.getenv("QDRANT_API_KEY")
            if cloud_url and cloud_key:
                self.client = QdrantClient(url=cloud_url, api_key=cloud_key, timeout=30)
            else:
                local_path = BASE_DIR / "indexes" / "qdrant_storage"
                self.client = QdrantClient(path=str(local_path))

    def search(self, query: str, top_k: int = 10) -> Dict[int, float]:
        """
        Pencarian sparse vector BM25 di Qdrant.
        Mengembalikan kamus: {doc_id: skor_ternormalisasi_0_sampai_1}.
        """
        tokens = legal_tokenize(query)
        q_weights = []
        for t in tokens:
            if t in self.vocab_to_id:
                q_weights.append((self.vocab_to_id[t], 1.0))

        if not q_weights:
            return {}

        q_weights.sort(key=lambda x: x[0])
        q_sparse = models.SparseVector(
            indices=[qw[0] for qw in q_weights],
            values=[qw[1] for qw in q_weights],
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=q_sparse,
            using="bm25",
            limit=top_k,
        )

        if not results.points:
            return {}

        max_score = results.points[0].score if results.points[0].score > 0 else 1.0
        return {p.id: float(p.score / max_score) for p in results.points}

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Mengembalikan dokumen pasal lengkap dari Qdrant Cloud berdasarkan BM25.
        """
        tokens = legal_tokenize(query)
        q_weights = []
        for t in tokens:
            if t in self.vocab_to_id:
                q_weights.append((self.vocab_to_id[t], 1.0))

        if not q_weights:
            return []

        q_weights.sort(key=lambda x: x[0])
        q_sparse = models.SparseVector(
            indices=[qw[0] for qw in q_weights],
            values=[qw[1] for qw in q_weights],
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=q_sparse,
            using="bm25",
            limit=top_k,
        )

        output = []
        for rank, p in enumerate(results.points, start=1):
            item = dict(p.payload or {})
            item["id"] = p.id
            item["score"] = float(p.score)
            item["rank"] = rank
            output.append(item)
        return output
