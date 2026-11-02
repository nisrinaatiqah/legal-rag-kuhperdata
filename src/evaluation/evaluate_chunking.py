"""
Modul: Evaluasi Komparatif 3 Skenario Chunking (C1 vs C2 vs C3)
Fungsi: Menguji akurasi Information Retrieval (MRR, Recall@K, MAP@K) pada 30 kueri benchmark
ground truth menggunakan 3 korpus hasil strategi pemotongan teks:
1. C1: Structure-Based (Per Pasal Utuh, 2.276 chunk)
2. C2: Fixed-Size Small (256 Tokens, 822 chunk)
3. C3: Fixed-Size Medium (512 Tokens, 411 chunk)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi


def normalize_pasal_str(p_str: str) -> str:
    """Normalisasi format nomor pasal."""
    if not p_str:
        return ""
    m = re.search(r"(\d+[a-z]?)", str(p_str), re.IGNORECASE)
    return m.group(1).lower() if m else str(p_str).strip().lower()


def tokenize(text: str) -> List[str]:
    """Tokenisasi standar teks hukum Indonesia."""
    return [w.lower() for w in re.findall(r"\b\w+\b", text)]


def load_corpus(path: Path) -> List[Dict[str, Any]]:
    """Memuat berkas korpus JSONL."""
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def evaluate_retrieval_on_corpus(
    chunks: List[Dict[str, Any]],
    queries: List[Dict[str, Any]],
    scenario_name: str,
    is_fixed_size: bool = False
) -> Dict[str, Any]:
    """
    Mengevaluasi performa pencarian pada suatu korpus skenario chunking.
    """
    corpus_tokens = [tokenize(c.get("content", "")) for c in chunks]
    bm25 = BM25Okapi(corpus_tokens)
    
    k_list = [1, 3, 5, 10]
    recalls = {k: [] for k in k_list}
    rr_list = []
    
    for q in queries:
        target_pasals = [normalize_pasal_str(p) for p in q.get("nomor_pasal", [])]
        query_toks = tokenize(q["query"])
        
        # Ambil top 10 dokumen dari BM25
        scores = bm25.get_scores(query_toks)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
        
        retrieved_pasals = []
        for idx in top_indices:
            c = chunks[idx]
            if is_fixed_size:
                # Pada fixed-size, satu chunk bisa memuat multi pasal
                p_list = [normalize_pasal_str(p) for p in c.get("detected_pasals", [])]
                retrieved_pasals.append(p_list)
            else:
                p = normalize_pasal_str(c.get("pasal") or c.get("nomor_pasal", ""))
                retrieved_pasals.append([p])
                
        # Hitung Reciprocal Rank (RR)
        rr = 0.0
        for rank, p_group in enumerate(retrieved_pasals, start=1):
            if any(tp in p_group for tp in target_pasals):
                rr = 1.0 / rank
                break
        rr_list.append(rr)
        
        # Hitung Recall@K
        for k in k_list:
            top_k_pasals = [p for group in retrieved_pasals[:k] for p in group]
            hit = 1.0 if any(tp in top_k_pasals for tp in target_pasals) else 0.0
            recalls[k].append(hit)
            
    mrr = sum(rr_list) / len(rr_list) if rr_list else 0.0
    summary = {
        "mrr": round(mrr, 4),
        "recall": {f"Recall@{k}": round(sum(recalls[k]) / len(recalls[k]), 4) for k in k_list}
    }
    return summary


def main():
    root_dir = Path(__file__).resolve().parents[2]
    processed_dir = root_dir / "data" / "processed"
    eval_dir = root_dir / "data" / "evaluation"
    
    c1_path = processed_dir / "legal_corpus_clean.jsonl"
    c2_path = processed_dir / "corpus_c2_fixed_256.jsonl"
    c3_path = processed_dir / "corpus_c3_fixed_512.jsonl"
    gt_path = eval_dir / "ground_truth_perdata.json"
    
    with open(gt_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
        
    print("=" * 80)
    print("BENCHMARK RETRIEVAL PADA 3 SKENARIO CHUNKING (30 KUERI GROUND TRUTH)")
    print("=" * 80)
    
    print("\n[*] 1. Mengevaluasi Skenario C1: Structure-Based (Per Pasal Utuh - 2.276 chunk)...")
    c1_chunks = load_corpus(c1_path)
    res_c1 = evaluate_retrieval_on_corpus(c1_chunks, queries, "C1", is_fixed_size=False)
    
    print("\n[*] 2. Mengevaluasi Skenario C2: Fixed-Size Small (256 Tokens - 822 chunk)...")
    c2_chunks = load_corpus(c2_path)
    res_c2 = evaluate_retrieval_on_corpus(c2_chunks, queries, "C2", is_fixed_size=True)
    
    print("\n[*] 3. Mengevaluasi Skenario C3: Fixed-Size Medium (512 Tokens - 411 chunk)...")
    c3_chunks = load_corpus(c3_path)
    res_c3 = evaluate_retrieval_on_corpus(c3_chunks, queries, "C3", is_fixed_size=True)
    
    # Simpan hasil evaluasi
    eval_results = {
        "C1_Structure_Based": res_c1,
        "C2_Fixed_256": res_c2,
        "C3_Fixed_512": res_c3
    }
    
    out_json = eval_dir / "eval_results_chunking_scenarios.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
        
    print("\n" + "=" * 80)
    print("REKAPITULASI HASIL EKSPERIMEN RETRIEVAL 3 SKENARIO CHUNKING")
    print("=" * 80)
    print(f"{'Strategi Chunking':<25} | {'MRR':<8} | {'Recall@1':<10} | {'Recall@3':<10} | {'Recall@5':<10} | {'Recall@10'}")
    print("-" * 80)
    print(f"{'C1: Structure-Based':<25} | {res_c1['mrr']:<8} | {res_c1['recall']['Recall@1']:<10} | {res_c1['recall']['Recall@3']:<10} | {res_c1['recall']['Recall@5']:<10} | {res_c1['recall']['Recall@10']}")
    print(f"{'C2: Fixed 256 Tokens':<25} | {res_c2['mrr']:<8} | {res_c2['recall']['Recall@1']:<10} | {res_c2['recall']['Recall@3']:<10} | {res_c2['recall']['Recall@5']:<10} | {res_c2['recall']['Recall@10']}")
    print(f"{'C3: Fixed 512 Tokens':<25} | {res_c3['mrr']:<8} | {res_c3['recall']['Recall@1']:<10} | {res_c3['recall']['Recall@3']:<10} | {res_c3['recall']['Recall@5']:<10} | {res_c3['recall']['Recall@10']}")
    print("=" * 80)
    print(f"[+] Hasil tersimpan ke: {out_json}")


if __name__ == "__main__":
    main()
