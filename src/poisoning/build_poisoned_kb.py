"""
Modul: Adversarial Knowledge Poisoning - Pembuatan Basis Pengetahuan Terkontaminasi
Fungsi: Menghasilkan dataset korpus hukum yang diracuni dengan 3 tingkat rasio serangan (attack rate):
1. Rasio 1%  (~23 pasal terkontaminasi)  -> Skenario Uji S3 & S4
2. Rasio 5%  (~114 pasal terkontaminasi) -> Skenario Uji S5 & S6
3. Rasio 10% (~228 pasal terkontaminasi) -> Skenario Uji S7 & S8

Prioritas serangan diarahkan pertama kali ke 30 pasal pada ground truth agar kita bisa mengukur
Attack Success Rate (ASR) dan ketahanan modul deteksi secara presisi.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Set

from src.poisoning.transformations import poison_article_chunk, TARGETED_POISON_TRANSFORMATIONS


def load_clean_corpus(corpus_path: Path) -> List[Dict[str, Any]]:
    """[UTILITAS] Membaca seluruh data korpus bersih dari file JSONL."""
    chunks = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def load_ground_truth_target_keys(gt_path: Path) -> Set[tuple]:
    """
    [IDENTIFIKASI TARGET]
    Mengekstrak pasangan (sumber, nomor_pasal) dari file benchmark ground truth
    untuk dijadikan target prioritas serangan poisoning.
    """
    target_keys = set()
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
    for q in gt_data:
        src = q.get("source", "")
        for no in q.get("nomor_pasal", []):
            target_keys.add((src, str(no).strip().lower()))
    return target_keys


def generate_poisoned_dataset(
    clean_chunks: List[Dict[str, Any]],
    target_keys: Set[tuple],
    poison_rate: float,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    [PROSES INJEKSI RACUN PENGETAHUAN]
    Membuat salinan korpus di mana sejumlah persen tertentu artikel diganti dengan teks manipulasi:
    - poison_rate 0.01 = 1% dari total 2.276 pasal = ~23 pasal
    - poison_rate 0.05 = 5% dari total 2.276 pasal = ~114 pasal
    - poison_rate 0.10 = 10% dari total 2.276 pasal = ~228 pasal
    """
    random.seed(seed)
    total_count = len(clean_chunks)
    num_to_poison = int(round(total_count * poison_rate))

    # Memisahkan indeks pasal yang masuk daftar target ground truth dan pasal lainnya
    target_indices = []
    other_indices = []

    for idx, c in enumerate(clean_chunks):
        p_val = str(c.get("pasal") or c.get("nomor_pasal") or "").strip().lower()
        key = (c.get("source", ""), p_val)
        if key in target_keys:
            target_indices.append(idx)
        else:
            other_indices.append(idx)

    # Menentukan pasal mana saja yang akan diracuni
    # Jika kuota racun <= jumlah target (misal 1% = 23 pasal), pilih acak dari target
    # Jika kuota racun > jumlah target (misal 5% dan 10%), racuni SEMUA target dan sisanya ambil acak dari pasal lain
    if num_to_poison <= len(target_indices):
        chosen_indices = set(random.sample(target_indices, num_to_poison))
    else:
        chosen_indices = set(target_indices)
        remaining_needed = num_to_poison - len(target_indices)
        sampled_others = random.sample(other_indices, remaining_needed)
        chosen_indices.update(sampled_others)

    poisoned_corpus = []
    poisoned_count = 0
    targeted_count = 0

    # Iterasi seluruh pasal: jika terpilih, ganti isinya dengan isi racun
    for idx, chunk in enumerate(clean_chunks):
        if idx in chosen_indices:
            poisoned_chunk, was_targeted = poison_article_chunk(chunk)
            poisoned_corpus.append(poisoned_chunk)
            poisoned_count += 1
            if was_targeted:
                targeted_count += 1
        else:
            clean_copy = dict(chunk)
            clean_copy["is_poisoned"] = False
            poisoned_corpus.append(clean_copy)

    print(f"Hasil korpus beracun (Rasio: {poison_rate*100:.0f}%):")
    print(f"  Total pasal        : {len(poisoned_corpus)}")
    print(f"  Pasal diracuni     : {poisoned_count} ({poisoned_count/total_count*100:.2f}%)")
    print(f"  Target uji terkena : {targeted_count}")

    return poisoned_corpus


def save_corpus(chunks: List[Dict[str, Any]], output_path: Path):
    """[UTILITAS] Menyimpan dataset beracun ke format JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Tersimpan: {output_path}")


def main():
    """
    [EKSEKUSI PEMBUATAN 3 LEVEL DATASET RACUN]
    1. Membaca korpus bersih dan daftar target ground truth.
    2. Menghasilkan korpus terkontaminasi 1%, 5%, dan 10%.
    3. Menyimpannya ke folder data/poisoning/.
    """
    base_dir = Path(__file__).resolve().parents[2]
    clean_corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"
    gt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"
    poison_dir = base_dir / "data" / "poisoning"

    clean_chunks = load_clean_corpus(clean_corpus_path)
    target_keys = load_ground_truth_target_keys(gt_path)

    # 1. Dataset 1% Racun (~23 pasal) -> Skenario S3 & S4
    corpus_1pct = generate_poisoned_dataset(clean_chunks, target_keys, poison_rate=0.01, seed=42)
    save_corpus(corpus_1pct, poison_dir / "corpus_poisoned_1pct.jsonl")

    # 2. Dataset 5% Racun (~114 pasal) -> Skenario S5 & S6
    corpus_5pct = generate_poisoned_dataset(clean_chunks, target_keys, poison_rate=0.05, seed=42)
    save_corpus(corpus_5pct, poison_dir / "corpus_poisoned_5pct.jsonl")

    # 3. Dataset 10% Racun (~228 pasal) -> Skenario S7 & S8
    corpus_10pct = generate_poisoned_dataset(clean_chunks, target_keys, poison_rate=0.10, seed=42)
    save_corpus(corpus_10pct, poison_dir / "corpus_poisoned_10pct.jsonl")

    print("\nSemua dataset knowledge poisoning berhasil dibuat!")


if __name__ == "__main__":
    main()
