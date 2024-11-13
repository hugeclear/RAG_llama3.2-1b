from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
import torch
import os
from config.config import MODEL_CONFIG, RAG_CONFIG, CHROMA_DIR

class RAGBase:
    def __init__(self):
        self.setup_text_splitter()
        self.setup_embeddings()
        self.setup_vectorstore()
    
    def setup_text_splitter(self):
        self.text_splitter = CharacterTextSplitter(
            separator="。",
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"],
            length_function=len,
        )
    
    def setup_embeddings(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_CONFIG["embedding_model"],
            model_kwargs={'device': MODEL_CONFIG["device"]}
        )
    
    def setup_vectorstore(self):
        # ディレクトリの作成
        os.makedirs(CHROMA_DIR, exist_ok=True)
        
        self.vectorstore = Chroma(
            collection_name="test_collection",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DIR
        )
    
    def add_texts(self, texts: list[str]):
        try:
            all_splits = []
            for text in texts:
                cleaned_text = text.strip().replace("\n", "")
                splits = [s + "。" for s in cleaned_text.split("。") if s]
                all_splits.extend(splits)
            
            all_splits = [s for s in all_splits if s.strip()]
            
            if all_splits:
                self.vectorstore.add_texts(all_splits)
                return True
            return False
        except Exception as e:
            print(f"Error adding texts: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = None):
        k = k or RAG_CONFIG["default_search_k"]
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return None