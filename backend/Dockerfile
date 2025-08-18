FROM python:3.11-slim

WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ポートを公開
EXPOSE $PORT

# gunicornでアプリを起動
CMD gunicorn --bind 0.0.0.0:$PORT app:app