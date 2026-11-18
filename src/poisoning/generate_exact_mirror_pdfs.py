"""
Skrip Pembangun Dokumen PDF Mirror Sempurna (1:1 Exact In-Place Mirror)
- KUHPerdata (354 Halaman, A4, Garamond/Times)
- HIR (27 Halaman, Letter, Helvetica)
Setiap pasal yang teracuni (poisoned) diganti persis di posisi aslinya dengan WARNA MERAH (#C00000).
Seluruh halaman, margin, header, footer, dan pasal non-poison tetap 100% identik dengan raw trusted PDF.
"""

import json
import re
from pathlib import Path
import pymupdf

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw_trusted"
OUT_DIR = BASE_DIR / "data" / "poisoning"

RED_COLOR = (0.78, 0.0, 0.0)  # Crimson Red #C70000 / #C00000


def load_poisoned_targets(rate_str: str = "1pct"):
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


def build_kuhperdata_pdf_mirror():
    raw_pdf = RAW_DIR / "kuhperdata.pdf"
    out_pdf = OUT_DIR / "KUHPerdata_Raw_Mirror_Exact_354pages_1pct.pdf"
    targets, _ = load_poisoned_targets("1pct")

    doc = pymupdf.open(raw_pdf)
    print(f"[KUHPerdata] Opening {raw_pdf.name} ({len(doc)} pages)...")

    # Precise coordinates for each of the 14 articles
    # Each item: pasal: (page_num_1based, y_start, y_end)
    # Special: Pasal 1792 splits between p. 323 and 324
    article_coords = {
        "330": (64, 328.0, 594.0),
        "570": (116, 696.0, 750.0),
        "830": (154, 334.0, 384.0),
        "852": (157, 571.0, 718.0),
        "863": (160, 298.0, 485.0),
        "1162": (210, 661.0, 724.0),
        "1243": (225, 192.0, 281.0),
        "1320": (236, 208.0, 323.0),
        "1365": (242, 82.0, 158.0),
        "1458": (257, 211.0, 287.0),
        "1740": (316, 228.0, 317.0),
        "1754": (318, 274.0, 364.0),
        "1967": (350, 132.0, 221.0),
    }

    # Process standard 13 articles
    for pasal, (pno, y0, y1) in article_coords.items():
        page = doc[pno - 1]
        t_data = targets[pasal]
        poison_content = t_data["content"].strip()

        # 1. Redact existing text area with pure white fill
        redact_rect = pymupdf.Rect(80.0, y0 - 2, 530.0, y1 + 2)
        page.add_redact_annot(redact_rect, fill=(1, 1, 1))
        page.apply_redactions()

        # 2. Insert Centered Heading "Pasal X" in RED
        heading_rect = pymupdf.Rect(80.0, y0, 530.0, y0 + 22.0)
        rc_h = page.insert_textbox(
            heading_rect,
            f"Pasal {t_data['pasal']}",
            fontname="times-bold",
            fontsize=11.0,
            color=RED_COLOR,
            align=1,  # Centered
        )

        # 3. Insert Article Body in RED
        body_rect = pymupdf.Rect(84.8, y0 + 24.0, 523.8, max(y1 + 4, y0 + 80.0))
        rc_b = page.insert_textbox(
            body_rect,
            poison_content,
            fontname="times-roman",
            fontsize=10.5,
            color=RED_COLOR,
            align=3,  # Justified
        )
        print(f"  Processed KUHPerdata Pasal {pasal} on page {pno} (head: {rc_h:.1f}pt, body: {rc_b:.1f}pt)")

    # Special handling for Pasal 1792 (p. 323 & 324)
    # Page 323 has the heading
    p323 = doc[322]
    p323_redact = pymupdf.Rect(80.0, 725.0, 530.0, 748.0)
    p323.add_redact_annot(p323_redact, fill=(1, 1, 1))
    p323.apply_redactions()
    p323_heading_rect = pymupdf.Rect(80.0, 726.0, 530.0, 744.0)
    p323.insert_textbox(
        p323_heading_rect,
        "Pasal 1792",
        fontname="times-bold",
        fontsize=11.0,
        color=RED_COLOR,
        align=1,
    )

    # Page 324 has the body before Pasal 1793
    p324 = doc[323]
    t1792 = targets["1792"]
    p324_redact = pymupdf.Rect(80.0, 83.0, 530.0, 128.0)
    p324.add_redact_annot(p324_redact, fill=(1, 1, 1))
    p324.apply_redactions()
    p324_body_rect = pymupdf.Rect(84.8, 84.5, 523.8, 126.0)
    rc1792 = p324.insert_textbox(
        p324_body_rect,
        t1792["content"].strip(),
        fontname="times-roman",
        fontsize=10.5,
        color=RED_COLOR,
        align=3,
    )
    print(f"  Processed KUHPerdata Pasal 1792 on pages 323 & 324 (spare space: {rc1792:.1f}pt)")

    doc.save(out_pdf)
    print(f"[KUHPerdata] Saved exact mirror to: {out_pdf} ({len(doc)} pages)\n")


def build_hir_pdf_mirror():
    raw_pdf = RAW_DIR / "hir.pdf"
    out_pdf = OUT_DIR / "HIR_Raw_Mirror_Exact_27pages_1pct.pdf"
    _, targets = load_poisoned_targets("1pct")

    doc = pymupdf.open(raw_pdf)
    print(f"[HIR] Opening {raw_pdf.name} ({len(doc)} pages)...")

    # Bounding boxes for all 9 HIR poisoned articles
    hir_coords = {
        "120": (3, 537.0, 589.5, "Pasal 120."),
        "121": (3, 688.5, 741.0, "Pasal 121."),
        "123": (4, 299.0, 449.0, "Pasal 123."),
        "125": (4, 526.0, 719.0, "Pasal 125."),
        "132a": (6, 137.0, 168.0, "Pasal 132a."),
        "132b": (6, 270.0, 441.5, "Pasal 132b."),
        "227": (23, 223.5, 416.5, "Pasal 227."),
        "374": (25, 721.0, 742.0, "374."),
        "390": (27, 310.0, 470.5, "390."),
    }

    for pasal, (pno, y0, y1, prefix) in hir_coords.items():
        page = doc[pno - 1]
        t_data = targets[pasal]
        poison_content = t_data["content"].strip()

        # 1. Redact existing text area with pure white fill
        redact_rect = pymupdf.Rect(98.0, y0 - 2, 545.0, y1 + 2)
        page.add_redact_annot(redact_rect, fill=(1, 1, 1))
        page.apply_redactions()

        # 2. Insert Poisoned Article Text in RED (Helvetica, 10pt)
        # Format matching HIR style: Prefix + paragraph or Prefix \n body
        if prefix.endswith("."):
            full_text = f"{prefix} {poison_content}"
        else:
            full_text = f"{prefix}\n{poison_content}"

        body_rect = pymupdf.Rect(101.5, y0, 541.0, max(y1 + 4, y0 + 50))
        rc = page.insert_textbox(
            body_rect,
            full_text,
            fontname="helvetica",
            fontsize=10.0,
            color=RED_COLOR,
            align=3,  # Justified
        )
        print(f"  Processed HIR Pasal {pasal} on page {pno} (spare space: {rc:.1f}pt)")

    doc.save(out_pdf)
    print(f"[HIR] Saved exact mirror to: {out_pdf} ({len(doc)} pages)\n")


if __name__ == "__main__":
    build_kuhperdata_pdf_mirror()
    build_hir_pdf_mirror()
