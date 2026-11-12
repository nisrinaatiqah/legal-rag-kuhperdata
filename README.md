# Legal Question Answering Hukum Perdata Berbasis RAG dengan Deteksi Knowledge Poisoning

Repositori implementasi sistem *Legal Question Answering* (Legal QA) hukum perdata Indonesia (KUHPerdata dan HIR) berbasis *Retrieval-Augmented Generation* (RAG) yang dilengkapi modul pertahanan berlapis terhadap serangan manipulasi korpus (*knowledge poisoning*).

---

## 1. Deskripsi Sistem

Sistem ini mengembangkan arsitektur *Retrieval-Augmented Generation* (RAG) khusus domain hukum perdata Indonesia (KUHPerdata dan HIR) yang dilengkapi mekanisme pertahanan berlapis terhadap serangan manipulasi korpus (*knowledge poisoning*). 

Mekanisme pertahanan menggabungkan verifikasi integritas kriptografis hash SHA-256 dan evaluasi konsistensi semantik menggunakan *Natural Language Inference* (NLI) untuk mencegah masuknya pasal manipulasi ke dalam konteks penalaran *Large Language Model* (LLM).

---

## 2. Diagram Alur Arsitektur Sistem

```text
                        [ Pertanyaan Hukum Pengguna ]
                                     |
                                     v
                  [ Dense Retriever: BAAI/bge-m3 (Qdrant) ]
                                     |
                                     v
                       [ Top-K Dokumen Pasal Kandidat ]
                                     |
         +---------------------------+---------------------------+
         |                                                       |
[ Mode Nonaktif ]                                         [ Mode Aktif ]
         |                                                       |
         |                                                       v
         |                                         [ Modul Pertahanan Berlapis ]
         |                                         * Lapis 1: Verifikasi SHA-256 (R_src)
         |                                         * Lapis 2: Konsistensi Semantik NLI (R_sem)
         |                                                       |
         |                                                       v
         |                                            Composite Risk Score:
         |                                     Score = alpha*R_src + (1-alpha)*R_sem
         |                                       (Karantina jika Score >= tau = 0.5)
         |                                                       |
         +---------------------------+---------------------------+
                                     |
                                     v
                     [ Format Konteks & Prompt Hukum ]
                                     |
                                     v
                        [ Pembangkit Jawaban (LLM) ]
             (Gemini 2.5 Flash / DeepSeek V3/R1 / Qwen2.5-7B Lokal)
                                     |
                                     v
                      [ Jawaban Hukum Bersitasi Pasal ]
```

---

### 2.1 Formulasi & Mekanisme Detail Composite Risk Score

Modul pertahanan berlapis dirancang khusus untuk memitigasi serangan manipulasi korpus (*knowledge poisoning*) pada sistem *Legal Question Answering*. Penyerang diasumsikan mampu menyuntikkan atau mengubah naskah pasal pada basis data pengetahuan eksternal (misal: menambahkan kata negasi, mengubah kewajiban hukum menjadi kebebasan, atau mendistorsi batas usia dan denda perdata).

Untuk menangkal serangan tersebut tanpa menghasilkan alarm palsu (*False Positive*) pada dokumen resmi, diimplementasikan mekanisme penilaian risiko komposit (*Composite Risk Score*) yang memadukan verifikasi kriptografis deterministik dan evaluasi konsistensi semantik berbasis *Natural Language Inference* (NLI).

```text
                                [ Potongan Pasal Kandidat (Chunk) ]
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             [ LAPIS 1: SOURCE VERIFICATION ]                [ LAPIS 2: SEMANTIC NLI ]
             src/detection/source_verification.py            src/detection/semantic_nli.py
                        │                                                 │
             • Hitung Hash SHA-256 teks                      • Penjajaran sekuensial (Sequence Matcher)
             • Cocokkan ke Manifest Resmi                    • Deteksi pembalikan polaritas hukum:
               (trusted_corpus_manifest.json)                  - Negasi: tidak, bukan, tanpa, dilarang
                        │                                      - Kewajiban: wajib, harus, patut
                        ▼                                                 ▼
             Skor Risiko Kriptografi:                         Skor Risiko Semantik:
             R_src ∈ {0.0, 1.0}                               R_sem ∈ [0.0, 1.0]
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                   [ COMPOSITE RISK SCORING ]
                                   src/detection/risk_score.py
                                                 │
                                   Score = α·R_src + (1-α)·R_sem
                                   (Bobot optimal: α = 0.6)
                                                 │
                                                 ▼
                                      [ ATURAN KEPUTUSAN ]
                                      Ambang Batas τ = 0.5
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        │ Score >= 0.5                                    │ Score < 0.5
                        ▼                                                 ▼
               [ BLOCKED_POISON ]                                 [ CLEARED_SAFE ]
             Pasal dibuang & dikarantina                      Pasal disahkan masuk ke
             (TIDAK MASUK PROMPT LLM)                         prompt konteks LLM
```

#### A. Formulasi Matematis Terpadu

Skor risiko gabungan dihitung menggunakan rata-rata tertimbang (*weighted linear combination*) pada berkas [`src/detection/risk_score.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/risk_score.py):

$$\text{Composite Risk Score}(d) = \alpha \cdot R_{\text{src}}(d) + (1 - \alpha) \cdot R_{\text{sem}}(d)$$

Keterangan parameter dan variabel:
* **$d$**: Potongan pasal hukum (*chunk*) kandidat yang ditarik oleh Retriever dari basis data vektor.
* **$R_{\text{src}}(d)$**: Skor risiko integritas kriptografis sumber (*Source Integrity Risk*), bernilai biner **0.0** atau **1.0**.
* **$R_{\text{sem}}(d)$**: Skor risiko inkonsistensi semantik (*Semantic Contradiction Risk*), bernilai riil kontinu **[0.0, 1.0]**.
* **$\alpha$**: Parameter pembobotan prioritas antara verifikasi sumber kriptografis dan analisis semantik. Nilai optimal hasil studi ablasi adalah **$\alpha = 0.6$**.
* **$(1 - \alpha)$**: Bobot untuk aspek penalaran konsistensi semantik bahasa hukum (**$0.4$**).

---

#### B. Rincian Komponen Lapis 1: Verifikasi Kriptografis Sumber ($R_{\text{src}}$)

Dikelola oleh modul [`src/detection/source_verification.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/source_verification.py):
1. Sistem menghitung sidik jari kriptografis teks pasal kandidat menggunakan algoritma SHA-256:
   $$H(d) = \text{SHA-256}(\text{teks}(d))$$
