"""
CiviLex AI — Hugging Face Spaces Runner (Gradio + FastAPI)
Menjalankan FastAPI backend (server.py) secara terpadu di dalam Hugging Face Space
lengkap dengan antarmuka status interaktif dan endpoint API untuk Vercel.
"""

import os
import sys
from pathlib import Path

# Pastikan direktori saat ini ada di sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

# Shim untuk kompatibilitas gradio 4.44 dengan versi terbaru huggingface_hub
try:
    import huggingface_hub
    if not hasattr(huggingface_hub, "HfFolder"):
        class HfFolder:
            @staticmethod
            def get_token():
                try:
                    return huggingface_hub.get_token()
                except Exception:
                    return os.environ.get("HF_TOKEN")
            @staticmethod
            def save_token(token):
                pass
            @staticmethod
            def delete_token():
                pass
        huggingface_hub.HfFolder = HfFolder
except Exception:
    pass

import gradio as gr
from server import app as fastapi_app

# Kompatibilitas dengan Hugging Face ZeroGPU
try:
    import spaces
    gpu_decorator = spaces.GPU
except Exception:
    def gpu_decorator(fn):
        return fn

@gpu_decorator
def check_health():
    return "🟢 Server CiviLex AI Aktif! Endpoint API siap melayani kueri hukum perdata (KUHPerdata & HIR)."

# Antarmuka monitoring elegan untuk kunjungan langsung via browser
with gr.Blocks(title="CiviLex AI — Legal RAG Backend") as demo:
    gr.Markdown(
        """
        # ⚖️ CiviLex AI — Backend API Server
        **Sistem Legal Question Answering Hukum Perdata (KUHPerdata & HIR) dengan Pertahanan Knowledge Poisoning**
        
        Server ini aktif melayani API untuk frontend resmi yang di-deploy di Vercel:
        [https://civilexai-kuhperdata.vercel.app](https://civilexai-kuhperdata.vercel.app)
        """
    )
    with gr.Row():
        btn = gr.Button("Cek Status Server", variant="primary")
        output = gr.Textbox(label="Status Server", value="🟢 Siap Menerima Permintaan")
    btn.click(fn=check_health, outputs=output)

    gr.Markdown("---")
    gr.Markdown("Documentation Swagger API tersedia di: `/docs`")

# Mount aplikasi FastAPI ke Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
