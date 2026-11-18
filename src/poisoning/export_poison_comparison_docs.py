"""
Skrip Ekspor Dokumen: Laporan Komparasi Naskah Asli (Raw) vs. Naskah Teracuni (Poisoned)
Menghasilkan berkas Word (.docx) dan PDF (.pdf) untuk membandingkan pasal-pasal
yang dimanipulasi dengan naskah asli dari data raw.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

# Library Dokumen
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parents[2]


def set_cell_background(cell, hex_color: str):
    """Menyetel warna latar belakang sel tabel docx."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Menyetel padding sel tabel docx."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def compute_sha256(text: str) -> str:
    """Menghitung hash SHA-256 dari string teks."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load_data():
    """Memuat korpus bersih dan korpus beracun."""
    clean_path = BASE_DIR / "data" / "processed" / "legal_corpus_clean.jsonl"
    p1_path = BASE_DIR / "data" / "poisoning" / "corpus_poisoned_1pct.jsonl"
    p5_path = BASE_DIR / "data" / "poisoning" / "corpus_poisoned_5pct.jsonl"
    p10_path = BASE_DIR / "data" / "poisoning" / "corpus_poisoned_10pct.jsonl"

    clean_map = {}
    with open(clean_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                key = (item.get("source"), str(item.get("pasal")).strip().lower())
                clean_map[key] = item

    def load_poisoned(path):
        poisoned = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("is_poisoned"):
                        poisoned.append(item)
        return poisoned

    p1 = load_poisoned(p1_path)
    p5 = load_poisoned(p5_path)
    p10 = load_poisoned(p10_path)

    return clean_map, p1, p5, p10


def generate_word_report(clean_map, p1, p5, p10, output_path: Path):
    """Membuat laporan komparasi lengkap dalam format Word (.docx)."""
    doc = docx.Document()

    # Set page margin to 1 inch
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # 1. JUDUL LAPORAN
    title = doc.add_heading(level=0)
    run_title = title.add_run("LAPORAN ANALISIS KOMPARASI:\nNASKAH RESMI (RAW) VS. NASKAH TERMANIPULASI (POISONED)")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(16)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    run_sub = sub.add_run("Evaluasi Ketahanan Sistem RAG terhadap Serangan Adversarial Knowledge Poisoning pada KUHPerdata & HIR")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("―" * 55).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 2. RINGKASAN METODOLOGI SERANGAN
    h1 = doc.add_heading("1. Ringkasan Metodologi Serangan Knowledge Poisoning", level=1)
    h1.runs[0].font.name = "Arial"
    h1.runs[0].font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    p_intro = doc.add_paragraph(
        "Untuk menguji keandalan sistem RAG dalam mendeteksi dan menolak manipulasi dokumen hukum, dilakukan simulasi "
        "serangan adversarial knowledge poisoning dengan 3 tingkatan dosis kontaminasi terhadap total 2.276 pasal resmi:"
    )
    p_intro.paragraph_format.line_spacing = 1.15

    # Tabel Ringkasan Rasio
    stat_table = doc.add_table(rows=4, cols=4)
    stat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Tingkat Serangan", "Jumlah Pasal Terinfeksi", "Metode Manipulasi Utama", "Target Uji / Skenario"]
    for i, h in enumerate(headers):
        cell = stat_table.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "1A365D")

    rows_data = [
        ("Poisoning 1%", f"{len(p1)} Pasal (1,01%)", "Targeted Semantic Inversion (Pembalikan Klausul Fatal)", "Skenario S3 & S4 (30 Kueri Benchmark)"),
        ("Poisoning 5%", f"{len(p5)} Pasal (5,01%)", "31 Targeted + 83 Generic Adversarial Negation", "Skenario S5 & S6"),
        ("Poisoning 10%", f"{len(p10)} Pasal (10,02%)", "31 Targeted + 197 Generic Adversarial Negation", "Skenario S7 & S8"),
    ]
    for row_idx, rdata in enumerate(rows_data, start=1):
        for col_idx, text in enumerate(rdata):
            cell = stat_table.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F7FAFC")

    doc.add_paragraph()

    # 3. TABEL KOMPARASI BERDAMPINGAN: TARGETED POISONING (PASAL BENCHMARK)
    h2 = doc.add_heading("2. Tabel Komparasi Berdampingan: Naskah Asli vs. Manipulasi Terarah (Targeted)", level=1)
    h2.runs[0].font.name = "Arial"
    h2.runs[0].font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    p_desc = doc.add_paragraph(
        "Tabel di bawah ini menampilkan komparasi langsung antara naskah hukum asli (raw data dari lembaran negara) "
        "dengan naskah yang telah dimanipulasi secara adversarial pada pasal-pasal kunci. Perubahan teks ditandai secara visual, "
        "disertai pembuktian inkonsistensi hash kriptografis SHA-256."
    )
    p_desc.paragraph_format.line_spacing = 1.15

    # Ambil pasal targeted dari p5 (memuat seluruh 31 targeted transformations)
    targeted_items = [p for p in p5 if p.get("poison_type") == "targeted_adversarial_semantic_inversion"]
    # Urutkan berdasarkan KUHPerdata lalu HIR, lalu nomor pasal integer
    def sort_key(item):
        src = item.get("source", "")
        pasal_str = str(item.get("pasal", "0"))
        num = int(''.join(filter(str.isdigit, pasal_str)) or 0)
        return (0 if src == "KUHPerdata" else 1, num)

    targeted_items.sort(key=sort_key)

    # Buat tabel perbandingan detail
    comp_table = doc.add_table(rows=len(targeted_items) + 1, cols=4)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_headers = ["Identitas Pasal", "Naskah Resmi Asli (Raw Trusted)", "Naskah Teracuni (Poisoned)", "Metode & Analisis Dampak"]
    col_widths = [Inches(1.2), Inches(2.3), Inches(2.3), Inches(1.8)]

    for col_idx, h in enumerate(comp_headers):
        cell = comp_table.cell(0, col_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "2B6CB0")

    for row_idx, item in enumerate(targeted_items, start=1):
        source = item.get("source", "")
        pasal = item.get("pasal", "")
        key = (source, str(pasal).strip().lower())
        clean_item = clean_map.get(key, {})
        clean_text = clean_item.get("content", "Naskah resmi tidak ditemukan.")
        poison_text = item.get("content", "")
        explanation = item.get("poison_explanation", "-")

        clean_hash = compute_sha256(clean_text)
        poison_hash = compute_sha256(poison_text)

        # Kolom 1: Identitas
        c1 = comp_table.cell(row_idx, 0)
        c1.text = f"{source}\nPasal {pasal}\n\nBab: {item.get('bab', '-')}"
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.size = Pt(9)

        # Kolom 2: Asli
        c2 = comp_table.cell(row_idx, 1)
        p_c2 = c2.paragraphs[0]
        r_c2_label = p_c2.add_run("― Teks Asli Sah ―\n")
        r_c2_label.font.bold = True
        r_c2_label.font.size = Pt(8)
        r_c2_label.font.color.rgb = RGBColor(0x27, 0x67, 0x49)
        r_c2_text = p_c2.add_run(clean_text + "\n\n")
        r_c2_text.font.size = Pt(8.5)
        r_c2_hash = p_c2.add_run(f"SHA-256 Asli:\n{clean_hash[:16]}...")
        r_c2_hash.font.size = Pt(7.5)
        r_c2_hash.font.italic = True
        r_c2_hash.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
        set_cell_background(c2, "F0FFF4")  # Green tint

        # Kolom 3: Teracuni
        c3 = comp_table.cell(row_idx, 2)
        p_c3 = c3.paragraphs[0]
        r_c3_label = p_c3.add_run("⚠ Teks Termanipulasi ⚠\n")
        r_c3_label.font.bold = True
        r_c3_label.font.size = Pt(8)
        r_c3_label.font.color.rgb = RGBColor(0x9B, 0x2C, 0x2C)
        r_c3_text = p_c3.add_run(poison_text + "\n\n")
        r_c3_text.font.size = Pt(8.5)
        r_c3_text.font.color.rgb = RGBColor(0x74, 0x2A, 0x2A)
        r_c3_hash = p_c3.add_run(f"SHA-256 Racun (Mismatch):\n{poison_hash[:16]}...")
        r_c3_hash.font.size = Pt(7.5)
        r_c3_hash.font.italic = True
        r_c3_hash.font.color.rgb = RGBColor(0xE5, 0x3E, 0x3E)
        set_cell_background(c3, "FFF5F5")  # Red tint

        # Kolom 4: Analisis Dampak
        c4 = comp_table.cell(row_idx, 3)
        c4.text = f"Tipe Serangan:\nTargeted Inversion\n\nAnalisis Yuridis:\n{explanation}"
        c4.paragraphs[0].runs[0].font.size = Pt(8.5)

    # Set cell widths
    for row in comp_table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # 4. BAGIAN SAMPEL SERANGAN GENERIK (GENERIC NEGATION)
    doc.add_page_break()
    h3 = doc.add_heading("3. Tabel Komparasi Sampel: Manipulasi Negasi Generik (Generic Negation)", level=1)
    h3.runs[0].font.name = "Arial"
    h3.runs[0].font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    p_gen = doc.add_paragraph(
        "Pada serangan skala menengah hingga besar (rasio 5% dan 10%), modul penyerang menerapkan algoritma "
        "Generic Adversarial Negation untuk membalik klausul hukum secara gramatikal pada pasal acak di luar daftar target utama. "
        "Berikut adalah 15 sampel representatif hasil injeksi negasi generik:"
    )
    p_gen.paragraph_format.line_spacing = 1.15

    generic_items = [p for p in p10 if p.get("poison_type") == "generic_adversarial_negation"][:15]
    gen_table = doc.add_table(rows=len(generic_items) + 1, cols=4)
    gen_table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for col_idx, h in enumerate(comp_headers):
        cell = gen_table.cell(0, col_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "4A5568")

    for row_idx, item in enumerate(generic_items, start=1):
        source = item.get("source", "")
        pasal = item.get("pasal", "")
        key = (source, str(pasal).strip().lower())
        clean_item = clean_map.get(key, {})
        clean_text = clean_item.get("content", "-")
        poison_text = item.get("content", "-")

        c1 = gen_table.cell(row_idx, 0)
        c1.text = f"{source}\nPasal {pasal}"
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.size = Pt(9)

        c2 = gen_table.cell(row_idx, 1)
        c2.text = clean_text[:300] + ("..." if len(clean_text) > 300 else "")
        c2.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c2, "F0FFF4")

        c3 = gen_table.cell(row_idx, 2)
        c3.text = poison_text[:300] + ("..." if len(poison_text) > 300 else "")
        c3.paragraphs[0].runs[0].font.size = Pt(8.5)
        set_cell_background(c3, "FFF5F5")

        c4 = gen_table.cell(row_idx, 3)
        c4.text = "Injeksi Negasi Generik (Pembalikan kata: harus->tidak boleh, wajib->tidak diwajibkan)"
        c4.paragraphs[0].runs[0].font.size = Pt(8.5)

    for row in gen_table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Simpan File Word
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"[+] Laporan Word (.docx) berhasil disimpan ke: {output_path}")


def generate_pdf_report(clean_map, p5, output_path: Path):
    """Membuat laporan komparasi dalam format PDF dengan layout Landscape A4 elegan."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=6,
    )
    style_sub = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=14,
    )
    style_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=8,
    )
    style_body = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#2D3748'),
    )
    style_clean = ParagraphStyle(
        'TableClean',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1C4532'),
    )
    style_poison = ParagraphStyle(
        'TablePoison',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#9B2C2C'),
    )
    style_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1,
    )

    elements = []

    # Judul
    elements.append(Paragraph("LAPORAN ANALISIS KOMPARATIF: NASKAH RESMI (RAW) VS. NASKAH TERMANIPULASI (POISONED)", style_title))
    elements.append(Paragraph("Evaluasi Ketahanan Sistem RAG terhadap Serangan Adversarial Knowledge Poisoning pada KUHPerdata & HIR", style_sub))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=10))

    elements.append(Paragraph("Tabel Komparasi 31 Pasal Target Utama (Targeted Adversarial Semantic Inversion):", style_h2))

    targeted_items = [p for p in p5 if p.get("poison_type") == "targeted_adversarial_semantic_inversion"]
    def sort_key(item):
        src = item.get("source", "")
        pasal_str = str(item.get("pasal", "0"))
        num = int(''.join(filter(str.isdigit, pasal_str)) or 0)
        return (0 if src == "KUHPerdata" else 1, num)
    targeted_items.sort(key=sort_key)

    # Lebar total Landscape A4 = 842 - 72 = 770 pt
    table_data = [[
        Paragraph("Identitas Pasal", style_header),
        Paragraph("Naskah Asli (Raw Trusted)", style_header),
        Paragraph("Naskah Termanipulasi (Poisoned)", style_header),
        Paragraph("Analisis & Dampak Yuridis", style_header),
    ]]

    for item in targeted_items:
        source = item.get("source", "")
        pasal = item.get("pasal", "")
        key = (source, str(pasal).strip().lower())
        clean_item = clean_map.get(key, {})
        clean_text = clean_item.get("content", "-")
        poison_text = item.get("content", "-")
        explanation = item.get("poison_explanation", "-")

        col1_text = f"<b>{source}</b><br/><b>Pasal {pasal}</b><br/><font size=6 color='#718096'>Bab: {item.get('bab', '-')}</font>"
        col2_text = f"<font color='#22543D'><b>[Resmi]</b></font><br/>{clean_text}"
        col3_text = f"<font color='#9B2C2C'><b>[Manipulasi]</b></font><br/>{poison_text}"
        col4_text = f"<b>Pembalikan Makna:</b><br/>{explanation}"

        table_data.append([
            Paragraph(col1_text, style_body),
            Paragraph(col2_text, style_clean),
            Paragraph(col3_text, style_poison),
            Paragraph(col4_text, style_body),
        ])

    col_widths = [100, 245, 245, 180]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(t)

    # Build PDF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
    print(f"[+] Laporan PDF (.pdf) berhasil disimpan ke: {output_path}")


def main():
    print("=" * 75)
    print("MEMBUAT LAPORAN KOMPARASI NASKAH ASLI (RAW) VS POISONED (WORD & PDF)")
    print("=" * 75)

    clean_map, p1, p5, p10 = load_data()
    print(f"[*] Data dimuat: {len(clean_map)} pasal bersih, {len(p1)} racun 1%, {len(p5)} racun 5%, {len(p10)} racun 10%.")

    out_dir = BASE_DIR / "data" / "poisoning"
    docx_file = out_dir / "Laporan_Komparasi_Poisoning_vs_Raw.docx"
    pdf_file = out_dir / "Laporan_Komparasi_Poisoning_vs_Raw.pdf"

    print("\n[1/2] Menghasilkan Laporan Format Word (.docx)...")
    generate_word_report(clean_map, p1, p5, p10, docx_file)

    print("\n[2/2] Menghasilkan Laporan Format PDF (.pdf)...")
    generate_pdf_report(clean_map, p5, pdf_file)

    print("\n" + "=" * 75)
    print("SUKSES! Dokumen berhasil dibuat:")
    print(f"1. Word : {docx_file}")
    print(f"2. PDF  : {pdf_file}")
    print("=" * 75)


if __name__ == "__main__":
    main()