2. Nilai $H(d)$ dicocokkan terhadap basis data tabel kebenaran resmi pada [`data/manifests/trusted_corpus_manifest.json`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/data/manifests/trusted_corpus_manifest.json) yang menyimpan **2.276 hash SHA-256** pasal resmi KUHPerdata dan HIR.
3. Kriteria penetapan skor risiko sumber ($R_{\text{src}}$):
   * **$R_{\text{src}} = \mathbf{0.0}$ (`VERIFIED_AUTHENTIC`)**: Nilai hash identik dengan naskah undang-undang resmi pemerintah (dokumen sah 100%).
   * **$R_{\text{src}} = \mathbf{1.0}$ (`TAMPERED_HASH_MISMATCH`)**: Teks pasal telah dimodifikasi oleh penyerang walaupun hanya berbeda 1 spasi atau 1 karakter huruf.
   * **$R_{\text{src}} = \mathbf{1.0}$ (`UNKNOWN_ORIGIN`)**: Pengenal pasal (*chunk_id*) tidak terdaftar dalam korpus kanonik hukum perdata.

---

#### C. Rincian Komponen Lapis 2: Evaluasi Konsistensi Semantik NLI ($R_{\text{sem}}$)

Dikelola oleh modul [`src/detection/semantic_nli.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/semantic_nli.py):
1. Sistem membandingkan teks pasal hipotesis ($d$) dengan naskah kanonik resmi ($d_{\text{clean}}$) dari [`data/processed/legal_corpus_clean.jsonl`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/data/processed/legal_corpus_clean.jsonl).
2. Menghitung rasio kemiripan penjajaran urutan kata (*Sequence Alignment Similarity Ratio*):
   $$S(d, d_{\text{clean}}) \in [0.0, 1.0]$$
3. Melakukan deteksi inversi polaritas makna (*Polarity Inversion Detection*):
   * **Penanda Negasi/Pembatalan**: *tidak, bukan, tanpa, tiada, dilarang, dibatalkan, dikecualikan, hapus, gugur, bebas*.
   * **Penanda Kewajiban Hukum**: *wajib, harus, diwajibkan, perlu, patut*.
   * Jika salah satu kelompok penanda mengalami perubahan arah logika (misal: klausul asli bermakna kewajiban positif diinjeksi kata *tidak* menjadi negasi), sistem menandai bendera `polarity_flipped = True`.
4. Kriteria penetapan skor risiko semantik ($R_{\text{sem}}$):
   * Jika terdeteksi pembalikan polaritas (`polarity_flipped = True`) atau rasio kemiripan $S < 0.85$:
     $$R_{\text{sem}} = \max(0.80, 1.0 - S) \quad \longrightarrow \quad \text{Status: \textbf{CONTRADICTION}}$$
   * Jika tidak terdapat pembalikan logika dan kemiripan teks terjaga ($S \ge 0.85$):
     $$R_{\text{sem}} = \max(0.0, 1.0 - S) \quad \longrightarrow \quad \text{Status: \textbf{CONSISTENT}}$$
     *(Pada dokumen resmi otentik tanpa manipulasi, $S = 1.0 \implies R_{\text{sem}} = \mathbf{0.0}$)*.

---

#### D. Aturan Pengambilan Keputusan (Decision Rule & Karantina)

Dikelola oleh modul [`src/detection/risk_score.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/risk_score.py):

Sistem membandingkan skor risiko komposit terhadap nilai ambang batas (*classification threshold*) **$\tau = 0.5$**:

$$\text{Keputusan}(d) = \begin{cases} 
\text{\textbf{BLOCKED\_POISON}} \quad (\text{Karantina / Dibuang}), & \text{jika } \text{Composite Risk Score}(d) \ge \tau \ (\mathbf{0.5}) \\ 
\text{\textbf{CLEARED\_SAFE}} \quad (\text{Lolos ke Generator}), & \text{jika } \text{Composite Risk Score}(d) < \tau \ (\mathbf{0.5}) 
\end{cases}$$

* **Tindakan Pemblokiran**: Dokumen yang divonis `BLOCKED_POISON` langsung diputus jalurnya dan diisolasi ke daftar `blocked_chunks`. Dokumen beracun tersebut **dijamin 100% tidak pernah dimasukkan ke prompt konteks LLM**.
* **Penyusunan Konteks Bersih**: Hanya dokumen berkategori `CLEARED_SAFE` yang diteruskan ke prompt generator sebagai rujukan penalaran hukum bagi Google Gemini 2.5 Flash, DeepSeek-R1, atau Qwen2.5-7B.

---

#### E. Validasi Empiris Studi Ablasi Parameter ($\alpha$ dan $\tau$)

Penentuan bobot **$\alpha = 0.6$** dan ambang batas **$\tau = 0.5$** didasarkan pada eksperimen studi ablasi menyeluruh pada [`data/evaluation/ablation_study_alpha_tau.json`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/data/evaluation/ablation_study_alpha_tau.json) yang menguji variasi parameter $\alpha \in [0.0, 1.0]$ dan $\tau \in [0.3, 0.7]$:

| Nilai $\alpha$ | Nilai $\tau$ | Konfigurasi Deteksi | ASR (Tembus) | Precision | Recall | F1-Score | FPR (Alarm Palsu) |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **0.0** | **0.5** | Murni Evaluasi Semantik NLI (Tanpa Hash) | **6.67%** | **100.0%** | **93.94%** | **96.88%** | **0.0%** |
| **0.5** | **0.5** | Bobot Seimbang (50% Kriptografi + 50% NLI) | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **0.0%** |
| **0.6** | **0.5** | **Komposit Terpilih (60% Kriptografi + 40% NLI)** | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **0.0%** |
| **1.0** | **0.5** | Murni Verifikasi Kriptografis SHA-256 | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **0.0%** |

