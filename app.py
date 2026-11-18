"""
CiviLex AI — Hugging Face Spaces Runner (FastAPI Backend Server)
Menjalankan FastAPI backend (server.py) di dalam Hugging Face Space
lengkap dengan antarmuka status elegan di root (/) dan endpoint API untuk Vercel.
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

# Kompatibilitas dengan Hugging Face ZeroGPU
try:
    import spaces
    @spaces.GPU
    def zero_gpu_keepalive():
        return True
except Exception:
    pass

from fastapi.responses import HTMLResponse
from server import app as fastapi_app

# Root dashboard elegan untuk kunjungan langsung via browser Hugging Face Spaces
@fastapi_app.get("/", response_class=HTMLResponse)
def index_dashboard():
    return """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CiviLex AI — Legal RAG Backend</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #FAF6EE;
            color: #241819;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }
        .card {
            background: #FFFFFF;
            border: 1px solid #E8DEC9;
            border-radius: 16px;
            padding: 36px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #E8F5E9;
            color: #2E7D32;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .dot {
            width: 8px;
            height: 8px;
            background: #2E7D32;
            border-radius: 50%;
            display: inline-block;
        }
        h1 {
            font-size: 24px;
            color: #75162D;
            margin: 0 0 8px;
        }
        p {
            color: #6B5559;
            line-height: 1.6;
            margin: 0 0 20px;
            font-size: 14px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
        }
        .metric {
            background: #FAF6EE;
            border: 1px solid #E8DEC9;
            border-radius: 10px;
            padding: 12px 16px;
        }
        .metric-title {
            font-size: 11px;
            color: #8C787C;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 14px;
            font-weight: 700;
            color: #241819;
            margin-top: 4px;
        }
        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .btn {
            display: block;
            text-align: center;
            padding: 12px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #75162D;
            color: #FAF6EE;
        }
        .btn-primary:hover {
            background: #5B1022;
        }
        .btn-secondary {
            background: #FAF6EE;
            color: #75162D;
            border: 1px solid #75162D;
        }
        .btn-secondary:hover {
            background: #E8DEC9;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">
            <span class="dot"></span>
            Server Backend Aktif (Online)
        </div>
        <h1>⚖️ CiviLex AI Backend API</h1>
        <p>Sistem Legal Question Answering Hukum Perdata (KUHPerdata &amp; HIR) dengan pertahanan Knowledge Poisoning berlapis (SHA-256 + NLI).</p>
        
        <div class="grid">
            <div class="metric">
                <div class="metric-title">Korpus Hukum</div>
                <div class="metric-value">2.276 Pasal Terindeks</div>
            </div>
            <div class="metric">
                <div class="metric-title">Vector Store</div>
                <div class="metric-value">Qdrant Cloud (BGE-M3)</div>
            </div>
            <div class="metric">
                <div class="metric-title">Model LLM</div>
                <div class="metric-value">Google Gemini (Active)</div>
            </div>
            <div class="metric">
                <div class="metric-title">Pertahanan</div>
                <div class="metric-value">SHA-256 + NLI Filter</div>
            </div>
        </div>

        <div class="btn-group">
            <a href="https://civilexai-kuhperdata.vercel.app/chat" target="_blank" class="btn btn-primary">
                Buka Aplikasi Web (Vercel) &rarr;
            </a>
            <a href="/docs" target="_blank" class="btn btn-secondary">
                Dokumentasi Swagger API (/docs)
            </a>
            <a href="/api/health" target="_blank" class="btn btn-secondary">
                Cek Status Health API (/api/health)
            </a>
        </div>
    </div>
</body>
</html>"""

# Ekspor objek app utama untuk uvicorn / Hugging Face runner
app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
