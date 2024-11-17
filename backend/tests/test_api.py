import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_add_document():
    """ドキュメント追加エンドポイントのテスト"""
    url = "https://ja.wikipedia.org/wiki/Python"
    response = client.post(
        "/api/documents/add",
        json={"url": url}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_search():
    """検索エンドポイントのテスト"""
    # まずドキュメントを追加
    url = "https://ja.wikipedia.org/wiki/Python"
    client.post("/api/documents/add", json={"url": url})
    
    # 検索を実行
    query = "Pythonプログラミング言語の特徴は？"
    response = client.post(
        "/api/search",
        json={"query": query, "k": 3}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_stats():
    """統計情報エンドポイントのテスト"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "sources" in data

def test_error_handling():
    """エラーハンドリングのテスト"""
    # 無効なURL形式のテスト
    response = client.post(
        "/api/documents/add",
        json={"url": "invalid-url"}
    )
    assert response.status_code == 422  # Pydanticのバリデーションエラー
    
    # 空のクエリのテスト
    response = client.post(
        "/api/search",
        json={"query": ""}
    )
    assert response.status_code == 422  # Pydanticのバリデーションエラー
    assert "query" in response.json()["detail"][0]["loc"]
    
    # 不正なkの値のテスト
    response = client.post(
        "/api/search",
        json={"query": "test", "k": -1}
    )
    assert response.status_code == 422
    assert "k" in response.json()["detail"][0]["loc"]
    
    # 不正なthresholdのテスト
    response = client.post(
        "/api/search",
        json={"query": "test", "threshold": 2.0}
    )
    assert response.status_code == 422
    assert "threshold" in response.json()["detail"][0]["loc"]
    
    # 存在しないエンドポイントのテスト
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

def test_malformed_requests():
    """不正な形式のリクエストのテスト"""
    # JSONでない入力
    response = client.post(
        "/api/search",
        data="not a json"
    )
    assert response.status_code == 422
    
    # 必須フィールドの欠落
    response = client.post(
        "/api/search",
        json={}
    )
    assert response.status_code == 422
    assert "query" in response.json()["detail"][0]["loc"]

if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])