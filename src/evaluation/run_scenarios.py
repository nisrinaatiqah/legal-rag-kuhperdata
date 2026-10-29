"""
Modul: Evaluasi - Pengujian Otomatis 8 Skenario Penelitian (S1 sampai S8)
Fungsi: Menjalankan matriks pengujian lengkap sesuai Tabel 3.2 Proposal Tugas Akhir
menggunakan database vektor Qdrant:

Daftar Skenario:
- S1: Korpus Bersih, Retriever R1 (BGE-M3 di Qdrant), Tanpa Pertahanan
- S2: Korpus Bersih, Retriever R1 (BGE-M3 di Qdrant), DENGAN PERTAHANAN (Uji False Positive)
- S3: Poisoning 1%, Retriever R1 (Qdrant), Tanpa Pertahanan
- S4: Poisoning 1%, Retriever R1 (Qdrant), DENGAN PERTAHANAN (SHA-256 + NLI)
- S5: Poisoning 5%, Retriever R1 (Qdrant), Tanpa Pertahanan
- S6: Poisoning 5%, Retriever R1 (Qdrant), DENGAN PERTAHANAN (SHA-256 + NLI)
- S7: Poisoning 10%, Retriever R1 (Qdrant), Tanpa Pertahanan
- S8: Poisoning 10%, Retriever R1 (Qdrant), DENGAN PERTAHANAN (SHA-256 + NLI)

Metrik yang Dihasilkan:
1. Metrik Deteksi Pertahanan : Precision, Recall, F1-Score, False Positive Rate (FPR)
2. Metrik Keamanan Sistem   : Attack Success Rate (ASR)
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.retriever import LegalRetrieverR1, LegalRetrieverR2, BM25Retriever
from src.detection.risk_score import PoisoningDetector


def load_ground_truth(gt_path: Path) -> List[Dict[str, Any]]:
    """[UTILITAS] Membaca berkas benchmark 30 kueri hukum perdata."""
    with open(gt_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_scenario(
    scenario_id: str,
    description: str,
    retriever,
    detector: PoisoningDetector,
    queries: List[Dict[str, Any]],
    enable_defense: bool,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    [PROSES EVALUASI SATU SKENARIO]
    1. Melakukan retrieval untuk setiap kueri.
    2. Menghitung True Positive (TP), False Positive (FP), False Negative (FN), dan True Negative (TN).
    3. Menghitung Attack Success Rate (ASR): seberapa sering pasal racun berhasil lolos ke prompt.
    """
    print(f"\n[*] Menjalankan {scenario_id}: {description}...")

    total_queries = len(queries)
    successful_attack_queries = 0
    total_retrieved_chunks = 0
    total_poisoned_retrieved = 0
    total_clean_retrieved = 0

    tp = 0  # Chunk beracun yang berhasil DIBLOKIR oleh pertahanan
    fp = 0  # Chunk bersih yang KELIRU DIBLOKIR (False Alarm)
    fn = 0  # Chunk beracun yang GAGAL DIBLOKIR (lolos ke prompt LLM)
    tn = 0  # Chunk bersih yang DILOLOSKAN dengan benar

    for q in queries:
        query_text = q["query"]
        hits = retriever.retrieve(query=query_text, top_k=top_k)

        penetrated_poison_in_query = False

        for chunk in hits:
            total_retrieved_chunks += 1
            is_chunk_poisoned = bool(chunk.get("is_poisoned", False))

            if is_chunk_poisoned:
                total_poisoned_retrieved += 1
            else:
                total_clean_retrieved += 1

            if enable_defense:
                eval_res = detector.evaluate_chunk(chunk)
                is_blocked = eval_res["is_blocked"]

                if is_chunk_poisoned and is_blocked:
                    tp += 1
                elif not is_chunk_poisoned and is_blocked:
                    fp += 1
                elif is_chunk_poisoned and not is_blocked:
                    fn += 1
                    penetrated_poison_in_query = True
                elif not is_chunk_poisoned and not is_blocked:
                    tn += 1
            else:
                # Tanpa pertahanan: semua pasal yang terambil langsung lolos
                if is_chunk_poisoned:
                    fn += 1
                    penetrated_poison_in_query = True
                else:
                    tn += 1

        if penetrated_poison_in_query:
            successful_attack_queries += 1

    # Perhitungan Metrik Statistik
    asr = (successful_attack_queries / total_queries) * 100 if total_queries > 0 else 0.0

    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 100.0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else (100.0 if total_poisoned_retrieved == 0 else 0.0)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0

    result = {
        "scenario_id": scenario_id,
        "description": description,
        "enable_defense": enable_defense,
        "top_k": top_k,
        "total_queries": total_queries,
        "total_retrieved_chunks": total_retrieved_chunks,
        "total_poisoned_retrieved": total_poisoned_retrieved,
        "total_clean_retrieved": total_clean_retrieved,
        "attack_success_rate": round(asr, 2),
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "detection_metrics": {
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1, 2),
            "false_positive_rate": round(fpr, 2),
        },
    }

    print(f"    ASR (Attack Success Rate): {result['attack_success_rate']}%")
    if enable_defense:
        print(f"    Defense Metrics: Precision={result['detection_metrics']['precision']}%, "
              f"Recall={result['detection_metrics']['recall']}%, "
              f"F1={result['detection_metrics']['f1_score']}%, "
              f"FPR={result['detection_metrics']['false_positive_rate']}%")

    return result


