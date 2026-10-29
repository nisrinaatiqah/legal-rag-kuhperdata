"""
Modul: Pengujian Otomatis (Unit Testing) - Verifikasi Pipeline RAG & Pertahanan
Fungsi: Menguji integritas fungsional seluruh modul sistem secara otomatis:
1. Uji Kelengkapan Korpus Bersih (Wajib tepat 2.276 pasal).
2. Uji Kelengkapan Manifest Kriptografi SHA-256 (Wajib tepat 2.276 catatan hash).
3. Uji Modul Deteksi Racun (Pasal asli tidak boleh diblokir, pasal manipulasi wajib diblokir).
4. Uji Format Grounding Prompt (Memastikan konteks pasal masuk ke teks prompt).
5. Uji Factory Generator LLM (Memastikan class model Gemini, DeepSeek, dan Qwen terinisialisasi tepat).
"""

import unittest
import json
import sys
from pathlib import Path

# Daftarkan root legal-rag-perdata ke path sistem Python
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.detection.risk_score import PoisoningDetector
from src.rag.prompt import build_legal_prompt
from src.rag.generator import get_generator, GeminiGenerator, DeepSeekGenerator, QwenOllamaGenerator


class TestLegalRAGPipeline(unittest.TestCase):
    """Kumpulan pengujian unit untuk validasi sistem Legal RAG."""

    def test_clean_corpus_count(self):
        """[TEST 1] Memastikan korpus perdata bersih berjumlah tepat 2.276 pasal (KUHPerdata + HIR)."""
        clean_path = ROOT_DIR / "data" / "processed" / "legal_corpus_clean.jsonl"
        self.assertTrue(clean_path.exists(), "File korpus bersih harus ada")
        count = 0
        with open(clean_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        self.assertEqual(count, 2276, "Total pasal harus tepat 2.276")

    def test_manifest_sha256_count(self):
        """[TEST 2] Memastikan manifes hash kriptografi memuat 2.276 sidik jari SHA-256."""
        manifest_path = ROOT_DIR / "data" / "manifests" / "trusted_corpus_manifest.json"
        self.assertTrue(manifest_path.exists(), "File manifest SHA-256 harus ada")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data.get("chunks", [])), 2276, "Manifest harus memuat 2.276 hash")

    def test_poisoning_detector_clean_and_tampered(self):
        """
        [TEST 3] Menguji akurasi detektor racun:
        - Pasal asli harus lolos (is_blocked = False, r_source = 0.0).
        - Pasal yang dimanipulasi harus diblokir (is_blocked = True, r_source = 1.0).
        """
        detector = PoisoningDetector(alpha=0.6, tau=0.5)

        # 1. Uji pasal asli dari korpus bersih
        clean_path = ROOT_DIR / "data" / "processed" / "legal_corpus_clean.jsonl"
        with open(clean_path, "r", encoding="utf-8") as f:
            first_clean_chunk = json.loads(f.readline())

        res_clean = detector.evaluate_chunk(first_clean_chunk)
        self.assertFalse(res_clean["is_blocked"], "Pasal asli tidak boleh diblokir")
        self.assertEqual(res_clean["r_source"], 0.0, "Risiko sumber pasal asli harus 0.0")
        self.assertLess(res_clean["composite_score"], 0.5, "Skor risiko pasal asli harus < 0.5")

        # 2. Uji pasal manipulasi (teks diubah sengaja)
        tampered_chunk = dict(first_clean_chunk)
        tampered_chunk["content"] = "Menikmati hak-hak ini sepenuhnya dilarang dan dibatalkan bagi semua orang."
        res_tampered = detector.evaluate_chunk(tampered_chunk)
        self.assertTrue(res_tampered["is_blocked"], "Pasal manipulasi wajib diblokir")
        self.assertEqual(res_tampered["r_source"], 1.0, "Risiko sumber pasal manipulasi harus 1.0")
        self.assertGreaterEqual(res_tampered["composite_score"], 0.5, "Skor risiko pasal manipulasi harus >= 0.5")

    def test_prompt_builder_grounding(self):
        """[TEST 4] Memastikan perakitan prompt menyertakan header pasal dan pertanyaan pengguna."""
        chunk = {
            "source": "KUHPerdata",
            "pasal": "1320",
            "content": "Supaya terjadi persetujuan yang sah, perlu dipenuhi empat syarat..."
        }
        p = build_legal_prompt("Apa syarat sah perjanjian?", [chunk])
        self.assertIn("KONTEKS DOKUMEN HUKUM:", p["user_prompt"])
        self.assertIn("KUHPerdata Pasal 1320", p["user_prompt"])
        self.assertIn("PERTANYAAN PENGGUNA:", p["user_prompt"])

    def test_generator_initialization(self):
        """[TEST 5] Memastikan fungsi get_generator mengembalikan instance class yang benar."""
        g_gemini = get_generator("gemini")
        g_deepseek = get_generator("deepseek")
        g_qwen = get_generator("qwen")
        self.assertIsInstance(g_gemini, GeminiGenerator)
        self.assertIsInstance(g_deepseek, DeepSeekGenerator)
        self.assertIsInstance(g_qwen, QwenOllamaGenerator)


if __name__ == "__main__":
    unittest.main()
