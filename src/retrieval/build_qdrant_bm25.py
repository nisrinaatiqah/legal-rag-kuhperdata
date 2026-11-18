"""
Modul: Retrieval - Pembangun Indeks Sparse BM25 di Qdrant Cloud & Lokal
Fungsi: Membaca korpus resmi perdata (legal_corpus_clean.jsonl), menghitung representasi
Sparse Vector BM25Okapi untuk 2.276 pasal, dan mengunggahnya ke koleksi mandiri:
'kuhperdata_hir_bm25' pada Qdrant.

Koleksi ini independen dan TIDAK MENGGANGGU koleksi dense 'kuhperdata_hir_bgem3'.
"""

import os
import json
import math
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Impor fungsi tokenisasi standar hukum
from src.retrieval.build_bm25 import legal_tokenize

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def compute_bm25_sparse_vectors(
    corpus: List[Dict[str, Any]],
    k1: float = 1.5,
    b: float = 0.75,
) -> Tuple[List[models.SparseVector], Dict[str, int], Dict[str, float]]:
    """
    Menghitung vektor sparse BM25Okapi untuk setiap dokumen dalam korpus.
    Mengembalikan:
    - sparse_vectors: daftar objek models.SparseVector
    - vocab_to_id: kamus pemetaan kata -> integer ID
    - idf_dict: kamus skor IDF setiap kata
    """
    N = len(corpus)
    tokenized_docs = []
    enriched_texts = []

    print("[*] Melakukan tokenisasi dokumen dan pembentukan korpus diperkaya...")
    for item in corpus:
        source = item.get("source", "")
        bab = item.get("bab", "")
        pasal = item.get("pasal", "")
        content = item.get("content", "")
        enriched = f"{source} {bab} Pasal {pasal}\n{content}"
        enriched_texts.append(enriched)
        tokens = legal_tokenize(enriched)
        tokenized_docs.append(tokens)

    # 1. Hitung Document Frequency (DF)
    df = Counter()
    doc_lens = []
    for tokens in tokenized_docs:
        doc_lens.append(len(tokens))
        unique_tokens = set(tokens)
        for t in unique_tokens:
            df[t] += 1

    avgdl = sum(doc_lens) / N if N > 0 else 1.0

    # 2. Bangun Kosakata (Vocabulary) terurut alfabetis
    sorted_terms = sorted(df.keys())
    vocab_to_id = {term: idx for idx, term in enumerate(sorted_terms)}

    # 3. Hitung IDF standar BM25
    idf_dict = {}
    for term, freq in df.items():
        # Formula Okapi IDF
        idf_dict[term] = math.log(1.0 + (N - freq + 0.5) / (freq + 0.5))

    # 4. Bangun Vektor Sparse untuk Tiap Dokumen
    print(f"[*] Menghitung bobot term BM25 untuk {N} dokumen (Kosakata: {len(vocab_to_id)} kata unik)...")
    sparse_vectors = []
    for i, tokens in enumerate(tokenized_docs):
        tf = Counter(tokens)
        dl = doc_lens[i]
        
        term_weights = []
        for term, count in tf.items():
            if term in vocab_to_id:
                t_id = vocab_to_id[term]
                t_idf = idf_dict[term]
                # Formula bobot BM25 term dalam dokumen
                weight = t_idf * ((count * (k1 + 1.0)) / (count + k1 * (1.0 - b + b * (dl / avgdl))))
                if weight > 0:
                    term_weights.append((t_id, float(weight)))

        # Qdrant menyarankan indeks sparse diurutkan menaik (ascending)
        term_weights.sort(key=lambda x: x[0])
        indices = [tw[0] for tw in term_weights]
        values = [tw[1] for tw in term_weights]

        sparse_vectors.append(models.SparseVector(indices=indices, values=values))

    return sparse_vectors, vocab_to_id, idf_dict


def get_qdrant_client() -> Tuple[QdrantClient, bool]:
    """Menginisialisasi koneksi ke Qdrant Cloud atau Lokal."""
    cloud_url = os.getenv("QDRANT_URL")
    cloud_key = os.getenv("QDRANT_API_KEY")

    if cloud_url and cloud_key:
        try:
            print(f"[*] Menghubungkan ke Qdrant Cloud: {cloud_url[:45]}...")
            client = QdrantClient(url=cloud_url, api_key=cloud_key, timeout=60)
            client.get_collections()
            print("[+] Terhubung ke Qdrant Cloud!")
            return client, True
        except Exception as e:
            print(f"[!] Gagal koneksi cloud ({e}). Beralih ke lokal...")

    local_path = BASE_DIR / "indexes" / "qdrant_storage"
    local_path.mkdir(parents=True, exist_ok=True)
    print(f"[*] Inisialisasi Qdrant lokal: {local_path}...")
    client = QdrantClient(path=str(local_path))
    return client, False


