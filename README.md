# RAG System with LLaMA 3.2-1b

[English](#english) | [日本語](#japanese)

---
<a name="english"></a>
# RAG System with LLaMA 3.2-1b [English]

## Overview
A Retrieval-Augmented Generation (RAG) system powered by LLaMA 3.2-1b, designed to provide accurate, context-aware responses by combining web-scraped information with powerful language model capabilities.

## Features
- Web content scraping and knowledge base creation
- Semantic search using vector embeddings
- LLM-powered response generation
- Source tracking and citation
- Multilingual support (English/Japanese)

## System Architecture
- **Web Scraper**: Automated content collection from specified URLs
- **Vector Store**: ChromaDB-based efficient document storage
- **LLM Integration**: LLaMA 3.2-1b for response generation
- **API Layer**: FastAPI-based REST API interface

## Use Cases
1. **Technical Documentation Assistant**
   - Code explanation and examples
   - Technical concept clarification
   - Documentation search and summarization

2. **Research Assistant**
   - Multi-source information gathering
   - Content summarization
   - Source tracking and citation

3. **Custom Knowledge Base**
   - Domain-specific document learning
   - Organization-specific information management
   - Dynamic content updates

## Installation

### Prerequisites
- Python 3.10+
- CUDA compatible GPU (recommended)
- conda environment

### Setup
```bash
# Create conda environment
conda create -n rag python=3.10
conda activate rag

# Install dependencies
pip install -r requirements.txt
```

## Usage
```python
from rag.system import RAGSystem

# Initialize system
rag = RAGSystem()

# Add content from URL
rag.add_from_url("https://example.com/document")

# Query the system
response = rag.get_response("Your question here")
```

## Development Roadmap
- [ ] Multimodal support (images, audio)
- [ ] Advanced search features
- [ ] Conversation history management
- [ ] Performance optimization
- [ ] UI/UX improvements

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---
<a name="japanese"></a>
# RAG システム with LLaMA 3.2-1b [日本語]

## 概要
LLaMA 3.2-1bを活用したRetrieval-Augmented Generation (RAG) システムです。Webスクレイピングで得た情報と言語モデルの機能を組み合わせて、正確でコンテキストを考慮した応答を提供します。

## 主な機能
- Webコンテンツのスクレイピングと知識ベース化
- ベクトル埋め込みを使用した意味検索
- LLMによる回答生成
- ソース追跡と引用
- 多言語対応（日本語/英語）

## システム構成
- **Webスクレイパー**: 指定URLからのコンテンツ自動収集
- **ベクトルストア**: ChromaDBを使用した効率的な文書保存
- **LLM統合**: LLaMA 3.2-1bによる回答生成
- **APIレイヤー**: FastAPIベースのREST APIインターフェース

## ユースケース
1. **技術文書アシスタント**
   - コードの説明と例示
   - 技術概念の解説
   - ドキュメント検索と要約

2. **リサーチアシスタント**
   - 複数ソースからの情報収集
   - コンテンツの要約
   - ソース追跡と引用

3. **カスタム知識ベース**
   - 特定分野の文書学習
   - 組織固有の情報管理
   - 動的なコンテンツ更新

## インストール

### 必要条件
- Python 3.10以上
- CUDA対応GPU（推奨）
- conda環境

### セットアップ
```bash
# conda環境の作成
conda create -n rag python=3.10
conda activate rag

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法
```python
from rag.system import RAGSystem

# システムの初期化
rag = RAGSystem()

# URLからコンテンツを追加
rag.add_from_url("https://example.com/document")

# システムへの問い合わせ
response = rag.get_response("あなたの質問をここに")
```

## 開発ロードマップ
- [ ] マルチモーダル対応（画像、音声）
- [ ] 高度な検索機能
- [ ] 会話履歴の管理
- [ ] パフォーマンス最適化
- [ ] UI/UXの改善

## ライセンス
このプロジェクトはMITライセンスの下で提供されています - 詳細はLICENSEファイルを参照してください。