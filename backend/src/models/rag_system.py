from typing import Dict, List, Optional
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .llm_model import LlamaModel, CodeLlamaModel  # CodeLlamaModelをインポート
import requests
from bs4 import BeautifulSoup
import logging
import os
import io
import numpy as np
from PyPDF2 import PdfReader
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, model_type: str = "llama"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small",
            model_kwargs={'device': 'cuda'}
        )
        
        # 2つのベクトルストアのパスを設定
        self.persist_directory_general = "./data/chroma_db_general"
        self.persist_directory_code = "./data/chroma_db_code"
        os.makedirs(self.persist_directory_general, exist_ok=True)
        os.makedirs(self.persist_directory_code, exist_ok=True)
        
        # 2つのベクトルストアの初期化
        self.vectorstore_general = Chroma(
            persist_directory=self.persist_directory_general,
            embedding_function=self.embeddings,
            collection_name="general_documents"
        )
        
        self.vectorstore_code = Chroma(
            persist_directory=self.persist_directory_code,
            embedding_function=self.embeddings,
            collection_name="code_documents"
        )
        
        # モデルの初期化
        self.model_classes = {
            "llama": LlamaModel,
            "codellama": CodeLlamaModel
        }
        
        self.model_type = model_type
        self.llm = self._initialize_model(model_type)
        
        # ソース管理用（カテゴリ別）
        self.sources = {
            "general": {},
            "code": {}
        }
        
        # チャンクサイズの設定
        self.chunk_size = 500
        self.chunk_overlap = 50
        
        # トークナイザーの初期化
        self.tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-small")

    def _initialize_model(self, model_type: str):
        """モデルの初期化"""
        if model_type not in self.model_classes:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = self.model_classes[model_type]
        return model_class()
    async def clear_database(self, category: str = None) -> bool:
        """データベースのクリア（カテゴリ指定可能）"""
        try:
            logger.info(f"Clearing database for category: {category if category else 'all'}")
            
            if category in ['general', None]:
                if os.path.exists(self.persist_directory_general):
                    import shutil
                    shutil.rmtree(self.persist_directory_general)
                    os.makedirs(self.persist_directory_general, exist_ok=True)
                self.vectorstore_general = Chroma(
                    persist_directory=self.persist_directory_general,
                    embedding_function=self.embeddings,
                    collection_name="general_documents"
                )
                self.sources["general"] = {}
                
            if category in ['code', None]:
                if os.path.exists(self.persist_directory_code):
                    import shutil
                    shutil.rmtree(self.persist_directory_code)
                    os.makedirs(self.persist_directory_code, exist_ok=True)
                self.vectorstore_code = Chroma(
                    persist_directory=self.persist_directory_code,
                    embedding_function=self.embeddings,
                    collection_name="code_documents"
                )
                self.sources["code"] = {}
            
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            logger.exception(e)
            return False

    def chunk_text(self, text: str) -> List[str]:
        """テキストを指定されたトークン数で分割"""
        try:
            tokens = self.tokenizer.encode(text)
            chunks = []
            
            start = 0
            while start < len(tokens):
                end = start + self.chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                chunks.append(chunk_text)
                start += (self.chunk_size - self.chunk_overlap)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return [text]

    async def add_from_url(self, url: str, category: str = "general") -> bool:
        """URLからコンテンツを追加（カテゴリ指定可能）"""
        try:
            logger.info(f"Scraping content from URL: {url} for category: {category}")
            
            if category not in ["general", "code"]:
                logger.error(f"Invalid category: {category}")
                return False
            
            # Webページの取得
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=100)
            response.raise_for_status()
            
            text_content = []
            title = url

            # PDFの処理
            if url.lower().endswith('.pdf'):
                text_content, title = self._process_pdf(response.content, url)
            # Wikipediaの処理
            elif 'wikipedia.org' in url:
                text_content, title = self._process_wikipedia(response.content, url)
            # 通常のWebページの処理
            else:
                text_content, title = self._process_webpage(response.content, url)

            if not text_content:
                logger.warning(f"No content extracted from {url}")
                return False

            logger.info(f"Extracted {len(text_content)} chunks from {url}")
            
            # メタデータの準備
            metadata = [
                {
                    'source': url,
                    'title': title,
                    'timestamp': datetime.now().isoformat(),
                    'chunk_index': i,
                    'total_chunks': len(text_content),
                    'category': category
                }
                for i in range(len(text_content))
            ]
            
            # カテゴリに応じたベクトルストアを選択
            vectorstore = self.vectorstore_code if category == "code" else self.vectorstore_general
            
            # ベクトルストアに追加
            try:
                vectorstore.add_texts(
                    texts=text_content,
                    metadatas=metadata
                )
                
                # ソース情報の保存
                self.sources[category][url] = {
                    'title': title,
                    'chunk_count': len(text_content),
                    'added_at': datetime.now().isoformat(),
                    'content_type': 'pdf' if url.lower().endswith('.pdf') else 'web',
                    'category': category
                }
                
                logger.info(f"Successfully added content from {url} with {len(text_content)} chunks to {category} database")
                return True
                
            except Exception as e:
                logger.error(f"Error adding chunks to vector store: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding content from URL: {str(e)}")
            return False

    async def generate_answer(self, query: str, k: int = 2, model_type: str = None) -> Dict:
        """Generate an answer using the specified model"""
        try:
            if model_type and model_type != self.model_type:
                self.model_type = model_type
                self.llm = self._initialize_model(model_type)

            # モデルタイプに応じてベクトルストアを選択
            vectorstore = self.vectorstore_code if model_type == "codellama" else self.vectorstore_general
            
            # 関連文書の検索
            docs = vectorstore.similarity_search_with_relevance_scores(query, k=k)
            
            if not docs:
                return {
                    'answer': f"申し訳ありません。お探しの情報が見つかりませんでした。",
                    'sources': []
                }

            relevant_docs = []
            for doc, score in docs:
                if score >= 0.5:
                    relevant_docs.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': score
                    })

            if not relevant_docs:
                return {
                    'answer': f"関連する情報が見つかりませんでした。",
                    'sources': []
                }

            # コンテキストの構築
            context = "\n\n---\n\n".join([
                f"{doc['content']}\nSource: {doc['metadata'].get('source', 'Unknown')}"
                for doc in relevant_docs
            ])

            # モデルに応じてプロンプトを選択
            if model_type == "codellama":
                prompt = f"""You are an expert programmer. Please answer the following question about programming or technical topics based on the provided context.

Question: {query}

Context:
{context}

Answer:"""
            else:
                prompt = f"""You are medical expert Assistant. Please answer the following question based on the provided context.

Question: {query}

Context:
{context}

Answer:"""

            response = await self.llm.generate_response(
                prompt,
                max_length=2048,
                temperature=0.7,
                top_p=0.9
            )

            if not response:
                return {
                    'answer': "申し訳ありません。回答を生成できませんでした。",
                    'sources': []
                }

            return {
                'answer': response,
                'sources': [
                    {
                        'content': doc['content'],
                        'metadata': doc['metadata'],
                        'relevance_score': float(doc['score'])
                    }
                    for doc in relevant_docs
                ]
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            logger.exception(e)
            return {
                'answer': '回答の生成中にエラーが発生しました。',
                'sources': []
            }

    def get_statistics(self) -> Dict:
        """システムの統計情報を取得（カテゴリ別）"""
        try:
            stats = {
                "general": {
                    "total_documents": len(self.sources["general"]),
                    "total_chunks": len(self.vectorstore_general.get()["ids"]),
                    "sources": [
                        {
                            "url": url,
                            "title": info["title"],
                            "chunks": info["chunk_count"],
                            "added_at": info["added_at"]
                        }
                        for url, info in self.sources["general"].items()
                    ]
                },
                "code": {
                    "total_documents": len(self.sources["code"]),
                    "total_chunks": len(self.vectorstore_code.get()["ids"]),
                    "sources": [
                        {
                            "url": url,
                            "title": info["title"],
                            "chunks": info["chunk_count"],
                            "added_at": info["added_at"]
                        }
                        for url, info in self.sources["code"].items()
                    ]
                }
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "general": {"total_documents": 0, "total_chunks": 0, "sources": []},
                "code": {"total_documents": 0, "total_chunks": 0, "sources": []}
            }