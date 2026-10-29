"""
Modul: Ingestion - Finalisasi Korpus Hukum Bersih & Manifest Kriptografi
Fungsi:
1. Memilih pasal HIR yang benar-benar mengatur Hukum Acara Perdata (133 pasal dari BAB IX
   ditambah 16 pasal ketentuan pendukung dari BAB XV).
2. Mengeliminasi pasal-pasal pidana dan pasal usang dari HIR.
3. Menggabungkan pasal HIR terpilih dengan seluruh pasal KUHPerdata (Total: 2.276 pasal).
4. Menghitung sidik jari kriptografi SHA-256 untuk setiap pasal ke dalam file manifest
   sebagai basis pertahanan modul Source Verification terhadap manipulasi teks (knowledge poisoning).

File Hasil:
- data/processed/hir_chunks_final.jsonl (149 pasal)
- data/processed/kuhperdata_chunks_final.jsonl (2.127 pasal)
- data/processed/legal_corpus_clean.jsonl (2.276 pasal bersih)
- data/manifests/trusted_corpus_manifest.json (Index hash SHA-256 terpercaya)
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set

# [DAFTAR SELEKSI HIR BAB XV]
# 16 pasal ketentuan umum yang mutlak berlaku dalam praktik peradilan perdata
HIR_BAB_XV_CIVIL_ARTICLES: Set[str] = {
    "372",  # Tata tertib persidangan & wewenang ketua majelis hakim
    "373",  # Penertiban dan keamanan ruang sidang
    "374",  # Hak ingkar hakim (larangan memeriksa perkara kepentingan keluarga/pribadi)
    "377",  # Arbitrase / juru pisah / wasit perdamaian perdata
    "378",  # Pembebanan biaya perkara perdata
    "379",  # Biaya pokrol / penasihat hukum / advokat
    "381",  # Tata cara pengangkatan sumpah saksi & para pihak menurut agamanya
    "382",  # Format surat keputusan dan penetapan perintah hakim perdata
    "383",  # Penyimpanan arsip keputusan dalam buku register majelis
    "388",  # Wewenang juru sita dalam menjalankan eksekusi putusan hakim
    "389",  # Laporan tertulis berita acara pelaksanaan tugas juru sita
    "390",  # Tata cara pemanggilan resmi (relaas panggilan) pihak tergugat/penggugat
    "391",  # Perhitungan tenggang waktu hukum acara
    "392",  # Hak kompensasi dan penggantian biaya hadir bagi saksi perkara perdata
    "393",  # Larangan menyimpang dari tata cara hukum acara yang ditentukan reglemen
    "394",  # Pemeriksaan setempat (descente) oleh hakim
}

# Daftar pasal HIR BAB XV yang sengaja DIKELUARKAN karena murni hukum pidana
HIR_BAB_XV_EXCLUDED_CRIMINAL: Set[str] = {
    "375",  # Tahanan perkara pidana
    "376",  # Kuasa pidana denda (psl 82 KUHP)
    "384",  # Register perkara pidana
    "385",  # Larangan salinan putusan perkara pidana
    "386",  # Pembelaan pesakitan/terdakwa pidana
    "387",  # Denda kelalaian panitera dalam pidana
}

# Daftar pasal HIR BAB XV yang DIKELUARKAN karena sudah usang/tidak berlaku
HIR_BAB_XV_EXCLUDED_OBSOLETE: Set[str] = {
    "380"   # "Tidak dimuat karena tidak sesuai lagi dengan keadaan sekarang"
}


def compute_sha256(text: str) -> str:
    """[UTILITAS] Menghitung nilai hash SHA-256 dari sebuah teks string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """[UTILITAS] Membaca file format JSON Lines (.jsonl)."""
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_jsonl(path: Path, items: List[Dict[str, Any]]) -> None:
    """[UTILITAS] Menyimpan data list ke dalam format JSON Lines (.jsonl)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def finalize_hir(hir_all_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    [PENYARINGAN PASAL HIR]
    Hanya meloloskan:
    1. Seluruh pasal dari BAB IX (Pemeriksaan Perkara Perdata).
    2. 16 pasal terpilih dari BAB XV yang relevan dengan tata cara perdata.
    """
    final_chunks = []

    for chunk in hir_all_chunks:
        bab = chunk.get("bab", "")
        pasal = chunk.get("pasal", "")

        # 1. Masukkan seluruh pasal BAB IX (Inti Perdata)
        if "BAB IX" in bab:
            chunk_copy = dict(chunk)
            chunk_copy["corpus_category"] = "hukum_acara_perdata_inti"
            final_chunks.append(chunk_copy)
            continue

        # 2. Masukkan pasal-pasal terpilih dari BAB XV
        if "BAB XV" in bab and pasal in HIR_BAB_XV_CIVIL_ARTICLES:
            chunk_copy = dict(chunk)
            chunk_copy["corpus_category"] = "hukum_acara_perdata_peraturan_umum"
            final_chunks.append(chunk_copy)
            continue

    return final_chunks


