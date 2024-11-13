from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from ..models.rag_system import RAGSystem
import uvicorn

app = FastAPI(
    title="RAG API",
    description="LLaMA 3.2-1bを使用したRAGシステムのAPI",
    version="1.0.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAGシステムのインスタンス
rag_system = RAGSystem()

class URLInput(BaseModel):
    url: str

class SearchQuery(BaseModel):
    query: str
    k: Optional[int] = 3

class SearchResult(BaseModel):
    content: str
    source: Optional[str] = None
    relevance_score: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.post("/api/add-url")
async def add_url(url_input: URLInput):
    """URLからコンテンツを追加"""
    success = rag_system.add_from_url(url_input.url)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add URL content")
    return {
        "status": "success",
        "message": "Content added successfully",
        "url": url_input.url
    }

@app.post("/api/search")
async def search(query: SearchQuery):
    """コンテンツの検索"""
    results = rag_system.search_similar(query.query, query.k)
    
    formatted_results = [
        SearchResult(
            content=doc.page_content,
            source=doc.metadata.get('source', 'Unknown'),
            relevance_score=doc.metadata.get('score', None)
        )
        for doc in results
    ]
    
    return SearchResponse(results=formatted_results)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)