import json
from pathlib import Path

base_dir = Path("legal-rag-perdata")
gt_json_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.json"
clean_corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"
out_txt_path = base_dir / "data" / "evaluation" / "ground_truth_perdata.txt"

with open(gt_json_path, "r", encoding="utf-8") as f:
    queries = json.load(f)

clean_map = {}
with open(clean_corpus_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            it = json.loads(line)
            clean_map[(it.get("source"), str(it.get("pasal")).strip().lower())] = it.get("content", "").strip()

# Daftar pasal yang diracuni di 1% untuk penanda peran evaluasi
poisoned_1pct_kuhp = {"330", "570", "830", "852", "863", "1162", "1243", "1320", "1365", "1458", "1740", "1754", "1792", "1967"}
poisoned_1pct_hir = {"120", "121", "123", "125", "132a", "132b", "227", "374", "390"}

lines = []
lines.append("=" * 85)
lines.append("DATASET GROUND TRUTH EVALUASI RAG HUKUM PERDATA INDONESIA (CIVILEX AI)")
lines.append("Kitab Undang-Undang Hukum Perdata (KUHPerdata) & Herziene Inlandsch Reglement (HIR)")
lines.append("Total Kueri: 30 Butir Pertanyaan Hukum Standar Emas (Gold Standard)")
lines.append("=" * 85)
lines.append("")
lines.append("DESKRIPSI DATASET:")
lines.append("Dataset ini dirancang khusus untuk menguji performa Information Retrieval (MRR, Recall@K,")
lines.append("MAP@K), kualitas generasi jawaban LLM (ROUGE, BLEU, Faithfulness, Citation Accuracy),")
lines.append("serta ketahanan sistem terhadap serangan manipulasi naskah hukum (Knowledge Poisoning).")
lines.append("")
lines.append("-" * 85)
lines.append("DAFTAR 30 BUTIR GROUND TRUTH LENGKAP")
lines.append("-" * 85)
lines.append("")

for idx, q in enumerate(queries, 1):
    qid = q["id"]
    query_text = q["query"]
    src = q["source"]
    pasal_list = q["nomor_pasal"]
    pasal_str = ", ".join([f"Pasal {p}" for p in pasal_list])
    topik = q["topik"]

    # Tentukan peran pengujian
    is_p1 = False
    if src == "KUHPerdata":
        is_p1 = any(str(p).lower() in poisoned_1pct_kuhp for p in pasal_list)
    elif src == "HIR":
        is_p1 = any(str(p).lower() in poisoned_1pct_hir for p in pasal_list)

    peran = "Uji Serangan Poisoning (Target Manipulasi 1%, 5%, 10%)" if is_p1 else "Uji Pertahanan Bersih & False Alarm (Zero False Positive Test)"

    lines.append(f"[{idx:02d}] ID KUERI      : {qid}")
    lines.append(f"     PERTANYAAN    : \"{query_text}\"")
    lines.append(f"     SUMBER HUKUM  : {src} ({pasal_str})")
    lines.append(f"     TOPIK / DOKTRIN: {topik}")
    lines.append(f"     FUNGSI UJI    : {peran}")
    lines.append(f"     REFERENSI ISI PASAL ASLI:")

    # Ambil isi teks pasal asli
    for p in pasal_list:
        p_clean = str(p).strip().lower()
        content = clean_map.get((src, p_clean), "(Teks pasal tidak ditemukan di master)")
        # Rapikan indentasi
        content_lines = content.splitlines()
        if len(content_lines) > 6:
            preview = "\n".join([f"       | {l}" for l in content_lines[:5]])
            lines.append(f"       * {src} Pasal {p}:")
            lines.append(preview)
            lines.append(f"       | ... [dan seterusnya, total {len(content_lines)} baris]")
        else:
            lines.append(f"       * {src} Pasal {p}:")
            for l in content_lines:
                lines.append(f"       | {l}")

    lines.append("")
    lines.append("-" * 85)
    lines.append("")

# Statistik penutup
lines.append("REKAPITULASI DISTRIBUSI GROUND TRUTH:")
lines.append(f"- Total Kueri KUHPerdata : 19 butir (63.3%) -> Meliputi Hukum Orang, Benda, Waris, Perikatan/Perjanjian, Kedaluwarsa")
lines.append(f"- Total Kueri HIR         : 11 butir (36.7%) -> Meliputi Gugatan, Kuasa, Verstek, Perdamaian, Rekonvensi, Alat Bukti, Sita Jaminan")
lines.append(f"- Kueri Target Serangan   : 20 butir (Menguji ketahanan terhadap pasal beracun)")
lines.append(f"- Kueri Kontrol Bersih    : 10 butir (Menguji kepatuhan zero false positive saat filter aktif)")
lines.append("=" * 85)

with open(out_txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"[SUCCESS] Berhasil membuat file: {out_txt_path} ({len(lines)} baris)")
