"""
Modul: RAG - Format Prompt & Konstruksi Konteks Hukum
Fungsi: Mengelola template instruksi sistem (system prompt) dan format blok konteks pasal
untuk menjamin jawaban LLM 100% berlandaskan hukum (grounded) dan wajib menyertakan sitasi nomor pasal.
"""

from typing import List, Dict, Any, Optional

# [INSTRUKSI SISTEM KHUSUS HUKUM PERDATA]
# Memberikan panduan asisten hukum cerdas yang natural dan komprehensif layaknya ChatGPT/Gemini
LEGAL_QA_SYSTEM_PROMPT = """Anda adalah CiviLex AI, asisten kecerdasan buatan ahli hukum perdata Indonesia (KUHPerdata dan HIR) yang cerdas, profesional, dan komunikatif layaknya ChatGPT/Gemini.

PANDUAN MENJAWAB:
1. Jawablah pertanyaan pengguna secara komprehensif, mengalir (natural), dan mudah dipahami, tanpa menggunakan gaya bahasa yang kaku atau template robotik.
2. Dasarkan analisis Anda pada naskah pasal yang tercantum dalam konteks yang diberikan. Jelaskan isi ketentuan pasal dan bagaimana pasal tersebut menjawab persoalan hukum pengguna secara lugas.
3. Bila pengguna menanyakan akibat hukum atau implikasi hukum (seperti akibat tidak terpenuhinya syarat sah perjanjian), jelaskan secara lengkap, jelas, dan tuntas berdasarkan prinsip serta doktrin hukum perdata yang berlaku.
4. Hindari penggunaan format yang kaku seperti garis pembatas ('---') atau kalimat sangkalan berulang yang robotik. Sampaikan penjelasan secara lugas, berbobot, dan terstruktur rapi."""


def format_context_for_prompt(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    [PROSES 1: FORMATTING KONTEKS PASAL]
    Menyusun daftar potongan pasal yang berhasil diambil oleh retriever menjadi teks berstruktur,
    lengkap dengan nomor dokumen, nama undang-undang, bab, dan nomor pasal.
    """
    context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        source = chunk.get("source", "Hukum Perdata")
        bab = chunk.get("bab", "")
        pasal = chunk.get("pasal", "")
        content = chunk.get("content", "").strip()

        header = f"=== DOKUMEN {idx}: {source} Pasal {pasal} ==="
        if bab:
            header += f"\n(Bab: {bab})"

        context_blocks.append(f"{header}\n{content}\n")

    return "\n".join(context_blocks)


def build_legal_prompt(query: str, retrieved_chunks: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, str]:
    """
    [PROSES 2: PERAKITAN PROMPT LENGKAP]
    Menggabungkan teks konteks pasal hukum dengan pertanyaan pengguna ke dalam format pesan LLM.
    Mengembalikan dictionary:
    - system_prompt: Aturan perilaku dan kewajiban sitasi.
    - user_prompt  : Gabungan konteks pasal + pertanyaan pengguna.
    - formatted_prompt: Seluruh prompt utuh untuk keperluan logging.
    """
    chunks = retrieved_chunks or kwargs.get("context_chunks", [])
    context_text = format_context_for_prompt(chunks)

    user_prompt = f"""KONTEKS DOKUMEN HUKUM:
{context_text}

PERTANYAAN PENGGUNA:
{query}

JAWABAN (sertakan nomor pasal dan kutipan dasar hukum yang relevan):"""

    formatted_prompt = f"{LEGAL_QA_SYSTEM_PROMPT}\n\n{user_prompt}"

    return {
        "system_prompt": LEGAL_QA_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "formatted_prompt": formatted_prompt,
    }
