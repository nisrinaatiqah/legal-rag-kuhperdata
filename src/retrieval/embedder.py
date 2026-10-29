"""
Modul: Retrieval - Legal Text Embedder
Fungsi: Menghasilkan representasi vektor rapat (dense embeddings) untuk pasal hukum dan kueri pengguna
menggunakan model bahasa multibahasa BAAI/bge-m3 (dimensi: 1024) atau SimCSE-IndoBERT (dimensi: 768).
Vektor ini dinormalisasi ke satuan L2 agar Cosine Similarity setara dengan Inner Product.
"""

from typing import List, Union
import numpy as np


class LegalEmbedder:
    """
    Kelas pembungkus (wrapper) SentenceTransformer untuk mengenkode teks hukum Indonesia.
    Model default yang diusulkan adalah BAAI/bge-m3.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = None):
        """
        [PROSES 1: INISIALISASI MODEL]
        Memuat bobot pre-trained model ke memori GPU (CUDA) jika tersedia, atau CPU sebagai fallback.
        """
        from sentence_transformers import SentenceTransformer
        import torch

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"[*] Memuat embedding model: {model_name} pada device: {self.device}...")
        self.model_name = model_name
        try:
            # Coba muat langsung dari cache lokal agar instan tanpa delay request ke HuggingFace
            self.model = SentenceTransformer(model_name, device=self.device, local_files_only=True)
        except Exception:
            self.model = SentenceTransformer(model_name, device=self.device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"[+] Model siap. Dimensi embedding: {self.embedding_dim}")

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = True,
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        """
        [PROSES 2: ENKODE BATCH TEKS]
        Mengonversi daftar string teks hukum menjadi array NumPy vektor dense float32.
        - normalize_embeddings=True: Menghitung vektor satuan untuk pencarian Cosine Similarity cepat.
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=normalize_embeddings,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """
        [PROSES 3: ENKODE KUERI TUNGGAL]
        Mengonversi kueri pertanyaan pengguna menjadi vektor 1-dimensi berukuran 1024.
        """
        vec = self.encode([query], show_progress_bar=False, normalize_embeddings=True)
        return vec[0]
