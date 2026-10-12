"""
Module for chunking Indonesian Civil Law documents (KUHPerdata and HIR)
into verified article-level (per-pasal) chunks with rich structural metadata.

Produces:
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
    """Loads extracted JSONL file containing page-level texts."""
    pages = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pages.append(json.loads(line))
    return pages


def chunk_kuhperdata(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses KUHPerdata pages into article chunks.
    Detects Book, Chapter (BAB), Section (Bagian), and Articles (Pasal).
    Filters out inline article citations from being misidentified as new article headers.
    """
    buku_regex = re.compile(r"^\s*(BUKU\s+(?:KESATU|KEDUA|KETIGA|KEEMPAT|[A-Z]+))\b.*$", re.IGNORECASE)
    bab_regex = re.compile(r"^\s*(BAB\s+[IVXLCDM0-9]+)\.?\b.*$", re.IGNORECASE)
    bagian_regex = re.compile(r"^\s*(Bagian\s+\d+[a-z]?)\.?\b.*$", re.IGNORECASE)
    # Authentic article heading in KUHPerdata stands alone on its line:
    # "Pasal 1", "Pasal 1.", "Pasal 120a", etc.
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

    # Non-heading lines that wrapped inside sentences (prepositions / conjunctions)
    inline_preceding_words = {
        "dalam", "dengan", "pada", "atau", "dan", "terhadap", "ketentuan",
        "menurut", "maksud", "sebagaimana", "dimaksud", "berdasarkan", "keempat"
    }

    for page in pages:
        p_num = page["page_number"]
        lines = page.get("text", "").splitlines()

        for i, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                if current_pasal is not None and current_content:
                    current_content.append("")
                continue

            # Check BUKU
            # Only match if it's a standalone title or short heading line
            if len(line) < 40 and buku_regex.match(line):
                flush_article()
                current_buku = line
                current_bab = ""
                current_bagian = ""
                continue

            # Check BAB
            if len(line) < 60 and bab_regex.match(line):
                flush_article()
                current_bab = line
                current_bagian = ""
                continue

            # Check Bagian
            if len(line) < 60 and bagian_regex.match(line):
                flush_article()
                current_bagian = line
                continue

            # Check Article header
            m_pasal = pasal_header_regex.match(line)
            if m_pasal:
                # Validate whether this is an actual article header or wrapped sentence fragment
                # Check previous non-empty line in this page
                prev_line = ""
                for k in range(i - 1, -1, -1):
                    if lines[k].strip():
                        prev_line = lines[k].strip()
                        break

                prev_words = prev_line.lower().split()
                is_wrapped_sentence = False
                if prev_words and prev_words[-1] in inline_preceding_words:
                    is_wrapped_sentence = True

                # Also if prev line does not end with sentence terminal punctuation (. : ;)
                # and line starts with lowercase "pasal", it's an inline citation
                if raw_line.lstrip().startswith("pasal "):
                    is_wrapped_sentence = True

                if not is_wrapped_sentence:
                    flush_article()
                    current_pasal = m_pasal.group(1)
                    start_page = p_num
                    current_page = p_num
                    continue

            # Regular text line of the current article
            if current_pasal is not None:
                current_content.append(line)
                current_page = p_num

    flush_article()
    return chunks


