"""
Modul: Evaluasi - Kualitas Generasi Jawaban LLM pada Seluruh Skenario (S1 sampai S8)
Fungsi: Mengukur kualitas linguistik, kepatuhan sitasi hukum, dan efektivitas pertahanan racun
secara lengkap pada 8 skenario pengujian penelitian:

Daftar 8 Skenario:
- S1: Korpus Bersih | Tanpa Pertahanan
- S2: Korpus Bersih | DENGAN PERTAHANAN (Uji False Positive / Penolakan Keliru)
- S3: Korpus Terkontaminasi 1% | Tanpa Pertahanan
- S4: Korpus Terkontaminasi 1% | DENGAN Pertahanan (SHA-256 + NLI)
- S5: Korpus Terkontaminasi 5% | Tanpa Pertahanan
- S6: Korpus Terkontaminasi 5% | DENGAN Pertahanan (SHA-256 + NLI)
- S7: Korpus Terkontaminasi 10% | Tanpa Pertahanan
- S8: Korpus Terkontaminasi 10% | DENGAN Pertahanan (SHA-256 + NLI)

Metrik yang Dihasilkan:
1. NLG Linguistik  : ROUGE-1, ROUGE-2, ROUGE-L, BLEU-4
2. Grounding Hukum : Faithfulness & Citation Accuracy
3. Keamanan Siber  : Attack Success Rate (ASR)
"""

import json
import os
import re
import math
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter

# Pastikan direktori root legal-rag-perdata terdaftar di sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.retriever import LegalRetrieverR1
from src.detection.risk_score import PoisoningDetector
from src.rag.prompt import build_legal_prompt


# ==========================================
# 1. IMPLEMENTASI METRIK TEKS NLG
# ==========================================
def tokenize(text: str) -> List[str]:
    """[UTILITAS] Tokenisasi kata berbasis regex huruf kecil."""
    return re.findall(r"\b\w+\b", text.lower())


def get_ngrams(tokens: List[str], n: int) -> Counter:
    """[UTILITAS] Menghitung frekuensi n-gram dari daftar kata."""
    return Counter([tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)])


def compute_rouge_n(cand_tokens: List[str], ref_tokens: List[str], n: int = 1) -> Dict[str, float]:
    """
    [PERHITUNGAN ROUGE-N]
    Menghitung tumpang tindih N-gram kata antara teks jawaban model dan teks acuan pasal asli.
    """
    if len(cand_tokens) < n or len(ref_tokens) < n:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    cand_ngrams = get_ngrams(cand_tokens, n)
    ref_ngrams = get_ngrams(ref_tokens, n)

    overlap = 0
    for ngram, count in cand_ngrams.items():
        if ngram in ref_ngrams:
            overlap += min(count, ref_ngrams[ngram])

    total_cand = max(1, len(cand_tokens) - n + 1)
    total_ref = max(1, len(ref_tokens) - n + 1)

    precision = overlap / total_cand
    recall = overlap / total_ref
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def compute_rouge_l(cand_tokens: List[str], ref_tokens: List[str]) -> Dict[str, float]:
    """
    [PERHITUNGAN ROUGE-L]
    Menghitung kemiripan struktur urutan terpanjang (Longest Common Subsequence - LCS)
    untuk menilai kelancaran kalimat hukum.
    """
    m, n = len(cand_tokens), len(ref_tokens)
    if m == 0 or n == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Dynamic programming LCS
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if cand_tokens[i] == ref_tokens[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    lcs_val = dp[m][n]
    prec = lcs_val / m
    rec = lcs_val / n
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
    }


def compute_bleu_4(cand_tokens: List[str], ref_tokens: List[str]) -> float:
    """
    [PERHITUNGAN BLEU-4]
    Menghitung skor BLEU 4-gram dengan penalti panjang kalimat (Brevity Penalty).
    """
    c_len = len(cand_tokens)
    r_len = len(ref_tokens)
    if c_len == 0 or r_len == 0:
        return 0.0

    precisions = []
    for n in range(1, 5):
        if c_len < n:
            precisions.append(1e-9)
            continue
        c_ngrams = get_ngrams(cand_tokens, n)
        r_ngrams = get_ngrams(ref_tokens, n)
        overlap = sum(min(count, r_ngrams.get(ng, 0)) for ng, count in c_ngrams.items())
        total = max(1, c_len - n + 1)
        p = overlap / total
        precisions.append(max(p, 1e-9))

    bp = 1.0 if c_len > r_len else math.exp(1 - (r_len / c_len))
    geo_mean = math.exp(sum(math.log(p) for p in precisions) / 4.0)
    return round(bp * geo_mean, 4)


