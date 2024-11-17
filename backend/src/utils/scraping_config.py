from typing import List

# スクレイピング設定
SCRAPING_CONFIG = {
    # 一般設定
    'timeout': 10,
    'min_text_length': 50,
    'max_retries': 3,
    'cache_size': 100,
    
    # 並列処理設定
    'max_workers': 5,
    'chunk_size': 10,
    
    # 除外するタグ
    'exclude_tags': [
        'script', 'style', 'header', 'footer', 
        'nav', 'aside', 'iframe', 'meta'
    ],
    
    # 抽出するタグ
    'content_tags': [
        'p', 'article', 'section', 'div', 
        'main', 'h1', 'h2', 'h3'
    ],
    
    # 日本語コンテンツの設定
    'japanese': {
        'min_japanese_ratio': 0.3,  # 日本語文字の最小比率
        'keep_symbols': ['。', '、', '々', '「', '」'],
    }
}

# 除外するURLパターン
EXCLUDED_PATTERNS: List[str] = [
    r'.*\.(jpg|jpeg|png|gif|pdf|zip)$',
    r'.*/(login|signin|signup|register).*',
    r'.*/admin/.*',
]