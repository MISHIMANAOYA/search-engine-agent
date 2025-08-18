#!/usr/bin/env python3
import boto3
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# AWS STS クライアントの初期化
sts_client = boto3.client(
    'sts',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

try:
    # 現在の認証情報の詳細を取得
    response = sts_client.get_caller_identity()
    
    print("=== AWS認証情報の確認 ===")
    print(f"User ARN: {response.get('Arn', 'N/A')}")
    print(f"Account ID: {response.get('Account', 'N/A')}")
    print(f"User ID: {response.get('UserId', 'N/A')}")
    
    # ARNからユーザー名を抽出
    arn = response.get('Arn', '')
    if 'user/' in arn:
        username = arn.split('user/')[-1]
        print(f"Username: {username}")
    else:
        print("Username: 抽出できませんでした")
        
except Exception as e:
    print(f"エラー: {e}")
