from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from typing import List, Optional, Dict
from ..utils.config import MODEL_CONFIG, RAG_CONFIG, CHROMA_DIR

class BaseRAG:
    def __init__(self):
        self.setup_embeddings()
        self.setup_vectorstore()
        self.setup_text_splitter()
    
    def setup_embeddings(self):
        """埋め込みモデルの初期化"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_CONFIG["embedding_model"],
            model_kwargs={'device': MODEL_CONFIG["device"]}
        )
    
    def setup_vectorstore(self):
        """ベクトルストアの初期化"""
        self.vectorstore = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=str(CHROMA_DIR)
        )
    
    def setup_text_splitter(self):
        """テキストスプリッターの初期化"""
        self.text_splitter = CharacterTextSplitter(
            separator="。",
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"],
            length_function=len,
        )
    
    def add_texts(self, texts: list[str]):
        """テキストの追加"""
        try:
            # 各テキストを個別に処理
            all_splits = []
            print("\nSplitting texts:")
            for i, text in enumerate(texts, 1):
                # 空白と改行を整理
                cleaned_text = text.strip().replace("\n", "")
                # 文分割
                splits = [s + "。" for s in cleaned_text.split("。") if s]
                print(f"\nText {i} splits into {len(splits)} parts:")
                for j, split in enumerate(splits, 1):
                    print(f"Part {j}: {split}")
                all_splits.extend(splits)
            
            # 空の文字列を除去
            all_splits = [s for s in all_splits if s.strip()]
            
            if all_splits:
                # ベクトルストアに追加
                self.vectorstore.add_texts(all_splits)
                print(f"\nSuccessfully added {len(all_splits)} chunks to the database")
                return True
            print("No valid text chunks to add")
            return False
            
        except Exception as e:
            print(f"Error adding texts: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = None) -> List[Dict]:
        """類似テキストの検索"""
        try:
            k = k or RAG_CONFIG["default_search_k"]
            results = self.vectorstore.similarity_search(
                query,
                k=k
            )
            return results
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return []