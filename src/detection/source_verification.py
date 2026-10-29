"""
Modul: Deteksi Pertahanan - Source Verification (Verifikasi Integritas Sumber Kriptografi)
Fungsi: Memeriksa keaslian potongan pasal (chunk) yang diambil oleh retriever dengan
mencocokkan sidik jari hash SHA-256 terhadap manifest resmi (trusted manifest).
Jika teks telah diubah walau 1 huruf saja oleh penyerang, hash tidak akan cocok (tampered).
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional


class SourceVerifier:
    """Kelas pemeriksa integritas kriptografi menggunakan hash SHA-256."""

    def __init__(self, manifest_path: Optional[Path] = None):
        """[INISIALISASI] Membaca tabel hash resmi dari trusted_corpus_manifest.json."""
        if manifest_path is None:
            base_dir = Path(__file__).resolve().parents[2]
            manifest_path = base_dir / "data" / "manifests" / "trusted_corpus_manifest.json"

        self.manifest_path = manifest_path
        self.trusted_hashes: Dict[str, str] = {}
        self._load_manifest()

    def _load_manifest(self):
        """[PROSES 1: MEMUAT MANIFEST RESMI] Menyimpan pasangan {chunk_id: sha256_resmi} ke RAM."""
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("chunks", []):
            cid = item.get("chunk_id")
            h = item.get("content_sha256")
            if cid and h:
                self.trusted_hashes[cid] = h

    @staticmethod
    def compute_hash(text: str) -> str:
        """[UTILITAS] Menghitung nilai hash SHA-256 dari teks artikel."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def verify_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        [PROSES 2: VALIDASI KEASLIAN CHUNK]
        1. Menghitung hash SHA-256 dari teks pasal yang didapat.
        2. Mencocokkannya dengan hash resmi di manifest.
        Hasil kembalian:
        - is_valid (bool): True jika identik dan terdaftar resmi.
        - status (str):
            * 'VERIFIED_AUTHENTIC'    : Asli 100%, skor risiko = 0.0
            * 'TAMPERED_HASH_MISMATCH': Teks telah diubah/diracuni, skor risiko = 1.0
            * 'UNKNOWN_ORIGIN'        : Pasal tidak dikenal, skor risiko = 1.0
        - source_risk_score (float): 0.0 (aman) atau 1.0 (bahaya).
        """
        cid = chunk.get("chunk_id", "")
        content = chunk.get("content") or chunk.get("isi_pasal") or ""
        computed = self.compute_hash(content)

        # Kasus A: Chunk ID tidak ada di arsip terpercaya
        if cid not in self.trusted_hashes:
            return {
                "chunk_id": cid,
                "is_valid": False,
                "status": "UNKNOWN_ORIGIN",
                "source_risk_score": 1.0,
                "computed_hash": computed,
                "trusted_hash": None,
            }

        trusted = self.trusted_hashes[cid]
        # Kasus B: Hash sama persis (Teks Asli dan Valid)
        if computed == trusted:
            return {
                "chunk_id": cid,
                "is_valid": True,
                "status": "VERIFIED_AUTHENTIC",
                "source_risk_score": 0.0,
                "computed_hash": computed,
                "trusted_hash": trusted,
            }
        # Kasus C: Hash berbeda (Teks Palsu / Telah Diracuni)
        else:
            return {
                "chunk_id": cid,
                "is_valid": False,
                "status": "TAMPERED_HASH_MISMATCH",
                "source_risk_score": 1.0,
                "computed_hash": computed,
                "trusted_hash": trusted,
            }
