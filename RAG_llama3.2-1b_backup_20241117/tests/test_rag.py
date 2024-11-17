import unittest
from src.models.enhanced_rag import EnhancedRAG

class TestRAG(unittest.TestCase):
    def setUp(self):
        self.rag = EnhancedRAG()
    
    def test_url_scraping(self):
        url = "https://ja.wikipedia.org/wiki/Python"
        success = self.rag.add_from_url(url)
        self.assertTrue(success)
        
        # 検索テスト
        query = "Pythonプログラミング言語について"
        results = self.rag.search_similar(query)
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)

if __name__ == '__main__':
    unittest.main()