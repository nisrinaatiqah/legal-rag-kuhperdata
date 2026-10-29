"""
Modul: RAG - Antarmuka Generator Model Bahasa Besar (LLM Generator)
Fungsi: Mengelola pemanggilan model LLM untuk menghasilkan jawaban analisis hukum perdata:
1. QwenOllamaGenerator      (Konfigurasi L1: Qwen2.5-7B-Instruct via Ollama lokal)
2. GeminiGenerator          (Konfigurasi L2: Google Gemini via Cloud API)
3. DeepSeekGenerator        (Konfigurasi L3: DeepSeek-V3 / DeepSeek-R1 via Cloud API)
4. DeepSeekOllamaGenerator  (Konfigurasi L3 Lokal: DeepSeek-R1-8B dengan Chain-of-Thought reasoning)
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLegalGenerator(ABC):
    """Kelas dasar abstrak (interface) untuk semua model generator jawaban hukum."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Menghasilkan teks jawaban berdasarkan instruksi sistem dan prompt pengguna."""
        pass


class QwenOllamaGenerator(BaseLegalGenerator):
    """
    [GENERATOR L1: QWEN2.5-7B LOKAL VIA OLLAMA]
    - Model opensource yang berjalan 100% lokal dan offline di laptop/komputer.
    - Parameter: Temperature rendah (0.1) untuk meminimalkan halusinasi dan menjaga kepatuhan fakta.
    """

    def __init__(self, model_name: str = "qwen2.5:7b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Mengirim permintaan inferensi ke Ollama server lokal."""
        try:
            import ollama

            client = ollama.Client(host=self.host)
            response = client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.1, "top_p": 0.9},
            )
            return response["message"]["content"]
        except Exception as e:
            return (
                f"[KONEKSI OLLAMA GAGAL]: Pastikan Ollama telah terpasang dan dijalankan "
                f"di komputer Anda ('ollama run {self.model_name}').\nDetail error: {e}"
            )


class DeepSeekOllamaGenerator(BaseLegalGenerator):
    """
    [GENERATOR L3 LOKAL: DEEPSEEK-R1-8B LOKAL VIA OLLAMA]
    - Menjalankan model penalaran hukum (Reasoning Model) secara gratis dan offline.
    - Menangkap tag <think>...</think> untuk memisahkan alur penalaran (Chain-of-Thought)
      dengan jawaban akhir analisis hukum.
    """

    def __init__(self, model_name: str = "deepseek-r1:8b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Mengirim prompt ke model DeepSeek-R1 di Ollama dan memformat Chain-of-Thought."""
        try:
            import ollama

            client = ollama.Client(host=self.host)
            response = client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.1},
            )
            raw = response["message"]["content"]
            # Memisahkan alur berpikir <think> agar rapi saat ditampilkan ke pengguna
            if "<think>" in raw and "</think>" in raw:
                parts = raw.split("</think>")
                think_part = parts[0].replace("<think>", "").strip()
                answer_part = parts[1].strip()
                return (
                    f"**Alur Penalaran Hukum (Chain-of-Thought):**\n\n"
                    f"> *{think_part}*\n\n"
                    f"---\n\n"
                    f"**Jawaban Analisis Hukum:**\n\n"
                    f"{answer_part}"
                )
            return raw
        except Exception as e:
            return (
                f"[KONEKSI OLLAMA GAGAL]: Pastikan Ollama telah terpasang dan dijalankan "
                f"di komputer Anda ('ollama run {self.model_name}').\nDetail error: {e}"
            )


class GeminiGenerator(BaseLegalGenerator):
    """
    [GENERATOR L2: GOOGLE GEMINI VIA OFFICIAL SDK]
    - Menggunakan API Google Gemini (model default: gemini-3.5-flash).
    - Cepat, memiliki jendela konteks besar, dan penulisan bahasa Indonesia yang sangat luwes.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Memanggil API Google GenAI untuk menghasilkan jawaban hukum."""
        if not self.api_key:
            return (
                "[GEMINI_API_KEY TIDAK DITEMUKAN]: Masukkan API Key Google Gemini Anda "
                "ke environment variable GEMINI_API_KEY, berkas .env, atau kolom input sidebar."
            )

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Memastikan model mengarah ke versi aktif
            target_model = self.model_name
            if target_model in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                target_model = "gemini-3.5-flash"

            response = client.models.generate_content(
                model=target_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,
                ),
            )
            return response.text
        except Exception as e:
            return f"[ERROR PEMANGGILAN GEMINI]: {e}"


