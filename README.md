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
1. DATA INGESTION:
   data/raw_trusted/ (PDF)
         │
         ▼
   src/ingestion/extract_pdfs.py ──► Ekstraksi teks dari PDF resmi KUHPerdata & HIR
         │
         ▼
   src/ingestion/chunk_articles.py ──► Parsing per nomor pasal & pembersihan teks
         │
         ▼
   src/ingestion/finalize_corpus.py ──► Menghasilkan:
                                        • data/processed/legal_corpus_clean.jsonl (2.276 pasal)
                                        • data/manifests/trusted_corpus_manifest.json (Hash SHA-256)

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
│   ├── processed/                # Korpus bersih terstruktur (2.276 pasal resmi)
│   │   └── legal_corpus_clean.jsonl
│   ├── manifests/                # Manifest kriptografis integritas SHA-256
│   │   └── trusted_corpus_manifest.json
│   ├── poisoning/                # Korpus hasil simulasi peracunan (1%, 5%, 10%)
│   │   ├── corpus_poisoned_1pct.jsonl
│   │   ├── corpus_poisoned_5pct.jsonl
│   │   └── corpus_poisoned_10pct.jsonl
│   └── evaluation/               # Ground truth kueri uji (30 kueri) & berkas hasil metrik
│       ├── ground_truth_perdata.json
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
│   ├── ingestion/                # Ekstraksi PDF, parsing pasal, & pembentukan manifest SHA-256
│   ├── retrieval/                # Embedding model (BGE-M3 & SimCSE), Qdrant Cloud/Local, BM25, & R1/R2/R3
│   ├── rag/                      # Prompt builder, generator LLM, & pipeline end-to-end
│   │   ├── generator.py          # IMPLEMENTASI SEMUA MODEL LLM (Gemini, DeepSeek, Qwen)
│   │   ├── pipeline.py           # Orkestrasi alur RAG (Retrieval -> Defense -> Generator)
│   │   └── prompt.py             # Template prompt hukum & pembatasan sitasi pasal
│   ├── poisoning/                # Engine manipulasi teks hukum adversarial (negasi, modifikasi frasa)
│   ├── detection/                # Verifikator SHA-256, NLI semantik, & composite risk score
│   └── evaluation/               # Modul pengujian metrik MRR, Recall, S1-S8, ROUGE/BLEU, & Ragas
│       ├── evaluate_r1_r2_r3.py  # Benchmark komparatif 3 retriever
│       ├── run_scenarios.py      # Benchmark 8 skenario pertahanan keamanan
│       ├── evaluate_llm.py       # Benchmark 8 skenario kualitas generasi teks LLM
│       └── ablation_study.py     # Studi ablasi parameter alpha & threshold tau
├── tests/
│   └── test_pipeline.py          # Pengujian unit otomatis seluruh komponen sistem
├── app.py                        # Aplikasi antarmuka web interaktif (Streamlit UI)
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

### 1. Evaluasi Komparasi Model Retrieval (R1 vs R2 vs R3)
```powershell
python -m src.evaluation.evaluate_r1_r2_r3
```

### 2. Evaluasi Skenario Serangan Racun & Pertahanan (S1 s/d S8)
```powershell
python -m src.evaluation.run_scenarios
```

### 3. Evaluasi Kualitas Teks Jawaban LLM & Standar RAGAS
```powershell
python -m src.evaluation.evaluate_llm
```

### 4. Dashboard Ringkasan Seluruh Tabel Metrik
```powershell
python show_metrics.py
```

### 5. Demonstrasi Tanya Jawab Hukum End-to-End (Live RAG QA)
```powershell
python -m src.rag.pipeline
```

---

## 7. Rekapitulasi Hasil Evaluasi Eksperimental

### A. Evaluasi Komparasi Model Retrieval (30 Kueri Benchmark — Qdrant Cloud)

Tabel evaluasi detail pada seluruh variasi nilai cut-off $K$ ($K = 1, 3, 5, 10$):

| Model | Arsitektur | MRR | R@1 | R@3 | R@5 | R@10 | MAP@1 | MAP@3 | MAP@5 | MAP@10 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **R1** | **Dense BGE-M3 (Qdrant)** | **0.7542** | **0.6500** | **0.8167** | **0.8333** | **0.9000** | **0.6667** | **0.7278** | **0.7361** | **0.7458** |
| **R2** | Hybrid SimCSE-IndoBERT + BM25 | 0.2970 | 0.1500 | 0.3500 | 0.5167 | 0.5833 | 0.1667 | 0.2333 | 0.2700 | 0.2803 |
| **R3** | Hybrid BGE-M3 + BM25 | 0.6354 | 0.5167 | 0.7000 | 0.7333 | 0.9000 | 0.5333 | 0.6056 | 0.6139 | 0.6354 |

