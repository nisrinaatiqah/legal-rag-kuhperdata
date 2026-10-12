Dataset pertanyaan hukum akan ditambahkan setelah chunk corpus tervalidasi. Simpan train/dev, validation, dan test terpisah. Contoh bentuk record untuk rancangan nanti:

```json
{"query_id":"q001","question":"...","relevant_chunk_ids":["kuhperdata_pasal_1234"],"reference_answer":"..."}
```

Jangan gunakan korpus test untuk menyetel threshold deteksi atau bobot gabungan.
