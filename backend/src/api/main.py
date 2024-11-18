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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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
    metadata: Optional[Dict] = None # "source"を"metadata"内部に移動

class SearchResponse(BaseModel):
    query: Optional[str] = None
    answer: str
    sources: List[SearchResult]
    processing_time: Optional[float] = None
    timestamp: Optional[datetime] = None

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    sources: List[Dict[str, str]]
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

@app.post("/api/search")
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
        sources = [
            SearchResult(
                content=source["content"],
                metadata=source.get("metadata", {})
            )
            for source in response["sources"]
        ]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SearchResponse(
            answer=response["answer"],
            sources=sources,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        logger.exception(e)  # スタックトレースを出力
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

# main.py に追加
@app.post("/api/database/clear", response_model=Dict)
async def clear_database():
    """データベースの全データを削除"""
    try:
        success = await rag_system.clear_database()
        if success:
            return {
                "status": "success",
                "message": "Database cleared successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear database"
            )
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing database: {str(e)}"
        )

@app.get("/api/stats", response_model=SystemStats)
async def get_stats():
    """システム統計の取得"""
    try:
        stats = rag_system.get_statistics()
        sources = [
            {
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "chunk_count": source.get("chunk_count", 0),
                "added_at": source.get("added_at", ""),
            }
            for source in stats["sources"]
        ]
        return SystemStats(
            total_documents=stats["total_documents"],
            total_chunks=stats["total_chunks"],
            sources=sources,
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