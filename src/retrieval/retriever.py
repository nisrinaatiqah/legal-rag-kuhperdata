"""
Modul: Retrieval - Mesin Pencari Dokumen Hukum Terpadu (Unified Legal Retriever)
Fungsi: Mengimplementasikan 3 konfigurasi retriever yang diteliti dalam Tugas Akhir:
1. LegalRetrieverR1: Pure Dense Retriever menggunakan BAAI/bge-m3 pada database Qdrant (Model Usulan Inti).
2. LegalRetrieverR2: Hybrid Retriever (Baseline) menggunakan SimCSE-IndoBERT + BM25Okapi.
3. LegalRetrieverR3: Hybrid Retriever (Inovasi Gabungan) menggunakan BAAI/bge-m3 + BM25Okapi.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.build_bm25 import legal_tokenize


class BM25Retriever:
    """
    [KOMPONEN SPARSE RETRIEVAL]
    Melakukan pencarian berbasis pencocokan kata kunci leksikal menggunakan BM25Okapi.
    Sangat efektif ketika pengguna menyebut nomor pasal secara eksplisit (misal: 'Pasal 1320').
    """

    def __init__(self, index_path: Optional[Path] = None):
        """Memuat file pickle indeks BM25 yang sudah dibangun sebelumnya."""
        base_dir = Path(__file__).resolve().parents[2]
        if index_path is None:
            index_path = base_dir / "indexes" / "bm25" / "bm25_perdata_clean.pkl"

        with open(index_path, "rb") as f:
            data = pickle.load(f)

        self.bm25 = data["bm25"]
        self.chunks = data["chunks"]

    def search(self, query: str, top_k: int = 10) -> Dict[int, float]:
        """
        Mencari pasal paling relevan berdasarkan frekuensi kata kunci.
        Mengembalikan kamus: {indeks_dokumen: skor_ternormalisasi_0_sampai_1}.
        """
        tokens = legal_tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        max_score = scores[top_indices[0]] if top_indices and scores[top_indices[0]] > 0 else 1.0
        return {idx: float(scores[idx] / max_score) for idx in top_indices}


class LegalRetrieverR1:
    """
    [KONFIGURASI R1: PURE DENSE RETRIEVER - MODEL USULAN UTAMA]
    - Model Embedding: BAAI/bge-m3 (vektor dense 1024-dimensi).
    - Database Vektor : Qdrant (mendukung Cosine Similarity).
    - Keunggulan      : Memahami sinonimitas dan makna konteks hukum mendalam tanpa bergantung kecocokan kata persis.
    """

    def __init__(self, embedder: Optional[LegalEmbedder] = None, qdrant_store: Optional[QdrantVectorStore] = None):
        self.embedder = embedder or LegalEmbedder(model_name="BAAI/bge-m3")
        self.qdrant_store = qdrant_store or QdrantVectorStore(collection_name="kuhperdata_hir_bgem3")

    @classmethod
    def load(
        cls,
        embedder: Optional[LegalEmbedder] = None,
        qdrant_store: Optional[QdrantVectorStore] = None,
    ) -> "LegalRetrieverR1":
        """Memuat retriever R1 pada koleksi bersih (clean)."""
        return cls(embedder=embedder, qdrant_store=qdrant_store)

    load_clean_index = load

    @classmethod
    def load_poisoned(
        cls,
        rate_str: str = "1pct",
        embedder: Optional[LegalEmbedder] = None,
    ) -> "LegalRetrieverR1":
        """
        Memuat retriever R1 pada koleksi terkontaminasi untuk pengujian serangan (attack simulation):
        - rate_str: '1pct', '5pct', atau '10pct'.
        """
        collection_name = f"kuhperdata_hir_bgem3_p{rate_str}"
        store = QdrantVectorStore(collection_name=collection_name)
        return cls(embedder=embedder, qdrant_store=store)

    load_poisoned_index = load_poisoned

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        [PROSES PENGAMBILAN DOKUMEN R1]
        1. Mengubah teks kueri pertanyaan menjadi vektor dense 1024-d.
        2. Mencari top-K vektor terdekat di koleksi Qdrant.
        3. Mengembalikan daftar dokumen hukum beserta skor relevansinya.
        """
        query_vector = self.embedder.encode_query(query)
        return self.qdrant_store.search(query_vector=query_vector, top_k=top_k)


