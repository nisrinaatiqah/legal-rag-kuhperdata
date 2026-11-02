"""
Modul: Ingestion - Pembangunan Skenario Chunking (C1, C2, C3)
Fungsi:
1. C1: Structure-Based (Article-Level / Per Pasal Utuh) - Baseline (2.276 pasal)
2. C2: Fixed-Size Small (256 Tokens, Overlap 32 Tokens)
3. C3: Fixed-Size Medium (512 Tokens, Overlap 64 Tokens)

Menganalisis statistik keutuhan pasal (pasal terpotong vs utuh) dan menyimpan korpus
ke data/processed/ untuk pengujian komparatif sistem Legal RAG.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any
from transformers import AutoTokenizer


def compute_sha256(text: str) -> str:
    """Menghitung hash SHA-256 dari teks."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def load_extracted_text(extracted_path: Path) -> List[Dict[str, Any]]:
    """Membaca berkas JSONL hasil ekstraksi halaman."""
    pages = []
    with open(extracted_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                pages.append(json.loads(line))
    return pages


def build_c1_structure_based(clean_corpus_path: Path) -> List[Dict[str, Any]]:
    """Memuat korpus C1 (Structure-Based / Per Pasal Utuh) yang sudah tervalidasi."""
    chunks = []
    with open(clean_corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def build_fixed_size_chunks(
    pages: List[Dict[str, Any]],
    source_name: str,
    tokenizer,
    chunk_size: int,
    overlap: int
) -> List[Dict[str, Any]]:
    """
    Membangun potongan teks sekuensial dengan jendela tetap (Fixed-Size Sliding Window).
    """
    # 1. Gabungkan seluruh teks per halaman
    full_text = "\n\n".join(p.get("text", "") for p in pages)
    
    # 2. Tokenisasi teks penuh
    encoded = tokenizer(full_text, add_special_tokens=False, return_offsets_mapping=True)
    input_ids = encoded["input_ids"]
    offset_mapping = encoded["offset_mapping"]
    
    step = chunk_size - overlap
    chunks = []
    chunk_idx = 1
    
    pasal_pattern = re.compile(r"Pasal\s+(\d+[a-z]?)", re.IGNORECASE)
    
    for start_idx in range(0, len(input_ids), step):
        end_idx = min(start_idx + chunk_size, len(input_ids))
        
        # Ambil karakter asli dari teks
        char_start = offset_mapping[start_idx][0]
        char_end = offset_mapping[end_idx - 1][1]
        chunk_text = full_text[char_start:char_end].strip()
        
        if not chunk_text:
            continue
            
        token_len = end_idx - start_idx
        
        # Deteksi pasal apa saja yang ada di dalam potongan ini
        found_pasals = list(dict.fromkeys(pasal_pattern.findall(chunk_text)))
        
        chunks.append({
            "chunk_id": f"{source_name.upper()}_FIXED_{chunk_size}_{chunk_idx:04d}",
            "source": source_name,
            "strategy": f"Fixed-Size ({chunk_size} tokens)",
            "chunk_index": chunk_idx,
            "token_count": token_len,
            "char_count": len(chunk_text),
            "detected_pasals": found_pasals,
            "is_multi_article": len(found_pasals) > 1,
            "content": chunk_text,
            "content_sha256": compute_sha256(chunk_text)
        })
        chunk_idx += 1
        
        if end_idx >= len(input_ids):
            break
            
    return chunks


def analyze_scenarios(c1_chunks, c2_chunks, c3_chunks) -> Dict[str, Any]:
    """Menganalisis perbandingan struktural antara C1, C2, dan C3."""
    def get_stats(chunks, is_fixed=False):
        lens = [c.get("token_count", c.get("char_count", 0) // 4) for c in chunks]
        multi_count = sum(1 for c in chunks if c.get("is_multi_article", False)) if is_fixed else 0
        return {
            "total_chunks": len(chunks),
            "avg_tokens": round(sum(lens) / len(lens), 1) if lens else 0,
            "min_tokens": min(lens) if lens else 0,
            "max_tokens": max(lens) if lens else 0,
            "multi_article_chunks": multi_count,
            "multi_article_ratio_pct": round((multi_count / len(chunks)) * 100, 2) if chunks else 0.0
        }

    return {
        "C1_Structure_Based": get_stats(c1_chunks, is_fixed=False),
        "C2_Fixed_256": get_stats(c2_chunks, is_fixed=True),
        "C3_Fixed_512": get_stats(c3_chunks, is_fixed=True)
    }


def main():
    root_dir = Path(__file__).resolve().parents[2]
    extracted_dir = root_dir / "data" / "extracted"
    processed_dir = root_dir / "data" / "processed"
    eval_dir = root_dir / "data" / "evaluation"
    
    clean_corpus_path = processed_dir / "legal_corpus_clean.jsonl"
    kuhp_extracted = extracted_dir / "kuhperdata.jsonl"
    hir_extracted = extracted_dir / "hir.jsonl"
    
    print("=" * 80)
    print("PEMBANGUNAN DAN ANALISIS 3 SKENARIO CHUNKING (C1, C2, C3)")
    print("=" * 80)
    
    # 1. Skenario C1 (Structure-Based / Per Pasal Utuh)
    print("\n[*] 1. Memuat Skenario C1: Structure-Based (Per Pasal Utuh)...")
    c1_chunks = build_c1_structure_based(clean_corpus_path)
    print(f"[+] Skenario C1 berhasil dimuat: {len(c1_chunks)} pasal utuh.")
    
    # 2. Inisialisasi Tokenizer BGE-M3
    print("\n[*] 2. Menginisialisasi tokenizer BAAI/bge-m3...")
    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3", local_files_only=True)
    
    # Memuat teks ekstrak
    pages_kuhp = load_extracted_text(kuhp_extracted)
    pages_hir = load_extracted_text(hir_extracted)
    
    # 3. Skenario C2: Fixed-Size 256 tokens (overlap 32)
    print("\n[*] 3. Membangun Skenario C2: Fixed-Size Small (256 Tokens, Overlap 32)...")
    c2_kuhp = build_fixed_size_chunks(pages_kuhp, "KUHPerdata", tokenizer, chunk_size=256, overlap=32)
    c2_hir = build_fixed_size_chunks(pages_hir, "HIR", tokenizer, chunk_size=256, overlap=32)
    c2_chunks = c2_kuhp + c2_hir
    
    c2_path = processed_dir / "corpus_c2_fixed_256.jsonl"
    with open(c2_path, "w", encoding="utf-8") as f:
        for c in c2_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[+] Skenario C2 berhasil disimpan ke: {c2_path} (Total: {len(c2_chunks)} chunks)")
    
    # 4. Skenario C3: Fixed-Size 512 tokens (overlap 64)
    print("\n[*] 4. Membangun Skenario C3: Fixed-Size Medium (512 Tokens, Overlap 64)...")
    c3_kuhp = build_fixed_size_chunks(pages_kuhp, "KUHPerdata", tokenizer, chunk_size=512, overlap=64)
    c3_hir = build_fixed_size_chunks(pages_hir, "HIR", tokenizer, chunk_size=512, overlap=64)
    c3_chunks = c3_kuhp + c3_hir
    
    c3_path = processed_dir / "corpus_c3_fixed_512.jsonl"
    with open(c3_path, "w", encoding="utf-8") as f:
        for c in c3_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[+] Skenario C3 berhasil disimpan ke: {c3_path} (Total: {len(c3_chunks)} chunks)")
    
    # 5. Analisis Perbandingan Statistik
    stats = analyze_scenarios(c1_chunks, c2_chunks, c3_chunks)
    report_path = eval_dir / "chunking_scenarios_comparison.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 80)
    print("HASIL ANALISIS STRUKTURAL 3 SKENARIO CHUNKING")
    print("=" * 80)
    print(f"{'Metrik':<28} | {'C1: Structure-Based':<20} | {'C2: Fixed 256':<15} | {'C3: Fixed 512':<15}")
    print("-" * 80)
    print(f"{'Total Chunks':<28} | {stats['C1_Structure_Based']['total_chunks']:<20} | {stats['C2_Fixed_256']['total_chunks']:<15} | {stats['C3_Fixed_512']['total_chunks']:<15}")
    print(f"{'Rata-rata Ukuran Token':<28} | {stats['C1_Structure_Based']['avg_tokens']:<20} | {stats['C2_Fixed_256']['avg_tokens']:<15} | {stats['C3_Fixed_512']['avg_tokens']:<15}")
    print(f"{'Chunk Berisi Multi-Pasal':<28} | {'0 (0.0%)':<20} | {stats['C2_Fixed_256']['multi_article_chunks']} ({stats['C2_Fixed_256']['multi_article_ratio_pct']}%) | {stats['C3_Fixed_512']['multi_article_chunks']} ({stats['C3_Fixed_512']['multi_article_ratio_pct']}%)")
    print("=" * 80)
    print(f"[+] Laporan lengkap disimpan ke: {report_path}")


if __name__ == "__main__":
    main()
