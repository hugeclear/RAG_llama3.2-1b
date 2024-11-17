import os
import sys
import asyncio
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from src.scrapers.web_scraper import WebScraper

@pytest.mark.asyncio
async def test_single_url_scraping():
    """単一URLのスクレイピングテスト"""
    scraper = WebScraper()
    urls = [
        "https://ja.wikipedia.org/wiki/Python",
        "https://ja.wikipedia.org/wiki/機械学習",
        "https://www.python.org/about/"
    ]
    
    for url in urls:
        print(f"\nTesting scraping of: {url}")
        result = await scraper.scrape(url)
        
        assert result is not None, f"Scraping result should not be None for {url}"
        assert result.title, "Title should not be empty"
        assert len(result.content) > 0, "Content should not be empty"
        
        print(f"Title: {result.title}")
        print(f"Number of paragraphs: {len(result.content)}")
        print("First paragraph preview:")
        print(result.content[0][:100] + "...")

@pytest.mark.asyncio
async def test_bulk_scraping():
    """一括スクレイピングテスト"""
    scraper = WebScraper()
    urls = [
        "https://ja.wikipedia.org/wiki/Python",
        "https://ja.wikipedia.org/wiki/機械学習"
    ]
    
    print("\nTesting bulk scraping...")
    results = await scraper.bulk_scrape(urls)
    
    assert len(results) == len(urls), "Should have results for all URLs"
    for url, result in results.items():
        assert result is not None, f"Should have valid result for {url}"
        print(f"\nResults for {url}:")
        print(f"Title: {result.title}")
        print(f"Paragraphs: {len(result.content)}")

@pytest.mark.asyncio
async def test_error_handling():
    """エラーハンドリングテスト"""
    scraper = WebScraper()
    invalid_url = "https://this-is-an-invalid-url.com"
    
    print(f"\nTesting error handling with invalid URL: {invalid_url}")
    result = await scraper.scrape(invalid_url)
    assert result is None, "Invalid URL should return None"

@pytest.mark.asyncio
async def test_caching():
    """キャッシュ機能のテスト"""
    scraper = WebScraper()
    url = "https://ja.wikipedia.org/wiki/Python"
    
    print("\nTesting caching functionality...")
    
    # First scrape
    start_time = asyncio.get_event_loop().time()
    result1 = await scraper.scrape(url)
    time1 = asyncio.get_event_loop().time() - start_time
    
    # Cached scrape
    start_time = asyncio.get_event_loop().time()
    result2 = await scraper.scrape(url)
    time2 = asyncio.get_event_loop().time() - start_time
    
    assert result1.to_dict() == result2.to_dict()
    assert time2 < time1
    
    print(f"First access time: {time1:.2f}s")
    print(f"Cached access time: {time2:.2f}s")

if __name__ == '__main__':
    asyncio.run(test_single_url_scraping())
    asyncio.run(test_bulk_scraping())
    asyncio.run(test_error_handling())
    asyncio.run(test_caching())