"""
Modul: Deteksi Pertahanan - Composite Risk Scoring & Poisoning Defense Filter
Fungsi: Menggabungkan hasil verifikasi kriptografi (Source Verification) dan
analisis semantik (Semantic NLI Contradiction) menjadi satu skor risiko terpadu:
    Skor Risiko = (alpha * R_source) + ((1 - alpha) * R_semantic)

Jika Skor Risiko >= ambang batas (threshold tau), potongan pasal dinyatakan SEBAGAI RACUN (BLOCKED_POISON)
dan langsung disaring agar tidak masuk ke prompt LLM generator.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from src.detection.source_verification import SourceVerifier
from src.detection.semantic_nli import SemanticConsistencyVerifier


class PoisoningDetector:
    """
    Kelas Detektor Komposit Pertahanan Anti-Knowledge Poisoning.
    Parameter:
        alpha (float): Bobot verifikasi sumber kriptografi [0.0 - 1.0]. Default: 0.6.
        tau (float)  : Ambang batas klasifikasi racun [0.0 - 1.0]. Default: 0.5.
    """

    def __init__(
        self,
        alpha: float = 0.6,
        tau: float = 0.5,
        manifest_path: Optional[Path] = None,
        clean_corpus_path: Optional[Path] = None,
    ):
        """[INISIALISASI] Memuat modul SourceVerifier dan SemanticConsistencyVerifier."""
        self.alpha = alpha
        self.tau = tau
        self.source_verifier = SourceVerifier(manifest_path=manifest_path)
        self.semantic_verifier = SemanticConsistencyVerifier(clean_corpus_path=clean_corpus_path)

    def evaluate_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        [PROSES 1: EVALUASI SKOR RISIKO CHUNK TUNGGAL]
        1. Menghitung risiko integritas hash SHA-256 (r_source: 0.0 atau 1.0).
        2. Menghitung risiko pergeseran polaritas makna (r_semantic: 0.0 - 1.0).
        3. Menghitung rata-rata tertimbang (composite_score).
        4. Memutuskan status pemblokiran jika composite_score >= tau.
        """
        src_res = self.source_verifier.verify_chunk(chunk)
        sem_res = self.semantic_verifier.verify_chunk(chunk)

        r_source = src_res["source_risk_score"]
        r_semantic = sem_res["contradiction_risk"]

        # Rumus gabungan pertahanan
        composite_score = (self.alpha * r_source) + ((1.0 - self.alpha) * r_semantic)
        is_blocked = composite_score >= self.tau

        return {
            "chunk_id": chunk.get("chunk_id"),
            "source": chunk.get("source"),
            "pasal": chunk.get("pasal") or chunk.get("nomor_pasal"),
            "r_source": round(r_source, 4),
            "r_semantic": round(r_semantic, 4),
            "composite_score": round(composite_score, 4),
            "threshold_tau": self.tau,
            "status": "BLOCKED_POISON" if is_blocked else "CLEARED_SAFE",
            "is_blocked": is_blocked,
            "source_status": src_res["status"],
            "semantic_status": sem_res["status"],
        }

    def filter_context(
        self, retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        [PROSES 2: PENYARINGAN KONTEKS SEBELUM MASUK GENERATOR LLM]
        Memeriksa setiap pasal hasil retrieval:
        - Dokumen yang aman (CLEARED_SAFE) dimasukkan ke cleared_chunks untuk jadi konteks prompt LLM.
        - Dokumen yang terindikasi racun (BLOCKED_POISON) dipisahkan ke blocked_chunks agar tidak merusak jawaban LLM.
        """
        cleared_chunks = []
        blocked_chunks = []

        for chunk in retrieved_chunks:
            eval_res = self.evaluate_chunk(chunk)
            annotated_chunk = dict(chunk)
            annotated_chunk["defense_evaluation"] = eval_res

            if eval_res["is_blocked"]:
                blocked_chunks.append(annotated_chunk)
            else:
                cleared_chunks.append(annotated_chunk)

        return cleared_chunks, blocked_chunks