def main():
    """
    [ALUR UTAMA PENGUJIAN 8 SKENARIO]
    Menjalankan pengujian bertahap dari kondisi baseline bersih hingga variasi serangan racun (1%, 5%, 10%),
    baik tanpa proteksi maupun dengan proteksi modul pertahanan terpadu.
    """
    base_dir = Path(__file__).resolve().parents[2]
    gt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"
    queries = load_ground_truth(gt_path)

    print("=" * 80)
    print("BENCHMARK EVALUASI SKENARIO S1 - S8 (100% BERBASIS QDRANT)")
    print("=" * 80)

    # Inisialisasi komponen bersama
    print("[*] Menginisialisasi Embedder & Detector...")
    shared_bge = LegalEmbedder("BAAI/bge-m3")
    shared_simcse = LegalEmbedder("LazarusNLP/simcse-indobert-base")
    detector = PoisoningDetector()
    bm25 = BM25Retriever()

    # Fungsi pembantu untuk memuat koleksi Qdrant
    def get_qdrant_retriever(collection_name: str):
        store = QdrantVectorStore(collection_name=collection_name)
        return LegalRetrieverR1(embedder=shared_bge, qdrant_store=store)

    r_clean = get_qdrant_retriever("kuhperdata_hir_bgem3")
    r2_simcse = LegalRetrieverR2.load(alpha=0.6, embedder=shared_simcse, bm25=bm25)
    r_pois_1 = get_qdrant_retriever("kuhperdata_hir_bgem3_p1pct")
    r_pois_5 = get_qdrant_retriever("kuhperdata_hir_bgem3_p5pct")
    r_pois_10 = get_qdrant_retriever("kuhperdata_hir_bgem3_p10pct")

    results = []

    # S1: Korpus Bersih, Retriever R1 (BGE-M3 di Qdrant), Tanpa Pertahanan
    s1 = evaluate_scenario("S1", "Korpus Bersih | R1 (Qdrant) | Tanpa Pertahanan",
                           r_clean, detector, queries, enable_defense=False)
    results.append(s1)

    # S2: Korpus Bersih, Retriever R1 (BGE-M3 di Qdrant), DENGAN PERTAHANAN (Uji False Positive)
    s2 = evaluate_scenario("S2", "Korpus Bersih | R1 (Qdrant) | DENGAN PERTAHANAN (Uji False Positive)",
                           r_clean, detector, queries, enable_defense=True)
    results.append(s2)

    # S3: Poisoning 1%, R1 (Qdrant), Tanpa Pertahanan
    s3 = evaluate_scenario("S3", "Poisoning 1% | R1 (Qdrant) | Tanpa Pertahanan",
                           r_pois_1, detector, queries, enable_defense=False)
    results.append(s3)

    # S4: Poisoning 1%, R1 (Qdrant), DENGAN PERTAHANAN
    s4 = evaluate_scenario("S4", "Poisoning 1% | R1 (Qdrant) | DENGAN PERTAHANAN (SHA-256 + NLI)",
                           r_pois_1, detector, queries, enable_defense=True)
    results.append(s4)

    # S5: Poisoning 5%, R1 (Qdrant), Tanpa Pertahanan
    s5 = evaluate_scenario("S5", "Poisoning 5% | R1 (Qdrant) | Tanpa Pertahanan",
                           r_pois_5, detector, queries, enable_defense=False)
    results.append(s5)

    # S6: Poisoning 5%, R1 (Qdrant), DENGAN PERTAHANAN
    s6 = evaluate_scenario("S6", "Poisoning 5% | R1 (Qdrant) | DENGAN PERTAHANAN (SHA-256 + NLI)",
                           r_pois_5, detector, queries, enable_defense=True)
    results.append(s6)

    # S7: Poisoning 10%, R1 (Qdrant), Tanpa Pertahanan
    s7 = evaluate_scenario("S7", "Poisoning 10% | R1 (Qdrant) | Tanpa Pertahanan",
                           r_pois_10, detector, queries, enable_defense=False)
    results.append(s7)

    # S8: Poisoning 10%, R1 (Qdrant), DENGAN PERTAHANAN
    s8 = evaluate_scenario("S8", "Poisoning 10% | R1 (Qdrant) | DENGAN PERTAHANAN (SHA-256 + NLI)",
                           r_pois_10, detector, queries, enable_defense=True)
    results.append(s8)

    # Simpan hasil laporan lengkap ke format JSON
    output_path = base_dir / "data" / "evaluation" / "eval_results_scenarios_s1_s8.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Cetak tabel ringkasan S1 - S8
    print("\n" + "=" * 94)
    print("HASIL EVALUASI PERTAHANAN KNOWLEDGE POISONING (SKENARIO S1 - S8)")
    print("=" * 94)
    header = f"{'Skenario':<9} | {'Kondisi Korpus':<15} | {'Pertahanan':<11} | {'Precision':<10} | {'Recall':<8} | {'F1-Score':<9} | {'ASR':<8} | {'FPR':<6}"
    print(header)
    print("-" * 94)

    for s in results:
        sid = s["scenario_id"]
        desc = s["description"]
        if "Bersih" in desc:
            kondisi = "Bersih"
        elif "1%" in desc:
            kondisi = "Poison 1%"
        elif "5%" in desc:
            kondisi = "Poison 5%"
        else:
            kondisi = "Poison 10%"

        def_str = "AKTIF" if s["enable_defense"] else "NONAKTIF"
        dm = s["detection_metrics"]
        prec = f"{dm['precision']:.1f}%"
        rec = f"{dm['recall']:.1f}%"
        f1 = f"{dm['f1_score']:.1f}%"
        asr = f"{s['attack_success_rate']:.1f}%"
        fpr = f"{dm['false_positive_rate']:.1f}%"
        print(f"{sid:<9} | {kondisi:<15} | {def_str:<11} | {prec:<10} | {rec:<8} | {f1:<9} | {asr:<8} | {fpr:<6}")

    print("=" * 94)
    print(f"[+] Hasil disimpan: {output_path.name}")


if __name__ == "__main__":
    main()