def main():
    """
    [PROSES UTAMA FINALISASI]
    1. Membaca data chunk mentah KUHPerdata dan HIR.
    2. Menyaring pasal HIR (membuang pidana dan usang).
    3. Menggabungkan kedua dokumen menjadi satu korpus perdata bersih.
    4. Menghitung SHA-256 setiap pasal dan menyusun file manifest terpercaya.
    """
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
    print("FINALISASI KORPUS HUKUM PERDATA & INTEGRITAS SUMBER")
    print("=" * 70)

    # 1. Proses Filter Dokumen HIR
    print("[*] Membaca seluruh chunk HIR...")
    hir_all = load_jsonl(hir_file)
    print(f"    Total kandidat chunk HIR mentah: {len(hir_all)}")

    hir_final = finalize_hir(hir_all)
    print(f"    [+] Terpilih untuk Korpus Final HIR: {len(hir_final)} pasal")
    print(f"        - Dari BAB IX (Pemeriksaan Perkara Perdata) : {sum(1 for c in hir_final if 'BAB IX' in c.get('bab', ''))} pasal")
    print(f"        - Dari BAB XV (Ketentuan Acara Perdata Terpilih) : {sum(1 for c in hir_final if 'BAB XV' in c.get('bab', ''))} pasal")
    print(f"        - Pasal Pidana BAB XV Dieliminasi : {len(HIR_BAB_XV_EXCLUDED_CRIMINAL)} pasal ({', '.join(sorted(HIR_BAB_XV_EXCLUDED_CRIMINAL))})")
    print(f"        - Pasal Usang BAB XV Dieliminasi  : {len(HIR_BAB_XV_EXCLUDED_OBSOLETE)} pasal ({', '.join(sorted(HIR_BAB_XV_EXCLUDED_OBSOLETE))})")
    print(f"        - Pasal BAB I Kepolisian Dieliminasi : {sum(1 for c in hir_all if c.get('bab', '').startswith('BAB I.'))} pasal")

    # 2. Proses Dokumen KUHPerdata
    print("\n[*] Membaca seluruh chunk KUHPerdata...")
    kuh_all = load_jsonl(kuh_file)
    print(f"    [+] Total pasal KUHPerdata: {len(kuh_all)} pasal")

    # 3. Penggabungan Korpus Bersih & Perhitungan Hash Kriptografi SHA-256
    print("\n[*] Menggabungkan ke Korpus Bersih Terpadu (legal_corpus_clean.jsonl)...")
    clean_corpus = []
    manifest_records = []

    # Memproses pasal-pasal KUHPerdata
    for c in kuh_all:
        chunk_data = dict(c)
        # Menghitung sidik jari SHA-256 dari isi teks pasal asli
        chunk_data["content_sha256"] = compute_sha256(chunk_data["content"])
        clean_corpus.append(chunk_data)

        # Mencatat metadata pasal ke dalam manifes integritas
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

    # Memproses pasal-pasal HIR terpilih
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

    # 4. Menyimpan File Korpus Final
    print("\n[*] Menyimpan file korpus...")
    write_jsonl(processed_dir / "hir_chunks_final.jsonl", hir_final)
    write_jsonl(processed_dir / "kuhperdata_chunks_final.jsonl", kuh_all)
    write_jsonl(processed_dir / "legal_corpus_clean.jsonl", clean_corpus)

    # 5. Menyimpan File Manifes Integritas (Basis Pertahanan Source Verification)
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
