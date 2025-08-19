# 検索エンジンエージェント 🔍

AI搭載の次世代検索エンジンエージェント

## 🚀 機能

- **🤖 AI分析**: AWS Bedrock Claude 3による検索クエリの自動分析
- **📹 YouTube検索**: 動画コンテンツの検索と表示
- **🌐 Web検索**: Googleカスタム検索API対応
- **📝 AI要約**: YouTube動画の内容を自動要約
- **💬 対話機能**: 動画について追加質問が可能

## 🛠️ 技術スタック

### フロントエンド
- React 19
- Axios
- 動的API URL設定

### バックエンド
- Flask (Python 3.12)
- AWS Bedrock (Claude 3 Haiku)
- YouTube Data API v3
- Google Custom Search API
- YouTube Transcript API

## 🏠 ローカル環境での使用

### 必要な環境変数

バックエンドディレクトリに `.env` ファイルを作成：

```bash
# AWS Bedrock設定
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# Google Custom Search
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_CX=your_custom_search_engine_id
```

### 📋 セットアップ手順

#### 1. バックエンドの起動

```bash
cd backend
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install -r requirements.txt
python app.py
```

バックエンドは `http://localhost:5000` で起動します。

#### 2. フロントエンドの起動

```bash
cd frontend
npm install
npm start
```

フロントエンドは `http://localhost:3000` で起動します。

### � API キーの取得方法

#### AWS Bedrock
1. AWSコンソールでIAMユーザー作成
2. `AmazonBedrockFullAccess` ポリシーを付与
3. アクセスキー・シークレットキーを取得

#### YouTube Data API
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. YouTube Data API v3 を有効化
3. APIキーを作成

#### Google Custom Search
1. [Google Custom Search Engine](https://cse.google.com/) でカスタム検索エンジン作成
2. 検索エンジンIDを取得
3. [Google Cloud Console](https://console.cloud.google.com/) でCustom Search API を有効化

## 🎯 使用方法

1. **検索キーワード入力**: 検索したい内容を入力
2. **AI分析**: Claude 3がクエリを分析して最適な検索戦略を決定
3. **結果表示**: YouTube動画とWeb検索結果を同時表示
4. **動画要約**: 気になる動画の「📝 AI要約」ボタンをクリック
5. **AI対話**: 要約内容について追加質問が可能

## 📁 プロジェクト構造

```
search-engine-agent/
├── backend/                 # Flask API サーバー
│   ├── app.py              # メインアプリケーション
│   ├── requirements.txt    # Python依存関係
│   ├── runtime.txt         # Pythonバージョン
│   └── .env.example        # 環境変数テンプレート
├── frontend/               # React フロントエンド
│   ├── src/
│   │   ├── App.js         # メインコンポーネント
│   │   └── ...
│   ├── package.json       # Node.js依存関係
│   └── public/
└── README.md              # このファイル
```

## 🔒 セキュリティ

- ✅ API キーは環境変数で安全に管理
- ✅ CORS設定でクロスオリジンアクセス制御
- ✅ 本番環境用の設定分離
- ✅ AWSリソースは企業環境で安全に使用

## 🐛 トラブルシューティング

### よくある問題

**1. AWS Bedrock接続エラー**
- IAMユーザーの権限を確認
- リージョン設定を確認（us-east-1推奨）

**2. YouTube API エラー**
- API キーの有効性を確認
- YouTube Data API v3が有効化されているか確認

**3. CORS エラー**
- フロントエンドとバックエンドのポート設定を確認
- app.pyのCORS設定を確認

## 🎨 カスタマイズ

### 検索戦略の調整
`app.py` の `analyze_query_with_local_ai()` 関数でキーワード分析ロジックをカスタマイズ可能

### UI のカスタマイズ
`frontend/src/App.css` でスタイリングを調整可能

## 📄 ライセンス

このプロジェクトはMIT ライセンスの下で公開されています。

---

Made with ❤️ by MISHIMA NAOYA  
Last Updated: 2025-08-19
