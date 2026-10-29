"""
Modul: Evaluasi - Analisis Sensitivitas & Parameter Ablation Study (Alpha & Tau)
Fungsi: Menyelidiki perilaku sistem pertahanan komposit pada berbagai variasi parameter:
- Alpha (Bobot Verifikasi Kriptografi SHA-256 vs Konsistensi Semantik NLI): [0.0 s/d 1.0]
- Tau   (Ambang Batas Pemblokiran Racun / Threshold): [0.3 s/d 0.8]

Membantu membuktikan secara empiris mengapa kombinasi (alpha=0.6, tau=0.5) menjadi nilai optimal
yang mencapai ASR = 0% tanpa menghasilkan False Positive pada dokumen hukum asli.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.retriever import LegalRetrieverR1
from src.detection.risk_score import PoisoningDetector


def run_ablation():
    """
    [PROSES GRID SEARCH ABLASI PARAMETER]
    1. Membaca kueri benchmark dan mengambil top-5 kandidat pasal dari koleksi teracuni 5%.
    2. Menguji setiap kombinasi nilai alpha dan tau.
    3. Menghitung ASR, Precision, Recall, F1, dan False Positive Rate (FPR).
    4. Menyimpan tabel hasil ke data/evaluation/ablation_study_alpha_tau.json.
    """
    base_dir = Path(__file__).resolve().parents[2]
    gt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"

    with open(gt_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print("=" * 80)
    print("ANALISIS SENSITIVITAS PARAMETER PERTAHANAN (ALPHA & TAU)")
    print("Pengujian pada Poisoning Rate 5% (Skenario Representatif S5 vs S6 - 100% Qdrant Cloud)")
    print("=" * 80)

    # Inisialisasi retriever dan detector
    embedder = LegalEmbedder("BAAI/bge-m3")
    store = QdrantVectorStore(collection_name="kuhperdata_hir_bgem3_p5pct")
    retriever = LegalRetrieverR1(embedder=embedder, qdrant_store=store)
    detector = PoisoningDetector()

    # Cache hasil retrieval agar iterasi grid search berlangsung sangat cepat tanpa query berulang
    print("[*] Melakukan retrieval untuk 30 benchmark queries dari Qdrant Cloud...")
    cached_hits = []
    for q in queries:
        hits = retriever.retrieve(q["query"], top_k=5)
        cached_hits.append(hits)

    # Grid parameter yang dieksplorasi
    alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    tau_values = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    grid_results = []

    # Iterasi eksplorasi kombinasi (Grid Search)
    for alpha in alpha_values:
        for tau in tau_values:
            tp, fp, fn, tn = 0, 0, 0, 0
            penetrated_queries = 0

            for hits in cached_hits:
                query_has_penetrated_poison = False
                for chunk in hits:
                    is_poison = bool(chunk.get("is_poisoned", False))

                    # Evaluasi skor mentah dari kedua modul pertahanan
                    src_res = detector.source_verifier.verify_chunk(chunk)
                    sem_res = detector.semantic_verifier.verify_chunk(chunk)

                    r_src = src_res["source_risk_score"]
                    r_sem = sem_res["contradiction_risk"]

                    # Hitung skor komposit berbobot
                    score = (alpha * r_src) + ((1.0 - alpha) * r_sem)
                    is_blocked = (score >= tau)

                    if is_poison and is_blocked:
                        tp += 1
                    elif not is_poison and is_blocked:
                        fp += 1
                    elif is_poison and not is_blocked:
                        fn += 1
                        query_has_penetrated_poison = True
                    elif not is_poison and not is_blocked:
                        tn += 1

                if query_has_penetrated_poison:
                    penetrated_queries += 1

            # Hitung metrik performa untuk kombinasi (alpha, tau) ini
            asr = (penetrated_queries / len(queries)) * 100
            precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 100.0
            recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0

            grid_results.append({
                "alpha": alpha,
                "tau": tau,
                "asr": round(asr, 2),
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "f1_score": round(f1, 2),
                "fpr": round(fpr, 2),
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            })

    # Simpan hasil grid search ke file JSON
    out_file = base_dir / "data" / "evaluation" / "ablation_study_alpha_tau.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(grid_results, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Grid search selesai ({len(grid_results)} kombinasi parameter).")
    print(f"[+] Hasil disimpan ke: {out_file.name}")


if __name__ == "__main__":
    run_ablation()
