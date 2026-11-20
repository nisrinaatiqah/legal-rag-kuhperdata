"""
Generator Dokumen PDF Mirror Sempurna (1:1 Exact In-Place Mirror)
Menghasilkan replika PDF KUHPerdata (354 Halaman) dan HIR (27 Halaman)
untuk tingkat keracunan 1%, 5%, dan 10%.
Setiap pasal yang teracuni diganti persis di posisi aslinya dengan WARNA MERAH (#C70000).
Semua halaman, tata letak, margin, header, footer, dan pasal asli lainnya 100% identik dengan raw trusted PDF.
File disimpan langsung dengan format standar:
- KUHPerdata_Raw_Poisoned_{rate}.pdf
- HIR_Raw_Poisoned_{rate}.pdf
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pymupdf

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw_trusted"
OUT_DIR = BASE_DIR / "data" / "poisoning"

RED_COLOR = (0.78, 0.0, 0.0)  # Crimson Red #C70000

# Koordinat presisi untuk seluruh 25 pasal beracun HIR (tercakup dari 1%, 5%, hingga 10%)
# Format: pasal: (page_1based, y0, y1, prefix)
HIR_PRECISE_COORDS = {
    "14": (2, 234.7, 277.1, "14."),
    "94": (19, 494.2, 590.5, "Pasal 94."),
    "97": (20, 105.0, 147.3, "Pasal 97."),
    "118": (3, 256.3, 493.2, "Pasal 118."),
    "120": (3, 537.4, 590.5, "Pasal 120."),
    "121": (3, 688.7, 740.0, "Pasal 121."),
    "123": (4, 299.5, 450.0, "Pasal 123."),
    "125": (4, 526.7, 720.1, "Pasal 125."),
    "130": (5, 494.2, 612.1, "Pasal 130."),
    "132a": (6, 137.5, 173.6, "Pasal 132a."),
    "132b": (6, 270.5, 442.4, "Pasal 132b."),
    "134": (6, 519.1, 582.9, "Pasal 134."),
    "164": (11, 677.9, 740.0, "Pasal 164."),
    "175": (12, 710.4, 740.0, "Pasal 175."),
    "181": (13, 505.0, 687.7, "Pasal 181."),
    "186": (14, 463.6, 538.3, "Pasal 186."),
    "199": (17, 645.5, 720.1, "Pasal 199."),
    "214": (21, 105.0, 147.3, "Pasal 214."),
    "215": (21, 148.3, 190.5, "Pasal 215."),
    "216": (21, 191.5, 320.3, "Pasal 216."),
    "227": (23, 223.9, 417.5, "Pasal 227."),
    "373": (25, 667.1, 720.1, "373."),
    "374": (25, 721.1, 740.0, "374."),
    "377": (26, 267.3, 309.5, "377."),
    "390": (27, 310.5, 471.6, "390."),
}


def load_poisoned_corpus(rate_str: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Memuat pasal-pasal yang teracuni untuk rate tertentu."""
    p_path = OUT_DIR / f"corpus_poisoned_{rate_str}.jsonl"
    with open(p_path, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]

    kuhp = {
        str(it["pasal"]).strip().lower(): it
        for it in items
        if it.get("is_poisoned") and it.get("source") == "KUHPerdata"
    }
    hir = {
        str(it["pasal"]).strip().lower(): it
        for it in items
        if it.get("is_poisoned") and it.get("source") == "HIR"
    }
    return kuhp, hir


# ==============================================================================
# KUHPerdata Exact Mirror Builder
# ==============================================================================

def index_kuhperdata_structure(doc: pymupdf.Document):
    """
    Mengindeks seluruh blok teks KUHPerdata untuk menemukan posisi dan batas setiap pasal.
    """
    struct_re = re.compile(r'^\s*(?:Pasal\s+\d+[a-z]?|BUKU\s+|BAB\s+|BAGIAN\s+)', re.IGNORECASE)
    pages_blocks = []
    for pno in range(len(doc)):
        page = doc[pno]
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        pages_blocks.append(blocks)

    return pages_blocks, struct_re


