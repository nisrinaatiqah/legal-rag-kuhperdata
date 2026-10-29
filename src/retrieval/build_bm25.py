"""
Modul: Retrieval - Pembangun Indeks Sparse BM25 Bersih
Fungsi: Membaca korpus perdata bersih (legal_corpus_clean.jsonl), menerapkan penyaringan
stopwords bahasa Indonesia khusus hukum, dan menyimpan indeks BM25 ke:
indexes/bm25/bm25_perdata_clean.pkl.
"""

import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

# [DAFTAR STOPWORDS HUKUM]
# Kata-kata fungsional yang disaring agar pencarian fokus pada entitas hukum inti
STOPWORDS_ID = {
    "apa", "bagaimana", "berapa", "siapa", "kapan", "dimana",
    "apakah", "adalah", "untuk", "dengan", "yang", "dan", "atau",
    "dalam", "oleh", "dari", "ke", "di", "ini", "itu", "jika",
    "hukuman", "sanksi", "ancaman", "perdata",
    "hukumnya", "jelaskan", "sebutkan", "tentang", "pada",
}


def legal_tokenize(text: str) -> List[str]:
    """
    [PROSES TOKENISASI HUKUM]
    Membersihkan simbol, mengubah huruf kecil, dan menyaring kata-kata stopword.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS_ID and len(t) > 1]


def main():
    """
    [ALUR UTAMA PEMBUATAN INDEKS BM25]
    1. Membaca seluruh pasal perdata bersih (2.276 pasal).
    2. Menggabungkan konteks nama dokumen, bab, nomor pasal, dan teks pasal.
    3. Mentokenisasi dan membangun struktur pohon frekuensi term BM25Okapi.
    4. Menyimpan file pickle terkompresi.
    """
    base_dir = Path(__file__).resolve().parents[2]
    corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"
    bm25_out_dir = base_dir / "indexes" / "bm25"
    bm25_out_dir.mkdir(parents=True, exist_ok=True)
    bm25_out_file = bm25_out_dir / "bm25_perdata_clean.pkl"

    print("=" * 75)
    print("MEMBANGUN INDEKS SPARSE BM25 UNTUK KUHPERDATA & HIR")
    print("=" * 75)

    # 1. Membaca Korpus
    chunks: List[Dict[str, Any]] = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    print(f"[*] Total pasal yang diproses: {len(chunks)}")

    # 2. Persiapan Teks & Tokenisasi
    corpus_texts = []
    tokenized_corpus = []

    for c in chunks:
        source = c.get("source", "")
        bab = c.get("bab", "")
        pasal = c.get("pasal", "")
        content = c.get("content", "")

        # Tambahkan prefix struktural agar pencarian kata kunci pasal lebih peka
        enriched_text = f"{source} {bab} Pasal {pasal}\n{content}"
        corpus_texts.append(enriched_text)
        tokenized_corpus.append(legal_tokenize(enriched_text))

    # 3. Komputasi Model BM25Okapi
    print("[*] Menginisialisasi BM25Okapi...")
    bm25 = BM25Okapi(tokenized_corpus)

    data_to_save = {
        "bm25": bm25,
        "chunks": chunks,
        "tokenized_corpus": tokenized_corpus,
    }

    # 4. Simpan ke File Pickle
    with open(bm25_out_file, "wb") as f:
        pickle.dump(data_to_save, f)

    print(f"[+] Indeks BM25 berhasil dibangun dan disimpan ke: {bm25_out_file.name}")


if __name__ == "__main__":
    main()
