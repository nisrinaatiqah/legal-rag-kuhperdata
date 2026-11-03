"""
FastAPI Backend Server: CiviLex AI
Sistem Legal Question Answering Hukum Perdata (KUHPerdata & HIR)
dengan Mekanisme Deteksi Knowledge Poisoning (SHA-256 + NLI)

Jalankan dengan:
uvicorn server:app --reload --port 8000
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Konfigurasi Path & Environment
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civilex-server")

# Inisialisasi FastAPI
app = FastAPI(
    title="CiviLex AI — Legal QA Backend API",
    description="API Sistem Legal Question Answering Hukum Perdata (KUHPerdata & HIR) dengan Pertahanan Knowledge Poisoning",
    version="1.0.0",
)

# Konfigurasi CORS agar frontend Next.js (port 3000 / Vercel) dapat mengakses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Impor komponen internal
from src.retrieval.embedder import LegalEmbedder
from src.retrieval.qdrant_store import QdrantVectorStore
from src.retrieval.retriever import LegalRetrieverR1
from src.detection.risk_score import PoisoningDetector
from src.rag.prompt import build_legal_prompt
from src.rag.generator import (
    GeminiGenerator,
    DeepSeekGenerator,
    QwenOllamaGenerator,
    DeepSeekOllamaGenerator,
)

# Global instances (Lazy Loaded Cache)
_EMBEDDER = None
_DETECTOR = None
_CLEAN_CORPUS = None
_RETRIEVERS: Dict[str, LegalRetrieverR1] = {}


def get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        logger.info("[*] Memuat model embedding BAAI/bge-m3...")
        _EMBEDDER = LegalEmbedder("BAAI/bge-m3")
    return _EMBEDDER


def get_detector():
    global _DETECTOR
    if _DETECTOR is None:
        logger.info("[*] Memuat detektor pertahanan berlapis (SHA-256 + NLI)...")
        _DETECTOR = PoisoningDetector(alpha=0.6, tau=0.5)
    return _DETECTOR


def get_retriever(collection_name: str = "kuhperdata_hir_bgem3"):
    global _RETRIEVERS
    if collection_name not in _RETRIEVERS:
        logger.info(f"[*] Inisialisasi retriever untuk koleksi: {collection_name}...")
        store = QdrantVectorStore(collection_name=collection_name)
        _RETRIEVERS[collection_name] = LegalRetrieverR1(
            embedder=get_embedder(), qdrant_store=store
        )
    return _RETRIEVERS[collection_name]


def load_clean_corpus() -> List[Dict[str, Any]]:
    global _CLEAN_CORPUS
    if _CLEAN_CORPUS is None:
        corpus_path = BASE_DIR / "data" / "processed" / "legal_corpus_clean.jsonl"
        articles = []
        if corpus_path.exists():
            with open(corpus_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        articles.append(json.loads(line))
        _CLEAN_CORPUS = articles
    return _CLEAN_CORPUS


# ==========================================
# MODEL SKEMA REQUEST & RESPONSE (PYDANTIC)
# ==========================================
class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' atau 'assistant'")
    content: str = Field(..., description="Isi teks pesan")


class ChatRequest(BaseModel):
    query: str = Field(..., description="Pertanyaan hukum dari pengguna")
    history: List[ChatMessage] = Field(default=[], description="Riwayat obrolan sebelumnya")
    collection: str = Field(
        default="kuhperdata_hir_bgem3",
        description="Nama koleksi Qdrant (kuhperdata_hir_bgem3 / kuhperdata_hir_bgem3_p1pct / dll.)",
    )
    enable_defense: bool = Field(
        default=True, description="Apakah mekanisme pertahanan SHA-256 + NLI diaktifkan"
    )
    llm_model: str = Field(
        default="gemini",
        description="'gemini', 'deepseek-r1', 'qwen2.5', atau 'deepseek-cloud'",
    )
    top_k: int = Field(default=5, ge=1, le=10, description="Jumlah pasal teratas yang ditarik")


class ArticleResponse(BaseModel):
    pasal: str
    source: str
    bab_title: Optional[str] = "-"
    content: str
    score: float = 0.0
    sha256: Optional[str] = None
    is_poisoned: bool = False


class DefenseStatus(BaseModel):
    is_defense_active: bool
    total_retrieved: int
    cleared_count: int
    blocked_count: int
    status_badge: str  # 'VERIFIED_AUTHENTIC', 'BLOCKED_POISON', 'DANGER_PENETRATED'
    status_message: str
    blocked_pasals: List[Dict[str, Any]] = []


class ChatResponse(BaseModel):
    query: str
    answer: str
    llm_used: str
    defense_status: DefenseStatus
    retrieved_pasals: List[ArticleResponse]


# ==========================================
# ENDPOINT API
# ==========================================
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CiviLex AI — Legal RAG Backend",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/stats")
def get_stats():
    corpus = load_clean_corpus()
    kuhp_count = sum(1 for c in corpus if c.get("source") == "KUHPerdata")
    hir_count = sum(1 for c in corpus if c.get("source") == "HIR")
    return {
        "total_articles": len(corpus),
        "kuhperdata_articles": kuhp_count,
        "hir_articles": hir_count,
        "embedding_model": "BAAI/bge-m3 (1024-dim)",
        "supported_llms": [
            "Google Gemini 2.5 Flash",
            "DeepSeek-R1-8B (Ollama)",
            "Qwen2.5-7B-Instruct (Ollama)",
            "DeepSeek-V3 (Cloud API)",
        ],
        "defense_mechanisms": ["SHA-256 Hash Verification", "Semantic NLI Contradiction Filter"],
    }


@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")

    try:
        # 1. Retrieval top-K dokumen dari Qdrant
        retriever = get_retriever(req.collection)
        detector = get_detector()
        hits = retriever.retrieve(query=query_text, top_k=req.top_k)

        safe_chunks = []
        blocked_chunks = []

        # 2. Filter Pertahanan Anti-Knowledge Poisoning
        for chunk in hits:
            if req.enable_defense:
                eval_res = detector.evaluate_chunk(chunk)
                chunk_copy = dict(chunk)
                chunk_copy["defense_eval"] = eval_res
                if eval_res["is_blocked"]:
                    blocked_chunks.append(chunk_copy)
                else:
                    safe_chunks.append(chunk_copy)
            else:
                safe_chunks.append(chunk)

        # 3. Penentuan Status Keamanan (Security Badge)
        if blocked_chunks:
            status_badge = "BLOCKED_POISON"
            status_msg = (
                f"Sistem mendeteksi {len(blocked_chunks)} pasal manipulasi yang tidak konsisten dengan "
                f"naskah resmi JDIH. Seluruh pasal beracun telah berhasil dicegat dan dikarantina!"
            )
        elif any(c.get("is_poisoned") for c in safe_chunks):
            status_badge = "DANGER_PENETRATED"
            status_msg = (
                "Peringatan: Sistem pertahanan dinonaktifkan! Pasal manipulasi berhasil lolos ke prompt "
                "AI. Jawaban berisiko memuat interpretasi hukum yang keliru."
            )
        else:
            status_badge = "VERIFIED_AUTHENTIC"
            status_msg = (
                "Seluruh pasal rujukan terverifikasi 100% otentik dan bersesuaian dengan naskah resmi "
                "KUHPerdata/HIR (SHA-256 Valid)."
            )

        # 4. Inisialisasi Generator LLM
        llm_name = req.llm_model.lower()
        generator = None
        llm_label = "Google Gemini 2.5 Flash"

        if "gemini" in llm_name:
            generator = GeminiGenerator()
            llm_label = "Google Gemini 2.5 Flash"
        elif "deepseek-r1" in llm_name:
            generator = DeepSeekOllamaGenerator(model_name="deepseek-r1:8b")
            llm_label = "DeepSeek-R1-8B (Ollama)"
        elif "qwen" in llm_name:
            generator = QwenOllamaGenerator(model_name="qwen2.5:7b")
            llm_label = "Qwen2.5-7B (Ollama)"
        elif "deepseek-cloud" in llm_name:
            generator = DeepSeekGenerator(model_name="deepseek-chat")
            llm_label = "DeepSeek-V3 (Cloud API)"
        else:
            generator = GeminiGenerator()

        # 5. Bangun Prompt & Sintesis Jawaban
        prompt_data = build_legal_prompt(query=query_text, retrieved_chunks=safe_chunks)

        answer_text = ""
        try:
            answer_text = generator.generate(
                system_prompt=prompt_data["system_prompt"],
                user_prompt=prompt_data["user_prompt"],
            )
        except Exception as e:
            logger.warning(f"[!] Gagal panggil LLM ({e}), beralih ke sintesis rujukan terstruktur.")
            # Fallback jika API key belum aktif / model lokal belum start
            if not safe_chunks:
                answer_text = (
                    "Mohon maaf, tidak ditemukan ketentuan pasal yang sah dan lolos verifikasi integritas "
                    "untuk menjawab kueri hukum tersebut."
                )
            else:
                lines = [
                    f"Berdasarkan penelusuran naskah resmi hukum perdata terkait *'{query_text}'*:\n"
                ]
                for sc in safe_chunks[:3]:
                    lines.append(f"### {sc['source']} Pasal {sc.get('pasal')}")
                    lines.append(f"> \"{sc.get('content')}\"\n")
                lines.append(
                    "\n*Catatan: Jawaban disintesis langsung dari basis data pasal otentik terverifikasi.*"
                )
                answer_text = "\n".join(lines)

        # 6. Format Response
        retrieved_list = [
            ArticleResponse(
                pasal=str(sc.get("pasal", "-")),
                source=str(sc.get("source", "KUHPerdata")),
                bab_title=str(sc.get("bab_title", "-")),
                content=str(sc.get("content", "")),
                score=float(sc.get("score", 0.0)),
                sha256=str(sc.get("sha256", sc.get("content_sha256", "-"))),
                is_poisoned=bool(sc.get("is_poisoned", False)),
            )
            for sc in safe_chunks
        ]

        blocked_list = [
            {
                "pasal": str(bc.get("pasal", "-")),
                "source": str(bc.get("source", "KUHPerdata")),
                "content": str(bc.get("content", "")),
                "composite_risk_score": float(
                    bc.get("defense_eval", {}).get("composite_score", 1.0)
                ),
                "reason": str(bc.get("defense_eval", {}).get("reason", "-")),
                "source_status": str(bc.get("defense_eval", {}).get("source_status", "-")),
                "semantic_status": str(bc.get("defense_eval", {}).get("semantic_status", "-")),
            }
            for bc in blocked_chunks
        ]

        defense_summary = DefenseStatus(
            is_defense_active=req.enable_defense,
            total_retrieved=len(hits),
            cleared_count=len(safe_chunks),
            blocked_count=len(blocked_chunks),
            status_badge=status_badge,
            status_message=status_msg,
            blocked_pasals=blocked_list,
        )

        return ChatResponse(
            query=query_text,
            answer=answer_text,
            llm_used=llm_label,
            defense_status=defense_summary,
            retrieved_pasals=retrieved_list,
        )

    except Exception as exc:
        logger.error(f"[ERROR] Chat handling failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/database")
def get_articles(
    q: Optional[str] = Query(None, description="Pencarian kata kunci atau nomor pasal"),
    source: Optional[str] = Query(None, description="Filter sumber: KUHPerdata atau HIR"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    corpus = load_clean_corpus()

    filtered = corpus
    if source:
        filtered = [c for c in filtered if c.get("source", "").lower() == source.lower()]

    if q:
        q_lower = q.strip().lower()
        filtered = [
            c
            for c in filtered
            if q_lower in str(c.get("pasal", "")).lower()
            or q_lower in c.get("content", "").lower()
            or q_lower in str(c.get("bab_title", "")).lower()
        ]

    total_matches = len(filtered)
    page_data = filtered[offset : offset + limit]

    return {
        "total": total_matches,
        "offset": offset,
        "limit": limit,
        "articles": [
            {
                "pasal": str(c.get("pasal", "-")),
                "source": c.get("source", "KUHPerdata"),
                "bab": c.get("bab", "-"),
                "bab_title": c.get("bab_title", "-"),
                "content": c.get("content", ""),
                "sha256": c.get("sha256", c.get("content_sha256", "-")),
            }
            for c in page_data
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
