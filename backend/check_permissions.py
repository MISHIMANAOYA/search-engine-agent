#!/usr/bin/env python3
import boto3
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# IAM クライアントの初期化
iam_client = boto3.client(
    'iam',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

try:
    username = 'claude_code'
    
    print("=== IAMユーザーの権限確認 ===")
    print(f"ユーザー名: {username}")
    print()
    
    # アタッチされたポリシーを確認
    print("1. 直接アタッチされたポリシー:")
    attached_policies = iam_client.list_attached_user_policies(UserName=username)
    
    if attached_policies['AttachedPolicies']:
        for policy in attached_policies['AttachedPolicies']:
            print(f"  - {policy['PolicyName']} (ARN: {policy['PolicyArn']})")
    else:
        print("  なし")
    
    print()
    
    # インラインポリシーを確認
    print("2. インラインポリシー:")
    inline_policies = iam_client.list_user_policies(UserName=username)
    
    if inline_policies['PolicyNames']:
        for policy_name in inline_policies['PolicyNames']:
            print(f"  - {policy_name}")
    else:
        print("  なし")
    
    print()
    
    # グループのポリシーを確認
    print("3. グループ経由のポリシー:")
    groups = iam_client.get_groups_for_user(UserName=username)
    
    if groups['Groups']:
        for group in groups['Groups']:
            group_name = group['GroupName']
            print(f"  グループ: {group_name}")
            
            # グループのポリシーを確認
            group_policies = iam_client.list_attached_group_policies(GroupName=group_name)
            for policy in group_policies['AttachedPolicies']:
                print(f"    - {policy['PolicyName']}")
    else:
        print("  グループに所属していません")
    
    print()
    
    # Bedrock権限の確認
    print("4. Bedrock関連の権限:")
    bedrock_found = False
    
    for policy in attached_policies['AttachedPolicies']:
        if 'bedrock' in policy['PolicyName'].lower() or 'Bedrock' in policy['PolicyName']:
            print(f"  ✅ {policy['PolicyName']} - Bedrock権限あり")
            bedrock_found = True
    
    if not bedrock_found:
        print("  ❌ Bedrock関連のポリシーが見つかりません")
        print("  → AmazonBedrockFullAccess ポリシーの追加が必要です")
        
except Exception as e:
    print(f"エラー: {e}")
    print("IAM権限の確認ができませんでした")