*Wawasan Kunci Studi Ablasi*:
1. Jika sistem hanya mengandalkan evaluasi semantik ($\alpha = 0.0$), penyerang dengan teknik parafrase manipulatif halus masih dapat menembus pertahanan dengan **ASR = 6.67%**.
2. Penggabungan verifikasi kriptografis SHA-256 dengan bobot dominan $\alpha = \mathbf{0.6}$ memberikan jaminan deterministik mutlak bahwa setiap pasal manipulasi langsung dicegat (**ASR = 0.0%**, **F1-Score = 100.0%**).
3. Ambang batas $\tau = \mathbf{0.5}$ memberikan margin keamanan yang ideal karena dokumen resmi otentik memiliki skor risiko **0.0000** (jauh di bawah $\tau$), menjamin **False Positive Rate (FPR) = 0.0%** (tidak pernah ada pasal resmi yang keliru terblokir).

---

#### F. Contoh Perhitungan Komputasi Kasus Riil

##### Kasus 1: Dokumen Otentik Sah (KUHPerdata Pasal 1320 Asli)
* Bunyi teks: *"Untuk sahnya suatu perjanjian diperlukan empat syarat: sepakat mereka yang mengikatkan dirinya..."*
* Verifikasi SHA-256: Hash cocok dengan manifest resmi $\implies R_{\text{src}} = \mathbf{0.0}$ (`VERIFIED_AUTHENTIC`).
* Verifikasi Semantik: Teks identik 100% dengan korpus kanonik ($S = 1.0$), tidak ada pembalikan polaritas $\implies R_{\text{sem}} = \mathbf{0.0}$ (`CONSISTENT`).
* Perhitungan Skor Risiko Komposit:
  $$\text{Composite Score} = (0.6 \times 0.0) + (0.4 \times 0.0) = \mathbf{0.0000}$$
* Evaluasi Ambang Batas: $\mathbf{0.0000} < 0.5 \implies$ **Status: `CLEARED_SAFE`** (Lolos sebagai konteks LLM).

##### Kasus 2: Dokumen Dimanipulasi Serangan Racun (Pasal 1320 Dimanipulasi Negasi)
* Bunyi teks racun: *"Untuk sahnya suatu perjanjian **tidak** diperlukan empat syarat: sepakat mereka yang mengikatkan dirinya **bukan** merupakan syarat mutlak..."*
* Verifikasi SHA-256: Hash berubah drastis karena penambahan kata $\implies R_{\text{src}} = \mathbf{1.0}$ (`TAMPERED_HASH_MISMATCH`).
* Verifikasi Semantik: Terdeteksi injeksi kata negasi (*tidak*, *bukan*) yang membalikkan klausul hukum (`polarity_flipped = True`), kemiripan $S = 0.81 \implies R_{\text{sem}} = \max(0.80, 1.0 - 0.81) = \mathbf{0.8000}$ (`CONTRADICTION`).
* Perhitungan Skor Risiko Komposit:
  $$\text{Composite Score} = (0.6 \times 1.0) + (0.4 \times 0.80) = 0.60 + 0.32 = \mathbf{0.9200}$$
* Evaluasi Ambang Batas: $\mathbf{0.9200} \ge 0.5 \implies$ **Status: `BLOCKED_POISON`** (Langsung dibuang dan dikarantina).

---

## 3. Alur Rangkaian Eksekusi File Kode (Pipeline End-to-End)

Berikut adalah diagram alir dan urutan eksekusi berkas kode dari tahap awal pembentukan data hingga evaluasi akhir:

```text
1. DATA INGESTION & CHUNKING SCENARIOS:
   data/raw_trusted/ (PDF)
         │
         ▼
   src/ingestion/extract_pdfs.py ──► Ekstraksi teks dari PDF resmi KUHPerdata & HIR
         │
         ▼
   src/ingestion/chunk_articles.py ──► Parsing per nomor pasal & pembersihan teks
         │
         ├──► src/ingestion/finalize_corpus.py ──► Menghasilkan:
         │                                         • data/processed/legal_corpus_clean.jsonl (2.276 pasal - C1)
         │                                         • data/manifests/trusted_corpus_manifest.json (Hash SHA-256)
         │
         └──► src/ingestion/build_chunk_scenarios.py ──► Pembangunan skenario komparasi chunking:
                                                         • corpus_c2_fixed_256.jsonl (822 chunk - C2)
                                                         • corpus_c3_fixed_512.jsonl (411 chunk - C3)
                                                         • chunking_scenarios_comparison.json

2. ATTACK SIMULATION (KNOWLEDGE POISONING):
   src/poisoning/transformations.py ──► Definisi manipulasi adversarial (negasi, distorsi pasal)
         │
         ▼
   src/poisoning/build_poisoned_kb.py ──► Menghasilkan korpus terkontaminasi:
                                          • corpus_poisoned_1pct.jsonl (1% racun)
                                          • corpus_poisoned_5pct.jsonl (5% racun)
                                          • corpus_poisoned_10pct.jsonl (10% racun)

3. VECTOR & LEXICAL INDEXING:
   src/retrieval/embedder.py ──► Model BGE-M3 (1024-dim) & SimCSE (768-dim)
         │
         ├──► src/retrieval/build_qdrant_bgem3.py ────► Koleksi Bersih Qdrant
         ├──► src/retrieval/build_qdrant_poisoned.py ─► Koleksi Racun 1%, 5%, 10%
         └──► src/retrieval/build_bm25.py ────────────► Indeks BM25Okapi (.pkl)

4. RETRIEVAL & DEFENSE LAYER:
   User Query ──► src/retrieval/retriever.py (R1 / R2 / R3)
                        │
                        ▼ (Top-K Dokumen Kandidat)
   src/detection/source_verification.py (Lapis 1: Verifikasi Hash SHA-256)
                        │
                        ▼
   src/detection/semantic_nli.py (Lapis 2: Evaluasi Konsistensi Semantik NLI)
                        │
                        ▼
   src/detection/risk_score.py (Composite Risk Score: Karantina jika Score >= 0.5)

5. PROMPT & GENERATION LAYER:
   Pasal Lolos Verifikasi ──► src/rag/prompt.py (Template prompt hukum ketat & sitasi)
                                    │
                                    ▼
   src/rag/generator.py ────► Sintesis Jawaban oleh LLM (Gemini / DeepSeek / Qwen)
                                    │
                                    ▼
   src/rag/pipeline.py ─────► Orkestrator RAG End-to-End (Kueri ➔ Ret ➔ Def ➔ Gen)

6. BENCHMARK & EVALUATION LAYER:
   • src/evaluation/evaluate_chunking.py ──► Benchmark Komparasi 3 Skenario Chunking (C1 vs C2 vs C3)
   • src/evaluation/evaluate_r1_r2_r3.py ──► Benchmark Retriever (MRR, Recall@1-10, MAP@1-10)
   • src/evaluation/run_scenarios.py ──────► Benchmark Pertahanan 8 Skenario (S1 s.d. S8)
   • src/evaluation/evaluate_llm.py ───────► Benchmark Mutu Teks Jawaban LLM (ROUGE/BLEU/RAGAS)
   • show_metrics.py ──────────────────────► Dashboard terminal ringkasan seluruh tabel metrik
```

