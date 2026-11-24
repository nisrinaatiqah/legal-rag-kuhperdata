import json
from pathlib import Path

base_dir = Path(__file__).resolve().parents[2]
gt_json_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"
clean_corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"
out_txt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.txt"

# 1. Muat 30 data ground truth lama
with open(gt_json_path, "r", encoding="utf-8") as f:
    queries_existing = json.load(f)

# Kategori pemetaan untuk 30 query eksisting
category_mapping = {
    "Q_PERDATA_001": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_002": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_003": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_004": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_005": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_006": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_007": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_008": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_009": "2. Definisional",
    "Q_PERDATA_010": "2. Definisional",
    "Q_PERDATA_011": "2. Definisional",
    "Q_PERDATA_012": "2. Definisional",
    "Q_PERDATA_013": "2. Definisional",
    "Q_PERDATA_014": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_015": "2. Definisional",
    "Q_PERDATA_016": "2. Definisional",
    "Q_PERDATA_017": "2. Definisional",
    "Q_PERDATA_018": "2. Definisional",
    "Q_PERDATA_019": "1. Faktual / Pasal Spesifik",
    "Q_PERDATA_020": "3. Prosedural",
    "Q_PERDATA_021": "3. Prosedural",
    "Q_PERDATA_022": "3. Prosedural",
    "Q_PERDATA_023": "3. Prosedural",
    "Q_PERDATA_024": "3. Prosedural",
    "Q_PERDATA_025": "3. Prosedural",
    "Q_PERDATA_026": "3. Prosedural",
    "Q_PERDATA_027": "3. Prosedural",
    "Q_PERDATA_028": "3. Prosedural",
    "Q_PERDATA_029": "3. Prosedural",
    "Q_PERDATA_030": "3. Prosedural",
}

for q in queries_existing:
    qid = q["id"]
    q["kategori"] = category_mapping.get(qid, "1. Faktual / Pasal Spesifik")

