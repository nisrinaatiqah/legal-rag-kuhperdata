# TA Legal Question Answering — Starter Workspace

Kerangka awal untuk mengerjakan TA Legal Question Answering dengan KUHPerdata dan HIR. Kerangka ini **belum** berisi implementasi retrieval, generator, poisoning, atau detector. Tahap awalnya hanya memeriksa dan mengekstrak teks PDF dengan aman.

## 1. Letakkan PDF

Salin dua PDF sumber ke `data/raw_trusted/`. Nama file boleh berbeda, asalkan formatnya `.pdf`.

Jaga folder ini sebagai sumber tepercaya yang tidak diedit. Jangan menaruh PDF atau chunk hasil poisoning ke folder ini.

## 2. Buat environment (Windows PowerShell)

Pastikan Python 3.11 tersedia, lalu dari folder proyek jalankan:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Jika aktivasi PowerShell diblokir, gunakan Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## 3. Periksa apakah PDF bisa diekstrak sebagai teks

```powershell
python src/ingestion/inspect_pdfs.py
```

Periksa jumlah halaman, total karakter, halaman yang hampir tidak berisi teks, dan contoh hasil ekstraksi. Jika hampir semua halaman kosong, PDF mungkin berupa scan atau teksnya tidak terbaca. **Jangan langsung OCR**; periksa dulu satu halaman sumber secara manual.

## 4. Ekstrak teks halaman demi halaman

Jika hasil inspeksi masuk akal:

```powershell
python src/ingestion/extract_pdfs.py
```

File `.jsonl` akan dibuat di `data/extracted/`, satu baris untuk setiap halaman. Setiap baris mencatat nama PDF, nomor halaman, teks hasil ekstraksi, serta SHA-256 dari file PDF sumber.

## Tahap selanjutnya

Setelah hasil ekstraksi diperiksa, barulah tentukan pola heading pasal untuk KUHPerdata dan HIR, buat chunk per pasal, dan verifikasi bahwa nomor pasal serta isi chunk sesuai PDF sumber. Pola chunking tidak langsung diasumsikan di starter ini karena format teks hasil ekstraksi harus dilihat terlebih dahulu.
