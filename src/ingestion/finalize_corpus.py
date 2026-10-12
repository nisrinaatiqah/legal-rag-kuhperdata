"""
Module for finalizing the clean civil law corpus (Option B):
- Combines 133 articles from HIR BAB IX with 16 relevant civil procedure articles from HIR BAB XV.
- Excludes purely criminal and repealed articles from HIR.
- Combines final HIR chunks with KUHPerdata chunks to form the unified trusted corpus.
- Generates a SHA-256 integrity manifest for Source Verification defense.

Outputs:
- data/processed/hir_chunks_final.jsonl (149 articles)
- data/processed/kuhperdata_chunks_final.jsonl (2,127 articles)
- data/processed/legal_corpus_clean.jsonl (2,276 articles total)
- data/manifests/trusted_corpus_manifest.json (SHA-256 integrity index)
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set

# 16 civil procedure articles from HIR BAB XV (Berbagai Peraturan)
HIR_BAB_XV_CIVIL_ARTICLES: Set[str] = {
    "372",  # Tata tertib persidangan & wewenang ketua majelis
    "373",  # Penertiban dan keamanan ruang sidang
    "374",  # Hak ingkar hakim (larangan memeriksa perkara kepentingan keluarga/pribadi)
    "377",  # Arbitrase / juru pisah / wasit perdamaian perdata
    "378",  # Pembebanan biaya perkara perdata
    "379",  # Biaya pokrol / penasihat hukum / pembela
    "381",  # Tata cara pengangkatan sumpah saksi & pihak menurut agama
    "382",  # Format surat keputusan dan perintah hakim perdata
    "383",  # Penyimpanan arsip keputusan dalam arsip majelis
    "388",  # Wewenang juru sita dalam menjalankan perintah & keputusan hakim
    "389",  # Laporan tertulis pelaksanaan surat juru sita
    "390",  # Tata cara pemanggilan resmi (relaas panggilan) pihak tergugat/penggugat
    "391",  # Perhitungan tenggang waktu hukum acara
    "392",  # Hak kompensasi dan biaya bagi saksi perkara perdata
    "393",  # Larangan menyimpang dari hukum acara yang ditentukan reglemen
    "394",  # Pemeriksaan setempat (descente) oleh MA / hakim
}

# Articles explicitly excluded from BAB XV (Criminal & Obsolete)
HIR_BAB_XV_EXCLUDED_CRIMINAL: Set[str] = {
    "375",  # Tahanan perkara pidana
    "376",  # Kuasa pidana denda (psl 82 KUHP)
    "384",  # Register perkara pidana
    "385",  # Larangan salinan putusan perkara pidana
    "386",  # Pembelaan pesakitan/terdakwa pidana
    "387",  # Denda kelalaian panitera dalam pidana
}
HIR_BAB_XV_EXCLUDED_OBSOLETE: Set[str] = {
    "380"   # "Tidak dimuat karena tidak sesuai lagi dengan keadaan sekarang"
}


def compute_sha256(text: str) -> str:
    """Computes SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_jsonl(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def finalize_hir(hir_all_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters HIR chunks according to Option B."""
    final_chunks = []

    for chunk in hir_all_chunks:
        bab = chunk.get("bab", "")
        pasal = chunk.get("pasal", "")

        # 1. Include all BAB IX articles
        if "BAB IX" in bab:
            chunk_copy = dict(chunk)
            chunk_copy["corpus_category"] = "hukum_acara_perdata_inti"
            final_chunks.append(chunk_copy)
            continue

        # 2. Include selected civil articles from BAB XV
        if "BAB XV" in bab and pasal in HIR_BAB_XV_CIVIL_ARTICLES:
            chunk_copy = dict(chunk)
            chunk_copy["corpus_category"] = "hukum_acara_perdata_peraturan_umum"
            final_chunks.append(chunk_copy)
            continue

    return final_chunks


def main():
    base_dir = Path(__file__).resolve().parents[2]
    processed_dir = base_dir / "data" / "processed"
    manifests_dir = base_dir / "data" / "manifests"

    kuh_file = processed_dir / "kuhperdata_chunks_all.jsonl"
    hir_file = processed_dir / "hir_chunks_all.jsonl"

    if not kuh_file.exists():
        raise FileNotFoundError(f"File {kuh_file} belum dibuat. Jalankan chunk_articles.py terlebih dahulu.")
    if not hir_file.exists():
        raise FileNotFoundError(f"File {hir_file} belum dibuat. Jalankan chunk_articles.py terlebih dahulu.")

    print("=" * 70)
    print("FINALISASI KORPUS HUKUM PERDATA & INTEGRITAS SUMBER (OPSI B)")
    print("=" * 70)

    # 1. Proses HIR
    print("[*] Membaca seluruh chunk HIR...")
    hir_all = load_jsonl(hir_file)
    print(f"    Total kandidat chunk HIR mentah: {len(hir_all)}")

    hir_final = finalize_hir(hir_all)
    print(f"    [+] Terpilih untuk Korpus Final HIR (Opsi B): {len(hir_final)} pasal")
    print(f"        - Dari BAB IX (Pemeriksaan Perkara Perdata) : {sum(1 for c in hir_final if 'BAB IX' in c.get('bab', ''))} pasal")
    print(f"        - Dari BAB XV (Ketentuan Acara Perdata Terpilih) : {sum(1 for c in hir_final if 'BAB XV' in c.get('bab', ''))} pasal")
    print(f"        - Pasal Pidana BAB XV Dieliminasi : {len(HIR_BAB_XV_EXCLUDED_CRIMINAL)} pasal ({', '.join(sorted(HIR_BAB_XV_EXCLUDED_CRIMINAL))})")
    print(f"        - Pasal Usang BAB XV Dieliminasi  : {len(HIR_BAB_XV_EXCLUDED_OBSOLETE)} pasal ({', '.join(sorted(HIR_BAB_XV_EXCLUDED_OBSOLETE))})")
    print(f"        - Pasal BAB I Kepolisian Dieliminasi : {sum(1 for c in hir_all if c.get('bab', '').startswith('BAB I.'))} pasal")

    # 2. Proses KUHPerdata
    print("\n[*] Membaca seluruh chunk KUHPerdata...")
    kuh_all = load_jsonl(kuh_file)
    print(f"    [+] Total pasal KUHPerdata: {len(kuh_all)} pasal")

    # 3. Gabungkan menjadi Korpus Terpercaya Bersih (Clean Corpus)
    print("\n[*] Menggabungkan ke Korpus Bersih Terpadu (legal_corpus_clean.jsonl)...")
    clean_corpus = []

    # Tagging source category and computing SHA-256 hash per chunk
    manifest_records = []

    for c in kuh_all:
        chunk_data = dict(c)
        chunk_data["content_sha256"] = compute_sha256(chunk_data["content"])
        clean_corpus.append(chunk_data)

        manifest_records.append({
            "chunk_id": chunk_data["chunk_id"],
            "source": chunk_data["source"],
            "buku": chunk_data.get("buku", ""),
            "bab": chunk_data.get("bab", ""),
            "bagian": chunk_data.get("bagian", ""),
            "pasal": chunk_data["pasal"],
            "page_start": chunk_data["page_start"],
            "page_end": chunk_data["page_end"],
            "char_count": chunk_data["char_count"],
            "content_sha256": chunk_data["content_sha256"]
        })

    for c in hir_final:
        chunk_data = dict(c)
        chunk_data["content_sha256"] = compute_sha256(chunk_data["content"])
        clean_corpus.append(chunk_data)

        manifest_records.append({
            "chunk_id": chunk_data["chunk_id"],
            "source": chunk_data["source"],
            "buku": "",
            "bab": chunk_data.get("bab", ""),
            "bagian": chunk_data.get("bagian", ""),
            "pasal": chunk_data["pasal"],
            "page_start": chunk_data["page_start"],
            "page_end": chunk_data["page_end"],
            "char_count": chunk_data["char_count"],
            "content_sha256": chunk_data["content_sha256"]
        })

    print(f"    [+] Total Korpus Bersih (KUHPerdata + HIR): {len(clean_corpus)} pasal")

    # 4. Simpan hasil
    print("\n[*] Menyimpan file korpus...")
    write_jsonl(processed_dir / "hir_chunks_final.jsonl", hir_final)
    write_jsonl(processed_dir / "kuhperdata_chunks_final.jsonl", kuh_all)
    write_jsonl(processed_dir / "legal_corpus_clean.jsonl", clean_corpus)

    # 5. Simpan manifest integritas
    manifest_file = manifests_dir / "trusted_corpus_manifest.json"
    manifest_payload = {
        "corpus_name": "Indonesian Civil Law Clean Corpus (KUHPerdata + HIR)",
        "version": "1.0.0",
        "total_chunks": len(clean_corpus),
        "kuhperdata_count": len(kuh_all),
        "hir_count": len(hir_final),
        "chunks": manifest_records
    }
    with manifest_file.open("w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)

    print(f"    [+] File tersimpan:")
    print(f"        - data/processed/hir_chunks_final.jsonl ({len(hir_final)} chunks)")
    print(f"        - data/processed/kuhperdata_chunks_final.jsonl ({len(kuh_all)} chunks)")
    print(f"        - data/processed/legal_corpus_clean.jsonl ({len(clean_corpus)} chunks)")
    print(f"        - data/manifests/trusted_corpus_manifest.json ({len(manifest_records)} records)")

    print("\n" + "=" * 70)
    print("STATUS KORPUS: BERHASIL DIKUNCI DAN TERINTEGRASI SHA-256")
    print("=" * 70)


if __name__ == "__main__":
    main()
