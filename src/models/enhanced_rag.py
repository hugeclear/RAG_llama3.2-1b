from .base_rag import RAGBase
from ..scrapers.web_scraper import WebScraper

class EnhancedRAG(RAGBase):
    def __init__(self):
        super().__init__()
        self.scraper = WebScraper()
        self.sources = {}
    
    def add_from_url(self, url: str) -> bool:
        try:
            data = self.scraper.scrape_url(url)
            if not data:
                return False
            
            texts_with_metadata = []
            for i, text in enumerate(data['content']):
                metadata = {
                    'source': url,
                    'title': data['title'],
                    'chunk_id': i
                }
                texts_with_metadata.append((text, metadata))
            
            success = self.add_texts([t[0] for t in texts_with_metadata])
            
            if success:
                self.sources[url] = {
                    'title': data['title'],
                    'chunk_count': len(data['content'])
                }
            
            return success
            
        except Exception as e:
            print(f"Error adding content from URL: {str(e)}")
            return False