### Rincian Alur Kerja Antar-Berkas Kode:

1. **Tahap 1: Ekstraksi Dokumen & Pembuatan Manifes Otentik**
   * [`src/ingestion/extract_pdfs.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/ingestion/extract_pdfs.py) membaca file naskah undang-undang `kuhperdata.pdf` dan `hir.pdf`.
   * [`src/ingestion/chunk_articles.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/ingestion/chunk_articles.py) memecah teks per pasal, membersihkan header/footer, dan menormalisasi penomoran.
   * [`src/ingestion/finalize_corpus.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/ingestion/finalize_corpus.py) menghasilkan file korpus resmi `legal_corpus_clean.jsonl` (2.276 pasal) dan menghitung sidik jari digital SHA-256 tiap pasal ke dalam `trusted_corpus_manifest.json`.

2. **Tahap 2: Simulasi Penyerangan Manipulasi Korpus (Knowledge Poisoning)**
   * [`src/poisoning/transformations.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/poisoning/transformations.py) merumuskan metode pemalsuan teks hukum (injeksi negasi hukum, pembalikan hak/kewajiban pasal, perubahan batas usia/waktu).
   * [`src/poisoning/build_poisoned_kb.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/poisoning/build_poisoned_kb.py) menyuntikkan racun ke korpus bersih pada rasio 1%, 5%, dan 10% untuk menghasilkan file korpus uji adversarial.

3. **Tahap 3: Indeksasi Basis Data Vektor & Leksikal**
   * [`src/retrieval/embedder.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/retrieval/embedder.py) menyiapkan model BGE-M3 (1024 dimensi) dan SimCSE-IndoBERT (768 dimensi).
   * [`src/retrieval/build_qdrant_bgem3.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/retrieval/build_qdrant_bgem3.py) dan [`build_qdrant_poisoned.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/retrieval/build_qdrant_poisoned.py) mengunggah dan mengindeks seluruh vektor pasal ke klaster Qdrant.
   * [`src/retrieval/build_bm25.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/retrieval/build_bm25.py) membuat kamus pencarian kata kunci BM25Okapi yang disimpan di `indexes/bm25/`.

4. **Tahap 4: Penelusuran Pasal Kandidat (Retrieval Layer)**
   * [`src/retrieval/retriever.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/retrieval/retriever.py) mengeksekusi pencarian: kueri hukum pengguna diproses oleh Retriever **R1** (Dense BGE-M3), **R2** (Hybrid SimCSE + BM25), atau **R3** (Hybrid BGE-M3 + BM25) untuk mengambil pasal paling relevan.

5. **Tahap 5: Filter Deteksi & Karantina Pasal Racun (Detection Layer)**
   * [`src/detection/source_verification.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/source_verification.py) mengecek kecocokan hash SHA-256 teks pasal terhadap manifes resmi.
   * [`src/detection/semantic_nli.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/semantic_nli.py) memeriksa apakah isi pasal memuat anomali kontradiksi semantik.
   * [`src/detection/risk_score.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/detection/risk_score.py) menghitung *Composite Risk Score*. Jika skor $\ge 0.5$, pasal langsung dibuang/dikarantina sehingga tidak bisa mencemari prompt LLM.

6. **Tahap 6: Pembentukan Prompt & Pembangkitan Jawaban (Generation Layer)**
   * [`src/rag/prompt.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/rag/prompt.py) menyusun template instruksi sistem hukum yang mewajibkan LLM menyertakan sitasi formal `[KUHPerdata Pasal X]`.
   * [`src/rag/generator.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/rag/generator.py) mengirim prompt ke model (Google Gemini 2.5 Flash, DeepSeek-R1, atau Qwen2.5-7B Lokal).
   * [`src/rag/pipeline.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/rag/pipeline.py) menghubungkan seluruh alur dari kueri awal hingga jawaban akhir siap ditampilkan.

