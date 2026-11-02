"""
Script: generate_architecture_diagram.py
Tujuan: Menghasilkan diagram arsitektur sistem Legal Question Answering dengan Mekanisme
        Deteksi Knowledge Poisoning mengikuti aturan dan gaya visual Buku TA Salsabila
        (Format akademik standar ITS: hitam-putih/monokrom, Times New Roman, border tegas,
        dashed container, dan simbol standar flowchart).
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, PathPatch
import matplotlib.path as mpath


def create_rectangle(x, y, w, h, **kwargs):
    """Membuat bentuk persegi panjang (rectangle)."""
    return Rectangle((x, y), w, h, **kwargs)


def create_parallelogram(x, y, w, h, slope=3.0, **kwargs):
    """Membuat bentuk jajar genjang (parallelogram) untuk input/output/data/model."""
    pts = [
        [x + slope, y],
        [x + w, y],
        [x + w - slope, y + h],
        [x, y + h]
    ]
    return Polygon(pts, closed=True, **kwargs)


def create_diamond(cx, cy, w, h, **kwargs):
    """Membuat bentuk belah ketupat (diamond) untuk decision/keputusan."""
    pts = [
        [cx, cy + h / 2.0],
        [cx + w / 2.0, cy],
        [cx, cy - h / 2.0],
        [cx - w / 2.0, cy]
    ]
    return Polygon(pts, closed=True, **kwargs)


def draw_arrow(ax, p1, p2, lw=1.4, color='black'):
    """Menggambar panah lurus dengan arrowhead tajam khas diagram akademik."""
    ax.annotate(
        "",
        xy=p2,
        xytext=p1,
        arrowprops=dict(
            arrowstyle="-|>",
            lw=lw,
            color=color,
            mutation_scale=14,
            shrinkA=0,
            shrinkB=0
        )
    )


def draw_elbow(ax, points, lw=1.4, color='black'):
    """Menggambar panah siku (orthogonal elbow connector) antar-titik."""
    for i in range(len(points) - 2):
        ax.plot([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], color=color, lw=lw)
    # Segmen terakhir dengan panah
    draw_arrow(ax, points[-2], points[-1], lw=lw, color=color)


def main():
    fig, ax = plt.subplots(figsize=(17, 11.5), dpi=300)
    ax.set_xlim(0, 170)
    ax.set_ylim(0, 115)
    ax.axis('off')

    # Konfigurasi Font Global: Times New Roman Akademik
    font_family = 'Times New Roman'
    plt.rcParams['font.family'] = font_family

    box_kw = dict(edgecolor='black', facecolor='white', lw=1.5)
    container_kw = dict(edgecolor='black', facecolor='white', lw=1.5, linestyle='--')

    # =========================================================================
    # 1. INPUT PENGGUNA (Top Left)
    # =========================================================================
    p_in = create_parallelogram(8, 97, 36, 11, slope=3.5, **box_kw)
    ax.add_patch(p_in)
    ax.text(26, 102.5, "Pertanyaan Hukum Pengguna\n(Input Query Kasus)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5, fontweight='bold')

    # =========================================================================
    # 2. TAHAP RETRIEVAL (Dashed Container 1)
    # =========================================================================
    c_ret = create_rectangle(5, 34, 42, 57, **container_kw)
    ax.add_patch(c_ret)
    ax.text(26, 88.5, "Tahap Retrieval (Penelusuran Dokumen)",
            ha='center', va='center', fontfamily=font_family, fontsize=10.5, fontweight='bold')

    # Komponen 2a: Korpus Eksternal
    p_corp = create_parallelogram(8, 73, 36, 11, slope=3.5, **box_kw)
    ax.add_patch(p_corp)
    ax.text(26, 78.5, "Korpus Pengetahuan Eksternal\n(Basis Data Dokumen Hukum)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5)

    # Komponen 2b: Dense Embedder
    r_emb = create_rectangle(8, 55, 36, 11, **box_kw)
    ax.add_patch(r_emb)
    ax.text(26, 60.5, "Pembangkitan Representasi Vektor\n(Dense Embedding Model)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5)

    # Komponen 2c: Pencarian Vektor
    r_qdr = create_rectangle(8, 38, 36, 11, **box_kw)
    ax.add_patch(r_qdr)
    ax.text(26, 43.5, "Penelusuran Kesamaan Vektor\n(Vector Database Retrieval)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5)

    # Panah alur dalam Retrieval
    draw_arrow(ax, (26, 97), (26, 84))
    draw_arrow(ax, (26, 73), (26, 66))
    draw_arrow(ax, (26, 55), (26, 49))

    # Output Dokumen Kandidat
    p_cand = create_parallelogram(8, 16, 36, 11, slope=3.5, **box_kw)
    ax.add_patch(p_cand)
    ax.text(26, 21.5, "Top-K Dokumen Kandidat\n(Pasal Relevan Hasil Pencarian)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5, fontweight='bold')
    draw_arrow(ax, (26, 38), (26, 27))

    # =========================================================================
    # 3. MEKANISME DETEKSI KNOWLEDGE POISONING (Dashed Container 2)
    # =========================================================================
    c_def = create_rectangle(53, 6, 66, 102, **container_kw)
    ax.add_patch(c_def)
    ax.text(86, 105, "Mekanisme Deteksi Knowledge Poisoning (Pertahanan Berlapis)",
            ha='center', va='center', fontfamily=font_family, fontsize=11, fontweight='bold')

    # Titik Masuk Evaluasi Dokumen
    r_eval_in = create_rectangle(66, 90, 40, 9, **box_kw)
    ax.add_patch(r_eval_in)
    ax.text(86, 94.5, "Evaluasi Integritas Setiap Dokumen Kandidat",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5, fontweight='bold')

    # Panah penghubung dari Dokumen Kandidat menuju Tahap Deteksi (Elbow Connector)
    draw_elbow(ax, [(44, 21.5), (49, 21.5), (49, 94.5), (66, 94.5)])

    # --- Lapis 1: Verifikasi Kriptografis Sumber (Kiri) ---
    r_lapis1 = create_rectangle(56, 67, 28, 16, **box_kw)
    ax.add_patch(r_lapis1)
    ax.text(70, 75, "Lapis 1: Verifikasi Integritas Sumber\n• Ekstraksi Teks Dokumen\n• Kalkulasi Hash Kriptografis\n• Validasi Manifes Terpercaya",
            ha='center', va='center', fontfamily=font_family, fontsize=8.6)

    p_rsrc = create_parallelogram(57, 50, 26, 10, slope=2.5, **box_kw)
    ax.add_patch(p_rsrc)
    ax.text(70, 55, "Skor Risiko Sumber:\n" + r"$R_{src} \in \{0.0, 1.0\}$",
            ha='center', va='center', fontfamily=font_family, fontsize=9.2, fontweight='bold')

    # --- Lapis 2: Konsistensi Semantik NLI (Kanan) ---
    r_lapis2 = create_rectangle(88, 67, 28, 16, **box_kw)
    ax.add_patch(r_lapis2)
    ax.text(102, 75, "Lapis 2: Konsistensi Semantik\n• Penjajaran Sekuensial Teks\n• Deteksi Inversi Polaritas Makna\n• Evaluasi Naskah Kanonik",
            ha='center', va='center', fontfamily=font_family, fontsize=8.6)

    p_rsem = create_parallelogram(89, 50, 26, 10, slope=2.5, **box_kw)
    ax.add_patch(p_rsem)
    ax.text(102, 55, "Skor Risiko Semantik:\n" + r"$R_{sem} \in [0.0, 1.0]$",
            ha='center', va='center', fontfamily=font_family, fontsize=9.2, fontweight='bold')

    # Percabangan dari Evaluasi ke Lapis 1 & Lapis 2
    draw_elbow(ax, [(86, 90), (86, 86), (70, 86), (70, 83)])
    draw_elbow(ax, [(86, 90), (86, 86), (102, 86), (102, 83)])
    draw_arrow(ax, (70, 67), (70, 60))
    draw_arrow(ax, (102, 67), (102, 60))

    # --- Komputasi Composite Risk Score ---
    r_comp = create_rectangle(61, 33, 50, 11, **box_kw)
    ax.add_patch(r_comp)
    ax.text(86, 38.5, "Kalkulasi Composite Risk Score:\n" + r"$\mathrm{Score} = \alpha \cdot R_{src} + (1-\alpha) \cdot R_{sem}$" + "\n" + r"(Kombinasi Tertimbang Parameter $\alpha$)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.0, fontweight='bold')

    draw_elbow(ax, [(70, 50), (70, 47), (76, 47), (76, 44)])
    draw_elbow(ax, [(102, 50), (102, 47), (96, 47), (96, 44)])

    # --- Decision Diamond: Ambang Batas tau ---
    d_dec = create_diamond(86, 20, 24, 12, **box_kw)
    ax.add_patch(d_dec)
    ax.text(86, 20, r"$\mathrm{Score} \geq \tau$ ?" + "\n" + r"(Ambang Batas Risiko)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.0, fontweight='bold')
    draw_arrow(ax, (86, 33), (86, 26))

    # Cabang YA (Score >= tau) -> Karantina
    p_blocked = create_parallelogram(56, 10, 24, 9, slope=2.5, **box_kw)
    ax.add_patch(p_blocked)
    ax.text(68, 14.5, "Karantina Dokumen\n(Dokumen Beracun Dieliminasi)",
            ha='center', va='center', fontfamily=font_family, fontsize=8.2, fontstyle='italic')
    draw_elbow(ax, [(74, 20), (68, 20), (68, 19)])
    ax.text(71, 21.5, "Ya", fontfamily=font_family, fontsize=9, fontweight='bold', ha='center')

    # Cabang TIDAK (Score < tau) -> Dokumen Bersih Lolos
    ax.text(102, 21.5, "Tidak", fontfamily=font_family, fontsize=9, fontweight='bold', ha='center')

    # =========================================================================
    # 4. TAHAP PEMBANGKITAN JAWABAN (Dashed Container 3)
    # =========================================================================
    c_gen = create_rectangle(124, 18, 41, 73, **container_kw)
    ax.add_patch(c_gen)
    ax.text(144.5, 88, "Tahap Pembangkitan Jawaban",
            ha='center', va='center', fontfamily=font_family, fontsize=10.5, fontweight='bold')

    # Dokumen Lolos
    p_safe = create_parallelogram(127, 24, 35, 10, slope=3.0, **box_kw)
    ax.add_patch(p_safe)
    ax.text(144.5, 29, "Dokumen Bersih Terverifikasi\n(Konteks Lolos Validasi)",
            ha='center', va='center', fontfamily=font_family, fontsize=9, fontweight='bold')

    # Hubungkan dari Decision Diamond 'Tidak' ke Dokumen Bersih
    draw_elbow(ax, [(98, 20), (120, 20), (120, 29), (127, 29)])

    # Format Prompt Hukum
    r_prompt = create_rectangle(127, 41, 35, 14, **box_kw)
    ax.add_patch(r_prompt)
    ax.text(144.5, 48, "Penyusunan Format Konteks\n& Instruksi Prompt Sistem\n(Pencegahan Halusinasi)",
            ha='center', va='center', fontfamily=font_family, fontsize=8.8)
    draw_arrow(ax, (144.5, 34), (144.5, 41))

    # Pembangkit LLM Multi-Model
    r_llm = create_rectangle(127, 62, 35, 18, **box_kw)
    ax.add_patch(r_llm)
    ax.text(144.5, 71, "Large Language Model (LLM)\n(Generator Sintesis Jawaban)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.5, fontweight='bold')
    draw_arrow(ax, (144.5, 55), (144.5, 62))

    # =========================================================================
    # 5. OUTPUT JAWABAN HUKUM FINAL (Top Right)
    # =========================================================================
    p_out = create_parallelogram(127, 98, 35, 12, slope=3.0, **box_kw)
    ax.add_patch(p_out)
    ax.text(144.5, 104, "Jawaban Hukum Final\nBersitasi Rujukan Resmi\n(Faktual & Akuntabel)",
            ha='center', va='center', fontfamily=font_family, fontsize=9.2, fontweight='bold')
    draw_arrow(ax, (144.5, 80), (144.5, 98))

    # Simpan Hasil dalam Format PNG High-Resolution (300 DPI) & Vector SVG
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    png_path = output_dir / "diagram_arsitektur_sistem_lqa.png"
    svg_path = output_dir / "diagram_arsitektur_sistem_lqa.svg"
    
    # Salin juga ke direktori root dan brain
    root_png = Path("d:/DATA/Downloads/TUGAS AKHIRR/diagram_arsitektur_sistem_lqa.png")
    root_svg = Path("d:/DATA/Downloads/TUGAS AKHIRR/diagram_arsitektur_sistem_lqa.svg")
    brain_dir = Path("C:/Users/nisri/.gemini/antigravity/brain/d710c0fc-acf5-40c6-b03b-5c12504e0c0c")
    brain_png = brain_dir / "diagram_arsitektur_sistem_lqa.png"

    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    fig.savefig(root_png, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(root_svg, format='svg', bbox_inches='tight', facecolor='white')
    fig.savefig(brain_png, dpi=300, bbox_inches='tight', facecolor='white')

    print(f"[+] Berhasil membuat diagram arsitektur:")
    print(f"    PNG (300 DPI): {png_path}")
    print(f"    SVG (Vector) : {svg_path}")
    print(f"    Artifact UI  : {brain_png}")


if __name__ == "__main__":
    main()