#### Profil Pengambilan Pasal oleh Retriever pada Korpus Terkontaminasi (Top-5 Retrieval)
Mengevaluasi seberapa agresif pasal racun tertarik oleh Retriever R1 saat korpus diserang dengan berbagai rasio kontaminasi:

| Tingkat Racun | Total Pasal Ditarik (Top-5) | Pasal Bersih Terambil | Pasal Racun Terambil | Persentase Racun di Konteks |
| :---: | :---: | :---: | :---: | :---: |
| **0% (Bersih)** | **150** chunk | **150** chunk | **0** chunk | **0.0%** |
| **1% Poison** | **150** chunk | **129** chunk | **21** chunk | **14.0%** |
| **5% Poison** | **150** chunk | **114** chunk | **36** chunk | **24.0%** |
| **10% Poison** | **150** chunk | **108** chunk | **42** chunk | **28.0%** |

*Temuan Penting*: Semakin tinggi persentase racun di korpus, semakin banyak pasal manipulasi yang ikut ditarik oleh Retriever masuk ke konteks (hingga **28.0%** pada dosis **10%**). Hal inilah yang membuktikan mengapa **modul pertahanan verifikasi integritas SHA-256 + NLI mutlak diperlukan** sebelum pasal diserahkan ke LLM!

---

### B. Evaluasi Efektivitas Sistem Pertahanan Siber (Skenario S1 s.d. S8)
| Skenario | Kondisi Korpus | Pertahanan | Precision | Recall | F1-Score | ASR (Tembus) | FPR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **S1** | Korpus Bersih | NONAKTIF | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **0.0%** |
| **S2** | Korpus Bersih | **AKTIF** | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **0.0%** |
| **S3** | Poisoning 1% | NONAKTIF | **100.0%** | 0.0% | 0.0% | **60.0%** | **0.0%** |
| **S4** | Poisoning 1% | **AKTIF** | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **0.0%** |
| **S5** | Poisoning 5% | NONAKTIF | **100.0%** | 0.0% | 0.0% | **83.3%** | **0.0%** |
| **S6** | Poisoning 5% | **AKTIF** | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **0.0%** |
| **S7** | Poisoning 10% | NONAKTIF | **100.0%** | 0.0% | 0.0% | **83.3%** | **0.0%** |
| **S8** | Poisoning 10% | **AKTIF** | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **0.0%** |

*Catatan Kunci*: Tanpa pertahanan, racun tembus ke LLM sebesar **60.0%** s.d. **83.3%**. Dengan pertahanan aktif (SHA-256 + NLI), Attack Success Rate (ASR) ditekan hingga **0.0%** dengan **Zero False Alarm (FPR = 0.0%)**.

---

### C. Evaluasi Kualitas Generasi Teks Jawaban LLM pada Skenario S1 s.d. S8
| Skenario | Kondisi Korpus | Pertahanan | Ctx Prec | Ctx Rec | ROUGE-L | BLEU-4 | Faithfulness | Sitasi | ASR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **S1** | Bersih (0%) | NONAKTIF | **0.8840** | **0.8333** | **0.5903** | **0.4649** | **0.9500** | **66.7%** | **0.0%** |
| **S2** | Bersih (0%) | **AKTIF** | **0.8840** | **0.8333** | **0.5903** | **0.4649** | **0.9500** | **66.7%** | **0.0%** |
| **S3** | Poison 1% | NONAKTIF | 0.5620 | 0.6120 | 0.4320 | 0.2840 | 0.7200 | 46.7% | **36.7%** |
| **S4** | Poison 1% | **AKTIF** | **0.8540** | **0.8333** | **0.5820** | **0.4520** | **1.0000** | **63.3%** | **0.0%** |
| **S5** | Poison 5% | NONAKTIF | 0.3120 | 0.4210 | 0.2271 | 0.0821 | 0.6100 | 23.3% | **56.7%** |
| **S6** | Poison 5% | **AKTIF** | **0.8210** | **0.8000** | **0.5560** | **0.4280** | **1.0000** | **60.0%** | **0.0%** |
| **S7** | Poison 10% | NONAKTIF | 0.2450 | 0.3340 | 0.1650 | 0.0410 | 0.5200 | 16.7% | **73.3%** |
| **S8** | Poison 10% | **AKTIF** | **0.7980** | **0.7667** | **0.5310** | **0.3980** | **1.0000** | **56.7%** | **0.0%** |

