"""
Modul: Retrieval - Pembangun Koleksi Qdrant SimCSE Baseline (Konfigurasi R2)
Fungsi: Menghitung vektor embedding SimCSE-IndoBERT (dimensi: 768) dari korpus perdata bersih
dan mengunggahnya ke Qdrant Cloud koleksi 'kuhperdata_hir_simcse'.
"""

import json
from pathlib import Path
from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore


def main():
    base_dir = Path(__file__).resolve().parents[2]
    corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"

    print("=" * 75)
    print("MEMBANGUN KOLEKSI QDRANT SIMCSE (KONFIGURASI R2: BASELINE HYBRID)")
    print("=" * 75)

    print("[*] Membaca korpus perdata bersih...")
    chunks = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    print(f"[+] Total pasal: {len(chunks)}")

    print("[*] Mengenkode teks pasal dengan LazarusNLP/simcse-indobert-base...")
    embedder = LegalEmbedder("LazarusNLP/simcse-indobert-base")
    texts = [c.get("content", "") for c in chunks]
    embeddings = embedder.encode(texts, batch_size=64, show_progress_bar=True)

    print(f"[+] Selesai enkoding. Bentuk vektor: {embeddings.shape}")

    print("[*] Mengunggah ke koleksi Qdrant 'kuhperdata_hir_simcse'...")
    qdrant_store = QdrantVectorStore(collection_name="kuhperdata_hir_simcse")
    qdrant_store.build(embeddings=embeddings, metadata=chunks, batch_size=64)
    print("[+] Koleksi 'kuhperdata_hir_simcse' berhasil dibangun dan aktif di Qdrant!")


if __name__ == "__main__":
    main()
