import requests
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from readability import Document
import trafilatura
from typing import Dict, Optional, List, Union
import re
from urllib.parse import urlparse
import concurrent.futures
from functools import lru_cache
import logging
from datetime import datetime
import hashlib
import warnings
from dataclasses import dataclass
import json
import asyncio

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingResult:
    title: str
    content: List[str]
    url: str
    scraped_at: str
    metadata: Dict = None

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'scraped_at': self.scraped_at,
            'metadata': self.metadata or {}
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        }
        self.session = requests.Session()
        self.cache = {}

    def _get_url_content(self, url: str) -> Optional[str]:
        """URLからコンテンツを取得"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None

    def _extract_with_readability(self, html: str) -> Optional[Dict]:
        """Readabilityを使用してメインコンテンツを抽出"""
        try:
            doc = Document(html)
            return {
                'title': doc.title(),
                'content': doc.summary()
            }
        except Exception as e:
            logger.error(f"Readability extraction error: {str(e)}")
            return None

    def _clean_text(self, text: str) -> str:
        """テキストのクリーニング処理"""
        if not isinstance(text, str):
            return ""

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            text = BeautifulSoup(text, 'html.parser').get_text()

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'　', ' ', text)
        
        # 英語と日本語の両方を許可
        text = re.sub(r'[^\w\s。、々ぁ-んァ-ン一-龥()（）\[\]「」『』.,\-\'\"0-9A-Za-z]', '', text)
        
        return text.strip()

    def _is_valid_content(self, text: str) -> bool:
        """コンテンツの妥当性チェック"""
        if not text or len(text) < 30:  # 最小文字数を30に変更
            return False
        
        # 日本語または英語の文字が含まれているかチェック
        has_japanese = bool(re.search(r'[ぁ-んァ-ン一-龥]', text))
        has_english = bool(re.search(r'[A-Za-z]', text))
        
        return has_japanese or has_english

    async def scrape(self, url: str) -> Optional[ScrapingResult]:
        """メインのスクレイピング処理"""
        try:
            logger.info(f"Starting scrape of URL: {url}")
            
            cache_key = hashlib.md5(url.encode()).hexdigest()
            if cache_key in self.cache:
                logger.info(f"Cache hit for URL: {url}")
                cached_result = self.cache[cache_key]
                return ScrapingResult(**cached_result)

            html = self._get_url_content(url)
            if not html:
                return None

            readability_result = self._extract_with_readability(html)
            if not readability_result:
                return None

            soup = BeautifulSoup(readability_result['content'], 'html.parser')
            paragraphs = []
            
            for p in soup.find_all(['p', 'article', 'section', 'div']):
                text = self._clean_text(p.get_text())
                if self._is_valid_content(text):
                    paragraphs.append(text)

            if not paragraphs:
                logger.warning(f"No valid content found for URL: {url}")
                return None

            result = ScrapingResult(
                title=readability_result['title'],
                content=paragraphs,
                url=url,
                scraped_at=datetime.now().isoformat(),
                metadata={
                    'paragraph_count': len(paragraphs),
                    'source_domain': urlparse(url).netloc
                }
            )

            self.cache[cache_key] = result.to_dict()
            
            logger.info(f"Successfully scraped URL: {url}")
            return result

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None

    async def bulk_scrape(self, urls: List[str]) -> Dict[str, Optional[ScrapingResult]]:
        """複数URLの一括スクレイピング"""
        results = {}
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.scrape(url))
            tasks.append((url, task))
        
        for url, task in tasks:
            try:
                results[url] = await task
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                results[url] = None
        
        return results

    def clear_cache(self):
        """キャッシュのクリア"""
        self.cache.clear()