def get_kuhperdata_article_bounds(
    pasal_str: str,
    pages_blocks: List[Any],
    struct_re: re.Pattern
) -> Optional[List[Dict[str, Any]]]:
    """
    Mencari koordinat (halaman, y0, y1) untuk pasal tertentu di KUHPerdata.
    """
    p_clean = pasal_str.strip().lower()
    target_re = re.compile(rf'^\s*Pasal\s+{p_clean}\b', re.IGNORECASE)

    start_pno = None
    start_bidx = None

    for pno, blocks in enumerate(pages_blocks):
        for bidx, b in enumerate(blocks):
            txt = b[4].strip()
            lines = [l.strip() for l in txt.splitlines() if l.strip()]
            for l in lines:
                if target_re.match(l):
                    start_pno = pno
                    start_bidx = bidx
                    break
            if start_pno is not None:
                break
        if start_pno is not None:
            break

    if start_pno is None:
        return None

    bounds = []
    pno = start_pno
    bidx = start_bidx
    blocks = pages_blocks[pno]
    y0 = blocks[bidx][1]

    # Cari blok struktural berikutnya di halaman yang sama
    next_bidx = None
    for j in range(bidx + 1, len(blocks)):
        txt = blocks[j][4].strip()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if lines and struct_re.match(lines[0]):
            next_bidx = j
            break

    if next_bidx is not None:
        y1 = blocks[next_bidx][1]
        bounds.append({"page_idx": pno, "y0": y0, "y1": y1, "role": "full"})
    else:
        y1 = max(blocks[-1][3], 745.0)
        bounds.append({"page_idx": pno, "y0": y0, "y1": y1, "role": "start_split"})

        # Cek halaman berikutnya apakah ada kelanjutan sebelum header struktural pertama
        if pno + 1 < len(pages_blocks):
            next_blocks = pages_blocks[pno + 1]
            first_struct_idx = None
            for j, b in enumerate(next_blocks):
                txt = b[4].strip()
                lines = [l.strip() for l in txt.splitlines() if l.strip()]
                if lines and struct_re.match(lines[0]):
                    first_struct_idx = j
                    break

            if first_struct_idx is not None and first_struct_idx > 0:
                y0_cont = next_blocks[0][1]
                y1_cont = next_blocks[first_struct_idx][1]
                bounds.append({"page_idx": pno + 1, "y0": y0_cont, "y1": y1_cont, "role": "end_split"})

    return bounds


def build_kuhperdata_rate_mirror(rate_str: str):
    raw_pdf = RAW_DIR / "kuhperdata.pdf"
    out_pdf = OUT_DIR / f"KUHPerdata_Raw_Poisoned_{rate_str}.pdf"
    targets, _ = load_poisoned_corpus(rate_str)

    doc = pymupdf.open(raw_pdf)
    print(f"[KUHPerdata {rate_str}] Opening raw PDF ({len(doc)} pages)... Target poisoned: {len(targets)}")

    pages_blocks, struct_re = index_kuhperdata_structure(doc)
    processed = 0

    for pasal, t_data in targets.items():
        bounds = get_kuhperdata_article_bounds(pasal, pages_blocks, struct_re)
        if not bounds:
            print(f"  WARNING: Could not find Pasal {pasal} in KUHPerdata!")
            continue

        pasal_num_display = t_data.get("pasal", pasal)
        content_text = t_data.get("content", "").strip()

        if len(bounds) == 1:
            b = bounds[0]
            pno = b["page_idx"]
            page = doc[pno]
            y0, y1 = b["y0"], b["y1"]

            redact_rect = pymupdf.Rect(80.0, y0 - 2, 530.0, y1 + 2)
            page.add_redact_annot(redact_rect, fill=(1, 1, 1))
            page.apply_redactions()

            heading_rect = pymupdf.Rect(80.0, y0, 530.0, y0 + 20.0)
            page.insert_textbox(
                heading_rect,
                f"Pasal {pasal_num_display}",
                fontname="times-bold",
                fontsize=11.0,
                color=RED_COLOR,
                align=1,
            )

            body_rect = pymupdf.Rect(84.8, y0 + 22.0, 523.8, y1 + 2.0)
            for fsize in [10.5, 10.0, 9.5, 9.0, 8.5]:
                rc = page.insert_textbox(
                    body_rect,
                    content_text,
                    fontname="times-roman",
                    fontsize=fsize,
                    color=RED_COLOR,
                    align=3,
                )
                if rc >= 0:
                    break

        elif len(bounds) == 2:
            b1, b2 = bounds[0], bounds[1]
            page1 = doc[b1["page_idx"]]
            page2 = doc[b2["page_idx"]]

            r1 = pymupdf.Rect(80.0, b1["y0"] - 2, 530.0, b1["y1"] + 2)
            page1.add_redact_annot(r1, fill=(1, 1, 1))
            page1.apply_redactions()

            r2 = pymupdf.Rect(80.0, b2["y0"] - 2, 530.0, b2["y1"] + 2)
            page2.add_redact_annot(r2, fill=(1, 1, 1))
            page2.apply_redactions()

            h1 = b1["y1"] - b1["y0"]
            if h1 < 35.0:
                h_rect = pymupdf.Rect(80.0, b1["y0"], 530.0, b1["y0"] + 20.0)
                page1.insert_textbox(
                    h_rect,
                    f"Pasal {pasal_num_display}",
                    fontname="times-bold",
                    fontsize=11.0,
                    color=RED_COLOR,
                    align=1,
                )
                b_rect2 = pymupdf.Rect(84.8, b2["y0"], 523.8, b2["y1"])
                page2.insert_textbox(
                    b_rect2,
                    content_text,
                    fontname="times-roman",
                    fontsize=10.5,
                    color=RED_COLOR,
                    align=3,
                )
            else:
                h_rect = pymupdf.Rect(80.0, b1["y0"], 530.0, b1["y0"] + 20.0)
                page1.insert_textbox(
                    h_rect,
                    f"Pasal {pasal_num_display}",
                    fontname="times-bold",
                    fontsize=11.0,
                    color=RED_COLOR,
                    align=1,
                )
                b_rect1 = pymupdf.Rect(84.8, b1["y0"] + 22.0, 523.8, b1["y1"])
                rc1 = page1.insert_textbox(
                    b_rect1,
                    content_text,
                    fontname="times-roman",
                    fontsize=10.0,
                    color=RED_COLOR,
                    align=3,
                )
                if rc1 < 0:
                    b_rect2 = pymupdf.Rect(84.8, b2["y0"], 523.8, b2["y1"])
                    page2.insert_textbox(
                        b_rect2,
                        content_text,
                        fontname="times-roman",
                        fontsize=10.0,
                        color=RED_COLOR,
                        align=3,
                    )
        processed += 1

    doc.save(out_pdf)
    print(f"[KUHPerdata {rate_str}] SAVED: {out_pdf.name} ({len(doc)} pages, {processed}/{len(targets)} replaced)\n")


