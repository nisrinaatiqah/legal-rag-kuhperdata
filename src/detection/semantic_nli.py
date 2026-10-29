"""
Modul: Deteksi Pertahanan - Semantic Consistency & NLI-Style Contradiction Verifier
Fungsi: Memeriksa konsistensi makna (semantik) dan pergeseran polaritas hukum (misal: klausul yang
seharusnya 'wajib' diubah menjadi 'tidak wajib', atau 'sah' menjadi 'batal') antara dokumen
yang diambil dengan referensi kanonik bersih.
"""

import difflib
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


class SemanticConsistencyVerifier:
    """
    Kelas pemeriksa konsistensi semantik dan risiko kontradiksi hukum
    menggunakan analisis pergeseran kata penanda negasi dan kewajiban.
    """

    # Kata-kata penanda negasi / pembatalan dalam hukum
    NEGATION_MARKERS = {
        "tidak", "bukan", "tanpa", "tiada", "dilarang",
        "dibatalkan", "dikecualikan", "hapus", "gugur", "bebas"
    }

    # Kata-kata penanda kewajiban hukum
    OBLIGATION_MARKERS = {
        "wajib", "harus", "diwajibkan", "perlu", "patut"
    }

    def __init__(self, clean_corpus_path: Optional[Path] = None):
        """[INISIALISASI] Memuat teks rujukan kanonik bersih ke memori."""
        base_dir = Path(__file__).resolve().parents[2]
        if clean_corpus_path is None:
            clean_corpus_path = base_dir / "data" / "processed" / "legal_corpus_clean.jsonl"

        self.clean_corpus_path = clean_corpus_path
        self.clean_references: Dict[str, str] = {}
        self._load_clean_references()

    def _load_clean_references(self):
        """[PROSES 1: BACA REFERENSI RESMI] Memetakan chunk_id ke isi pasal kanonik bersih."""
        with open(self.clean_corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    cid = item.get("chunk_id")
                    content = item.get("content") or item.get("isi_pasal") or ""
                    if cid:
                        self.clean_references[cid] = content

    @staticmethod
    def _tokenize(text: str):
        """[UTILITAS] Ekstraksi kata-kata menjadi daftar token huruf kecil."""
        return re.findall(r"\b\w+\b", text.lower())

    def verify_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        [PROSES 2: ANALISIS KONTRAKDIKSI SEMANTIK]
        Membandingkan teks hipotesis (retrieved) dengan teks asli kanonik:
        1. Cek kesamaan persis (exact match).
        2. Hitung Sequence Alignment Similarity Ratio.
        3. Cek pembalikan polaritas hukum (misal ada penambahan kata 'tidak' atau hilangnya kata 'wajib').
        Mengembalikan kamus metrik: similarity, contradiction_risk, status ('CONSISTENT'/'CONTRADICTION').
        """
        cid = chunk.get("chunk_id", "")
        hyp_text = chunk.get("content") or chunk.get("isi_pasal") or ""

        # Jika tidak ada pasal pembanding di database referensi
        if cid not in self.clean_references:
            return {
                "chunk_id": cid,
                "has_reference": False,
                "similarity": 0.0,
                "contradiction_risk": 1.0,
                "polarity_flipped": True,
                "status": "NO_TRUSTED_REFERENCE",
            }

        clean_ref = self.clean_references[cid]

        # 1. Cek kecocokan mutlak teks
        if clean_ref.strip() == hyp_text.strip():
            return {
                "chunk_id": cid,
                "has_reference": True,
                "similarity": 1.0,
                "contradiction_risk": 0.0,
                "polarity_flipped": False,
                "status": "CONSISTENT",
            }

        words_ref = self._tokenize(clean_ref)
        words_hyp = self._tokenize(hyp_text)

        # 2. Hitung rasio kemiripan penjajaran sekuensial (Sequence Matcher)
        matcher = difflib.SequenceMatcher(None, words_ref, words_hyp)
        similarity = matcher.ratio()

        # 3. Deteksi pembalikan polaritas makna (Negation & Obligation Inversion)
        neg_ref = any(w in words_ref for w in self.NEGATION_MARKERS)
        neg_hyp = any(w in words_hyp for w in self.NEGATION_MARKERS)
        ob_ref = any(w in words_ref for w in self.OBLIGATION_MARKERS)
        ob_hyp = any(w in words_hyp for w in self.OBLIGATION_MARKERS)

        polarity_flipped = (neg_ref != neg_hyp) or (ob_ref != ob_hyp)

        # 4. Tentukan tingkat risiko kontradiksi
        if polarity_flipped or similarity < 0.85:
            # Terjadi penyimpangan substansial atau injeksi kontradiksi hukum
            contradiction_risk = max(0.80, 1.0 - similarity)
            status = "CONTRADICTION"
        else:
            contradiction_risk = max(0.0, 1.0 - similarity)
            status = "CONSISTENT"

        return {
            "chunk_id": cid,
            "has_reference": True,
            "similarity": round(similarity, 4),
            "contradiction_risk": round(contradiction_risk, 4),
            "polarity_flipped": polarity_flipped,
            "status": status,
        }
