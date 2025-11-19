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

### 必要なパッケージのインストール

```bash
pip install fastapi uvicorn "google-generativeai>=0.7.0" "google-cloud-aiplatform>=1.52.0"
pip install google-adk
```

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
