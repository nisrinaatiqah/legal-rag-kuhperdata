"""
Modul: Retrieval - BM25 Sparse Store untuk Hukum Perdata
Fungsi: Mengelola indeks pencarian kata kunci leksikal (sparse keyword search) berbasis BM25Okapi
pada dokumen KUHPerdata dan HIR.
"""

import pickle
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> List[str]:
    """
    [PROSES TOKENISASI]
    Mengubah teks menjadi huruf kecil (lowercase) dan menghapus tanda baca,
    lalu membaginya menjadi daftar token kata.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()


class BM25Store:
    """Kelas pengelola indeks BM25 untuk pencarian kata kunci hukum."""

    def __init__(self, bm25_index_path: Optional[Path] = None):
        """[INISIALISASI] Menentukan jalur lokasi penyimpanan file index .pkl."""
        base_dir = Path(__file__).resolve().parents[2]
        if bm25_index_path is None:
            bm25_index_path = base_dir / "indexes" / "bm25" / "bm25_clean_index.pkl"
        self.bm25_index_path = Path(bm25_index_path)

        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[int] = []

    def build_from_corpus(self, corpus_path: Optional[Path] = None) -> None:
        """
        [PROSES 1: MEMBANGUN INDEKS BM25 DARI KORPUS]
        Membaca data pasal bersih, memperkaya teks dengan konteks bab & pasal,
        menghitung frekuensi term BM25Okapi, dan menyimpannya ke disk (Pickle).
        """
        import json

        base_dir = Path(__file__).resolve().parents[2]
        if corpus_path is None:
            corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"

        corpus = []
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    corpus.append(json.loads(line))

        self.documents = []
        self.metadatas = []
        self.ids = []
        enriched_documents = []

        # Memperkaya teks dengan header pasal agar pencarian seperti "Pasal 1320" sangat akurat
        for idx, item in enumerate(corpus):
            pasal = item.get("pasal", "")
            bab = item.get("bab", "")
            buku = item.get("buku", "")
            source = item.get("source", "")
            content = item.get("content", "")

            enriched = f"{source} {buku} {bab} pasal {pasal} {content}"
            self.documents.append(content)
            self.metadatas.append(item)
            self.ids.append(idx)
            enriched_documents.append(enriched)

        print(f"[*] Membuat BM25 Index untuk {len(enriched_documents)} pasal...")
        tokenized_docs = [tokenize(doc) for doc in enriched_documents]
        self.bm25 = BM25Okapi(tokenized_docs)

        # Menyimpan model BM25 ke file .pkl
        self.bm25_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.bm25_index_path, "wb") as f:
            pickle.dump({
                "bm25": self.bm25,
                "documents": self.documents,
                "metadatas": self.metadatas,
                "ids": self.ids,
            }, f)
        print(f"[+] BM25 Index berhasil disimpan ke: {self.bm25_index_path}")

    def load(self) -> None:
        """[PROSES 2: MEMUAT INDEKS DARI DISK] Membaca file model .pkl ke memori RAM."""
        if not self.bm25_index_path.exists():
            print(f"[*] BM25 index belum ada di {self.bm25_index_path}. Membangun baru...")
            self.build_from_corpus()
            return

        with open(self.bm25_index_path, "rb") as f:
            data = pickle.load(f)
            self.bm25 = data["bm25"]
            self.documents = data["documents"]
            self.metadatas = data["metadatas"]
            self.ids = data["ids"]

    def search(self, query: str, top_k: int = 10) -> Dict[str, float]:
        """
        [PROSES 3: PENCARIAN SKOR BM25]
        Menghitung nilai kesesuaian kata kunci untuk kueri pengguna.
        Skor dinormalisasi ke rentang [0.0 - 1.0] dengan membaginya terhadap skor tertinggi.
        """
        if self.bm25 is None:
            self.load()

        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        max_score = scores[top_indices[0]] if scores[top_indices[0]] > 0 else 1.0

        return {str(self.ids[i]): float(scores[i] / max_score) for i in top_indices if scores[i] > 0}
