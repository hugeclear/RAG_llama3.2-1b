import pytest
import asyncio
from src.models.rag_system import RAGSystem

@pytest.mark.asyncio
async def test_document_addition():
    """ドキュメント追加のテスト"""
    rag = RAGSystem()
    
    # テスト用URL
    test_urls = [
        "https://ja.wikipedia.org/wiki/Python",
        "https://ja.wikipedia.org/wiki/機械学習"
    ]
    
    print("\nTesting document addition...")
    for url in test_urls:
        success = await rag.add_document(url)
        assert success, f"Failed to add document from {url}"
        print(f"Successfully added document from {url}")

@pytest.mark.asyncio
async def test_document_search():
    """文書検索のテスト"""
    rag = RAGSystem()
    
    # テストデータの追加
    await rag.add_document("https://ja.wikipedia.org/wiki/Python")
    
    print("\nTesting document search...")
    test_queries = [
        "Pythonとは何ですか？",
        "Pythonの特徴を説明してください"
    ]
    
    for query in test_queries:
        results = await rag.search_documents(query, k=2)
        assert len(results) > 0, f"No results found for query: {query}"
        print(f"\nQuery: {query}")
        print(f"Found {len(results)} relevant documents")
        print("First result preview:")
        print(results[0]['content'][:100] + "...")

@pytest.mark.asyncio
async def test_response_generation():
    """応答生成のテスト"""
    rag = RAGSystem()
    
    # テストデータの追加
    await rag.add_document("https://ja.wikipedia.org/wiki/Python")
    
    print("\nTesting response generation...")
    test_query = "Pythonプログラミング言語の主な特徴を3つ挙げてください"
    
    response = await rag.generate_response(test_query)
    
    # より詳細なアサーション
    assert isinstance(response, dict), "Response should be a dictionary"
    assert 'answer' in response, "Response should contain 'answer' key"
    assert 'sources' in response, "Response should contain 'sources' key"
    assert response['answer'], "Answer should not be empty"
    assert len(response['sources']) > 0, "Should have at least one source"
    
    print("\nGenerated response:")
    print(response['answer'])
    print("\nBased on sources:")
    for source in response['sources']:
        print(f"- {source['content'][:100]}...")

@pytest.mark.asyncio
async def test_system_statistics():
    """システム統計のテスト"""
    rag = RAGSystem()
    
    # テストデータの追加
    await rag.add_document("https://ja.wikipedia.org/wiki/Python")
    
    print("\nTesting system statistics...")
    stats = rag.get_statistics()
    
    assert stats['total_documents'] > 0, "No documents found in statistics"
    assert stats['total_chunks'] > 0, "No chunks found in statistics"
    
    print("\nSystem statistics:")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print("\nSources:")
    for source in stats['sources']:
        print(f"- {source['title']}: {source['paragraphs']} paragraphs")

def main():
    """すべてのテストを実行"""
    asyncio.run(test_document_addition())
    asyncio.run(test_document_search())
    asyncio.run(test_response_generation())
    asyncio.run(test_system_statistics())

if __name__ == "__main__":
    main()