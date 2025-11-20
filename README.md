# 生成AI議論ファシリテーションシステム

匿名で参加するオンライン議論において、生成AIエージェント群が司会者・分析者として機能し、議論を構造的に管理し、客観的なデータに基づいて結論へと導くシステムです。

## 主な特徴

* **匿名議論:** ユーザー認証なしで誰でも参加可能
* **AIファシリテーション:** Google ADKベースのエージェント群が議論を進行
* **多言語対応:** 英語と日本語の2言語に対応
* **リアルタイム通信:** WebSocketによる即座の情報共有
* **客観的な結論形成:** データ収集と意見要約による構造的な議論管理

## 技術スタック

* **フロントエンド:** Next.js
* **バックエンド:** Python (FastAPI) + WebSocket
* **エージェント基盤:** Google ADK (Agent Development Kit)
* **データベース:** PostgreSQL / Firestore / Redis

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install fastapi uvicorn "google-generativeai>=0.7.0" "google-cloud-aiplatform>=1.52.0"
pip install google-adk
```

### 2. 環境変数の設定

プロジェクトルート（`backend/`ディレクトリと同じ階層）に `.env` ファイルを作成し、以下の環境変数を設定してください：

```bash
# Google Generative AI API キー（必須）
GOOGLE_API_KEY=your_google_api_key_here

# Google Custom Search API（オプション：データ収集機能を使用する場合）
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**APIキーの取得方法:**

1. **Google Generative AI API キー（必須）**
   - [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
   - APIキーを作成
   - `.env` ファイルに `GOOGLE_API_KEY=作成したAPIキー` を追加

2. **Google Custom Search API（検索機能を使用する場合）**
   
   **手順1: Custom Search Engine の作成**
   - [Google Custom Search Engine](https://programmablesearchengine.google.com/controlpanel/create) にアクセス
   - 「新しい検索エンジンを作成」をクリック
   - 「検索するサイト」に `*` を入力（全サイトを検索する場合）
   - 検索エンジン名を入力して作成
   - 作成後、「設定」→「基本設定」から「検索エンジンID」をコピー
   
   **手順2: Custom Search API の有効化**
   - [Google Cloud Console](https://console.cloud.google.com/) にアクセス
   - プロジェクトを選択（または新規作成）
   - 「APIとサービス」→「ライブラリ」に移動
   - 「Custom Search API」を検索して有効化
   
   **手順3: APIキーの作成**
   - 「APIとサービス」→「認証情報」に移動
   - 「認証情報を作成」→「APIキー」を選択
   - 作成したAPIキーをコピー
   - （推奨）APIキーの制限を設定：
     - 「APIキーの制限」→「APIの制限」→「Custom Search API」を選択
   
   **手順4: 環境変数の設定**
   - `.env` ファイルに以下を追加：
     ```
     GOOGLE_SEARCH_API_KEY=作成したAPIキー
     GOOGLE_SEARCH_ENGINE_ID=コピーした検索エンジンID
     ```

**注意:** 
- `.env` ファイルは `.gitignore` に追加して、Gitリポジトリにコミットしないでください。
- Google Custom Search APIは1日100回まで無料で利用できます。それ以上は有料プランが必要です。

## ドキュメント

詳細な仕様書は [docs/SPECIFICATION.md](docs/SPECIFICATION.md) を参照してください。

## プロジェクト構成

```
/my_project_root (プロジェクトのルート)
├── /frontend/           <-- Next.js (フロントエンド) http://localhost:3000
│   ├── /app/
│   │   └── page.tsx
│   └── ...
│
├── /backend/            <-- Python (バックエンド / API) http://localhost:8000
│   ├── agents/
│   ├── tools/
│   ├── utils/
│   └── main.py
│
└── /docs/               <-- ドキュメント
    └── SPECIFICATION.md
```
