import os

# パス設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# モデル設定
MODEL_CONFIG = {
    "embedding_model": "intfloat/multilingual-e5-small",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "torch_dtype": "float16" if torch.cuda.is_available() else "float32"
}

# スクレイピング設定
SCRAPING_CONFIG = {
    "timeout": 10,
    "min_text_length": 50,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# RAG設定
RAG_CONFIG = {
    "chunk_size": 100,
    "chunk_overlap": 0,
    "default_search_k": 2
}