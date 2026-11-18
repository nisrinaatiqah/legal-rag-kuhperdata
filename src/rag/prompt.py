"""
Modul: RAG - Format Prompt & Konstruksi Konteks Hukum
Fungsi: Mengelola template instruksi sistem (system prompt) dan format blok konteks pasal
mengadopsi arsitektur terstruktur (gaya Mas Nicho) untuk hukum perdata (KUHPerdata & HIR):
1. Kalimat pertama langsung mengarahkan ke pasal yang relevan & menjawab pokok persoalan hukum secara lugas.
2. Penjelasan substantif mengalir natural, ringkas, padat, dan mudah dipahami orang awam layaknya ChatGPT/Gemini.
3. Tanpa kalimat pembuka klise ("Berdasarkan dokumen hukum yang tersedia...") dan tanpa catatan tambahan/disclaimer template.
4. Bagian akhir menyajikan rangkuman poin-poin kesimpulan secara eksplisit.
"""

from typing import List, Dict, Any, Optional

# [INSTRUKSI SISTEM KHUSUS HUKUM PERDATA — GAYA REFERENSI MAS NICHO]
LEGAL_QA_SYSTEM_PROMPT = """Anda adalah CiviLex AI, asisten hukum kecerdasan buatan yang ahli Kitab Undang-Undang Hukum Perdata (KUHPerdata) dan Het Herziene Inlandsch Reglement (HIR).

Tugas Anda:
1. Kalimat pertama harus langsung mengarahkan pengguna ke pasal yang relevan dan menjawab pokok persoalan hukum secara lugas, jelas, dan to-the-point.
2. Telaah pasal-pasal yang relevan secara urut, jelaskan apa yang diatur dan bagaimana keterkaitannya dengan persoalan pengguna dengan bahasa yang mengalir natural, padat, dan mudah dipahami orang awam layaknya ChatGPT/Gemini.
3. Jika pengguna menanyakan syarat sah perjanjian, unsur PMH, alat bukti persidangan, atau prosedur sita jaminan, uraikan unsur-unsur/syaratnya dengan penomoran atau poin-poin yang terstruktur rapi.
4. Bila pengguna menanyakan akibat hukum atau implikasi hukum (misalnya jika syarat perjanjian tidak terpenuhi), jelaskan secara lugas dan tuntas berdasarkan doktrin hukum perdata yang berlaku.
5. Jangan gunakan kalimat pembuka template/klise (seperti "Berdasarkan dokumen hukum yang tersedia...", "Berdasarkan konteks yang diberikan...", atau sejenisnya). Langsung mulai dengan substansi jawaban.
6. Jangan mengarang dasar hukum di luar naskah resmi yang ada dalam konteks.
7. Jangan berikan catatan tambahan, disclaimer template berulang, atau garis pembatas (---) di akhir jawaban.
8. Di bagian paling akhir jawaban, sediakan rangkuman inti dalam format:
=== KESIMPULAN ===
- [Poin kesimpulan 1]
- [Poin kesimpulan 2]
- [Poin kesimpulan 3 (opsional)]"""


def format_context_for_prompt(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    [PROSES 1: FORMATTING KONTEKS PASAL]
    Menyusun daftar naskah pasal yang berhasil ditarik menjadi blok teks yang rapi dan terstruktur.
    """
    context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        source = chunk.get("source", "KUHPerdata")
        bab = chunk.get("bab_title") or chunk.get("bab") or ""
        pasal = chunk.get("pasal", "")
        content = chunk.get("content", "").strip()

        header = f"[{source} Pasal {pasal}]"
        if bab and bab != "-":
            header += f" ({bab})"

        context_blocks.append(f"{header}\n{content}")

    return "\n\n---\n\n".join(context_blocks)


def build_legal_prompt(query: str, retrieved_chunks: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, str]:
    """
    [PROSES 2: PERAKITAN PROMPT LENGKAP]
    Menggabungkan naskah konteks hukum dengan pertanyaan pengguna ke dalam format prompt terpadu.
    """
    chunks = retrieved_chunks or kwargs.get("context_chunks", [])
    context_text = format_context_for_prompt(chunks)

    user_prompt = f"""=== KONTEKS NASKAH HUKUM ===
{context_text}

=== PERTANYAAN PENGGUNA ===
{query}

=== JAWABAN ==="""

    formatted_prompt = f"{LEGAL_QA_SYSTEM_PROMPT}\n\n{user_prompt}"

    return {
        "system_prompt": LEGAL_QA_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "formatted_prompt": formatted_prompt,
    }