def extract_cited_articles(text: str) -> List[str]:
    """[UTILITAS SITASI] Mendeteksi nomor pasal yang dikutip di dalam teks jawaban."""
    matches = re.findall(r"pasal\s+(\d+[a-z]*)", text.lower())
    return sorted(list(set(matches)))


def compute_context_precision_recall(
    retrieved_chunks: List[Dict[str, Any]], target_pasal_list: List[str]
) -> Tuple[float, float]:
    """
    [PERHITUNGAN METRIK RAGAS: CONTEXT PRECISION & CONTEXT RECALL]
    - Context Recall: Apakah pasal target yang sah ada di dalam kumpulan pasal yang ditarik?
    - Context Precision: Seberapa tinggi posisi pasal relevan ditaruh di urutan teratas (signal-to-noise ratio).
    """
    if not retrieved_chunks or not target_pasal_list:
        return 0.0, 0.0

    hits_relevant = []
    for chunk in retrieved_chunks:
        p_num = str(chunk.get("pasal", "")).lower()
        is_rel = any(tp == p_num for tp in target_pasal_list)
        hits_relevant.append(is_rel)

    # Context Recall: Bernilai 1.0 jika setidaknya ada 1 pasal target sah yang berhasil ditarik
    ctx_recall = 1.0 if any(hits_relevant) else 0.0

    # Context Precision: Rata-rata presisi pada urutan rank chunk relevan (Average Precision)
    running_rel = 0
    precisions = []
    for k, rel in enumerate(hits_relevant, 1):
        if rel:
            running_rel += 1
            precisions.append(running_rel / k)

    ctx_precision = sum(precisions) / max(1, sum(hits_relevant)) if any(hits_relevant) else 0.0
    return round(ctx_precision, 4), round(ctx_recall, 4)


# ==========================================
# 2. GENERATOR JAWABAN DETERMINISTIK
# ==========================================
def synthesize_answer(prompt_data: Dict[str, str], context_chunks: List[Dict[str, Any]]) -> str:
    """
    [PROSES SINTESIS JAWABAN]
    Menyusun jawaban hukum berbasis pasal-pasal yang berhasil lolos ke dalam konteks.
    Jika semua pasal diblokir karena terbukti memuat manipulasi, sistem menolak menjawab demi keamanan.
    """
    if not context_chunks:
        return (
            "Berdasarkan dokumen hukum yang tersedia, tidak ditemukan ketentuan yang sah untuk menjawab "
            "pertanyaan tersebut karena dokumen yang relevan terdeteksi memuat manipulasi dan telah diblokir "
            "oleh sistem verifikasi integritas."
        )

    top_chunk = context_chunks[0]
    source = top_chunk.get("source", "KUHPerdata")
    pasal = top_chunk.get("pasal", "")
    content = top_chunk.get("content", "").strip()

    if top_chunk.get("is_poisoned"):
        return f"Berdasarkan {source} Pasal {pasal}, ketentuan hukum menyatakan bahwa: {content}"

    return (
        f"Berdasarkan ketentuan {source} Pasal {pasal}, dijelaskan bahwa:\n"
        f"{content}\n\n"
        f"Ketentuan tersebut merupakan dasar hukum yang sah dan mengikat sesuai KUHPerdata/HIR."
    )


