import os
from pathlib import Path

# ベースディレクトリの設定
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"

# モデル設定
MODEL_CONFIG = {
    "embedding_model": "intfloat/multilingual-e5-small",
    "device": "cuda",  # GPU利用
    "torch_dtype": "float16"
}

# RAG設定
RAG_CONFIG = {
    "chunk_size": 100,
    "chunk_overlap": 0,
    "default_search_k": 2
}

# ディレクトリの作成
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)