def chunk_hir(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses HIR pages into article chunks.
    Detects BAB I (Kepolisian), BAB IX (Pemeriksaan Perkara Perdata), and BAB XV (Berbagai Peraturan).
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
        nonlocal current_pasal, current_content, start_page, current_page
        if current_pasal is not None:
            text_body = "\n".join(current_content).strip()
            # Determine chapter code for unique ID
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

            # BAB detection
            m_bab = bab_regex.match(line)
            if m_bab:
                flush_article()
                current_bab = line
                current_bagian = ""
                continue

            # Bagian detection
            m_bag = bagian_regex.match(line)
            if m_bag:
                flush_article()
                current_bagian = line
                continue

            # 1. Standard "Pasal XXX"
            m_pasal = pasal_header_regex.match(line)
            if m_pasal:
                flush_article()
                current_pasal = m_pasal.group(1)
                start_page = p_num
                current_page = p_num
                continue

            # Special case on Page 1: Pasal 3 has inline text "Pasal 3.  Di bawah pengawasan..."
            m_pasal_inline = re.match(r"^Pasal\s+(\d+[a-z]?)\.\s+(.*)$", line)
            if m_pasal_inline and "BAB I" in current_bab:
                flush_article()
                current_pasal = m_pasal_inline.group(1)
                start_page = p_num
                current_page = p_num
                current_content.append(m_pasal_inline.group(2).strip())
                continue

            # 2. Numbered articles in BAB XV (e.g. "372. (1) Ketua majelis...")
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

            # 3. Numbered articles in BAB I (e.g. "4.  (1) Seminggu sekali...")
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

            # Regular text line of current article
            if current_pasal is not None:
                current_content.append(line)
                current_page = p_num

    flush_article()
    return chunks


def build_report(kuh_chunks: List[Dict[str, Any]],
                 hir_chunks: List[Dict[str, Any]],
                 hir_bab_ix: List[Dict[str, Any]],
                 hir_other: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds a comprehensive audit report for the chunking process."""
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def main():
    base_dir = Path(__file__).resolve().parents[2]
    extracted_dir = base_dir / "data" / "extracted"
    processed_dir = base_dir / "data" / "processed"

    kuh_extracted_file = extracted_dir / "kuhperdata.jsonl"
    hir_extracted_file = extracted_dir / "hir.jsonl"

    print("=" * 65)
    print("MEMULAI PROSES CHUNKING ARTIKEL HUKUM (KUHPerdata & HIR)")
    print("=" * 65)

    # 1. KUHPerdata
    if not kuh_extracted_file.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {kuh_extracted_file}")
    print(f"[*] Membaca {kuh_extracted_file.name}...")
    kuh_pages = load_extracted_jsonl(kuh_extracted_file)
    kuh_chunks = chunk_kuhperdata(kuh_pages)
    print(f"    -> Berhasil mengekstrak {len(kuh_chunks)} pasal KUHPerdata.")

    # 2. HIR
    if not hir_extracted_file.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {hir_extracted_file}")
    print(f"[*] Membaca {hir_extracted_file.name}...")
    hir_pages = load_extracted_jsonl(hir_extracted_file)
    hir_chunks = chunk_hir(hir_pages)
    print(f"    -> Berhasil mengekstrak {len(hir_chunks)} total pasal HIR.")

    # Separate HIR BAB IX (hukum acara perdata) and others
    hir_bab_ix = [c for c in hir_chunks if "BAB IX" in c.get("bab", "")]
    hir_other = [c for c in hir_chunks if "BAB IX" not in c.get("bab", "")]

    print(f"    -> HIR BAB IX (kandidat utama perdata): {len(hir_bab_ix)} pasal.")
    print(f"    -> HIR Bab lainnya (BAB I & XV untuk review): {len(hir_other)} pasal.")

    # 3. Save outputs
    print("\n[*] Menyimpan file JSONL hasil chunking...")
    write_jsonl(processed_dir / "kuhperdata_chunks_all.jsonl", kuh_chunks)
    write_jsonl(processed_dir / "hir_chunks_all.jsonl", hir_chunks)
    write_jsonl(processed_dir / "hir_chunks_bab_ix_review.jsonl", hir_bab_ix)
    write_jsonl(processed_dir / "hir_chunks_other_chapters_review.jsonl", hir_other)

    # 4. Generate & Save report
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
    print(f"4. Total Semua File Output :")
    print(f"   - data/processed/kuhperdata_chunks_all.jsonl")
    print(f"   - data/processed/hir_chunks_all.jsonl")
    print(f"   - data/processed/hir_chunks_bab_ix_review.jsonl")
    print(f"   - data/processed/hir_chunks_other_chapters_review.jsonl")
    print(f"   - data/processed/chunking_report.json")
    print("=" * 65)


if __name__ == "__main__":
    main()