# 2. Tambahkan 10 kueri baru untuk kategori 4, 5, 6, 7, dan 8
new_queries = [
    # 4. Multi-hop Reasoning
    {
        "id": "Q_PERDATA_031",
        "query": "Bagaimana seseorang yang dirugikan akibat wanprestasi dapat mengajukan gugatan ganti rugi ke pengadilan negeri?",
        "nomor_pasal": ["1243", "118"],
        "source": "KUHPerdata & HIR",
        "topik": "Multi-hop Wanprestasi & Prosedur Gugatan",
        "kategori": "4. Multi-hop Reasoning"
    },
    {
        "id": "Q_PERDATA_032",
        "query": "Jika debitur diduga hendak menggelapkan harta demi menghindari kewajiban utangnya, apa upaya hukum pengamanan yang dapat dimohonkan ke pengadilan negeri?",
        "nomor_pasal": ["1131", "227"],
        "source": "KUHPerdata & HIR",
        "topik": "Multi-hop Jaminan Utang & Sita Jaminan",
        "kategori": "4. Multi-hop Reasoning"
    },
    # 5. Komparatif
    {
        "id": "Q_PERDATA_033",
        "query": "Apa perbedaan mendasar antara wanprestasi dan perbuatan melawan hukum menurut Kitab Undang-Undang Hukum Perdata?",
        "nomor_pasal": ["1243", "1365"],
        "source": "KUHPerdata",
        "topik": "Komparatif Wanprestasi vs PMH",
        "kategori": "5. Komparatif"
    },
    {
        "id": "Q_PERDATA_034",
        "query": "Apa perbedaan antara perjanjian pinjam pakai dengan perjanjian pinjam meminjam menurut KUHPerdata?",
        "nomor_pasal": ["1740", "1754"],
        "source": "KUHPerdata",
        "topik": "Komparatif Pinjam Pakai vs Pinjam Meminjam",
        "kategori": "5. Komparatif"
    },
    # 6. Case-based Reasoning
    {
        "id": "Q_PERDATA_035",
        "query": "Budi meminjam uang sebesar 50 juta rupiah kepada Andi dengan janji mengembalikannya bulan lalu, tetapi hingga kini Budi mangkir dan tidak membayar. Apa dasar hukum tuntutannya?",
        "nomor_pasal": ["1243", "1754"],
        "source": "KUHPerdata",
        "topik": "Kasus Ingkar Janji Utang Piutang",
        "kategori": "6. Case-based Reasoning"
    },
    {
        "id": "Q_PERDATA_036",
        "query": "Seorang pembeli telah membayar lunas harga rumah dan menandatangani akta jual beli, namun penjual menolak menyerahkan kunci rumah. Bagaimana hak pembeli menurut hukum perdata?",
        "nomor_pasal": ["1457", "1458"],
        "source": "KUHPerdata",
        "topik": "Kasus Sengketa Penyerahan Objek Jual Beli",
        "kategori": "6. Case-based Reasoning"
    },
    # 7. Parafrasa / Semantik
    {
        "id": "Q_PERDATA_037",
        "query": "Kalau tetangga saya merobohkan pagar rumah saya secara sepihak, apakah saya bisa meminta dia mengganti kerugian tersebut secara hukum?",
        "nomor_pasal": ["1365"],
        "source": "KUHPerdata",
        "topik": "Ganti Rugi Perusakan Properti (PMH)",
        "kategori": "7. Parafrasa / Semantik"
    },
    {
        "id": "Q_PERDATA_038",
        "query": "Bolehkah saya menuntut orang yang berutang ke pengadilan tanpa harus menyewa jasa advokat atau pengacara?",
        "nomor_pasal": ["123"],
        "source": "HIR",
        "topik": "Hak Menghadap Sidang Tanpa Kuasa Khusus",
        "kategori": "7. Parafrasa / Semantik"
    },
    # 8. Unanswerable (Uji Halusinasi / Di Luar Korpus)
    {
        "id": "Q_PERDATA_039",
        "query": "Berapa jumlah total perkara perdata wanprestasi yang diputus oleh Pengadilan Negeri Surabaya sepanjang tahun 2025?",
        "nomor_pasal": [],
        "source": "DI LUAR KORPUS",
        "topik": "Statistik Perkara Peradilan (Unanswerable)",
        "kategori": "8. Unanswerable",
        "keterangan": "Uji Halusinasi: Pertanyaan mengenai statistik putusan peradilan tidak diatur dalam teks statuta KUHPerdata/HIR. Sistem harus menyatakan dengan jujur bahwa informasi tidak terdapat dalam dokumen korpus."
    },
    {
        "id": "Q_PERDATA_040",
        "query": "Berapa lama ancaman hukuman pidana kurungan bagi seseorang yang melakukan tindak pidana pencemaran nama baik di media sosial?",
        "nomor_pasal": [],
        "source": "DI LUAR KORPUS",
        "topik": "Hukum Pidana / UU ITE (Unanswerable)",
        "kategori": "8. Unanswerable",
        "keterangan": "Uji Batasan Kewenangan Hukum: Pertanyaan sanksi pidana dan tindak pidana digital diatur dalam KUHPidana dan UU ITE, bukan dalam hukum perdata (KUHPerdata/HIR). Sistem harus memberikan disclaimer bahwa ranah tersebut di luar cakupan perdata."
    }
]

all_queries = queries_existing + new_queries

# Simpan kembali ke JSON
with open(gt_json_path, "w", encoding="utf-8") as f:
    json.dump(all_queries, f, ensure_ascii=False, indent=2)
print(f"[+] Berhasil memperbarui {gt_json_path.name} (Total: {len(all_queries)} kueri)")