def main():
    corpus_path = BASE_DIR / "data" / "processed" / "legal_corpus_clean.jsonl"
    vocab_out_dir = BASE_DIR / "indexes" / "bm25"
    vocab_out_dir.mkdir(parents=True, exist_ok=True)
    vocab_out_file = vocab_out_dir / "qdrant_bm25_vocab.json"
    collection_name = "kuhperdata_hir_bm25"

    print("=" * 75)
    print("PEMBANGUNAN INDEKS SPARSE BM25 DI QDRANT (KOLEKSI KHUSUS)")
    print(f"Target Koleksi: '{collection_name}' (Aman, Tanpa Mengubah Koleksi Lain)")
    print("=" * 75)

    # 1. Baca Korpus Bersih
    corpus = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                corpus.append(json.loads(line))
    print(f"[*] Membaca {len(corpus)} pasal hukum...")

    # 2. Hitung Sparse Vectors & Kosakata
    sparse_vectors, vocab_to_id, idf_dict = compute_bm25_sparse_vectors(corpus)

    # Simpan kosakata dan IDF untuk inferensi kueri
    metadata_export = {
        "collection_name": collection_name,
        "total_documents": len(corpus),
        "vocab_size": len(vocab_to_id),
        "k1": 1.5,
        "b": 0.75,
        "vocab_to_id": vocab_to_id,
        "idf_dict": idf_dict,
    }
    with open(vocab_out_file, "w", encoding="utf-8") as f:
        json.dump(metadata_export, f, ensure_ascii=False)
    print(f"[+] Kosakata BM25 berhasil diekspor ke: {vocab_out_file.name}")

    # 3. Hubungkan ke Qdrant
    client, is_cloud = get_qdrant_client()

    # 4. Buat Koleksi Baru Khusus Sparse BM25
    print(f"[*] Membuat/memperbarui koleksi '{collection_name}' dengan SparseVectorParams...")
    client.recreate_collection(
        collection_name=collection_name,
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(
                index=models.SparseIndexParams(on_disk=False)
            )
        },
    )
    print(f"[+] Koleksi '{collection_name}' berhasil dibuat di Qdrant!")

    # 5. Unggah Points Secara Batch
    batch_size = 128
    total_points = len(corpus)
    print(f"[*] Mengunggah {total_points} pasal ke Qdrant (batch size={batch_size})...")

    for i in range(0, total_points, batch_size):
        batch_end = min(i + batch_size, total_points)
        points = []
        for idx in range(i, batch_end):
            sparse_vec = sparse_vectors[idx]
            payload = dict(corpus[idx])
            points.append(
                models.PointStruct(
                    id=idx,
                    vector={"bm25": sparse_vec},
                    payload=payload,
                )
            )
        client.upsert(collection_name=collection_name, points=points)
        print(f"    - Berhasil mengunggah dokumen {i+1} sampai {batch_end}...")

    print(f"[+] SELESAI! Seluruh {total_points} pasal berhasil diindeks BM25 di Qdrant!")

    # 6. Verifikasi Pencarian Uji Coba
    print("\n" + "=" * 50)
    print("VERIFIKASI PENCARIAN BM25 DI QDRANT")
    print("=" * 50)
    test_query = "syarat sah perjanjian perdata 1320"
    print(f"Kueri Uji: '{test_query}'")
    query_tokens = legal_tokenize(test_query)
    
    # Buat sparse vector untuk kueri
    q_weights = []
    for t in query_tokens:
        if t in vocab_to_id:
            q_weights.append((vocab_to_id[t], 1.0))
    q_weights.sort(key=lambda x: x[0])
    
    if q_weights:
        q_sparse = models.SparseVector(
            indices=[qw[0] for qw in q_weights],
            values=[qw[1] for qw in q_weights],
        )
        results = client.query_points(
            collection_name=collection_name,
            query=q_sparse,
            using="bm25",
            limit=3,
        )
        for rank, p in enumerate(results.points, start=1):
            pasal = p.payload.get("pasal", "-")
            source = p.payload.get("source", "-")
            print(f"Rank #{rank} | Skor BM25: {p.score:.4f} | {source} Pasal {pasal}")


if __name__ == "__main__":
    main()
