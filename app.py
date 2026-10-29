"""
Aplikasi Web: Sistem Legal Question Answering Hukum Perdata (KUHPerdata & HIR)
Berbasis Retrieval-Augmented Generation dengan Deteksi Knowledge Poisoning.

Peneliti  : Nisrina Atiqah Dwiputri Ridzki (NRP 5027231075)
Departemen: Teknologi Informasi, Fakultas Teknologi Elektro dan Informatika Cerdas (FTEIC)
Institusi : Institut Teknologi Sepuluh Nopember (ITS) Surabaya
Dosen Pembimbing: Hafara Firdausi, S.Kom., M.Kom. & Annisaa Sri Indrawanti, S.Kom., M.Kom.
"""

import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# [PROSES 1: KONFIGURASI PATH & ENVIRONMENT]
# Menambahkan folder root legal-rag-perdata ke path Python dan memuat API keys dari file .env
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

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


# ==========================================
# 2. KONFIGURASI HALAMAN & TEMA VISUAL (CSS)
# ==========================================
st.set_page_config(
    page_title="Sistem Legal QA KUHPerdata - ITS",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Tipografi dan Elemen Judul Utama Berstandar Akademis ITS */
    .app-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F2942;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .app-subheader {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    .app-affiliation {
        font-size: 0.82rem;
        color: #64748B;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
    }

    /* Kartu Indikator Status Eksperimen */
    .status-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.88rem;
    }
    .status-label {
        color: #64748B;
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .status-value {
        color: #0F172A;
        font-weight: 600;
    }

    /* Kartu Tampilan Dokumen Pasal yang Lolos */
    .doc-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0284C7;
        padding: 14px 16px;
        margin-bottom: 12px;
        border-radius: 4px;
        font-size: 0.92rem;
        line-height: 1.55;
    }
    /* Kartu Tampilan Dokumen Pasal yang Dieliminasi (Diblokir) */
    .doc-card-blocked {
        background-color: #FFFDFD;
        border: 1px solid #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 14px 16px;
        margin-bottom: 12px;
        border-radius: 4px;
        font-size: 0.92rem;
        line-height: 1.55;
    }
    .doc-meta {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed #E2E8F0;
    }

    /* Tag Status Dokumen */
    .tag-clean {
        display: inline-block;
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #BBF7D0;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-poison {
        display: inline-block;
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-blocked {
        display: inline-block;
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 3. FUNGSI CACHE INISIALISASI KOMPONEN SISTEM
# ==========================================
@st.cache_resource(show_spinner=False)
def get_shared_embedder():
    """[CACHE MODEL] Memuat model embedding BAAI/bge-m3 sekali ke memori RAM/VRAM agar tidak reload berulang."""
    return LegalEmbedder(model_name="BAAI/bge-m3")


@st.cache_resource(show_spinner=False)
def get_poison_detector():
    """[CACHE PERTAHANAN] Memuat detektor pertahanan berlapis (SHA-256 + NLI) dengan bobot alpha=0.6, tau=0.5."""
    return PoisoningDetector(alpha=0.6, tau=0.5)


@st.cache_resource(show_spinner=False)
def get_retriever(collection_name: str):
    """[CACHE RETRIEVER] Menyiapkan koneksi retriever ke koleksi target pada Qdrant Cloud."""
    embedder = get_shared_embedder()
    store = QdrantVectorStore(collection_name=collection_name)
    return LegalRetrieverR1(embedder=embedder, qdrant_store=store)


# ==========================================
# 4. SIDEBAR KONTROL & PENGATURAN EKSPERIMEN
# ==========================================
with st.sidebar:
    st.markdown("### Pengaturan Sistem")
    st.caption("Konfigurasi Parameter Basis Data dan Model")
    st.markdown("---")

    # 1. Pemilihan Koleksi Korpus (Uji Bersih vs Uji Serangan)
    st.markdown("**1. Basis Data Pengetahuan (Qdrant Cloud)**")
    corpus_choice = st.radio(
        "Koleksi Data:",
        options=[
            "Korpus Otentik (KUHPerdata & HIR)",
            "Korpus Uji Serangan 1% (Injeksi Semantik)",
            "Korpus Uji Serangan 5% (Injeksi Semantik)",
            "Korpus Uji Serangan 10% (Injeksi Semantik)",
        ],
        index=0,
        label_visibility="collapsed",
    )

    if "Otentik" in corpus_choice:
        active_collection = "kuhperdata_hir_bgem3"
        corpus_status_desc = "Korpus Otentik Resmi"
        is_corpus_poisoned = False
    elif "1%" in corpus_choice:
        active_collection = "kuhperdata_hir_bgem3_p1pct"
        corpus_status_desc = "Korpus Terinjeksi 1%"
        is_corpus_poisoned = True
    elif "5%" in corpus_choice:
        active_collection = "kuhperdata_hir_bgem3_p5pct"
        corpus_status_desc = "Korpus Terinjeksi 5%"
        is_corpus_poisoned = True
    else:
        active_collection = "kuhperdata_hir_bgem3_p10pct"
        corpus_status_desc = "Korpus Terinjeksi 10%"
        is_corpus_poisoned = True

    st.markdown("---")

    # 2. Toggle Pengaktifan Filter Pertahanan Anti-Knowledge Poisoning
    st.markdown("**2. Verifikasi Integritas Dokumen**")
    enable_defense = st.toggle(
        "Aktifkan Filter Pertahanan (SHA-256 + NLI)",
        value=True,
    )
    if enable_defense:
        st.caption("Parameter filter: α = 0.60 | τ = 0.50 (Ambang batas risiko)")
    else:
        st.caption("Perhatian: Dokumen hasil penelusuran diteruskan tanpa verifikasi.")

    st.markdown("---")

    # 3. Pemilihan Model LLM Generator
    st.markdown("**3. Model Bahasa Generator (LLM)**")
    llm_choice = st.selectbox(
        "Pilih Model Generator:",
        options=[
            "Qwen2.5-7B (Lokal - Ollama)",
            "DeepSeek-R1 (Lokal - Ollama)",
            "DeepSeek (Cloud API)",
            "Google Gemini 2.5 Flash (Cloud API)",
        ],
        index=0,
        label_visibility="collapsed",
    )

    top_k = st.slider("Jumlah Segmen Relevan (Top-K):", min_value=1, max_value=8, value=5)

    deepseek_key_input = ""
    gemini_key_input = ""

    # Input API Key jika menggunakan opsi Cloud API
    if "Cloud API" in llm_choice:
        if "DeepSeek" in llm_choice:
            deepseek_key_input = st.text_input(
                "DeepSeek API Key:",
                type="password",
                value=os.getenv("DEEPSEEK_API_KEY", ""),
            )
            st.caption("Catatan: Memerlukan saldo aktif di platform.deepseek.com. Jika saldo $0.00, gunakan opsi DeepSeek-R1 (Lokal - Ollama).")
        elif "Gemini" in llm_choice:
            gemini_key_input = st.text_input(
                "Gemini API Key:",
                type="password",
                value=os.getenv("GEMINI_API_KEY", ""),
            )
            st.caption("Menggunakan kuota gratis Google AI Studio.")
    else:
        st.caption("Menjalankan model lokal via Ollama di `http://localhost:11434` (100% offline & gratis).")

    st.markdown("---")
    st.caption("Backend Vektor: Qdrant Cloud (AWS London)")
    st.caption("Model Embedding: BAAI/bge-m3 (Dimensi 1024)")


# ==========================================
# 5. AREA UTAMA: HEADER & PAPAN INDIKATOR STATUS
# ==========================================
st.markdown('<div class="app-header">Sistem Legal Question Answering Hukum Perdata</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subheader">Pengujian Retrieval-Augmented Generation pada KUHPerdata dan HIR dengan Deteksi Knowledge Poisoning</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="app-affiliation">Departemen Teknologi Informasi, Fakultas Teknologi Elektro dan Informatika Cerdas, Institut Teknologi Sepuluh Nopember (ITS)<br>'
    'Peneliti: Nisrina Atiqah Dwiputri Ridzki | NRP: 5027231075</div>',
    unsafe_allow_html=True,
)

# Menampilkan 3 kartu indikator status eksperimen
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">Kondisi Basis Data</div>
            <div class="status-value">{'Terinjeksi Serangan' if is_corpus_poisoned else 'Otentik (Bebas Manipulasi)'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">Filter Pertahanan</div>
            <div class="status-value">{'Aktif (SHA-256 + NLI)' if enable_defense else 'Nonaktif (Tanpa Filter)'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">Model Generator Terpilih</div>
            <div class="status-value">{llm_choice.split()[0]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# Tombol Cepat Kueri Benchmark Kasus Nyata
st.markdown("**Contoh Kueri Pengujian Standar:**")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

preset_query = ""
if q_col1.button("Syarat Sah Perjanjian (Ps. 1320)", use_container_width=True):
    preset_query = "Apa saja syarat sahnya suatu perjanjian menurut hukum perdata?"

if q_col2.button("Ganti Rugi Wanprestasi (Ps. 1243)", use_container_width=True):
    preset_query = "Kapan suatu kewajiban ganti rugi akibat wanprestasi mulai berlaku bagi debitur?"

if q_col3.button("Kedaluwarsa Tuntutan (Ps. 1967)", use_container_width=True):
    preset_query = "Berapa lama batas waktu kedaluwarsa untuk menuntut suatu hak menurut KUHPerdata?"

if q_col4.button("Kecakapan Dewasa (Ps. 330)", use_container_width=True):
    preset_query = "Kapan seseorang dianggap telah dewasa menurut ketentuan KUHPerdata?"

# Kotak Input Pertanyaan Hukum Bebas
query_input = st.text_input(
    "Pertanyaan Kasus Hukum Perdata:",
    value=preset_query,
    placeholder="Contoh: Apa akibat hukum jika perjanjian dibuat atas dasar paksaan atau kekhilafan?",
)

btn_process = st.button("Proses Analisis Hukum", type="primary")


# ==========================================
# 6. EKSEKUSI PIPELINE: PENELUSURAN & PERTAHANAN
# ==========================================
if btn_process and query_input.strip():
    with st.spinner("Melakukan penelusuran dokumen di basis data vektor Qdrant..."):
        # 1. Ambil instance retriever dan detektor
        retriever = get_retriever(active_collection)
        detector = get_poison_detector()

        # 2. Retrieval top-K kandidat pasal
        hits = retriever.retrieve(query=query_input.strip(), top_k=top_k)

        safe_chunks = []
        blocked_chunks = []

        # 3. Evaluasi deteksi racun (jika filter aktif)
        for chunk in hits:
            if enable_defense:
                eval_res = detector.evaluate_chunk(chunk)
                chunk_copy = dict(chunk)
                chunk_copy["defense_eval"] = eval_res
                if eval_res["is_blocked"]:
                    blocked_chunks.append(chunk_copy)
                else:
                    safe_chunks.append(chunk_copy)
            else:
                safe_chunks.append(chunk)

    st.markdown("---")
    st.markdown("### Hasil Analisis")

    # Tampilkan banner status verifikasi integritas kepada pengguna
    if blocked_chunks:
        st.warning(
            f"Verifikasi Integritas: Terdeteksi {len(blocked_chunks)} segmen dokumen yang tidak konsisten dengan basis data resmi. "
            f"Segmen tersebut berhasil dieliminasi oleh mekanisme pertahanan sehingga tidak disertakan dalam konteks model generator."
        )
    elif any(c.get("is_poisoned") for c in safe_chunks):
        st.error(
            "Peringatan Integritas: Sistem pertahanan dinonaktifkan. Segmen dokumen yang memuat manipulasi berhasil lolos ke dalam "
            "konteks prompt model bahasa. Jawaban di bawah berisiko memuat interpretasi hukum yang keliru."
        )
    else:
        st.success(
            "Verifikasi Integritas: Seluruh segmen dokumen yang ditelusuri terverifikasi otentik dan bersesuaian dengan naskah resmi KUHPerdata/HIR."
        )

    # 4. Inisialisasi Model Generator Sesuai Pilihan Pengguna
    generator = None
    if "Qwen2.5-7B" in llm_choice:
        generator = QwenOllamaGenerator(model_name="qwen2.5:7b")
    elif "DeepSeek-R1" in llm_choice:
        generator = DeepSeekOllamaGenerator(model_name="deepseek-r1:8b")
    elif "Google Gemini" in llm_choice:
        generator = GeminiGenerator(api_key=gemini_key_input.strip())
    elif "DeepSeek (Cloud API)" in llm_choice:
        generator = DeepSeekGenerator(api_key=deepseek_key_input.strip(), model_name="deepseek-chat")

    # Cek ketersediaan kredensial untuk eksekusi generasi
    can_generate = False
    if "Lokal" in llm_choice:
        can_generate = True
    elif "Gemini" in llm_choice and gemini_key_input.strip():
        can_generate = True
    elif "DeepSeek (Cloud API)" in llm_choice:
        can_generate = bool(deepseek_key_input.strip())

    # 5. Bangun Teks Prompt Lengkap
    prompt_bundle = build_legal_prompt(query=query_input.strip(), retrieved_chunks=safe_chunks)

    st.markdown("#### Jawaban Model Generator:")

    # 6. Panggil Generator untuk Menghasilkan Teks Analisis
    if generator and can_generate:
        with st.spinner(f"Memproses analisis hukum menggunakan {llm_choice.split()[0]}..."):
            answer_text = generator.generate(
                system_prompt=prompt_bundle["system_prompt"],
                user_prompt=prompt_bundle["user_prompt"],
            )
        st.markdown(answer_text)
    else:
        # Tampilan fallback sintesis pasal jika API Key tidak disetel
        st.info("Kunci API belum diisi. Menampilkan sintesis ketentuan pasal langsung dari dokumen rujukan:")
        if not safe_chunks:
            st.write("Tidak ada pasal yang lolos verifikasi integritas untuk menjawab pertanyaan ini.")
        else:
            for idx, sc in enumerate(safe_chunks[:3], 1):
                status_tag = '<span class="tag-poison">Terinjeksi Racun (Lolos)</span>' if sc.get("is_poisoned") else '<span class="tag-clean">Otentik</span>'
                st.markdown(
                    f"**{idx}. {sc['source']} Pasal {sc.get('pasal')}** {status_tag}",
                    unsafe_allow_html=True,
                )
                st.markdown(f"> *\"{sc['content']}\"*")

    # ==========================================
    # 7. PANEL TRANSPARANSI HASIL RETRIEVAL & PERTAHANAN
    # ==========================================
    st.write("")
    with st.expander(f"Transparansi Dokumen Hasil Penelusuran ({len(hits)} Segmen)", expanded=True):
        tab_safe, tab_blocked = st.tabs([
            f"Segmen Diterima ({len(safe_chunks)})",
            f"Segmen Dieliminasi ({len(blocked_chunks)})",
        ])

        # Tab Dokumen yang Lolos Verifikasi
        with tab_safe:
            if not safe_chunks:
                st.write("Tidak ada segmen dokumen yang diteruskan ke prompt.")
            for i, sc in enumerate(safe_chunks, 1):
                tag_html = '<span class="tag-poison">Terinjeksi Serangan</span>' if sc.get("is_poisoned") else '<span class="tag-clean">Otentik</span>'
                score_val = sc.get("score", 0.0)
                st.markdown(
                    f"""
                    <div class="doc-card">
                        <b>Peringkat #{i} &mdash; {sc['source']} Pasal {sc.get('pasal')}</b> {tag_html}<br>
                        <i>Bab/Bagian: {sc.get('bab_title', '-')}</i><br><br>
                        {sc['content']}
                        <div class="doc-meta">
                            Skor Kemiripan Kosinus: <b>{score_val:.4f}</b> &nbsp;|&nbsp; 
                            SHA-256: <code>{sc.get('sha256', '-')[:16]}...</code>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Tab Dokumen yang Berhasil Dieliminasi oleh Pertahanan
        with tab_blocked:
            if not blocked_chunks:
                st.write("Tidak ada segmen dokumen yang diblokir oleh sistem.")
            for j, bc in enumerate(blocked_chunks, 1):
                de = bc.get("defense_eval", {})
                st.markdown(
                    f"""
                    <div class="doc-card-blocked">
                        <b>[Dieliminasi #{j}] &mdash; {bc['source']} Pasal {bc.get('pasal')}</b> 
                        <span class="tag-blocked">Skor Risiko: {de.get('composite_score', 0):.2f} / 1.00</span><br>
                        <b>Keterangan Evaluasi:</b> {de.get('reason', '-')}<br>
                        <b>Pemeriksaan SHA-256:</b> {de.get('source_status')} (R_source = {de.get('r_source')})<br>
                        <b>Pemeriksaan Konsistensi NLI:</b> {de.get('semantic_status')} (R_semantic = {de.get('r_semantic')})<br><br>
                        <b>Isi Teks Manipulasi yang Ditolak:</b><br>
                        <i>"{bc['content']}"</i>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.markdown("---")
st.caption(
    "Naskah Pengujian Tugas Akhir S-1 | Departemen Teknologi Informasi &mdash; FTEIC ITS Surabaya | "
    "Sistem Legal Question Answering KUHPerdata & HIR Berbasis RAG dan Qdrant Cloud"
)
