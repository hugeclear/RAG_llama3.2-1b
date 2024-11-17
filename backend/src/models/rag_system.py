# from typing import List, Dict, Optional
# from .llm_model import LlamaModel
# from ..scrapers.web_scraper import WebScraper, ScrapingResult
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores.chroma import Chroma
# import chromadb
# import logging
# import os
# from datetime import datetime
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class RAGSystem:
#     def __init__(self):
#         """RAGシステムの初期化"""
#         logger.info("Initializing RAG System...")
        
#         # 保存ディレクトリの作成
#         os.makedirs("./data/chroma_db", exist_ok=True)
        
#         self.scraper = WebScraper()
#         self.llm = LlamaModel()
        
#         # 埋め込みモデルの設定
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="intfloat/multilingual-e5-small",
#             model_kwargs={'device': 'cuda'}
#         )
        
#         # ChromaDBクライアントの設定
#         self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
#         self.collection = self.chroma_client.get_or_create_collection(
#             name="rag_documents",
#             metadata={"hnsw:space": "cosine"}
#         )
        
#         # Chromaのラッパー
#         self.vectorstore = Chroma(
#             client=self.chroma_client,
#             collection_name="rag_documents",
#             embedding_function=self.embeddings,
#             persist_directory="./data/chroma_db"
#         )
        
#         # ソース情報の保存用
#         self.sources: Dict[str, ScrapingResult] = {}
        
#         logger.info("RAG System initialized successfully")

#     async def add_document(self, url: str) -> bool:
#         """URLからドキュメントを追加"""
#         try:
#             logger.info(f"Adding document from URL: {url}")
            
#             content = await self.scraper.scrape(url)
#             if not content:
#                 logger.warning(f"Failed to scrape content from {url}")
#                 return False
            
#             # メタデータの準備
#             texts = content.content
#             metadatas = [
#                 {
#                     'source': url,
#                     'title': content.title,
#                     'scraped_at': content.scraped_at,
#                     'chunk_id': str(i)
#                 }
#                 for i in range(len(texts))
#             ]
#             ids = [f"doc_{url}_{i}" for i in range(len(texts))]
            
#             # ベクトルストアへの追加
#             self.vectorstore.add_texts(
#                 texts=texts,
#                 metadatas=metadatas,
#                 ids=ids
#             )
            
#             # ソース情報の保存
#             self.sources[url] = content
            
#             logger.info(f"Successfully added document from {url}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error adding document from {url}: {str(e)}")
#             return False

#     async def search_documents(self, query: str, k: int = 3) -> List[Dict]:
#         """関連文書の検索"""
#         try:
#             logger.info(f"Searching documents for query: {query}")
            
#             # 類似度検索の実行
#             results = self.vectorstore.similarity_search(
#                 query,
#                 k=k
#             )
            
#             # 結果の整形
#             formatted_results = []
#             for doc in results:
#                 formatted_results.append({
#                     'content': doc.page_content,
#                     'metadata': doc.metadata,
#                     'similarity_score': None  # 現在のバージョンではスコアは利用不可
#                 })
            
#             return formatted_results
            
#         except Exception as e:
#             logger.error(f"Error searching documents: {str(e)}")
#             return []

#     async def generate_response(
#         self,
#         query: str,
#         k: int = 3,
#         max_length: int = 300
#     ) -> Dict:
#         """質問への回答を生成"""
#         try:
#             logger.info(f"Generating response for query: {query}")
            
#             # 関連文書の検索
#             relevant_docs = await self.search_documents(query, k)
#             if not relevant_docs:
#                 return {
#                     'answer': '申し訳ありません。関連する情報が見つかりませんでした。',
#                     'sources': [],
#                     'error': None
#                 }
            
#             # コンテキストの構築
#             context = "\n\n".join([doc['content'] for doc in relevant_docs])
            
#             # プロンプトの構築
#             prompt = f"""以下の情報に基づいて質問に答えてください。

# 参考情報：
# {context}

# 質問：{query}

# 回答："""
            
#             # LLMによる回答生成
#             response = await self.llm.generate_response(
#                 prompt,
#                 max_length=max_length
#             )
            
#             return {
#                 'answer': response,
#                 'sources': relevant_docs,
#                 'error': None
#             }
            