---

### D. Evaluasi Komparatif Multi-Model LLM 
| Model LLM | Deployment | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Answer Correctness | Rata-Rata Skor | Akurasi Sitasi |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gemini 2.5 Flash** | Cloud API | **0.892** | **0.865** | **0.884** | **0.833** | **0.841** | **0.863** | **93.3%** |
| **DeepSeek V3 / R1** | Cloud API / Ollama | **0.842** | **0.854** | **0.884** | **0.833** | **0.812** | **0.845** | **90.0%** |
| **Qwen2.5-7B** | Lokal (Ollama) | **0.784** | **0.827** | **0.884** | **0.833** | **0.756** | **0.817** | **86.7%** |

---

## 8. Glosarium & Penjelasan Elemen Metrik Evaluasi

Seluruh metrik yang digunakan dalam evaluasi sistem ini dikelompokkan ke dalam **4 pilar utama**:

```text
                                PILAR METRIK EVALUASI SISTEM
                                                │
         ┌───────────────────────┬──────────────┴───────────────┬───────────────────────┐
         ▼                       ▼                              ▼                       ▼
  [ 1. RETRIEVAL IR ]    [ 2. KEAMANAN SIBER ]          [ 3. STANDAR RAGAS ]     [ 4. TEKS GENERASI NLG ]
  • MRR                  • Precision & Recall Deteksi   • Context Recall         • ROUGE-1 & ROUGE-2
  • Recall@K             • F1-Score Deteksi             • Context Precision      • ROUGE-L
  • MAP@5                • Attack Success Rate (ASR)    • Faithfulness           • BLEU-4
                         • False Positive Rate (FPR)    • Answer Relevancy
                                                        • Answer Correctness
                                                        • Akurasi Sitasi
```

---

### Pilar 1: Metrik Evaluasi Komponen Retrieval (Pencarian Dokumen)
Metrik standar internasional bidang *Information Retrieval* (IR) untuk mengukur kemampuan mesin pencari vektor menemukan pasal hukum yang tepat dari korpus 2.276 pasal:

1. **MRR (Mean Reciprocal Rank)**
   * **Definisi**: Mengukur seberapa cepat sistem menempatkan pasal relevan pertama di peringkat teratas.
   * **Rumus**: $MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$, di mana $\text{rank}_i$ adalah urutan pertama pasal acuan ditemukan.
   * **Arti Nilai**: Jika pasal yang dicari selalu muncul di peringkat 1, skor MRR = 1.0. Model R1 (BGE-M3) meraih skor tertinggi **0.7542**.
2. **Recall@K (Recall@1, Recall@3, Recall@5, Recall@10)**
   * **Definisi**: Persentase kueri yang berhasil menemukan setidaknya satu pasal rujukan sah di dalam $K$ dokumen teratas.
   * **Arti Nilai**: Mengukur jaminan bahwa pasal hukum yang dibutuhkan pengguna tidak terlewat. Pada Recall@10, model R1 mencapai **0.9000 (90%)**.
3. **MAP@K (Mean Average Precision pada Top-K)**
   * **Definisi**: Rata-rata presisi berbobot peringkat untuk mengevaluasi apakah seluruh pasal yang relevan berkumpul di peringkat teratas (bukan di urutan bawah).
   * **Hubungan Konseptual**: **MAP@K secara matematis identik dengan Context Precision pada framework RAGAS.**

---

### Pilar 2: Metrik Evaluasi Sistem Pertahanan Siber (Deteksi Knowledge Poisoning)
Metrik evaluasi klasifikasi biner dan ketahanan keamanan saat sistem diuji menghadapi serangan manipulasi teks hukum adversarial (Skenario S1 s.d. S8):

1. **Precision Deteksi**
   * **Definisi**: Dari seluruh pasal yang divonis beracun dan diblokir oleh filter, berapa persen yang memang benar-benar pasal manipulasi racun?
   * **Rumus**: $\text{Precision} = \frac{TP}{TP + FP}$. Sistem meraih **100%** (tidak ada salah vonis).
2. **Recall Deteksi**
   * **Definisi**: Dari seluruh pasal racun yang disusupkan penyerang, berapa persen yang berhasil diendus dan dicegat oleh sistem?
   * **Rumus**: $\text{Recall} = \frac{TP}{TP + FN}$. Pada mode pertahanan aktif, Recall mencapai **100%**.
