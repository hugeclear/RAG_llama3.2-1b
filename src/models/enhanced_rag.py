from .base_rag import BaseRAG
from .llm_model import LlamaModel
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class EnhancedRAG(BaseRAG):
    def __init__(self):
        super().__init__()
        self.setup_llm()
        self.sources = {}  # URLとそのメタデータを保存
    
    def setup_llm(self):
        """LLaMAモデルの初期化"""
        self.llm = LlamaModel()
        self.llm.load_model()
    
    def add_from_url(self, url: str) -> bool:
        """URLからコンテンツを追加"""
        try:
            data = self._scrape_url(url)
            if not data:
                return False
            
            texts_with_metadata = []
            for i, text in enumerate(data['content']):
                metadata = {
                    'source': url,
                    'title': data['title'],
                    'chunk_id': i
                }
                texts_with_metadata.append((text, metadata))
            
            success = self.add_texts([t[0] for t in texts_with_metadata])
            
            if success:
                self.sources[url] = {
                    'title': data['title'],
                    'chunk_count': len(data['content'])
                }
            return success
            
        except Exception as e:
            print(f"Error adding content from URL: {str(e)}")
            return False
    
    def generate_answer(self, query: str, k: int = None) -> Dict:
        """質問への回答を生成"""
        try:
            # 関連文書の検索
            results = self.search_similar(query, k)
            if not results:
                return {
                    "answer": "申し訳ありませんが、関連する情報が見つかりませんでした。",
                    "sources": []
                }
            
            # コンテキストの作成
            context = "\n\n".join([doc.page_content for doc in results])
            
            # LLMによる回答生成
            answer = self.llm.generate_response(query, context)
            
            # ソース情報の収集
            sources = [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "title": doc.metadata.get("title", "Unknown")
                }
                for doc in results
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return {
                "answer": "エラーが発生しました。",
                "sources": []
            }
    
    def _scrape_url(self, url: str) -> Optional[Dict]:
        """URLからコンテンツを取得"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 不要なタグの削除
            for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
                tag.decompose()
            
            # テキストの抽出と前処理
            paragraphs = []
            for p in soup.find_all(['p', 'article', 'section', 'div']):
                text = self._clean_text(p.get_text())
                if len(text) > 50:  # 短すぎるテキストを除外
                    paragraphs.append(text)
            
            return {
                'title': soup.title.string if soup.title else urlparse(url).netloc,
                'url': url,
                'content': paragraphs
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """テキストのクリーニング"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s。、.,]', '', text)
        return text.strip()