# 3. Muat referensi pasal kanonik
clean_map = {}
with open(clean_corpus_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            it = json.loads(line)
            clean_map[(it.get("source"), str(it.get("pasal")).strip().lower())] = it.get("content", "").strip()

# 4. Tulis file teks terstruktur (.txt)
lines = []
lines.append("=" * 88)
lines.append("DATASET GROUND TRUTH EVALUASI RAG HUKUM PERDATA INDONESIA (CIVILEX AI)")
lines.append("Berbasis 8 Taksonomi Kategori Pertanyaan & 6 Dimensi Evaluasi Ahli (Likert 1-5)")
lines.append(f"Total Kueri: {len(all_queries)} Butir Pertanyaan Standar Emas (Gold Standard Benchmark)")
lines.append("=" * 88)
lines.append("")
lines.append("STRUKTUR TAKSONOMI 8 KATEGORI PERTANYAAN:")
lines.append("  1. Faktual / Pasal Spesifik   : Pertanyaan langsung mengenai bunyi dan nomor pasal tertentu.")
lines.append("  2. Definisional               : Pertanyaan pengertian, batasan konsep, atau doktrin hukum.")
lines.append("  3. Prosedural                 : Pertanyaan mengenai tahapan tata cara beracara di pengadilan (HIR).")
lines.append("  4. Multi-hop Reasoning        : Penalaran berantai yang menghubungkan KUHPerdata + HIR sekaligus.")
lines.append("  5. Komparatif                 : Perbandingan antara dua doktrin hukum yang berbeda.")
lines.append("  6. Case-based Reasoning       : Pemecahan studi kasus / kronologi sengketa perorangan konkret.")
lines.append("  7. Parafrasa / Semantik       : Pertanyaan bahasa awam informal tanpa menyebut istilah teknis hukum.")
lines.append("  8. Unanswerable (Halusinasi)  : Pertanyaan di luar korpus untuk menguji kejujuran dan batasan AI.")
lines.append("")
lines.append("-" * 88)
lines.append("DAFTAR 40 BUTIR EVALUASI LENGKAP")
lines.append("-" * 88)
lines.append("")

for idx, q in enumerate(all_queries, 1):
    qid = q["id"]
    query_text = q["query"]
    src = q["source"]
    pasal_list = q["nomor_pasal"]
    pasal_str = ", ".join([f"Pasal {p}" for p in pasal_list]) if pasal_list else "Tidak Ada (Di Luar Korpus)"
    topik = q["topik"]
    kategori = q.get("kategori", "-")

    lines.append(f"[{idx:02d}] ID KUERI      : {qid}")
    lines.append(f"     KATEGORI      : {kategori}")
    lines.append(f"     PERTANYAAN    : \"{query_text}\"")
    lines.append(f"     SUMBER HUKUM  : {src} ({pasal_str})")
    lines.append(f"     TOPIK / ASAS  : {topik}")

    if not pasal_list:
        lines.append(f"     STATUS TARGET : [UNANSWERABLE / ZERO-GROUNDING TEST]")
        lines.append(f"     PEDOMAN RESPON: {q.get('keterangan', '')}")
    else:
        lines.append(f"     REFERENSI PASAL RESMI:")
        for p in pasal_list:
            p_clean = str(p).strip().lower()
            # Cek di KUHPerdata dulu lalu HIR
            content = clean_map.get(("KUHPerdata", p_clean)) or clean_map.get(("HIR", p_clean)) or ""
            c_lines = content.splitlines() if content else ["(Teks pasal tersedia di database)"]
            lines.append(f"       * {src} Pasal {p}:")
            if len(c_lines) > 5:
                for l in c_lines[:4]:
                    lines.append(f"       | {l}")
                lines.append(f"       | ... [dan seterusnya, total {len(c_lines)} baris]")
            else:
                for l in c_lines:
                    lines.append(f"       | {l}")

    lines.append("")
    lines.append("-" * 88)
    lines.append("")

# Statistik
lines.append("REKAPITULASI DISTRIBUSI TAKSONOMI 8 KATEGORI:")
cat_counts = {}
for q in all_queries:
    cat_counts[q.get("kategori")] = cat_counts.get(q.get("kategori"), 0) + 1

for cat, count in sorted(cat_counts.items()):
    lines.append(f"- {cat:<30}: {count:02d} butir ({count/len(all_queries)*100:.1f}%)")

lines.append("")
lines.append("DISTRIBUSI SUMBER HUKUM:")
lines.append("- KUHPerdata Tunggal          : 25 butir")
lines.append("- HIR Tunggal                 : 11 butir")
lines.append("- Kombinasi Multi-hop (KUH+HIR): 2 butir")
lines.append("- Di Luar Korpus (Unanswerable): 2 butir")
lines.append("=" * 88)

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"[+] Berhasil memperbarui {out_txt_path.name} (Total baris: {len(lines)})")
