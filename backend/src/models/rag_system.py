from typing import Dict, List, Optional
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .llm_model import LlamaModel
import requests
from bs4 import BeautifulSoup
import logging
import os
import io
import numpy as np
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small",
            model_kwargs={'device': 'cuda'}
        )
        
        # ベクトルストアのパスを設定
        self.persist_directory = "./data/chroma_db"
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # ベクトルストアの初期化
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        
        self.llm = LlamaModel()
        self.sources = {}
        
        # チャンクサイズの設定
        self.chunk_size = 500  # トークン数
        self.chunk_overlap = 50  # オーバーラップするトークン数

    async def clear_database(self) -> bool:
        """ベクトルストアとソース情報を完全に削除"""
        try:
            logger.info("Clearing vector store and source information...")
            
            # Chromaデータベースの削除
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
                os.makedirs(self.persist_directory, exist_ok=True)
            
            # ベクトルストアの再初期化
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # ソース情報のクリア
            self.sources = {}
            
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            logger.exception(e)
            return False

    def chunk_text(self, text: str) -> List[str]:
        """テキストを指定されたトークン数で分割"""
        try:
            from transformers import AutoTokenizer
            
            # トークナイザーの初期化
            tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-small")
            
            # テキストのトークン化
            tokens = tokenizer.encode(text)
            chunks = []
            
            # チャンクの作成
            start = 0
            while start < len(tokens):
                end = start + self.chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                chunks.append(chunk_text)
                start += (self.chunk_size - self.chunk_overlap)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return [text]  # エラーの場合は元のテキストを1つのチャンクとして返す

    def calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """ベクトル間のコサイン類似度を計算"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def search_documents(self, query: str, k: int = 3, threshold: float = 0.5) -> List[Dict]:
        """MMRを使用して関連文書を検索"""
        try:
            # クエリの埋め込みを取得
            query_embedding = self.embeddings.embed_query(query)

            # より多くの候補を取得
            fetch_k = min(k * 3, 15)  # 初期候補数を増やす
            lambda_mult = 0.8  # 類似性をより重視

            # MMR検索の実行
            results = self.vectorstore.max_marginal_relevance_search(
                query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult,
            )

            # より厳密な類似度チェックとフィルタリング
            filtered_results = []
            for doc in results:
                doc_embedding = self.embeddings.embed_documents([doc.page_content])[0]
                similarity = self.calculate_cosine_similarity(query_embedding, doc_embedding)
                
                # 類似度の閾値を調整
                if similarity >= threshold:
                    # キーワードマッチングによる追加フィルタリング
                    query_words = set(query.lower().split())
                    content_words = set(doc.page_content.lower().split())
                    word_overlap = len(query_words & content_words)
                    
                    if word_overlap > 0:  # 少なくとも1つのキーワードが一致
                        filtered_results.append({
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'similarity_score': similarity,
                            'keyword_match': word_overlap
                        })

            # 類似度とキーワードマッチの組み合わせでソート
            filtered_results.sort(key=lambda x: (x['similarity_score'], x['keyword_match']), reverse=True)
            
            logger.info(f"Found {len(filtered_results)} relevant documents")
            return filtered_results

        except Exception as e:
            logger.error(f"Error in document search: {str(e)}")
            logger.exception(e)
            return []

    async def generate_answer(self, query: str, k: int = 2) -> Dict:  # k=2に変更
        """Generate an answer to the question"""
        try:
            # 上位2つの関連文書を検索
            docs = self.vectorstore.similarity_search_with_relevance_scores(query, k=1)
            
            if not docs:
                return {
                    'answer': f"申し訳ありません。お探しの情報が見つかりませんでした。",
                    'sources': []
                }

            # 関連性の高い文書を抽出
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

            # コンテキストの構築（シンプルに）
            context = "\n\n---\n\n".join([
                f"{doc['content']}\nSource: {doc['metadata'].get('source', 'Unknown')}"
                for doc in relevant_docs
            ])

            # シンプルなプロンプト
            prompt = f"""As a medical expert using the RAG system, please provide a detailed explanation based on the search results.
Please consider the following context carefully and provide a comprehensive answer.

Question: {query}

Instructions:
1. Base your answer strictly on the provided context
2. If the information is medical in nature, include relevant medical details
3. If the information is not medical or not relevant, clearly state so
4. Use bullet points or numbered lists where appropriate
5. Include relevant source references when applicable

Context:
{context}


"""
            prompt_alpha = 'answer:'
            prompt_final = prompt + prompt_alpha
            # 回答生成
            response = await self.llm.generate_response(
                prompt_final,
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

    async def add_from_url(self, url: str) -> bool:
        """URLからコンテンツを追加"""
        try:
            logger.info(f"Scraping content from URL: {url}")
            
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
                try:
                    pdf_file = io.BytesIO(response.content)
                    pdf_reader = PdfReader(pdf_file)
                    
                    # PDFから全テキストを抽出
                    raw_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            raw_text += text + "\n\n"
                    
                    # 抽出したテキストをチャンク分割
                    text_content = self.chunk_text(raw_text)
                    title = url.split('/')[-1]
                    
                except Exception as e:
                    logger.error(f"Error processing PDF: {str(e)}")
                    return False

            # Wikipediaの処理
            elif 'wikipedia.org' in url:
                soup = BeautifulSoup(response.content, 'html.parser')
                main_content = soup.find('div', {'id': 'mw-content-text'})
                
                if main_content:
                    # 不要な要素を削除
                    for unwanted in main_content.find_all(['table', 'style', 'script', 'sup']):
                        unwanted.decompose()
                    
                    # タイトルの取得
                    title = soup.title.string if soup.title else url
                    
                    # メインコンテンツの抽出と結合
                    raw_text = main_content.get_text()
                    # チャンク分割
                    text_content = self.chunk_text(raw_text)
                else:
                    logger.warning(f"No main content found in Wikipedia page: {url}")
                    return False

            # 通常のWebページの処理
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else url
                
                # メインコンテンツの抽出
                main_elements = soup.find_all(['article', 'main', 'div', 'section'])
                raw_text = ""
                
                for element in main_elements:
                    # スクリプトやスタイルを除去
                    for unwanted in element.find_all(['script', 'style']):
                        unwanted.decompose()
                    
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > 100:  # 意味のある長さのコンテンツのみ
                        raw_text += text + "\n\n"
                
                # チャンク分割
                text_content = self.chunk_text(raw_text)

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
                    'total_chunks': len(text_content)
                }
                for i in range(len(text_content))
            ]
            
            # ベクトルストアに追加
            try:
                self.vectorstore.add_texts(
                    texts=text_content,
                    metadatas=metadata
                )
                
                # ソース情報の保存
                self.sources[url] = {
                    'title': title,
                    'chunk_count': len(text_content),
                    'added_at': datetime.now().isoformat(),
                    'content_type': 'pdf' if url.lower().endswith('.pdf') else 'web'
                }
                
                logger.info(f"Successfully added content from {url} with {len(text_content)} chunks")
                return True
                
            except Exception as e:
                logger.error(f"Error adding chunks to vector store: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding content from URL: {str(e)}")
            return False
    
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