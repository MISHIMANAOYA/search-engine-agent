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
- Vercel (デプロイ)

### バックエンド
- Flask
- AWS Bedrock (Claude 3 Haiku)
- YouTube Data API
- Google Custom Search API
- Railway (デプロイ)

## 🌐 ライブデモ

- **フロントエンド**: https://search-engine-agent.vercel.app
- **バックエンドAPI**: https://search-engine-backend.up.railway.app

## 🏠 ローカル開発

### 必要な環境変数

```bash
# バックエンド (.env)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_CX=your_custom_search_engine_id
```

### 起動方法

```bash
# バックエンド
cd backend
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
python app.py

# フロントエンド
cd frontend
npm install
npm start
```

## 📦 デプロイ

このプロジェクトは以下のプラットフォームにデプロイ可能です：

- **Vercel** (フロントエンド推奨)
- **Railway** (バックエンド推奨) 
- **Heroku**
- **AWS**
- **Docker**

## 🎯 使用方法

1. 検索したいキーワードを入力
2. AIが最適な検索戦略を分析
3. YouTube動画とWeb結果を表示
4. 興味のある動画の「📝 AI要約」をクリック
5. 要約を読んで、さらに詳しく質問

## 🔒 セキュリティ

- API キーは環境変数で管理
- CORS設定でセキュアなアクセス制御
- プロダクション環境での最適化

---

Made with ❤️ by MISHIMA NAOYA
