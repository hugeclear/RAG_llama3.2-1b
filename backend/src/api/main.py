from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional, Dict
from ..models.rag_system import RAGSystem
import uvicorn
import asyncio
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="RAG System API",
    description="LLaMA 3.2-1bを使用したRAGシステムのAPI",
    version="1.0.0"
)

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAGシステムのグローバルインスタンス
rag_system = RAGSystem()

# リクエスト/レスポンスモデル
class URLInput(BaseModel):
    url: HttpUrl
    tags: Optional[List[str]] = []

    @validator('url')
    def validate_url(cls, v):
        if not str(v):
            raise ValueError('URL must not be empty')
        return v

class SearchQuery(BaseModel):
    query: str
    k: Optional[int] = 3
    threshold: Optional[float] = 0.0

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query must not be empty')
        return v.strip()

    @validator('k')
    def k_must_be_positive(cls, v):
        if v and v < 1:
            raise ValueError('k must be greater than 0')
        return v

    @validator('threshold')
    def threshold_must_be_valid(cls, v):
        if v and not 0 <= v <= 1:
            raise ValueError('threshold must be between 0 and 1')
        return v

class SearchResult(BaseModel):
    content: str
    source: str
    score: float
    metadata: Optional[Dict] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    processing_time: float
    timestamp: datetime

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    sources: List[Dict]
    last_updated: datetime

# APIエンドポイント
@app.post("/api/documents/add", response_model=Dict)
async def add_document(url_input: URLInput, background_tasks: BackgroundTasks):
    """新しいドキュメントの追加（非同期）"""
    try:
        # バックグラウンドタスクとしてドキュメント追加を実行
        background_tasks.add_task(rag_system.add_from_url, str(url_input.url))
        
        return {
            "status": "accepted",
            "message": "Document processing started",
            "url": str(url_input.url)
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

@app.post("/api/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    """コンテンツの検索と回答生成"""
    try:
        start_time = datetime.now()
        
        # 検索と回答生成
        response = await rag_system.generate_answer(
            query.query,
            query.k,
        )
        
        # 結果の整形
        results = [
            SearchResult(
                content=source["content"],
                source=source["metadata"].get("source", "unknown"),
                score=source.get("score", 0.0),
                metadata=source["metadata"]
            )
            for source in response["sources"]
        ]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SearchResponse(
            query=query.query,
            results=results,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/stats", response_model=SystemStats)
async def get_stats():
    """システム統計の取得"""
    try:
        stats = rag_system.get_statistics()
        return SystemStats(
            total_documents=stats["total_documents"],
            total_chunks=stats["total_chunks"],
            sources=stats["sources"],
            last_updated=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# グローバルなエラーハンドラー
@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 開発サーバー起動用
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)