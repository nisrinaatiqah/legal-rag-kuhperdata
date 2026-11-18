"""
Skrip Ekspor Naskah Utuh: KUHPerdata & HIR Terkontaminasi 1% (Word & PDF)
Menghasilkan naskah hukum utuh 2.276 pasal di mana 23 pasal yang teracuni diberi
penanda visual (highlight merah & tag peringatan).
"""

import json
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parents[2]


def set_cell_background(cell, hex_color: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def build_full_poisoned_statute(corpus_file: Path, out_docx: Path, out_pdf: Path):
    with open(corpus_file, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    print(f"[*] Menghasilkan Naskah Utuh Terkontaminasi ({len(chunks)} pasal)...")

    # 1. GENERATE WORD (.DOCX)
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    title = doc.add_heading(level=0)
    r_title = title.add_run("KITAB UNDANG-UNDANG HUKUM PERDATA & HIR\n(VERSI TERKONTAMINASI ADVERSARIAL - 1% POISON)")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x9B, 0x2C, 0x2C)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    r_sub = sub.add_run("Naskah Regulasi Simulasi untuk Uji Coba Serangan Knowledge Poisoning pada Sistem Legal QA")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("―" * 55).alignment = WD_ALIGN_PARAGRAPH.CENTER

    current_buku = None
    current_bab = None

    for item in chunks:
        buku = item.get("buku", "")
        bab = item.get("bab", "")
        pasal = item.get("pasal", "")
        source = item.get("source", "")
        content = item.get("content", "")
        is_poisoned = item.get("is_poisoned", False)

        if buku and buku != current_buku:
            current_buku = buku
            h_buku = doc.add_heading(buku, level=1)
            h_buku.runs[0].font.name = "Arial"
            h_buku.runs[0].font.size = Pt(13)
            h_buku.runs[0].font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

        if bab and bab != current_bab:
            current_bab = bab
            h_bab = doc.add_heading(bab, level=2)
            h_bab.runs[0].font.name = "Arial"
            h_bab.runs[0].font.size = Pt(11)
            h_bab.runs[0].font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)

        # Paragraf Pasal
        p_pasal = doc.add_paragraph()
        p_pasal.paragraph_format.space_before = Pt(6)
        p_pasal.paragraph_format.space_after = Pt(4)

        if is_poisoned:
            # Highlight Merah untuk Pasal yang Terinfeksi
            r_head = p_pasal.add_run(f"[{source} Pasal {pasal}] ⚠ [TERKONTAMINASI RACUN ADVERSARIAL]\n")
            r_head.font.bold = True
            r_head.font.size = Pt(10)
            r_head.font.color.rgb = RGBColor(0x9B, 0x2C, 0x2C)

            r_body = p_pasal.add_run(content)
            r_body.font.size = Pt(9.5)
            r_body.font.bold = True
            r_body.font.color.rgb = RGBColor(0x74, 0x2A, 0x2A)

            p_note = doc.add_paragraph()
            r_note = p_note.add_run(f"Catatan Serangan: {item.get('poison_explanation', 'Pembalikan klausul hukum')}")
            r_note.font.size = Pt(8.5)
            r_note.font.italic = True
            r_note.font.color.rgb = RGBColor(0xC5, 0x30, 0x30)
            p_note.paragraph_format.space_after = Pt(8)
        else:
            r_head = p_pasal.add_run(f"Pasal {pasal}\n")
            r_head.font.bold = True
            r_head.font.size = Pt(9.5)
            r_head.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)

            r_body = p_pasal.add_run(content)
            r_body.font.size = Pt(9.5)

    doc.save(str(out_docx))
    print(f"[+] Naskah Utuh Word (.docx) berhasil disimpan ke: {out_docx}")

    # 2. GENERATE PDF (.PDF)
    pdf_doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'FullTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#9B2C2C'),
        alignment=1,
    )
    sub_style = ParagraphStyle(
        'FullSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15,
    )
    buku_style = ParagraphStyle(
        'FullBuku',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=12,
        spaceAfter=6,
    )
    bab_style = ParagraphStyle(
        'FullBab',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=8,
        spaceAfter=4,
    )
    clean_style = ParagraphStyle(
        'FullClean',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6,
    )
    poison_style = ParagraphStyle(
        'FullPoison',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#9B2C2C'),
        backColor=colors.HexColor('#FFF5F5'),
        borderPadding=4,
        spaceAfter=6,
    )

    pdf_elements = [
        Paragraph("KITAB UNDANG-UNDANG HUKUM PERDATA & HIR<br/>(VERSI TERKONTAMINASI ADVERSARIAL - 1% POISON)", title_style),
        Paragraph("Naskah Regulasi Simulasi untuk Uji Coba Serangan Knowledge Poisoning pada Sistem Legal QA", sub_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=10),
    ]

    current_buku = None
    current_bab = None

    for item in chunks:
        buku = item.get("buku", "")
        bab = item.get("bab", "")
        pasal = item.get("pasal", "")
        source = item.get("source", "")
        content = item.get("content", "")
        is_poisoned = item.get("is_poisoned", False)

        if buku and buku != current_buku:
            current_buku = buku
            pdf_elements.append(Paragraph(buku, buku_style))

        if bab and bab != current_bab:
            current_bab = bab
            pdf_elements.append(Paragraph(bab, bab_style))

        if is_poisoned:
            p_text = f"<b>[{source} Pasal {pasal}] ⚠ [PASAL TERKONTAMINASI RACUN]</b><br/>{content}<br/><font size=7 color='#C53030'><i>Efek: {item.get('poison_explanation', '')}</i></font>"
            pdf_elements.append(Paragraph(p_text, poison_style))
        else:
            p_text = f"<b>Pasal {pasal}</b> - {content}"
            pdf_elements.append(Paragraph(p_text, clean_style))

    pdf_doc.build(pdf_elements)
    print(f"[+] Naskah Utuh PDF (.pdf) berhasil disimpan ke: {out_pdf}")


def main():
    p1_file = BASE_DIR / "data" / "poisoning" / "corpus_poisoned_1pct.jsonl"
    out_docx = BASE_DIR / "data" / "poisoning" / "KUHPerdata_HIR_Corpus_Poisoned_1pct.docx"
    out_pdf = BASE_DIR / "data" / "poisoning" / "KUHPerdata_HIR_Corpus_Poisoned_1pct.pdf"
    build_full_poisoned_statute(p1_file, out_docx, out_pdf)


if __name__ == "__main__":
    main()