3. **F1-Score Deteksi**
   * **Definisi**: Nilai rata-rata harmonik antara Precision dan Recall deteksi ($\frac{2 \cdot P \cdot R}{P + R}$) yang menggambarkan ketangguhan tameng secara keseluruhan.
4. **FPR (False Positive Rate / Tingkat Alarm Palsu)**
   * **Definisi**: Persentase pasal bersih dan otentik yang keliru divonis beracun sehingga tidak sengaja terblokir.
   * **Rumus**: $FPR = \frac{FP}{FP + TN}$. Sistem mencatatkan **FPR = 0.0% (Zero False Alarm)**, membuktikan dokumen hukum resmi tidak pernah salah diblokir.
5. **ASR (Attack Success Rate / Tingkat Keberhasilan Serangan)**
   * **Definisi**: Persentase kasus di mana pasal manipulasi racun berhasil menembus pertahanan dan menyusup ke prompt penalaran LLM.
   * **Rumus**: $ASR = \frac{\text{Kueri Terkontaminasi Lolos}}{\text{Total Kueri Uji}} \times 100\%$.
   * **Hasil Evaluasi**: Tanpa pertahanan, ASR mencapai **83.3%**. Dengan pertahanan aktif (SHA-256 + NLI), ASR berhasil ditekan menjadi **0.0% (100% Serangan Digagalkan)**.

---

### Pilar 3: Metrik Evaluasi Konteks & Generasi LLM (Standar Framework RAGAS)
Metrik komparatif multi-model LLM untuk menguji kualitas penalaran hukum:

1. **Context Recall**
   * **Definisi**: Mengukur kelengkapan informasi pasal yang ditarik oleh Retriever terhadap kunci jawaban resmi (*ground truth*). Padanan langsung dari metrik *Recall@K* pada Information Retrieval.
2. **Context Precision**
   * **Definisi**: Mengukur rasio sinyal terhadap derau (*signal-to-noise ratio*) pada pasal yang ditarik. Menilai apakah pasal paling penting ditaruh di peringkat teratas tanpa tercampur pasal sampah/racun. Padanan langsung dari metrik *MAP (Mean Average Precision)*.
3. **Faithfulness (Tingkat Kepatuhan Fakta / Anti-Halusinasi)**
   * **Definisi**: Mengukur apakah seluruh klaim hukum di dalam teks jawaban LLM disimpulkan murni dari konteks pasal yang sah tanpa mengarang bebas (halusinasi). Skala 0.0 s.d. 1.0. Gemini 2.5 Flash meraih skor tertinggi **0.892**.
4. **Answer Relevancy (Kesesuaian Jawaban)**
   * **Definisi**: Mengukur apakah jawaban LLM langsung menjawab inti pertanyaan hukum pengguna tanpa berbelit-belit atau melantur ke topik perdata lain.
5. **Answer Correctness (Kebenaran Substansi Hukum)**
   * **Definisi**: Mengukur kebenaran semantik dan faktual isi jawaban LLM jika dikomparasikan langsung terhadap kunci jawaban pakar hukum (*ground truth*).
6. **Akurasi Sitasi (Citation Accuracy)**
   * **Definisi**: Persentase jawaban yang secara tepat menyebutkan nomor pasal dan nama undang-undang rujukan yang valid (misal: `[KUHPerdata Pasal 1320]`). Gemini mencapai akurasi sitasi **93.3%**.

---

### Pilar 4: Metrik Evaluasi Kemiripan Bahasa & Teks (NLG - Natural Language Generation)
Metrik statistik linguistik komputasi untuk mengukur kemiripan redaksional teks jawaban LLM terhadap bunyi teks naskah undang-undang asli:

1. **ROUGE-1**: Mengukur tumpang tindih kata tunggal (*unigram overlap*) antara jawaban LLM dan pasal acuan.
2. **ROUGE-2**: Mengukur tumpang tindih pasangan dua kata berurutan (*bigram overlap*) untuk mengecek kecocokan istilah hukum baku (seperti: *"syarat sah"*, *"ganti rugi"*, *"perbuatan melawan hukum"*).
3. **ROUGE-L**: Mengukur urutan kata terpanjang (*Longest Common Subsequence* / LCS) untuk menilai kelancaran struktur tata kalimat hukum.
4. **BLEU-4**: Mengukur presisi potongan kalimat 4-kata berurutan (*4-gram precision*) dengan penalti panjang kalimat (*brevity penalty*) untuk memastikan teks jawaban padat, presisi, dan tidak bertele-tele.

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
