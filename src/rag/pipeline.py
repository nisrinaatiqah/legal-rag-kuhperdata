"""
Modul: RAG - Pipeline Utuh Tanya Jawab Hukum (End-to-End Legal RAG Pipeline)
Fungsi: Mengintegrasikan seluruh komponen sistem ke dalam satu siklus eksekusi:
1. Retriever         : Mengambil top-K pasal paling relevan dari database vektor Qdrant.
2. Pertahanan Racun  : (Opsional) Memfilter pasal yang terindikasi terkena Knowledge Poisoning.
3. Prompt Builder    : Merakit konteks pasal yang aman beserta instruksi sitasi hukum.
4. LLM Generator     : Menghasilkan jawaban hukum terstruktur via model pilihan (Qwen, Gemini, DeepSeek).
"""

from typing import Dict, Any, Optional, List
from src.retrieval.retriever import LegalRetriever
from src.rag.prompt import build_legal_prompt
from src.rag.generator import get_generator, BaseLegalGenerator
from src.detection.risk_score import PoisoningDetector


class LegalRAGPipeline:
    """Kelas orkestrator pipeline RAG Hukum Perdata Indonesia."""

    def __init__(
        self,
        retriever: Optional[LegalRetriever] = None,
        generator: Optional[BaseLegalGenerator] = None,
        default_model: str = "gemini",
        detector: Optional[PoisoningDetector] = None,
    ):
        """
        [PROSES INISIALISASI PIPELINE]
        Menyiapkan retriever, generator, dan modul deteksi pertahanan racun.
        """
        if retriever is None:
            print("[*] Memuat LegalRetriever R1 bawaan (BGE-M3 + Qdrant)...")
            self.retriever = LegalRetriever.load_clean_index()
        else:
            self.retriever = retriever

        self.default_model = default_model
        self.generator = generator
        self.detector = detector or PoisoningDetector()

    def answer(
        self,
        query: str,
        top_k: int = 5,
        model_type: Optional[str] = None,
        generator_kwargs: Optional[Dict[str, Any]] = None,
        enable_defense: bool = False,
    ) -> Dict[str, Any]:
        """
        [ALUR UTAMA MENJAWAB PERTANYAAN]
        1. Retrieval      : Mencari top-K pasal terkait dari database Qdrant.
        2. Filter Defense : Jika enable_defense=True, pisahkan pasal palsu/racun dengan SHA-256 + NLI.
        3. Prompting      : Bangun prompt dengan menyertakan hanya pasal yang lolos verifikasi.
        4. Generation     : Panggil LLM untuk menganalisis dan merumuskan jawaban hukum.
        """
        chosen_model = model_type or self.default_model
        gen_kwargs = generator_kwargs or {}

        # 1. Tahap Retrieval Dokumen Hukum
        hits = self.retriever.retrieve(query=query, top_k=top_k)

        # 2. Tahap Pertahanan Anti-Knowledge Poisoning
        blocked_chunks: List[Dict[str, Any]] = []
        context_chunks = hits
        if enable_defense:
            cleared_chunks, blocked_chunks = self.detector.filter_context(hits)
            context_chunks = cleared_chunks

        # 3. Tahap Konstruksi Prompt Berlandaskan Hukum
        prompt_data = build_legal_prompt(query=query, retrieved_chunks=context_chunks)

        # 4. Inisialisasi Generator Sesuai Pilihan Pengguna
        gen = self.generator or get_generator(model_type=chosen_model, **gen_kwargs)

        # 5. Tahap Inferensi / Pembangkitan Jawaban oleh LLM
        answer_text = gen.generate(
            system_prompt=prompt_data["system_prompt"],
            user_prompt=prompt_data["user_prompt"],
        )

        return {
            "query": query,
            "top_k": top_k,
            "model_type": chosen_model,
            "enable_defense": enable_defense,
            "retrieved_chunks": hits,
            "context_chunks": context_chunks,
            "blocked_chunks": blocked_chunks,
            "prompt": prompt_data,
            "answer": answer_text,
        }


def main():
    """
    [DEMO INTERAKTIF TERMINAL]
    Memungkinkan demonstrasi tanya jawab hukum perdata langsung dari terminal/command prompt
    tanpa perlu menjalankan aplikasi antarmuka web.
    """
    import sys

    # Konfigurasi UTF-8 pada terminal Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 75)
    print("DEMO TERMINAL: SISTEM LEGAL QUESTION ANSWERING HUKUM PERDATA (ITS)")
    print("=" * 75)

    pipeline = LegalRAGPipeline(default_model="gemini")

    # Kueri uji coba default
    sample_query = "Apa saja syarat sahnya suatu perjanjian menurut hukum perdata?"
    print(f"\n[*] Menguji kueri contoh: '{sample_query}'")
    print("[*] Mengambil pasal dari Qdrant Cloud & memproses jawaban via Gemini...\n")

    result = pipeline.answer(query=sample_query, top_k=3, enable_defense=True)

    print("1. DOKUMEN HUKUM RELEVAN (HASIL RETRIEVAL QDRANT):")
    for idx, doc in enumerate(result["context_chunks"], 1):
        print(f"   [{idx}] {doc.get('source')} Pasal {doc.get('pasal')} (Skor Kemiripan: {doc.get('score', 0):.4f})")

    print("\n2. STATUS PERTAHANAN KNOWLEDGE POISONING:")
    if result["blocked_chunks"]:
        print(f"   [!] Ditemukan & diblokir {len(result['blocked_chunks'])} pasal racun/terkontaminasi.")
    else:
        print("   [+] Seluruh dokumen terverifikasi otentik dan aman (SHA-256 + NLI Lolos).")

    print("\n3. ANALISIS JAWABAN HUKUM OLEH AI:")
    print("-" * 75)
    print(result["answer"])
    print("-" * 75)


if __name__ == "__main__":
    main()