class DeepSeekGenerator(BaseLegalGenerator):
    """
    [GENERATOR L3 CLOUD: DEEPSEEK-V3 / DEEPSEEK-R1 VIA API]
    - Memanggil endpoint resmi api.deepseek.com.
    - Jika saldo habis ($0.00) atau API key belum ada, otomatis menyarankan opsi DeepSeek-R1 lokal.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "deepseek-chat",  # 'deepseek-chat' = DeepSeek-V3, 'deepseek-reasoner' = DeepSeek-R1
        base_url: str = "https://api.deepseek.com",
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Mengirim HTTP POST request ke server DeepSeek Cloud API."""
        # 1. Jika ada API Key, gunakan DeepSeek Cloud API
        if self.api_key:
            try:
                import requests

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.1,
                    "stream": False,
                }
                resp = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    choice = data["choices"][0]["message"]
                    content = choice.get("content", "")
                    reasoning = choice.get("reasoning_content")
                    if reasoning:
                        return f"**Alur Penalaran Hukum (Chain-of-Thought):**\n\n> *{reasoning}*\n\n---\n\n**Jawaban Analisis Hukum:**\n\n{content}"
                    return content
                elif resp.status_code == 402:
                    return (
                        "**[DEEPSEEK API: SALDO $0.00 / INSUFFICIENT BALANCE]**\n\n"
                        "Akun DeepSeek API Anda saat ini belum memiliki saldo ($0.00 USD). "
                        "Untuk menjalankan analisis hukum secara gratis dan offline, silakan pilih opsi **DeepSeek-R1 (Lokal - Ollama)** "
                        "yang sudah terpasang dan aktif di laptop Anda."
                    )
                else:
                    return f"[ERROR API DEEPSEEK {resp.status_code}]: {resp.text}"
            except Exception as e:
                return f"[ERROR KONEKSI DEEPSEEK API]: {e}"

        # 2. Jika tidak ada API Key, coba fallback ke Ollama lokal (deepseek-r1:8b)
        try:
            import ollama

            local_model = "deepseek-r1:8b" if "r1" in self.model_name else "deepseek-r1:8b"
            client = ollama.Client(host="http://localhost:11434")
            response = client.chat(
                model=local_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.1},
            )
            return response["message"]["content"]
        except Exception:
            return (
                "[DEEPSEEK_API_KEY TIDAK DITEMUKAN]: Masukkan API Key DeepSeek Anda ke file .env "
                "atau kolom sidebar (DEEPSEEK_API_KEY=sk-...). Atau jalankan Ollama lokal: 'ollama run deepseek-r1:8b'."
            )


def get_generator(model_type: str = "gemini", **kwargs) -> BaseLegalGenerator:
    """
    [FACTORY FUNCTION]
    Fungsi pembuat instance generator berdasarkan nama model yang dipilih pengguna:
    'qwen', 'gemini', 'deepseek', atau 'deepseek-ollama'.
    """
    model_type = model_type.lower()
    if model_type in ["qwen", "l1", "ollama", "qwen2.5:7b"]:
        return QwenOllamaGenerator(**kwargs)
    elif model_type in ["deepseek-ollama", "deepseek-local", "deepseek-r1:8b"]:
        return DeepSeekOllamaGenerator(**kwargs)
    elif model_type in ["gemini", "l2"]:
        return GeminiGenerator(**kwargs)
    elif model_type in ["deepseek", "l3", "deepseek-v3", "deepseek-r1"]:
        return DeepSeekGenerator(**kwargs)
    else:
        raise ValueError(f"Tipe model tidak dikenal: '{model_type}'. Gunakan 'gemini', 'qwen', atau 'deepseek'.")