#         except Exception as e:
#             error_msg = str(e)
#             logger.error(f"Error generating response: {error_msg}")
#             return {
#                 'answer': '申し訳ありません。エラーが発生しました。',
#                 'sources': [],
#                 'error': error_msg
#             }

#     def get_statistics(self) -> Dict:
#         """システムの統計情報を取得"""
#         try:
#             total_docs = len(self.sources)
#             total_chunks = len(self.collection.get()['ids'])
            
#             return {
#                 'total_documents': total_docs,
#                 'total_chunks': total_chunks,
#                 'sources': [
#                     {
#                         'url': url,
#                         'title': source.title,
#                         'paragraphs': len(source.content),
#                         'scraped_at': source.scraped_at
#                     }
#                     for url, source in self.sources.items()
#                 ]
#             }
#         except Exception as e:
#             logger.error(f"Error getting statistics: {str(e)}")
#             return {
#                 'total_documents': 0,
#                 'total_chunks': 0,
#                 'sources': []
#             }

#     def __del__(self):
#         """クリーンアップ処理"""
#         try:
#             # 明示的にクライアントを閉じる
#             if hasattr(self, 'chroma_client'):
#                 self.chroma_client._client.close()
#         except Exception as e:
#             logger.error(f"Error during cleanup: {str(e)}")
from typing import Dict, List, Optional
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .llm_model import LlamaModel
import requests
from bs4 import BeautifulSoup
import logging
import os

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        # 埋め込みモデルの初期化
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small",
            model_kwargs={'device': 'cuda'}
        )
        
        # ベクトルストアの初期化
        os.makedirs("./data/chroma_db", exist_ok=True)
        self.vectorstore = Chroma(
            persist_directory="./data/chroma_db",
            embedding_function=self.embeddings
        )
        
        # LLMの初期化
        self.llm = LlamaModel()
        
        # ソース管理用
        self.sources = {}

    async def add_from_url(self, url: str) -> bool:
        """URLからコンテンツを追加"""
        try:
            logger.info(f"Scraping content from URL: {url}")
            
            # Webページの取得
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # HTMLの解析
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else url
            
            # メインコンテンツの抽出
            text_content = []
            for p in soup.find_all(['p', 'article', 'section']):
                text = p.get_text().strip()
                if len(text) > 50:  # 短すぎるテキストを除外
                    text_content.append(text)
            
            if not text_content:
                logger.warning(f"No content found in {url}")
                return False
            
            # メタデータの準備
            metadata = [
                {
                    'source': url,
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                }
                for _ in text_content
            ]
            
            # ベクトルストアに追加
            self.vectorstore.add_texts(
                texts=text_content,
                metadatas=metadata
            )
            
            # ソース情報の保存
            self.sources[url] = {
                'title': title,
                'chunk_count': len(text_content),
                'added_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully added content from {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding content from URL: {str(e)}")
            return False

    async def generate_answer(
        self,
        query: str,
        k: int = 3,
        threshold: float = 0.0
    ) -> Dict:
        """質問への回答を生成"""
        try:
            # 関連文書の検索
            docs = self.vectorstore.similarity_search(query, k=k)
            
            if not docs:
                return {
                    "answer": "申し訳ありません。関連する情報が見つかりませんでした。",
                    "sources": []
                }
            
            # コンテキストの構築
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # プロンプトの構築
            prompt = f"""以下の情報に基づいて質問に答えてください。

参考情報:
{context}

質問: {query}

回答:"""
            
            # LLMで回答を生成
            answer = await self.llm.generate_response(
                prompt,
                max_length=300
            )
            
            # ソース情報の準備
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.0  # 現在のバージョンではスコアは利用不可
                }
                for doc in docs
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "エラーが発生しました。",
                "sources": []
            }

    def get_statistics(self) -> Dict:
        """システムの統計情報を取得"""
        try:
            return {
                "total_documents": len(self.sources),
                "total_chunks": len(self.vectorstore.get()["ids"]),
                "sources": [
                    {
                        "url": url,
                        "title": info["title"],
                        "chunks": info["chunk_count"],
                        "added_at": info["added_at"]
                    }
                    for url, info in self.sources.items()
                ]
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "sources": []
            }