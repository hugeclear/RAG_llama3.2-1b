from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
import re
from ..utils.config import MODEL_CONFIG, RAG_CONFIG, CHROMA_DIR

class RAGSystem:
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
    
    def _scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """URLからテキストを取得"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 不要なタグを削除
            for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
                tag.decompose()
            
            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            
            return {
                'text': text,
                'title': soup.title.string if soup.title else url,
                'url': url
            }
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def add_from_url(self, url: str) -> bool:
        """URLからコンテンツを追加"""
        try:
            # URLからテキストを取得
            content = self._scrape_url(url)
            if not content:
                return False
            
            # テキストを分割
            texts = self.text_splitter.split_text(content['text'])
            
            # メタデータを準備
            metadatas = [
                {
                    'source': url,
                    'title': content['title'],
                    'chunk_id': i
                } for i in range(len(texts))
            ]
            
            # ベクトルストアに追加
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            return True
        except Exception as e:
            print(f"Error adding content from URL: {str(e)}")
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