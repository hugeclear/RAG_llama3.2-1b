# RAG System Frontend

## Overview (English)
This is the frontend application for the RAG (Retrieval-Augmented Generation) System. It is built using React and TypeScript, and interacts with a backend API powered by LLaMA 3.2-1b to perform document management, search, system statistics, and health checks. This README will guide you through setting up the environment, running the application, and understanding its features.

### Features
- **Add Document**: Users can add a document to the backend system.
- **Search**: Users can perform searches on existing documents using keywords.
- **System Stats**: View the system statistics, including document count and other relevant metadata.
- **Health Check**: Check the current health status of the backend system.

### Requirements
- Node.js and npm installed on your machine.
- Backend API server for the RAG system running locally or remotely.

### Installation and Setup
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd RAG_llama3.2-1b/frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. Run the development server:
   ```sh
   npm run dev
   ```

   The development server should now be running, usually on `http://localhost:3000`. Open this in your web browser.

4. Backend API Setup
   - Ensure the backend API server is running. The frontend expects it to be available at `http://127.0.0.1:8000`.
   - You can start the backend by running:
     ```sh
     uvicorn main:app --reload
     ```

### Navigation
- **Homepage**: A navigation menu provides links to add documents, search documents, view system stats, and perform health checks.
- **Page Links**: Click on any link in the navigation bar to go to that respective page.
- **Programmatic Navigation**: Certain actions, like adding a document successfully, will automatically redirect the user to a relevant page.

### Adding Documents
- Navigate to the **Add Document** page.
- Enter the document content in the provided textarea and click **Add Document**.
- Upon successful submission, you will be redirected to the homepage.

### Performing a Search
- Navigate to the **Search** page.
- Enter a search query and click **Search**.
- The results will be displayed in a list below the search bar.

### Viewing System Stats
- Navigate to the **System Stats** page.
- You can see information about the number of documents, chunks, and last updated timestamps.

### Health Check
- Navigate to the **Health Check** page.
- The current health status of the system will be displayed.

### Notes on Further Enhancements
- **Styling**: Currently, the UI is minimal. Styling can be improved using CSS libraries like Tailwind CSS or styled-components.
- **Authentication**: Future iterations might include user authentication to restrict access to certain features.
- **Error Handling**: Better error feedback is recommended to enhance the user experience.

## 概要 (日本語)
このフロントエンドアプリケーションは、RAG（Retrieval-Augmented Generation）システム用です。ReactとTypeScriptを使用して構築されており、バックエンドAPI（LLaMA 3.2-1b）と連携してドキュメント管理、検索、システム統計、ヘルスチェックの機能を提供します。このREADMEでは、環境のセットアップ、アプリケーションの実行、および機能の理解について説明します。

### 機能
- **ドキュメントの追加**: ユーザーはバックエンドシステムにドキュメントを追加できます。
- **検索**: 既存のドキュメントをキーワードで検索できます。
- **システム統計**: ドキュメント数など、システムに関する統計情報を表示します。
- **ヘルスチェック**: バックエンドシステムの現在の稼働状態を確認します。

### 必要条件
- Node.jsおよびnpmがインストールされていること。
- ローカルまたはリモートで稼働中のRAGシステム用バックエンドAPIサーバー。

### インストールとセットアップ
1. リポジトリをクローンします:
   ```sh
   git clone <repository_url>
   cd RAG_llama3.2-1b/frontend
   ```

2. 依存関係をインストールします:
   ```sh
   npm install
   ```

3. 開発サーバーを起動します:
   ```sh
   npm run dev
   ```

   開発サーバーは通常、`http://localhost:3000`で稼働します。ウェブブラウザでこのURLを開いてください。

4. バックエンドAPIのセットアップ
   - バックエンドAPIサーバーが稼働していることを確認してください。フロントエンドは、`http://127.0.0.1:8000`で利用できることを期待しています。
   - 以下のコマンドでバックエンドを起動できます:
     ```sh
     uvicorn main:app --reload
     ```

### ナビゲーション
- **ホームページ**: ナビゲーションメニューから、ドキュメントの追加、検索、システム統計の表示、ヘルスチェックへのリンクが利用可能です。
- **ページリンク**: ナビゲーションバーのリンクをクリックすると、該当するページに移動できます。
- **プログラムによるナビゲーション**: ドキュメント追加の成功時など、特定のアクション後には自動的に関連ページへリダイレクトされます。

### ドキュメントの追加
- **Add Document**ページに移動します。
- ドキュメント内容をテキストエリアに入力し、**Add Document**ボタンをクリックします。
- 正常に送信されると、ホームページにリダイレクトされます。

### 検索の実行
- **Search**ページに移動します。
- 検索クエリを入力して、**Search**ボタンをクリックします。
- 結果が検索バーの下にリスト形式で表示されます。

### システム統計の表示
- **System Stats**ページに移動します。
- ドキュメント数、チャンク数、最終更新日時などの情報が表示されます。

### ヘルスチェック
- **Health Check**ページに移動します。
- システムの現在の稼働状態が表示されます。

### 今後の改善についてのメモ
- **スタイリング**: 現在のUIはシンプルです。Tailwind CSSやstyled-componentsなどのCSSライブラリを使用して、UIを改善することが推奨されます。
- **認証**: 今後のバージョンでは、特定の機能へのアクセスを制限するためのユーザー認証を追加することが考えられます。
- **エラーハンドリング**: より良いエラーフィードバックを提供することで、ユーザーエクスペリエンスを向上させることができます。

これで、システム全体の動作や機能についてREADMEに追加する内容が完成しました。追加の説明や修正が必要な場合は、気軽に教えてください。

