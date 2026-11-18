"""
Skrip: Pembangun Naskah Hukum Persis Format Asli (Plek Format Raw)
Format: Word (.docx) dan PDF (.pdf)
Tujuan: Mereproduksi naskah regulasi KUHPerdata dan HIR persis seperti file PDF raw (data/raw_trusted/),
dengan tata letak, hierarki, dan urutan teks asli, di mana pasal yang teracuni (poisoned)
diganti dengan teks racun dan diberi WARNA MERAH secara langsung tanpa banner atau kotak tambahan.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parents[2]


def load_poisoned_map(rate_str: str = "1pct") -> Tuple[Dict[str, str], Dict[str, str]]:
    """Memuat daftar pasal yang teracuni untuk KUHPerdata dan HIR."""
    p_path = BASE_DIR / "data" / "poisoning" / f"corpus_poisoned_{rate_str}.jsonl"
    with open(p_path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f if line.strip()]

    kuhp_map = {}
    hir_map = {}
    for item in data:
        if item.get("is_poisoned"):
            src = item.get("source")
            pasal = str(item.get("pasal")).strip().lower()
            content = item.get("content", "")
            if src == "KUHPerdata":
                kuhp_map[pasal] = content
            elif src == "HIR":
                hir_map[pasal] = content

    return kuhp_map, hir_map


def parse_kuhperdata_stream() -> List[Dict[str, Any]]:
    """
    Mengekstrak seluruh aliran teks KUHPerdata dari data/extracted/kuhperdata.jsonl
    menjadi urutan elemen: Heading, Text biasa, atau Blok Pasal.
    """
    raw_path = BASE_DIR / "data" / "extracted" / "kuhperdata.jsonl"
    with open(raw_path, "r", encoding="utf-8") as f:
        pages = [json.loads(line) for line in f if line.strip()]

    all_lines = []
    for p in pages:
        all_lines.extend(p["text"].splitlines())

    pasal_regex = re.compile(r"^\s*Pasal\s+(\d+[a-z]?)\.?\s*$", re.IGNORECASE)
    buku_regex = re.compile(r"^\s*BUKU\s+(?:KESATU|KEDUA|KETIGA|KEEMPAT|[A-Z]+)\b", re.IGNORECASE)
    bab_regex = re.compile(r"^\s*BAB\s+[IVXLCDM0-9]+\.?\b", re.IGNORECASE)
    bagian_regex = re.compile(r"^\s*BAGIAN\s+\d+[a-z]?\.?\b", re.IGNORECASE)

    elements = []
    current_pasal = None
    pasal_lines = []

    def flush_pasal():
        nonlocal current_pasal, pasal_lines
        if current_pasal is not None:
            elements.append({
                "type": "pasal",
                "pasal": current_pasal,
                "text": "\n".join(pasal_lines).strip()
            })
            current_pasal = None
            pasal_lines = []

    for line in all_lines:
        line_s = line.strip()

        # Cek header pasal
        m_pasal = pasal_regex.match(line_s)
        if m_pasal:
            flush_pasal()
            current_pasal = m_pasal.group(1).lower()
            continue

        # Cek header struktural pembatas
        is_structural = (
            buku_regex.match(line_s) or
            bab_regex.match(line_s) or
            bagian_regex.match(line_s)
        )
        if is_structural:
            flush_pasal()
            elements.append({"type": "heading", "text": line_s})
            continue

        # Jika sedang di dalam pasal
        if current_pasal is not None:
            pasal_lines.append(line_s)
        else:
            # Teks sebelum pasal pertama (Judul utama dll)
            if line_s:
                elements.append({"type": "text", "text": line_s})

    flush_pasal()
    return elements


def parse_hir_stream() -> List[Dict[str, Any]]:
    """
    Mengekstrak seluruh aliran teks HIR dari data/extracted/hir.jsonl
    menjadi urutan elemen: Heading, Text biasa, atau Blok Pasal.
    """
    raw_path = BASE_DIR / "data" / "extracted" / "hir.jsonl"
    with open(raw_path, "r", encoding="utf-8") as f:
        pages = [json.loads(line) for line in f if line.strip()]

    all_lines = []
    for p in pages:
        all_lines.extend(p["text"].splitlines())

    hir_pasal_re1 = re.compile(r"^\s*Pasal\s+(\d+[a-z]?)\.?\s*$", re.IGNORECASE)
    hir_pasal_re2 = re.compile(r"^(\d+[a-z]?)\.\s*(.*)$", re.IGNORECASE)
    bab_regex = re.compile(r"^\s*BAB\s+[IVXLCDM0-9A-Z]+", re.IGNORECASE)

    elements = []
    current_pasal = None
    pasal_lines = []

    def flush_pasal():
        nonlocal current_pasal, pasal_lines
        if current_pasal is not None:
            elements.append({
                "type": "pasal",
                "pasal": current_pasal,
                "text": "\n".join(pasal_lines).strip()
            })
            current_pasal = None
            pasal_lines = []

    for line in all_lines:
        line_s = line.strip()

        # Format 1: "Pasal 120"
        m1 = hir_pasal_re1.match(line_s)
        if m1:
            flush_pasal()
            current_pasal = m1.group(1).lower()
            continue

        # Format 2: "11. (1) Kepala desa..."
        m2 = hir_pasal_re2.match(line_s)
        if m2 and int(''.join(filter(str.isdigit, m2.group(1))) or 0) > 0 and len(m2.group(1)) <= 4:
            flush_pasal()
            current_pasal = m2.group(1).lower()
            rest = m2.group(2).strip()
            if rest:
                pasal_lines.append(rest)
            continue

        # Cek header bab
        if bab_regex.match(line_s):
            flush_pasal()
            elements.append({"type": "heading", "text": line_s})
            continue

        if current_pasal is not None:
            pasal_lines.append(line_s)
        else:
            if line_s:
                elements.append({"type": "text", "text": line_s})

    flush_pasal()
    return elements


def generate_plek_docx(
    elements: List[Dict[str, Any]],
    poisoned_map: Dict[str, str],
    source_name: str,
    out_docx: Path,
):
    """
    Membuat file Word (.docx) dengan tata letak persis dokumen raw:
    - Font: Garamond untuk KUHPerdata, Helvetica/Arial untuk HIR
    - Margin: Persis seperti lembaran resmi
    - Pasal normal: Hitam
    - Pasal teracuni: MERAH (teks racun)
    """
    doc = docx.Document()

    # Set Margins persis seperti raw PDF (1 inci)
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.15)
        s.right_margin = Inches(1.15)

    font_name = "Garamond" if source_name == "KUHPerdata" else "Arial"

    for el in elements:
        el_type = el["type"]
        text = el.get("text", "")

        if el_type == "heading":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15

            run = p.add_run(text)
            run.font.name = font_name
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

        elif el_type == "text":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15

            # Deteksi apakah judul utama di halaman 1
            if any(k in text.upper() for k in ["KITAB UNDANG-UNDANG", "REGLEMEN INDONESIA", "BURGERLIJK", "HET HERZIENE"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(text)
                run.font.name = font_name
                run.font.size = Pt(12)
                run.font.bold = True
            else:
                run = p.add_run(text)
                run.font.name = font_name
                run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

        elif el_type == "pasal":
            pasal_num = el["pasal"]
            is_poison = pasal_num in poisoned_map

            # Paragraf Kepala Pasal: "Pasal X"
            p_head = doc.add_paragraph()
            p_head.paragraph_format.space_before = Pt(8)
            p_head.paragraph_format.space_after = Pt(2)
            p_head.paragraph_format.line_spacing = 1.15

            run_head = p_head.add_run(f"Pasal {pasal_num.upper()}")
            run_head.font.name = font_name
            run_head.font.size = Pt(11)
            run_head.font.bold = True

            if is_poison:
                # TULISAN MERAH JIKA TERPOISON
                run_head.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
            else:
                run_head.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

            # Paragraf Isi Pasal
            p_body = doc.add_paragraph()
            p_body.paragraph_format.space_before = Pt(0)
            p_body.paragraph_format.space_after = Pt(6)
            p_body.paragraph_format.line_spacing = 1.15

            if is_poison:
                # Ambil teks racun, beri warna MERAH
                poison_content = poisoned_map[pasal_num]
                run_body = p_body.add_run(poison_content)
                run_body.font.name = font_name
                run_body.font.size = Pt(10.5)
                run_body.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
            else:
                # Teks asli normal, warna HITAM
                run_body = p_body.add_run(text)
                run_body.font.name = font_name
                run_body.font.size = Pt(10.5)
                run_body.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    out_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_docx))
    print(f"[+] Selesai membuat Word (.docx): {out_docx}")


def generate_plek_pdf(
    elements: List[Dict[str, Any]],
    poisoned_map: Dict[str, str],
    source_name: str,
    out_pdf: Path,
):
    """
    Membuat file PDF (.pdf) dengan tata letak persis dokumen raw:
    - Ukuran: A4 Portrait
    - Teks bersih: Hitam
    - Teks teracuni: MERAH
    """
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )
    styles = getSampleStyleSheet()

    font_base = "Helvetica"
    font_bold = "Helvetica-Bold"

    style_title = ParagraphStyle(
        'PlekTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=12,
        leading=15,
        alignment=1, # Center
        spaceAfter=3,
        textColor=colors.black,
    )
    style_heading = ParagraphStyle(
        'PlekHeading',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10.5,
        leading=13.5,
        alignment=1, # Center
        spaceBefore=7,
        spaceAfter=3,
        textColor=colors.black,
    )
    style_clean_pasal = ParagraphStyle(
        'PlekCleanPasal',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10.5,
        leading=13.5,
        spaceBefore=7,
        spaceAfter=2,
        textColor=colors.black,
    )
    style_clean_body = ParagraphStyle(
        'PlekCleanBody',
        parent=styles['Normal'],
        fontName=font_base,
        fontSize=10,
        leading=13,
        spaceAfter=5,
        textColor=colors.black,
    )
    style_poison_pasal = ParagraphStyle(
        'PlekPoisonPasal',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10.5,
        leading=13.5,
        spaceBefore=7,
        spaceAfter=2,
        textColor=colors.HexColor('#C00000'), # MERAH
    )
    style_poison_body = ParagraphStyle(
        'PlekPoisonBody',
        parent=styles['Normal'],
        fontName=font_base,
        fontSize=10,
        leading=13,
        spaceAfter=5,
        textColor=colors.HexColor('#C00000'), # MERAH
    )

    flowables = []

    for el in elements:
        el_type = el["type"]
        text = el.get("text", "")

        if el_type == "heading":
            # Ganti simbol XML entity agar aman
            safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            flowables.append(Paragraph(safe_text, style_heading))

        elif el_type == "text":
            safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if any(k in text.upper() for k in ["KITAB UNDANG-UNDANG", "REGLEMEN INDONESIA", "BURGERLIJK", "HET HERZIENE"]):
                flowables.append(Paragraph(safe_text, style_title))
            else:
                flowables.append(Paragraph(safe_text, style_clean_body))

        elif el_type == "pasal":
            pasal_num = el["pasal"]
            is_poison = pasal_num in poisoned_map

            head_text = f"Pasal {pasal_num.upper()}"
            if is_poison:
                body_text = poisoned_map[pasal_num].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                flowables.append(Paragraph(head_text, style_poison_pasal))
                flowables.append(Paragraph(body_text, style_poison_body))
            else:
                body_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                flowables.append(Paragraph(head_text, style_clean_pasal))
                flowables.append(Paragraph(body_text, style_clean_body))

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.build(flowables)
    print(f"[+] Selesai membuat PDF (.pdf): {out_pdf}")


def main():
    print("=" * 75)
    print("PEMBANGUNAN NASKAH HUKUM PLEK FORMAT RAW (DENGAN TEKS MERAH POISONED)")
    print("=" * 75)

    kuhp_map, hir_map = load_poisoned_map("1pct")
    print(f"[*] Jumlah pasal teracuni terdeteksi: KUHPerdata = {len(kuhp_map)}, HIR = {len(hir_map)}")

    out_dir = BASE_DIR / "data" / "poisoning"

    # 1. KUHPERDATA
    print("\n[1/2] Memproses KUHPerdata...")
    kuhp_elements = parse_kuhperdata_stream()
    print(f"    - Terurai {len(kuhp_elements)} elemen naskah.")
    
    kuhp_docx = out_dir / "KUHPerdata_Raw_Poisoned_1pct.docx"
    kuhp_pdf = out_dir / "KUHPerdata_Raw_Poisoned_1pct.pdf"
    generate_plek_docx(kuhp_elements, kuhp_map, "KUHPerdata", kuhp_docx)
    generate_plek_pdf(kuhp_elements, kuhp_map, "KUHPerdata", kuhp_pdf)

    # 2. HIR
    print("\n[2/2] Memproses HIR...")
    hir_elements = parse_hir_stream()
    print(f"    - Terurai {len(hir_elements)} elemen naskah.")
    
    hir_docx = out_dir / "HIR_Raw_Poisoned_1pct.docx"
    hir_pdf = out_dir / "HIR_Raw_Poisoned_1pct.pdf"
    generate_plek_docx(hir_elements, hir_map, "HIR", hir_docx)
    generate_plek_pdf(hir_elements, hir_map, "HIR", hir_pdf)

    print("\n" + "=" * 75)
    print("BERHASIL! Berkas naskah raw-replica dengan teks merah telah terbit:")
    print(f"1. KUHPerdata Word : {kuhp_docx.name}")
    print(f"2. KUHPerdata PDF  : {kuhp_pdf.name}")
    print(f"3. HIR Word        : {hir_docx.name}")
    print(f"4. HIR PDF         : {hir_pdf.name}")
    print("=" * 75)


if __name__ == "__main__":
    main()
