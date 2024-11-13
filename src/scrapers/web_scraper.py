from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
from config.config import SCRAPING_CONFIG

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': SCRAPING_CONFIG["user_agent"]
        }
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s。、.,]', '', text)
        return text.strip()
    
    def extract_main_content(self, soup: BeautifulSoup) -> List[str]:
        for tag in soup(['style', 'script', 'header', 'footer', 'nav']):
            tag.decompose()
        
        paragraphs = []
        for p in soup.find_all(['p', 'article', 'section', 'div']):
            text = self.clean_text(p.get_text())
            if len(text) > SCRAPING_CONFIG["min_text_length"]:
                paragraphs.append(text)
        
        return paragraphs
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=SCRAPING_CONFIG["timeout"]
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else urlparse(url).netloc
            content = self.extract_main_content(soup)
            
            return {
                'title': title,
                'url': url,
                'content': content
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None