class LegalRetrieverR2:
    """
    [KONFIGURASI R2: BASELINE HYBRID RETRIEVER]
    - Dense Model : LazarusNLP/simcse-indobert-base (768-dimensi).
    - Sparse Model: BM25Okapi.
    - Kombinasi   : Skor = alpha * Dense + (1 - alpha) * Sparse.
    """

    def __init__(
        self,
        embedder: Optional[LegalEmbedder] = None,
        qdrant_store: Optional[QdrantVectorStore] = None,
        bm25: Optional[BM25Retriever] = None,
        alpha: float = 0.6,
    ):
        self.embedder = embedder or LegalEmbedder(model_name="LazarusNLP/simcse-indobert-base")
        self.qdrant_store = qdrant_store or QdrantVectorStore(collection_name="kuhperdata_hir_simcse")
        self.bm25 = bm25 or BM25Retriever()
        self.alpha = alpha

    @classmethod
    def load(
        cls,
        alpha: float = 0.6,
        embedder: Optional[LegalEmbedder] = None,
        qdrant_store: Optional[QdrantVectorStore] = None,
        bm25: Optional[BM25Retriever] = None,
    ) -> "LegalRetrieverR2":
        return cls(alpha=alpha, embedder=embedder, qdrant_store=qdrant_store, bm25=bm25)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        [PROSES PENGAMBILAN DOKUMEN R2]
        Menggabungkan pencarian semantik SimCSE dan pencarian leksikal BM25 secara linear.
        """
        # 1. Pencarian Dense SimCSE
        query_vector = self.embedder.encode_query(query)
        dense_hits = self.qdrant_store.search(query_vector=query_vector, top_k=20)
        dense_dict = {}
        payload_map = {}
        for h in dense_hits:
            cid = h.get("chunk_id")
            score = h.get("score", 0.0)
            dense_dict[cid] = max(0.0, score)
            payload_map[cid] = h

        # 2. Pencarian Sparse BM25
        sparse_scores = self.bm25.search(query, top_k=20)
        sparse_dict = {}
        for idx, s_score in sparse_scores.items():
            chunk = self.bm25.chunks[idx]
            cid = chunk.get("chunk_id")
            sparse_dict[cid] = s_score
            if cid not in payload_map:
                payload_map[cid] = dict(chunk)

        # 3. Penyesuaian alpha dinamis: jika kueri menyebut kata 'pasal', prioritaskan BM25
        active_alpha = 0.0 if "pasal" in query.lower() else self.alpha

        # 4. Penggabungan Skor Linear (Hybrid Scoring)
        all_cids = set(dense_dict.keys()) | set(sparse_dict.keys())
        combined = {}
        for cid in all_cids:
            d = dense_dict.get(cid, 0.0)
            s = sparse_dict.get(cid, 0.0)
            combined[cid] = (active_alpha * d) + ((1.0 - active_alpha) * s)

        top_cids = sorted(combined, key=combined.get, reverse=True)[:top_k]

        results = []
        for rank, cid in enumerate(top_cids, start=1):
            item = dict(payload_map[cid])
            item["rank"] = rank
            item["score"] = float(combined[cid])
            item["dense_score"] = float(dense_dict.get(cid, 0.0))
            item["sparse_score"] = float(sparse_dict.get(cid, 0.0))
            results.append(item)

        return results


class LegalRetrieverR3:
    """
    [KONFIGURASI R3: PROPOSED INNOVATION HYBRID RETRIEVER]
    - Dense Model : BAAI/bge-m3 (1024-dimensi).
    - Sparse Model: BM25Okapi.
    - Kombinasi   : Skor = alpha * BGE-M3 + (1 - alpha) * BM25.
    """

    def __init__(
        self,
        embedder: Optional[LegalEmbedder] = None,
        qdrant_store: Optional[QdrantVectorStore] = None,
        bm25: Optional[BM25Retriever] = None,
        alpha: float = 0.6,
    ):
        self.embedder = embedder or LegalEmbedder(model_name="BAAI/bge-m3")
        self.qdrant_store = qdrant_store or QdrantVectorStore(collection_name="kuhperdata_hir_bgem3")
        self.bm25 = bm25 or BM25Retriever()
        self.alpha = alpha

    @classmethod
    def load(
        cls,
        alpha: float = 0.6,
        embedder: Optional[LegalEmbedder] = None,
        qdrant_store: Optional[QdrantVectorStore] = None,
        bm25: Optional[BM25Retriever] = None,
    ) -> "LegalRetrieverR3":
        return cls(alpha=alpha, embedder=embedder, qdrant_store=qdrant_store, bm25=bm25)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        [PROSES PENGAMBILAN DOKUMEN R3]
        Menggabungkan representasi BGE-M3 dan pencarian leksikal BM25.
        """
        # 1. Pencarian Dense BGE-M3
        query_vector = self.embedder.encode_query(query)
        dense_hits = self.qdrant_store.search(query_vector=query_vector, top_k=20)
        dense_dict = {}
        payload_map = {}
        for h in dense_hits:
            cid = h.get("chunk_id")
            score = h.get("score", 0.0)
            dense_dict[cid] = max(0.0, score)
            payload_map[cid] = h

        # 2. Pencarian Sparse BM25
        sparse_scores = self.bm25.search(query, top_k=20)
        sparse_dict = {}
        for idx, s_score in sparse_scores.items():
            chunk = self.bm25.chunks[idx]
            cid = chunk.get("chunk_id")
            sparse_dict[cid] = s_score
            if cid not in payload_map:
                payload_map[cid] = dict(chunk)

        # 3. Penyesuaian alpha dinamis
        active_alpha = 0.0 if "pasal" in query.lower() else self.alpha

        # 4. Penggabungan Skor Linear
        all_cids = set(dense_dict.keys()) | set(sparse_dict.keys())
        combined = {}
        for cid in all_cids:
            d = dense_dict.get(cid, 0.0)
            s = sparse_dict.get(cid, 0.0)
            combined[cid] = (active_alpha * d) + ((1.0 - active_alpha) * s)

        top_cids = sorted(combined, key=combined.get, reverse=True)[:top_k]

        results = []
        for rank, cid in enumerate(top_cids, start=1):
            item = dict(payload_map[cid])
            item["rank"] = rank
            item["score"] = float(combined[cid])
            item["dense_score"] = float(dense_dict.get(cid, 0.0))
            item["sparse_score"] = float(sparse_dict.get(cid, 0.0))
            results.append(item)

        return results


# Alias default sistem: mengarahkan ke R1 (BGE-M3 Pure Dense)
LegalRetriever = LegalRetrieverR1