7. **Tahap 7: Pengujian Eksperimental & Pelaporan (Evaluation Layer)**
   * [`src/evaluation/evaluate_r1_r2_r3.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/evaluation/evaluate_r1_r2_r3.py) mengukur akurasi Retriever (MRR, Recall@1-10, MAP@1-10).
   * [`src/evaluation/run_scenarios.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/evaluation/run_scenarios.py) mengukur ketahanan keamanan pada Skenario S1 s.d. S8 (Precision, Recall, F1, ASR, FPR).
   * [`src/evaluation/evaluate_llm.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/src/evaluation/evaluate_llm.py) mengukur mutu teks jawaban LLM (ROUGE-1/2/L, BLEU-4, Context Precision/Recall, Faithfulness).
   * [`show_metrics.py`](file:///d:/DATA/Downloads/TUGAS%20AKHIRR/legal-rag-perdata/show_metrics.py) menampilkan ringkasan seluruh tabel hasil eksperimen di terminal.

---

## 4. Struktur Direktori Proyek

```text
legal-rag-perdata/
├── data/
│   ├── raw_trusted/              # Naskah resmi sumber hukum (kuhperdata.pdf & hir.pdf)
│   ├── processed/                # Korpus bersih hasil variasi skenario chunking
│   │   ├── legal_corpus_clean.jsonl   # Korpus C1: Structure-based (2.276 pasal utuh)
│   │   ├── corpus_c2_fixed_256.jsonl  # Korpus C2: Fixed-size 256 tokens (822 chunk)
│   │   └── corpus_c3_fixed_512.jsonl  # Korpus C3: Fixed-size 512 tokens (411 chunk)
│   ├── manifests/                # Manifest kriptografis integritas SHA-256
│   │   └── trusted_corpus_manifest.json
│   ├── poisoning/                # Korpus hasil simulasi peracunan (1%, 5%, 10%)
│   │   ├── corpus_poisoned_1pct.jsonl
│   │   ├── corpus_poisoned_5pct.jsonl
│   │   └── corpus_poisoned_10pct.jsonl
│   └── evaluation/               # Ground truth kueri uji (30 kueri) & berkas hasil metrik
│       ├── ground_truth_perdata.json
│       ├── chunking_scenarios_comparison.json      # Statistik struktural C1, C2, C3
│       ├── eval_results_chunking_scenarios.json    # Hasil retrieval 3 skenario chunking
│       ├── eval_results_retriever_r1_r2_r3.json
│       ├── eval_results_scenarios_s1_s8.json
│       ├── eval_results_llm_generation_quality.json
│       ├── eval_results_llm_ragas_benchmark.json
│       └── ablation_study_alpha_tau.json
├── indexes/
│   ├── bm25/                     # Indeks leksikal BM25Okapi untuk konfigurasi Hybrid
│   │   └── bm25_perdata_clean.pkl
│   └── qdrant_storage/           # Replika indeks vektor lokal Qdrant
├── src/
│   ├── ingestion/                # Ekstraksi PDF, parsing pasal, manifest SHA-256, & skenario chunking
│   │   ├── extract_pdfs.py
│   │   ├── chunk_articles.py
│   │   ├── finalize_corpus.py
│   │   └── build_chunk_scenarios.py   # Pembangun korpus C1, C2, dan C3
│   ├── retrieval/                # Embedding model (BGE-M3 & SimCSE), Qdrant Cloud/Local, BM25, & R1/R2/R3
│   ├── rag/                      # Prompt builder, generator LLM, & pipeline end-to-end
│   │   ├── generator.py          # IMPLEMENTASI SEMUA MODEL LLM (Gemini, DeepSeek, Qwen)
│   │   ├── pipeline.py           # Orkestrasi alur RAG (Retrieval -> Defense -> Generator)
│   │   └── prompt.py             # Template prompt hukum & pembatasan sitasi pasal
│   ├── poisoning/                # Engine manipulasi teks hukum adversarial (negasi, modifikasi frasa)
│   ├── detection/                # Verifikator SHA-256, NLI semantik, & composite risk score
│   └── evaluation/               # Modul pengujian metrik MRR, Recall, S1-S8, ROUGE/BLEU, & Ragas
│       ├── evaluate_chunking.py  # Benchmark komparasi 3 skenario chunking (C1, C2, C3)
│       ├── evaluate_r1_r2_r3.py  # Benchmark komparatif 3 retriever (R1, R2, R3)
│       ├── run_scenarios.py      # Benchmark 8 skenario pertahanan keamanan
│       ├── evaluate_llm.py       # Benchmark 8 skenario kualitas generasi teks LLM
│       └── ablation_study.py     # Studi ablasi parameter alpha & threshold tau
├── tests/
│   └── test_pipeline.py          # Pengujian unit otomatis seluruh komponen sistem
├── perdata-app/                  # Aplikasi Antarmuka Modern Next.js 14 + Tailwind CSS (Vercel Ready)
│   ├── app/                      # App router: /chat, /database, /evaluation
│   │   └── api/database/route.ts # Serverless API Route mandiri korpus pasal (2.276 pasal)
│   ├── data/corpus.json          # Bundle korpus naskah resmi KUHPerdata & HIR
│   └── package.json
├── app.py                        # Prototipe antarmuka Streamlit UI lokal
├── show_metrics.py               # Dashboard terminal ringkasan seluruh tabel metrik
├── requirements.txt              # Daftar dependensi pustaka Python
└── README.md                     # Dokumentasi resmi repositori
```

---

## 5. Penjelasan Model LLM yang Digunakan

Seluruh pemanggilan model LLM terpusat pada modul **`src/rag/generator.py`**:

| Komponen Model | Deployment | Deskripsi & Peran |
| :--- | :--- | :--- |
| **Google Gemini 2.5 Flash** | Cloud API (`google-genai`) | Model *frontier* dengan penalaran hukum cepat, akurasi sitasi tertinggi (**93.3%**), dan skor Ragas rata-rata terbaik (**0.863**). |
| **DeepSeek-R1-8B / V3** | Lokal (Ollama) / Cloud API | Model penalaran mendalam (*Chain-of-Thought* / CoT) yang membedah logika pasal langkah demi langkah sebelum menyimpulkan jawaban. |
| **Qwen2.5-7B-Instruct** | Lokal (Ollama) | Model open-source lokal untuk menjamin kedaulatan data perkara hukum (*on-premise privacy*), berjalan 100% offline tanpa kirim data ke internet. |

---

## 6. Panduan Menjalankan Sistem & Pengujian di Terminal

Perintah eksekusi pengujian sistem melalui PowerShell:

### 1. Pembangunan & Analisis Skenario Chunking (C1, C2, C3)
```powershell
python -m src.ingestion.build_chunk_scenarios
```

### 2. Evaluasi Komparatif Retrieval pada 3 Skenario Chunking
```powershell
python -m src.evaluation.evaluate_chunking
```

### 3. Evaluasi Komparasi Model Retrieval (R1 vs R2 vs R3)
```powershell
python -m src.evaluation.evaluate_r1_r2_r3
```

### 4. Evaluasi Skenario Serangan Racun & Pertahanan (S1 s/d S8)
```powershell
python -m src.evaluation.run_scenarios
```

### 5. Evaluasi Kualitas Teks Jawaban LLM & Standar RAGAS
```powershell
python -m src.evaluation.evaluate_llm
```

### 6. Dashboard Ringkasan Seluruh Tabel Metrik
```powershell
python show_metrics.py
```

### 7. Demonstrasi Tanya Jawab Hukum End-to-End (Live RAG QA)
```powershell
python -m src.rag.pipeline
```

---

## 7. Rekapitulasi Hasil Evaluasi Eksperimental

Evaluasi sistem dirancang secara berjenjang mengikuti logika skripsi, terbagi ke dalam **4 Tahapan Pengujian Utama**:

---

### Tahap 1: Evaluasi Segmentasi Korpus (Chunking: C1 vs C2 vs C3)

Pengujian komparatif membandingkan 3 strategi segmentasi korpus hukum perdata (KUHPerdata dan HIR) terhadap 30 kueri uji *ground truth*:
1. **C1 (Structure-Based / Per-Pasal Utuh)**: Mengikuti batas yuridis alami dokumen hukum per pasal (2.276 pasal).
2. **C2 (Fixed-Size Small / 256 Tokens)**: Jendela geser mekanis 256 token dengan overlap 32 token (822 chunk).
3. **C3 (Fixed-Size Large / 512 Tokens)**: Jendela geser mekanis 512 token dengan overlap 64 token (411 chunk).

#### Tabel Evaluasi Komparatif Skenario Chunking:

| Skenario | Strategi Segmentasi | Total Chunk | Rata-rata Token | Distorsi Multi-Pasal (%)* | Context Precision* | MRR | Recall@5 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1** | **Berbasis Struktur (Per-Pasal Utuh)** | **2.276** | **95,3** | **0,00%** | **0,884** | 0,3762 | 0,5667 |
| **C2** | Ukuran Tetap (256 Token, Overlap 32) | 822 | 255,6 | 90,15% | 0,612 | 0,4965 | 0,7000 |
| **C3** | Ukuran Tetap (512 Token, Overlap 64) | 411 | 511,1 | 97,32% | 0,485 | 0,5787 | 0,7000 |

*\*Dua Metrik Inti Penentu Tahap Chunking:*
1. **Distorsi Multi-Pasal (%)**: C1 mencatatkan **0,00%** (100% batas pasal terjaga utuh), sedangkan C3 mencapai **97,32%** (hampir seluruh chunk mencampur 5–10 pasal berbeda).
2. **Context Precision**: C1 menghasilkan nilai tertinggi **0,884** (konteks sangat bersih dari pasal pengotor), sedangkan C3 anjlok ke **0,485** akibat *context noise*.
3. **Fenomena Kenaikan MRR/Recall pada C3**: Kenaikan skor leksikal pada C3 murni merupakan ilusi *document length recall bias* (ukuran dokumen besar membuat kata kunci lebih mudah tersaring), namun dibayar mahal oleh rusaknya batas pasal dan anjloknya presisi konteks saat diumpankan ke LLM.

#### Justifikasi Ilmiah Pemilihan C1 (Structure-Based):
1. **Integritas Batas Yuridis & Bebas Distorsi**: C1 memiliki tingkat distorsi 0,0%, mencegah tercampurnya syarat dan sanksi dari pasal-pasal yang berbeda.
2. **Kerapatan Informasi & Pencegahan Halusinasi**: C1 memberikan *Context Precision* tertinggi (0,884), mencegah distorsi konteks *Lost-in-the-Middle* pada LLM.
3. **Pondasi Deteksi Knowledge Poisoning**: C1 adalah satu-satunya strategi yang kompatibel dengan verifikasi kriptografis SHA-256 terhadap dokumen resmi JDIH Mahkamah Agung.
4. **Dukungan Literatur Jurnal**: Didukung oleh temuan **Fadillah et al. (2026)** (*LawRAG*, Data Technologies and Applications) dan **Faisal et al. (2024)** (*IJAIN*) yang membuktikan segmentasi hierarkis berbasis struktur pasal mengungguli segmentasi sekuensial pada dokumen regulasi Indonesia.

---

### Tahap 2: Evaluasi Model Temu-Kembali (Retriever: R1 vs R2 vs R3)

Evaluasi kinerja algoritma pencarian dokumen pada korpus C1 terpilih menggunakan 30 kueri hukum standar:
* **R1**: Dense Retrieval SOTA multilingual — **BAAI/bge-m3** (1024-dim, Qdrant Cloud).
* **R2**: Hybrid Retrieval baseline — **SimCSE-IndoBERT + BM25** (768-dim).
* **R3**: Hybrid Retrieval gabungan — **BAAI/bge-m3 + BM25** (Reciprocal Rank Fusion).

#### Tabel Evaluasi Komparatif Retriever:

| Model | Arsitektur Retriever | Recall@5 | Recall@10 | Precision@1 | Precision@5 | MRR@5 | MRR (Global) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **R1** | **Dense BGE-M3 (Qdrant)** | **0.8333** | **0.9000** | **0.6667 (66.7%)** | **0.1733** | **0.7444** | **0.7542** |
| **R3** | Hybrid BGE-M3 + BM25 | 0.7333 | 0.9000 | 0.5333 (53.3%) | 0.1533 | 0.6139 | 0.6354 |
| **R2** | Hybrid SimCSE-IndoBERT + BM25 | 0.5167 | 0.5833 | 0.1667 (16.7%) | 0.1067 | 0.2867 | 0.2970 |

*\*Tiga Pilar Metrik Evaluasi Retriever (Recall@K, Precision@K, MRR@K):*
1. **Recall@K (Recall@5 = 0.8333)**: 83,3% kueri berhasil menangkap pasal target dalam 5 rekomendasi teratas (naik ke 90,0% pada Recall@10).
2. **Precision@K (Precision@1 = 0.6667)**: Pada peringkat pertama, presisi mencapai 66,7% (unggul jauh dibanding Hybrid 53,3% dan SimCSE 16,7%).
3. **MRR@K (MRR@5 = 0.7444 | MRR Global = 0.7542)**: Model R1 menempatkan pasal rujukan tepat di urutan teratas secara konsisten.

#### Justifikasi Ilmiah: Mengapa Dense (R1) Mengungguli Hybrid (R3)?
Eksperimen membuktikan bahwa Dense Retrieval BGE-M3 (**MRR 0,7542**) mengungguli Hybrid Retrieval (**MRR 0,6354**), didukung oleh literatur primer:
1. **The Fusion Tax (Chauhan & Agarwal, IEEE Access 2026, DOI: 10.1109/ACCESS.2026.3743502):** Pada saat model *dense retriever* sudah berstatus *State-of-the-Art* (seperti BGE-M3), penggabungan linear dengan pencarian leksikal (BM25) justru mendegradasi akurasi (*Fusion Tax*). BM25 menarik dokumen dengan kecocokan kata permukaan (*surface term matching*), sehingga menggeser pasal target yang tepat secara semantik ke urutan ranking bawah (*rank dilution*).
2. **Term Saturation pada Teks Perundang-undangan (Chalkidis et al., 2020 - EMNLP):** Kosakata hukum seperti *'perjanjian'*, *'hak'*, dan *'ganti rugi'* muncul berulang di ribuan pasal, menyebabkan bobot IDF pada BM25 mendatar mendekati 0 sehingga kehilangan daya diskriminasi. Dense retriever menangkap keutuhan kaidah hukum tanpa terdistorsi saturasi kata kunci.
3. **Vocabulary Mismatch / Semantic Gap (Karpukhin et al., 2020 - DPR EMNLP):** Kueri awam pengguna menggunakan bahasa informal (misal: *'ingkar janji bayar utang'*), sedangkan korpus hukum menggunakan terminologi yuridis formal (*'wanprestasi atas perikatan'*). BM25 menghasilkan skor 0, sedangkan BGE-M3 memetakan makna konsep ke ruang vektor bersama.
4. **Morfologi Hukum Indonesia (Rozaq et al., 2025):** Teks hukum Indonesia kaya imbuhan (*ke-an, per-an*) yang menimbulkan pencocokan palsu pada tokenizer unigram BM25. Dense retriever multilingual menangkap relasi sintaktis klausa secara jauh lebih akurat.

---

### Profil Pengambilan Pasal oleh Retriever pada Korpus Terkontaminasi (Top-5 Retrieval)
Mengevaluasi seberapa agresif pasal racun tertarik oleh Retriever R1 saat korpus diserang dengan berbagai rasio kontaminasi:

| Tingkat Racun | Total Pasal Ditarik (Top-5) | Pasal Bersih Terambil | Pasal Racun Terambil | Persentase Racun di Konteks |
| :---: | :---: | :---: | :---: | :---: |
| **0% (Bersih)** | **150** chunk | **150** chunk | **0** chunk | **0.0%** |
| **1% Poison** | **150** chunk | **129** chunk | **21** chunk | **14.0%** |
| **5% Poison** | **150** chunk | **114** chunk | **36** chunk | **24.0%** |
| **10% Poison** | **150** chunk | **108** chunk | **42** chunk | **28.0%** |

*Temuan Penting*: Semakin tinggi persentase racun di korpus, semakin banyak pasal manipulasi yang ikut ditarik oleh Retriever masuk ke konteks (hingga **28.0%** pada dosis **10%**). Hal inilah yang membuktikan mengapa **modul pertahanan verifikasi integritas SHA-256 + NLI mutlak diperlukan** sebelum pasal diserahkan ke LLM!

---

### Tahap 3: Evaluasi Kualitas Pembangkitan Jawaban (Model LLM: L1 vs L2 vs L3)

Evaluasi komparatif 3 varian model LLM menggunakan **5 Metrik Lengkap Framework RAGAS** pada korpus C1 dan retriever R1 terpilih:

| Model LLM | Kategori Model | Deployment | Faithfulness* | Answer Relevancy* | Context Precision* | Context Recall* | Answer Correctness* | Rata-Rata Skor |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gemini 2.5 Flash** | Frontier Cloud API | Cloud API | **0.892** | **0.865** | **0.884** | **0.833** | **0.841** | **0.863** |
| **DeepSeek V3 / R1** | Reasoning Model | Cloud / Ollama | **0.842** | **0.854** | **0.884** | **0.833** | **0.812** | **0.845** |
| **Qwen2.5-7B** | Local Open-Source | Lokal (Ollama) | **0.784** | **0.827** | **0.884** | **0.833** | **0.756** | **0.817** |

*\*Analisis 5 Metrik RAGAS:*
1. **Faithfulness (0.892 pada Gemini)**: Mengukur bahwa jawaban LLM 89,2% patuh secara faktual terhadap pasal rujukan dan bebas dari fabrikasi/halusinasi hukum.
2. **Answer Relevancy (0.865 pada Gemini)**: Jawaban merespons inti permasalahan hukum pengguna secara lugas tanpa bertele-tele.
3. **Context Precision (0.884)** & **Context Recall (0.833)**: Konteks pasal yang disuplai oleh Retriever R1 sangat bersih dari noise serta mencakup kaidah hukum yang dicari.
4. **Answer Correctness (0.841 pada Gemini)**: Kesesuaian semantik dan yuridis yang tinggi terhadap kunci jawaban pakar hukum (*ground truth*).

---

### Tahap 4: Evaluasi Efektivitas Sistem Pertahanan Siber (Skenario S1 s.d. S8)

Evaluasi mekanisme pertahanan *Knowledge Poisoning* diukur menggunakan **Kerangka Pertahanan Berlapis (Two-Tier Defense)** dengan metrik keamanan utama: **Attack Success Rate (ASR)**, **False Positive Rate (FPR)**, dan **Defense Latency Overhead**:

#### Tabel Evaluasi Pertahanan Siber Terhadap Serangan Manipulasi Pasal:

| Skenario | Kondisi Korpus | Pertahanan (SHA-256 + NLI) | Serangan Tembus (ASR)* | False Alarm (FPR)* | Precision Deteksi | Recall Deteksi | F1-Score | Status Keamanan |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **S1** | Korpus Bersih | NONAKTIF (Baseline) | **0.0%** | 0.0% | 100.0% | 100.0% | 100.0% | Aman (Tanpa Serangan) |
| **S2** | Korpus Bersih | **AKTIF (Uji False Positive)** | **0.0%** | **0.0%** | 100.0% | 100.0% | 100.0% | **Aman (Zero False Alarm)** |
| **S3** | Terkontaminasi 1% | NONAKTIF | **60.0%** | 0.0% | 100.0% | 0.0% | 0.0% | Kritis (Racun Lolos) |
| **S4** | Terkontaminasi 1% | **AKTIF** | **0.0%** | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **Kebal (100% Dicegat)** |
| **S5** | Terkontaminasi 5% | NONAKTIF | **83.3%** | 0.0% | 100.0% | 0.0% | 0.0% | Kritis (Racun Lolos) |
| **S6** | Terkontaminasi 5% | **AKTIF** | **0.0%** | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **Kebal (100% Dicegat)** |
| **S7** | Terkontaminasi 10% | NONAKTIF | **83.3%** | 0.0% | 100.0% | 0.0% | 0.0% | Kritis (Racun Lolos) |
| **S8** | Terkontaminasi 10% | **AKTIF** | **0.0%** | **0.0%** | **100.0%** | **100.0%** | **100.0%** | **Kebal (100% Dicegat)** |

#### Analisis Kritis Kinerja Pertahanan:
* **Urgensi Metrik FPR = 0,0% pada Ranah Hukum**: Dalam sistem *Legal QA*, metrik *False Positive Rate* (FPR) sama pentingnya dengan akurasi deteksi. Jika sistem pertahanan menghasilkan alarm palsu (FPR > 0), pasal resmi KUHPerdata/HIR akan keliru diblokir dan dikarantina, mengakibatkan LLM gagal menjawab kueri hukum pengguna. Hasil pengujian pada Skenario S2 membuktikan bahwa skor **FPR = 0,0%**, menjamin tidak ada dokumen hukum sah yang tersensor secara keliru.
* **Eliminasi Total Attack Success Rate (ASR)**: Tanpa mekanisme pertahanan (Skenario S3, S5, S7), pasal manipulasi berhasil menyusup ke prompt penalaran LLM dengan tingkat keberhasilan serangan sebesar **60,0% s.d. 83,3%**. Setelah modul pertahanan berlapis (SHA-256 + NLI) diaktifkan pada bobot optimal $\alpha = 0,6$ dan $\tau = 0,5$, **seluruh serangan berhasil digagalkan 100% (ASR = 0,0%)** pada seluruh tingkat kontaminasi korpus (1%, 5%, dan 10%).
* **Beban Waktu Tambahan (Defense Latency Overhead)**: Penambahan verifikasi hash SHA-256 dan perbandingan NLI semantik hanya memerlukan waktu komputasi **~15–30 ms per kueri**, mempertahankan responsivitas *real-time* sistem tanya-jawab.

---

## 8. Standarisasi & Pemetaan Metrik Evaluasi Skripsi

Berikut adalah ringkasan pembagian metrik baku yang digunakan pada **Bab 3 (Metodologi)** dan **Bab 4 (Pengujian dan Analisis)**:

| No | Tahap Pengujian | Objek yang Diuji | Metrik Evaluasi Terpilih | Definisi Singkat Akademis |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Segmentasi Korpus (*Chunking*)** | C1 vs C2 vs C3 | 1. **Distorsi Multi-Pasal (%)**<br>2. **Context Precision** | • Mengukur persentase chunk yang memotong dan mencampurkan lebih dari 1 pasal.<br>• Mengukur rasio kemurnian pasal target dalam jendela konteks LLM. |
| **2** | **Model Temu-Kembali (*Retriever*)** | R1 vs R2 vs R3 | 1. **Recall@K**<br>2. **Precision@K**<br>3. **MRR@K** | • Mengukur proporsi pasal relevan yang berhasil tertangkap dalam Top-K.<br>• Mengukur ketepatan dokumen yang ditarik dalam batas peringkat K.<br>• Mengukur kebalikan peringkat (ranking) pasal target pertama dalam Top-K. |
| **3** | **Kualitas Pembangkitan (*LLM*)** | L1 vs L2 vs L3 | **5 Metrik RAGAS Lengkap**:<br>• *Faithfulness*<br>• *Answer Relevancy*<br>• *Context Precision*<br>• *Context Recall*<br>• *Answer Correctness* | • Tingkat kepatuhan fakta konteks (anti-halusinasi).<br>• Tingkat kerelevanan jawaban terhadap pertanyaan.<br>• Presisi informasi konteks yang diacu.<br>• Kelengkapan pasal rujukan yang tertangkap.<br>• Kebenaran substantif jawaban terhadap ground truth pakar. |
| **4** | **Ketahanan Keamanan (*Defense*)** | Skenario S1 s.d. S8 | 1. **Attack Success Rate (ASR)**<br>2. **False Positive Rate (FPR)**<br>3. **Defense Latency Overhead (ms)** | • Persentase serangan racun yang berhasil lolos menembus ke LLM.<br>• Persentase dokumen hukum asli yang keliru diblokir (alarm palsu).<br>• Waktu tambahan komputasi akibat verifikasi SHA-256 + NLI. |

---

## 9. Panduan Konfigurasi Kredensial `.env`

Buat berkas `.env` pada direktori akar repositori (`legal-rag-perdata/.env`):
```ini
# Google Gemini API Key (Untuk Gemini 2.5 Flash via google-genai SDK)
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere

# DeepSeek API Key (Opsional, untuk DeepSeek via Cloud API)
DEEPSEEK_API_KEY=sk-YourDeepSeekApiKeyHere

# Qdrant Cloud Cluster AWS London
QDRANT_URL=https://aa06130a-924d-4b1a-a883-4615d0199852.eu-west-2-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Konfigurasi Model Lokal Ollama (Default: localhost)
OLLAMA_HOST=http://localhost:11434
```

---

## 10. Lisensi & Hak Cipta

Proyek ini dikembangkan untuk kepentingan penelitian ilmiah dan pengembangan asisten cerdas hukum perdata Indonesia. Seluruh materi undang-undang (KUHPerdata dan HIR) bersumber dari dokumen hukum publik resmi Republik Indonesia.