# ==============================================================================
# HIR Exact Mirror Builder
# ==============================================================================

def build_hir_rate_mirror(rate_str: str):
    raw_pdf = RAW_DIR / "hir.pdf"
    out_pdf = OUT_DIR / f"HIR_Raw_Poisoned_{rate_str}.pdf"
    _, targets = load_poisoned_corpus(rate_str)

    doc = pymupdf.open(raw_pdf)
    print(f"[HIR {rate_str}] Opening raw PDF ({len(doc)} pages)... Target poisoned: {len(targets)}")

    processed = 0
    for pasal, t_data in targets.items():
        if pasal not in HIR_PRECISE_COORDS:
            print(f"  WARNING: Pasal {pasal} not in HIR_PRECISE_COORDS!")
            continue

        pno_1based, y0, y1, prefix = HIR_PRECISE_COORDS[pasal]
        pno = pno_1based - 1
        page = doc[pno]
        content_text = t_data.get("content", "").strip()

        # Redact area
        redact_rect = pymupdf.Rect(98.0, y0 - 2.0, 545.0, y1 + 2.0)
        page.add_redact_annot(redact_rect, fill=(1, 1, 1))
        page.apply_redactions()

        # Text with prefix
        if prefix.endswith("."):
            full_text = f"{prefix} {content_text}"
        else:
            full_text = f"{prefix}\n{content_text}"

        body_rect = pymupdf.Rect(101.5, y0, 541.0, max(y1 + 4.0, y0 + 40.0))

        for fsize in [10.0, 9.5, 9.0, 8.5]:
            rc = page.insert_textbox(
                body_rect,
                full_text,
                fontname="helvetica",
                fontsize=fsize,
                color=RED_COLOR,
                align=3,  # Justified
            )
            if rc >= 0:
                break
        processed += 1

    doc.save(out_pdf)
    print(f"[HIR {rate_str}] SAVED: {out_pdf.name} ({len(doc)} pages, {processed}/{len(targets)} replaced)\n")


def main():
    rates = ["1pct", "5pct", "10pct"]
    for r in rates:
        build_kuhperdata_rate_mirror(r)
        build_hir_rate_mirror(r)
    print("[SUCCESS] Seluruh 6 file PDF Mirror Sempurna (1:1 Exact) berhasil dibuat persis di posisi aslinya!")


if __name__ == "__main__":
    main()
