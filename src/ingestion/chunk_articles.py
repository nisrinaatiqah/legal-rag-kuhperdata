"""
Modul: Ingestion - Pemotongan Teks Hukum Menjadi Satuan Pasal (Article-Level Chunking)
Fungsi: Memecah dokumen mentah KUHPerdata dan HIR menjadi potongan (chunks) setingkat pasal,
lengkap dengan hierarki struktur hukum (Buku, Bab, Bagian, Nomor Pasal, Halaman).

Hasil Output:
- data/processed/kuhperdata_chunks_all.jsonl
- data/processed/hir_chunks_all.jsonl
- data/processed/hir_chunks_bab_ix_review.jsonl
- data/processed/hir_chunks_other_chapters_review.jsonl
- data/processed/chunking_report.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_extracted_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    [PROSES BACA DATA] Membaca file JSONL hasil ekstraksi halaman per halaman.
    """
    pages = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pages.append(json.loads(line))
    return pages


def chunk_kuhperdata(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    [PARSER KHUSUS KUHPERDATA]
    Memindai baris teks KUHPerdata untuk mendeteksi batas struktural:
    1. BUKU (Buku I s/d IV)
    2. BAB (Bab I, II, dst.)
    3. Bagian (Bagian 1, dst.)
    4. Pasal (Kepala Pasal mandiri seperti 'Pasal 1320')
    
    *Catatan Filter:* Mencegah penyebutan pasal di tengah kalimat (misal: 'sebagaimana dimaksud dalam pasal...')
    agar tidak salah dideteksi sebagai judul pasal baru.
    """
    # Regex untuk mendeteksi hierarki KUHPerdata
    buku_regex = re.compile(r"^\s*(BUKU\s+(?:KESATU|KEDUA|KETIGA|KEEMPAT|[A-Z]+))\b.*$", re.IGNORECASE)
    bab_regex = re.compile(r"^\s*(BAB\s+[IVXLCDM0-9]+)\.?\b.*$", re.IGNORECASE)
    bagian_regex = re.compile(r"^\s*(Bagian\s+\d+[a-z]?)\.?\b.*$", re.IGNORECASE)
    # Header pasal sah berdiri sendiri di barisnya: "Pasal 1", "Pasal 1.", "Pasal 120a"
    pasal_header_regex = re.compile(r"^Pasal\s+(\d+[a-z]?)\.?\s*$", re.IGNORECASE)

    chunks = []
    current_buku = ""
    current_bab = ""
    current_bagian = ""
    current_pasal = None
    current_content: List[str] = []
    start_page = None
    current_page = None

    def flush_article():
        """Menyimpan pasal yang sedang aktif ke dalam daftar chunk jika sudah selesai dibaca."""
        nonlocal current_pasal, current_content, start_page, current_page
        if current_pasal is not None:
            text_body = "\n".join(current_content).strip()
            chunks.append({
                "chunk_id": f"KUHPERDATA_PASAL_{current_pasal}",
                "source": "KUHPerdata",
                "buku": current_buku,
                "bab": current_bab,
                "bagian": current_bagian,
                "pasal": current_pasal,
                "page_start": start_page,
                "page_end": current_page,
                "content": text_body,
                "char_count": len(text_body)
            })
            current_content = []
            current_pasal = None

    # Kata-kata penghubung yang mengindikasikan teks pasal berlanjut dan bukan header baru
    inline_preceding_words = {
        "dalam", "dengan", "pada", "atau", "dan", "terhadap", "ketentuan",
        "menurut", "maksud", "sebagaimana", "dimaksud", "berdasarkan", "keempat"
    }

    # Memproses halaman per halaman
    for page in pages:
        p_num = page["page_number"]
        lines = page.get("text", "").splitlines()

        for i, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                if current_pasal is not None and current_content:
                    current_content.append("")
                continue

            # 1. Deteksi Judul BUKU
            if len(line) < 40 and buku_regex.match(line):
                flush_article()
                current_buku = line
                current_bab = ""
                current_bagian = ""
                continue

            # 2. Deteksi Judul BAB
            if len(line) < 60 and bab_regex.match(line):
                flush_article()
                current_bab = line
                current_bagian = ""
                continue

            # 3. Deteksi Judul Bagian
            if len(line) < 60 and bagian_regex.match(line):
                flush_article()
                current_bagian = line
                continue

            # 4. Deteksi Header PASAL
            m_pasal = pasal_header_regex.match(line)
            if m_pasal:
                # Validasi apakah ini pasal sungguhan atau potongan kalimat lanjutan
                prev_line = ""
                for k in range(i - 1, -1, -1):
                    if lines[k].strip():
                        prev_line = lines[k].strip()
                        break

                prev_words = prev_line.lower().split()
                is_wrapped_sentence = False
                if prev_words and prev_words[-1] in inline_preceding_words:
                    is_wrapped_sentence = True

                # Jika baris sebelumnya tidak berakhiran tanda baca akhir dan diawali huruf kecil
                if raw_line.lstrip().startswith("pasal "):
                    is_wrapped_sentence = True

                if not is_wrapped_sentence:
                    flush_article()
                    current_pasal = m_pasal.group(1)
                    start_page = p_num
                    current_page = p_num
                    continue

            # 5. Isi Teks dari Pasal yang Sedang Aktif
            if current_pasal is not None:
                current_content.append(line)
                current_page = p_num

    flush_article()
    return chunks


def chunk_hir(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    [PARSER KHUSUS HIR - HUKUM ACARA PERDATA]
    Mengekstrak pasal-pasal dari dokumen HIR:
    - BAB I (Bagian Kepolisian)
    - BAB IX (Pemeriksaan Perkara Perdata - Bagian paling inti untuk perdata)
    - BAB XV (Berbagai Macam Peraturan Tambahan)
    """
    bab_regex = re.compile(r"^\s*(BAB\s+[IVXLCDM0-9]+)\.?\s*(.*?)$", re.IGNORECASE)
    bagian_regex = re.compile(r"^\s*(Bagian\s+\d+[a-z]?)\.?\s*(.*?)$", re.IGNORECASE)
    pasal_header_regex = re.compile(r"^Pasal\s+(\d+[a-z]?)\.?\s*$", re.IGNORECASE)
    bab_xv_art_regex = re.compile(r"^(3[7-9]\d)\.\s*(.*)$")
    bab_i_art_regex = re.compile(r"^(\d{1,2})\.\s*(.*)$")

    chunks = []
    current_bab = ""
    current_bagian = ""
    current_pasal = None
    current_content: List[str] = []
    start_page = None
    current_page = None

    def flush_article():
        """Menyimpan potongan pasal HIR ke daftar chunk."""
        nonlocal current_pasal, current_content, start_page, current_page
        if current_pasal is not None:
            text_body = "\n".join(current_content).strip()
            # Menentukan tag bab untuk penomoran ID unik
            ch_tag = "BAB_IX" if "BAB IX" in current_bab else ("BAB_I" if "BAB I" in current_bab else "BAB_XV")
            chunks.append({
                "chunk_id": f"HIR_{ch_tag}_PASAL_{current_pasal}",
                "source": "HIR",
                "bab": current_bab,
                "bagian": current_bagian,
                "pasal": current_pasal,
                "page_start": start_page,
                "page_end": current_page,
                "content": text_body,
                "char_count": len(text_body)
            })
            current_content = []
            current_pasal = None

    for page in pages:
        p_num = page["page_number"]
        lines = page.get("text", "").splitlines()

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                if current_pasal is not None and current_content:
                    current_content.append("")
                continue

            # Deteksi Bab
            m_bab = bab_regex.match(line)
            if m_bab:
                flush_article()
                current_bab = line
                current_bagian = ""
                continue

            # Deteksi Bagian
            m_bag = bagian_regex.match(line)
            if m_bag:
                flush_article()
                current_bagian = line
                continue

            # Deteksi Standar: "Pasal XXX"
            m_pasal = pasal_header_regex.match(line)
            if m_pasal:
                flush_article()
                current_pasal = m_pasal.group(1)
                start_page = p_num
                current_page = p_num
                continue

            # Kasus Khusus Halaman 1: "Pasal 3. Di bawah pengawasan..."
            m_pasal_inline = re.match(r"^Pasal\s+(\d+[a-z]?)\.\s+(.*)$", line)
            if m_pasal_inline and "BAB I" in current_bab:
                flush_article()
                current_pasal = m_pasal_inline.group(1)
                start_page = p_num
                current_page = p_num
                current_content.append(m_pasal_inline.group(2).strip())
                continue

            # Format Angka Langsung di BAB XV (misal: "372. (1) Ketua majelis...")
            if "BAB XV" in current_bab:
                m_xv = bab_xv_art_regex.match(line)
                if m_xv:
                    flush_article()
                    current_pasal = m_xv.group(1)
                    start_page = p_num
                    current_page = p_num
                    if m_xv.group(2).strip():
                        current_content.append(m_xv.group(2).strip())
                    continue

            # Format Angka Langsung di BAB I (misal: "4. (1) Seminggu sekali...")
            if "BAB I" in current_bab and not ("BAB IX" in current_bab or "BAB XV" in current_bab):
                m_i = bab_i_art_regex.match(line)
                if m_i and int(m_i.group(1)) >= 4:
                    flush_article()
                    current_pasal = m_i.group(1)
                    start_page = p_num
                    current_page = p_num
                    if m_i.group(2).strip():
                        current_content.append(m_i.group(2).strip())
                    continue

            # Baris Teks Isi Pasal
            if current_pasal is not None:
                current_content.append(line)
                current_page = p_num

    flush_article()
    return chunks


def build_report(kuh_chunks: List[Dict[str, Any]],
                 hir_chunks: List[Dict[str, Any]],
                 hir_bab_ix: List[Dict[str, Any]],
                 hir_other: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    [AUDIT & STATISTIK] Menyusun laporan statistik jumlah pasal, panjang karakter rata-rata,
    dan sebaran pasal per bab untuk memastikan tidak ada pasal yang terpotong aneh.
    """
    def stats_for(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not items:
            return {"count": 0}
        char_lens = [c["char_count"] for c in items]
        babs = {}
        for c in items:
            b = c.get("bab") or "TANPA_BAB"
            babs[b] = babs.get(b, 0) + 1

        short = [c["chunk_id"] for c in items if c["char_count"] < 100]
        return {
            "total_chunks": len(items),
            "min_char_count": min(char_lens),
            "max_char_count": max(char_lens),
            "avg_char_count": round(sum(char_lens) / len(char_lens), 1),
            "distribution_by_bab": babs,
            "short_chunks_count": len(short),
            "short_chunks_samples": short[:10]
        }

    return {
        "kuhperdata": stats_for(kuh_chunks),
        "hir_all": stats_for(hir_chunks),
        "hir_bab_ix_review": stats_for(hir_bab_ix),
        "hir_other_chapters_review": stats_for(hir_other)
    }


def write_jsonl(path: Path, items: List[Dict[str, Any]]) -> None:
    """[UTILITAS] Menyimpan list dictionary menjadi file format JSON Lines (.jsonl)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def main():
    """
    [ALUR UTAMA CHUNKING]
    Mengeksekusi pemotongan artikel untuk KUHPerdata dan HIR secara berurutan,
    memisahkan Bab Acara Perdata, dan menyimpan laporan audit.
    """
    base_dir = Path(__file__).resolve().parents[2]
    extracted_dir = base_dir / "data" / "extracted"
    processed_dir = base_dir / "data" / "processed"

    kuh_extracted_file = extracted_dir / "kuhperdata.jsonl"
    hir_extracted_file = extracted_dir / "hir.jsonl"

    print("=" * 65)
    print("MEMULAI PROSES CHUNKING ARTIKEL HUKUM (KUHPerdata & HIR)")
    print("=" * 65)

    # 1. Eksekusi Chunking KUHPerdata
    if not kuh_extracted_file.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {kuh_extracted_file}")
    print(f"[*] Membaca {kuh_extracted_file.name}...")
    kuh_pages = load_extracted_jsonl(kuh_extracted_file)
    kuh_chunks = chunk_kuhperdata(kuh_pages)
    print(f"    -> Berhasil mengekstrak {len(kuh_chunks)} pasal KUHPerdata.")

    # 2. Eksekusi Chunking HIR
    if not hir_extracted_file.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {hir_extracted_file}")
    print(f"[*] Membaca {hir_extracted_file.name}...")
    hir_pages = load_extracted_jsonl(hir_extracted_file)
    hir_chunks = chunk_hir(hir_pages)
    print(f"    -> Berhasil mengekstrak {len(hir_chunks)} total pasal HIR.")

    # Pisahkan BAB IX (Acara Perdata Murni) dengan bab lainnya
    hir_bab_ix = [c for c in hir_chunks if "BAB IX" in c.get("bab", "")]
    hir_other = [c for c in hir_chunks if "BAB IX" not in c.get("bab", "")]

    print(f"    -> HIR BAB IX (kandidat utama perdata): {len(hir_bab_ix)} pasal.")
    print(f"    -> HIR Bab lainnya (BAB I & XV untuk review): {len(hir_other)} pasal.")

    # 3. Simpan Hasil Pemotongan ke File JSONL
    print("\n[*] Menyimpan file JSONL hasil chunking...")
    write_jsonl(processed_dir / "kuhperdata_chunks_all.jsonl", kuh_chunks)
    write_jsonl(processed_dir / "hir_chunks_all.jsonl", hir_chunks)
    write_jsonl(processed_dir / "hir_chunks_bab_ix_review.jsonl", hir_bab_ix)
    write_jsonl(processed_dir / "hir_chunks_other_chapters_review.jsonl", hir_other)

    # 4. Buat dan Simpan Laporan Audit Chunking
    report = build_report(kuh_chunks, hir_chunks, hir_bab_ix, hir_other)
    report_file = processed_dir / "chunking_report.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[*] Laporan audit berhasil disimpan ke {report_file.name}")

    print("\n" + "=" * 65)
    print("RINGKASAN EKSEKUSI CHUNKING:")
    print("=" * 65)
    print(f"1. KUHPerdata Chunks Total : {len(kuh_chunks)}")
    print(f"   Rata-rata karakter      : {report['kuhperdata']['avg_char_count']} chars")
    print(f"2. HIR BAB IX (Utama)      : {len(hir_bab_ix)}")
    print(f"   Rata-rata karakter      : {report['hir_bab_ix_review']['avg_char_count']} chars")
    print(f"3. HIR Bab Lain (Review)   : {len(hir_other)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