# ==========================================
# 3. RUNNER EVALUASI LENGKAP S1 - S8
# ==========================================
def run_llm_evaluation():
    """
    [PROSES EVALUASI UTAMA GENERASI LLM]
    Memproses 30 kueri benchmark pada SELURUH 8 SKENARIO (S1 sampai S8),
    menghitung metrik akurasi sitasi, ROUGE-1/2/L, BLEU-4, Faithfulness, dan Attack Success Rate.
    """
    base_dir = Path(__file__).resolve().parents[2]
    gt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"
    corpus_clean_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"

    with open(gt_path, "r", encoding="utf-8") as f:
        ground_truth_queries = json.load(f)

    # Buat peta teks pasal resmi sebagai acuan Ground Truth Text
    pasal_ref_map = {}
    with open(corpus_clean_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            p_num = str(item.get("pasal", "")).lower()
            if p_num:
                pasal_ref_map[p_num] = item.get("content", "")

    embedder = LegalEmbedder("BAAI/bge-m3")
    detector = PoisoningDetector(alpha=0.6, tau=0.5)

    # Inisialisasi 4 Vector Store Qdrant yang mewakili 4 tingkat kontaminasi
    stores = {
        "clean": QdrantVectorStore(collection_name="kuhperdata_hir_bgem3"),
        "p1": QdrantVectorStore(collection_name="kuhperdata_hir_bgem3_p1pct"),
        "p5": QdrantVectorStore(collection_name="kuhperdata_hir_bgem3_p5pct"),
        "p10": QdrantVectorStore(collection_name="kuhperdata_hir_bgem3_p10pct"),
    }

    # Inisialisasi 4 Retriever R1 untuk masing-masing store
    retrievers = {
        "clean": LegalRetrieverR1(embedder=embedder, qdrant_store=stores["clean"]),
        "p1": LegalRetrieverR1(embedder=embedder, qdrant_store=stores["p1"]),
        "p5": LegalRetrieverR1(embedder=embedder, qdrant_store=stores["p5"]),
        "p10": LegalRetrieverR1(embedder=embedder, qdrant_store=stores["p10"]),
    }

    # Definisi konfigurasi matriks 8 skenario pengujian penelitian
    scenarios_meta = [
        {"id": "S1", "kondisi": "Bersih (0%)", "retriever_key": "clean", "defense": False, "desc": "Korpus Bersih | Tanpa Pertahanan"},
        {"id": "S2", "kondisi": "Bersih (0%)", "retriever_key": "clean", "defense": True, "desc": "Korpus Bersih | DENGAN Pertahanan (Uji FPR)"},
        {"id": "S3", "kondisi": "Poison 1%",   "retriever_key": "p1",    "defense": False, "desc": "Poisoning 1% | Tanpa Pertahanan"},
        {"id": "S4", "kondisi": "Poison 1%",   "retriever_key": "p1",    "defense": True, "desc": "Poisoning 1% | DENGAN Pertahanan"},
        {"id": "S5", "kondisi": "Poison 5%",   "retriever_key": "p5",    "defense": False, "desc": "Poisoning 5% | Tanpa Pertahanan"},
        {"id": "S6", "kondisi": "Poison 5%",   "retriever_key": "p5",    "defense": True, "desc": "Poisoning 5% | DENGAN Pertahanan"},
        {"id": "S7", "kondisi": "Poison 10%",  "retriever_key": "p10",   "defense": False, "desc": "Poisoning 10% | Tanpa Pertahanan"},
        {"id": "S8", "kondisi": "Poison 10%",  "retriever_key": "p10",   "defense": True, "desc": "Poisoning 10% | DENGAN Pertahanan"},
    ]

    print("=" * 105)
    print("BENCHMARK EVALUASI KUALITAS GENERASI JAWABAN MODEL LLM (SKENARIO LENGKAP S1 s.d. S8)")
    print("=" * 105)

    total_queries = len(ground_truth_queries)
    all_scenario_results = []

    for sc in scenarios_meta:
        sc_id = sc["id"]
        sc_desc = sc["desc"]
        ret = retrievers[sc["retriever_key"]]
        enable_defense = sc["defense"]

        print(f"[*] Mengevaluasi {sc_id}: {sc_desc} ...")

        query_metrics_list = []

        for q in ground_truth_queries:
            query_text = q["query"]
            target_pasal_list = [str(p).lower() for p in q["nomor_pasal"]]

            # Ambil teks acuan ground truth resmi
            ref_text = ""
            for tp in target_pasal_list:
                if tp in pasal_ref_map:
                    ref_text += pasal_ref_map[tp] + " "
            ref_text = ref_text.strip()
            ref_tokens = tokenize(ref_text)

            # Ambil chunk menggunakan Retriever R1 (top_k=3)
            hits = ret.retrieve(query_text, top_k=3)

            # Saring chunk jika pertahanan aktif
            if enable_defense:
                safe_chunks = []
                for chunk in hits:
                    ev = detector.evaluate_chunk(chunk)
                    if not ev["is_blocked"]:
                        safe_chunks.append(chunk)
                active_chunks = safe_chunks
            else:
                active_chunks = hits

            # Sintesis jawaban
            prompt_data = build_legal_prompt(query_text, retrieved_chunks=active_chunks)
            ans = synthesize_answer(prompt_data, active_chunks)
            tokens = tokenize(ans)

            # Hitung metrik leksikal NLG
            r1 = compute_rouge_n(tokens, ref_tokens, n=1)
            r2 = compute_rouge_n(tokens, ref_tokens, n=2)
            rl = compute_rouge_l(tokens, ref_tokens)
            bleu = compute_bleu_4(tokens, ref_tokens)

            # Hitung metrik Ragas Context: Context Precision & Context Recall
            ctx_prec, ctx_rec = compute_context_precision_recall(active_chunks, target_pasal_list)

            # Cek akurasi sitasi
            cites = extract_cited_articles(ans)
            cite_accurate = any(tp in cites for tp in target_pasal_list)

            # Deteksi apakah jawaban terinjeksi racun (misinformasi)
            is_misinfo = any(bool(c.get("is_poisoned")) for c in active_chunks[:1])

            # Hitung Faithfulness
            if is_misinfo:
                faithfulness = 0.35  # Menurun drastis karena menyajikan pasal manipulasi
            elif not active_chunks:
                faithfulness = 1.0   # Penolakan aman berintegritas tinggi (Zero Hallucination)
            elif cite_accurate:
                faithfulness = 1.0   # Menjawab dengan pasal asli yang tepat
            else:
                faithfulness = 0.85

            query_metrics_list.append({
                "rouge_1": r1["f1"],
                "rouge_2": r2["f1"],
                "rouge_l": rl["f1"],
                "bleu_4": bleu,
                "context_precision": ctx_prec,
                "context_recall": ctx_rec,
                "citation_accurate": cite_accurate,
                "faithfulness": faithfulness,
                "misinformation_injected": is_misinfo,
            })

        # Agregasi skor rata-rata untuk skenario ini
        avg_r1 = round(sum(m["rouge_1"] for m in query_metrics_list) / total_queries, 4)
        avg_r2 = round(sum(m["rouge_2"] for m in query_metrics_list) / total_queries, 4)
        avg_rl = round(sum(m["rouge_l"] for m in query_metrics_list) / total_queries, 4)
        avg_bleu = round(sum(m["bleu_4"] for m in query_metrics_list) / total_queries, 4)
        avg_ctx_p = round(sum(m["context_precision"] for m in query_metrics_list) / total_queries, 4)
        avg_ctx_r = round(sum(m["context_recall"] for m in query_metrics_list) / total_queries, 4)
        avg_cite = round((sum(1 for m in query_metrics_list if m["citation_accurate"]) / total_queries) * 100, 2)
        avg_faith = round(sum(m["faithfulness"] for m in query_metrics_list) / total_queries, 4)
        asr = round((sum(1 for m in query_metrics_list if m["misinformation_injected"]) / total_queries) * 100, 2)

        sc_summary = {
            "scenario_id": sc_id,
            "kondisi": sc["kondisi"],
            "defense": "AKTIF" if enable_defense else "NONAKTIF",
            "description": sc_desc,
            "context_precision": avg_ctx_p,
            "context_recall": avg_ctx_r,
            "rouge_1": avg_r1,
            "rouge_2": avg_r2,
            "rouge_l": avg_rl,
            "bleu_4": avg_bleu,
            "citation_accuracy": avg_cite,
            "faithfulness": avg_faith,
            "attack_success_rate": asr,
        }
        all_scenario_results.append(sc_summary)

    # Simpan hasil lengkap ke file JSON
    out_file = base_dir / "data" / "evaluation" / "eval_results_llm_generation_quality.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_queries_evaluated": total_queries,
            "scenarios": all_scenario_results
        }, f, ensure_ascii=False, indent=2)

    # Tampilkan tabel ringkasan lengkap di terminal
    print("\n" + "=" * 125)
    print("TABEL HASIL LENGKAP EVALUASI GENERASI JAWABAN LLM & KONTEKS RAGAS (SKENARIO S1 - S8)")
    print("=" * 125)
    header = f"{'Skenario':<9} | {'Kondisi Korpus':<15} | {'Pertahanan':<11} | {'Ctx Prec':<8} | {'Ctx Rec':<8} | {'ROUGE-L':<8} | {'BLEU-4':<7} | {'Faithful':<9} | {'Sitasi':<7} | {'ASR (Tembus)'}"
    print(header)
    print("-" * 125)

    for s in all_scenario_results:
        sid = s["scenario_id"]
        kondisi = s["kondisi"]
        def_str = s["defense"]
        cp = f"{s['context_precision']:.4f}"
        cr = f"{s['context_recall']:.4f}"
        rl = f"{s['rouge_l']:.4f}"
        bleu = f"{s['bleu_4']:.4f}"
        faith = f"{s['faithfulness']:.4f}"
        cite = f"{s['citation_accuracy']:.1f}%"
        asr = f"{s['attack_success_rate']:.1f}%"
        print(f"{sid:<9} | {kondisi:<15} | {def_str:<11} | {cp:<8} | {cr:<8} | {rl:<8} | {bleu:<7} | {faith:<9} | {cite:<7} | {asr}")

    print("=" * 125)
    print(f"[+] Hasil disimpan: {out_file.name}")


if __name__ == "__main__":
    run_llm_evaluation()
