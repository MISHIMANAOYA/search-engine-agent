from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import boto3
import json
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse, parse_qs

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)

# CORS設定（プロダクション環境に応じて調整）
if os.getenv('FLASK_ENV') == 'production':
    # プロダクション環境では特定のオリジンのみ許可
    CORS(app, origins=[
        "https://search-engine-agent.vercel.app",  # Vercelのドメイン
        "https://*.vercel.app",  # Vercelのサブドメイン
        "http://localhost:3000",  # 開発用
        "http://172.20.202.73:3000"  # ローカルネットワーク用
    ])
else:
    # 開発環境では全てのオリジンを許可
    CORS(app)

# Bedrockクライアントの初期化
# 方法1: 環境変数から取得（推奨）
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# 方法2: 直接指定（セキュリティ上推奨されません）
# bedrock_client = boto3.client(
#     'bedrock-runtime',
#     region_name='us-east-1',
#     aws_access_key_id='AKIA...',  # 実際のAccess Key ID
#     aws_secret_access_key='...'   # 実際のSecret Access Key
# )

def analyze_query_with_local_ai(query):
    """
    ローカルのルールベースでユーザーのクエリを分析し、適切な検索タイプを決定
    """
    query_lower = query.lower()
    
    # YouTube向けのキーワード
    youtube_keywords = [
        '動画', 'ビデオ', '講座', 'チュートリアル', 'tutorial', 'how to', 'やり方',
        '解説', '実演', 'demo', 'プレゼン', '音楽', 'music', 'song', '歌',
        'ライブ', 'live', '配信', 'stream', 'vlog', 'レビュー', 'review',
        '実況', 'ゲーム', 'game', 'アニメ', 'anime', 'ドラマ', 'drama',
        '映画', 'movie', 'trailer', 'mv', 'pv', 'コメディ', 'comedy'
    ]
    
    # Web検索向けのキーワード
    web_keywords = [
        'とは', 'とは何', '定義', '意味', 'meaning', 'definition', 'wiki',
        'ニュース', 'news', '最新', 'latest', '情報', 'info', 'information',
        '公式', 'official', 'サイト', 'site', 'website', 'ホームページ',
        '価格', '値段', 'price', '料金', 'cost', '比較', 'comparison',
        'レポート', 'report', '記事', 'article', '研究', 'research',
        'ダウンロード', 'download', 'インストール', 'install', '設定'
    ]
    
    # 学習系のキーワード（両方検索）
    learning_keywords = [
        '学習', '勉強', '習得', 'learn', 'study', '覚える', '身につける',
        '入門', '初心者', 'beginner', '基礎', 'basic', '上達', 'improve'
    ]
    
    youtube_score = sum(1 for keyword in youtube_keywords if keyword in query_lower)
    web_score = sum(1 for keyword in web_keywords if keyword in query_lower)
    learning_score = sum(1 for keyword in learning_keywords if keyword in query_lower)
    
    # 判定ロジック
    if learning_score > 0 or (youtube_score > 0 and web_score > 0):
        search_type = "both"
        reasoning = "学習や比較に関するクエリなので、動画と記事の両方が有用"
    elif youtube_score > web_score:
        search_type = "youtube"
        reasoning = "動画コンテンツに関するキーワードが含まれているため"
    elif web_score > youtube_score:
        search_type = "web"
        reasoning = "情報検索や定義に関するキーワードが含まれているため"
    else:
        search_type = "both"
        reasoning = "明確な判定ができないため、両方の結果を表示"
    
    # クエリの最適化
    if 'やり方' in query_lower or 'how to' in query_lower:
        optimized_youtube_query = f"{query} 解説 チュートリアル"
        optimized_web_query = f"{query} 方法 手順"
    elif '講座' in query_lower or 'tutorial' in query_lower:
        optimized_youtube_query = f"{query} 入門 基礎"
        optimized_web_query = f"{query} 学習 リソース"
    else:
        optimized_youtube_query = query
        optimized_web_query = query
    
    return {
        "search_type": search_type,
        "optimized_youtube_query": optimized_youtube_query,
        "optimized_web_query": optimized_web_query,
        "reasoning": reasoning
    }

def search_web(query):
    """
    Google Custom Search APIを使用してWeb検索を実行
    """
    # Google Custom Search API の設定
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    cx = os.getenv('GOOGLE_SEARCH_CX')
    
    if not api_key or not cx:
        print("Google Search API credentials not found")
        return []
    
    url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'thumbnail': item.get('pagemap', {}).get('cse_thumbnail', [{}])[0].get('src', '')
            })
        
        return results
    except requests.RequestException as e:
        print(f"Web search error: {e}")
        return []

@app.route('/')
def home():
    return "Welcome to the YouTube Search API! Use the /search endpoint with a query parameter."

@app.route('/bedrock-status', methods=['GET'])
def bedrock_status():
    """
    Bedrockクライアントの接続状態を確認するエンドポイント
    """
    try:
        # AWS認証情報の確認
        aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        status = {
            "bedrock_client_initialized": bedrock_client is not None,
            "aws_region": aws_region,
            "aws_access_key_exists": aws_access_key is not None,
            "aws_secret_key_exists": aws_secret_key is not None,
            "aws_access_key_preview": f"{aws_access_key[:4]}***" if aws_access_key else None
        }
        
        # 簡単なBedrockサービスへの接続テスト
        try:
            # Bedrock Runtimeクライアント用の簡単なテスト
            # 実際にモデルを呼び出して接続確認
            test_response = bedrock_client.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ]
                })
            )
            status["bedrock_connection"] = "SUCCESS"
            status["test_model"] = "anthropic.claude-3-haiku-20240307-v1:0"
        except Exception as e:
            status["bedrock_connection"] = "FAILED"
            status["bedrock_error"] = str(e)
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "error": "Failed to check Bedrock status",
            "details": str(e)
        }), 500

def search_youtube(query):
    api_key = os.getenv('YOUTUBE_API_KEY', 'AIzaSyCT5dERwL4bS2dZazoZGb2ec7mLyLUoYDY')
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={api_key}&maxResults=10'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = [
            {
                'title': item['snippet']['title'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'description': item['snippet']['description'],
                'channelTitle': item['snippet']['channelTitle']
            }
            for item in data.get('items', []) if item['id'].get('videoId')
        ]
        return results
    except requests.RequestException as e:
        return {'error': str(e)}

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    # Bedrockでクエリを分析
    analysis_result = analyze_query_with_bedrock(query)
    search_type = analysis_result.get("search_type", "both")
    optimized_youtube_query = analysis_result.get("optimized_youtube_query", query)
    optimized_web_query = analysis_result.get("optimized_web_query", query)
    
    youtube_results = []
    web_results = []
    
    # YouTube検索
    if search_type in ["youtube", "both"]:
        youtube_results = search_youtube(optimized_youtube_query)
    
    # Web検索
    if search_type in ["web", "both"]:
        web_results = search_web(optimized_web_query)
    
    return jsonify({
        'youtube': youtube_results,
        'web': web_results,
        'analysis': analysis_result
    })

def analyze_query_with_bedrock(query):
    """
    AWS BedrockのAIを使用してユーザーのクエリを分析
    """
    try:
        # プロンプトの作成
        prompt = f"""あなたは検索クエリ分析の専門家です。ユーザーの検索クエリを分析して、最適な検索戦略を提案してください。

ユーザーのクエリ: "{query}"

まず、このクエリについてのあなたの分析を自然な文章で説明してください。
その後、以下のJSON形式で技術的な分析結果を提供してください：

{{
    "search_type": "youtube/web/both",
    "optimized_youtube_query": "YouTubeに最適化されたクエリ",
    "optimized_web_query": "Web検索に最適化されたクエリ",
    "reasoning": "判断理由"
}}

判断基準：
- 動画が適している：チュートリアル、実演、解説、音楽、エンタメ
- Webが適している：定義、ニュース、公式情報、価格比較
- 両方が適している：学習、研究、比較検討"""

        # Bedrockへのリクエスト
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',  # Claude 3 Haikuを使用
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        # レスポンスの解析
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # JSONレスポンスを抽出
        import re
        json_match = re.search(r'\{[^{}]*\}', ai_response, re.DOTALL)
        if json_match:
            analysis_result = json.loads(json_match.group())
            # Bedrockの生レスポンス（自然な説明部分）を追加
            # JSON部分を除いた自然な説明を抽出
            natural_explanation = ai_response.replace(json_match.group(), '').strip()
            analysis_result["bedrock_raw_response"] = natural_explanation if natural_explanation else ai_response
        else:
            # JSONが見つからない場合のフォールバック
            analysis_result = analyze_query_with_local_ai(query)
            analysis_result["bedrock_raw_response"] = f"JSON解析に失敗しました。AI回答: {ai_response}"
            
        return analysis_result
        
    except Exception as e:
        print(f"Bedrock analysis error: {e}")
        # エラー時はローカル分析にフォールバック
        fallback_result = analyze_query_with_local_ai(query)
        fallback_result["bedrock_raw_response"] = f"Bedrockエラー: {str(e)} (ローカルAIにフォールバック)"
        return fallback_result

def extract_video_id(url):
    """
    YouTube URLから動画IDを抽出
    """
    # 様々なYouTube URL形式に対応
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_video_details(video_id):
    """
    YouTube Data APIを使用して動画の詳細情報を取得
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return None
    
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('items'):
            item = data['items'][0]
            return {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt'],
                'duration': item['contentDetails']['duration'],
                'viewCount': item['statistics'].get('viewCount', '0'),
                'likeCount': item['statistics'].get('likeCount', '0'),
                'thumbnail': item['snippet']['thumbnails']['high']['url']
            }
    except Exception as e:
        print(f"Error getting video details: {e}")
        return None

def get_video_transcript(video_id):
    """
    YouTube動画の字幕を取得
    """
    try:
        # 字幕を取得（日本語を優先、なければ英語、最後に自動生成）
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript = None
        try:
            # 日本語字幕を優先
            transcript = transcript_list.find_transcript(['ja'])
        except:
            try:
                # 英語字幕
                transcript = transcript_list.find_transcript(['en'])
            except:
                # 自動生成字幕
                transcript = transcript_list.find_generated_transcript(['ja', 'en'])
        
        if transcript:
            transcript_data = transcript.fetch()
            full_text = ' '.join([item['text'] for item in transcript_data])
            return full_text
        else:
            return None
            
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None

def summarize_with_bedrock(title, description, transcript):
    """
    AWS Bedrockを使用して動画を要約
    """
    try:
        # 字幕が長すぎる場合は最初の部分のみ使用
        if transcript and len(transcript) > 5000:
            transcript = transcript[:5000] + "..."
        
        prompt = f"""以下のYouTube動画の内容を日本語で要約してください。視聴者にとって有用で分かりやすい要約を作成してください。

動画タイトル: {title}

動画説明: {description[:500] if description else 'なし'}

字幕内容: {transcript if transcript else '字幕が取得できませんでした'}

以下の形式で要約してください：
1. **概要**: 動画の主な内容を2-3文で説明
2. **主なポイント**: 重要なポイントを箇条書きで3-5個
3. **対象者**: どんな人におすすめか
4. **所要時間**: 視聴にかかる時間の目安

自然で読みやすい日本語で回答してください。"""

        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        summary = response_body['content'][0]['text']
        return summary
        
    except Exception as e:
        print(f"Bedrock summarization error: {e}")
        return f"要約の生成に失敗しました: {str(e)}"

@app.route('/summarize-video', methods=['POST'])
def summarize_video():
    """
    YouTube動画を要約するエンドポイント
    """
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'Video URL is required'}), 400
    
    # 動画IDを抽出
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    # 動画詳細を取得
    video_details = get_video_details(video_id)
    if not video_details:
        return jsonify({'error': 'Failed to get video details'}), 400
    
    # 字幕を取得
    transcript = get_video_transcript(video_id)
    
    # AI要約を生成
    summary = summarize_with_bedrock(
        video_details['title'],
        video_details['description'],
        transcript
    )
    
    return jsonify({
        'video_details': video_details,
        'transcript_available': transcript is not None,
        'summary': summary,
        'video_id': video_id
    })

@app.route('/ask-about-video', methods=['POST'])
def ask_about_video():
    """
    動画に関する追加質問に答えるエンドポイント
    """
    data = request.get_json()
    question = data.get('question')
    video_id = data.get('video_id')
    previous_summary = data.get('previous_summary', '')
    
    if not question or not video_id:
        return jsonify({'error': 'Question and video_id are required'}), 400
    
    # 動画詳細と字幕を再取得
    video_details = get_video_details(video_id)
    transcript = get_video_transcript(video_id)
    
    if not video_details:
        return jsonify({'error': 'Failed to get video details'}), 400
    
    try:
        # より詳細な分析用プロンプト
        prompt = f"""あなたは動画分析の専門家です。以下の情報をもとに、ユーザーの質問に詳しく答えてください。

動画情報:
- タイトル: {video_details['title']}
- チャンネル: {video_details['channel']}
- 説明: {video_details['description'][:1000] if video_details['description'] else 'なし'}

字幕内容: {transcript[:3000] if transcript else '字幕が利用できません'}

前回の要約: {previous_summary[:500] if previous_summary else 'なし'}

ユーザーの質問: {question}

この質問に対して、動画の内容に基づいて具体的で有用な回答をしてください。字幕がある場合は、その内容を参考にしてください。字幕がない場合は、タイトルと説明から推測できる範囲で答えてください。

回答は自然な日本語で、分かりやすく丁寧に説明してください。"""

        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        return jsonify({
            'answer': answer,
            'transcript_available': transcript is not None
        })
        
    except Exception as e:
        print(f"Error answering question: {e}")
        return jsonify({
            'error': f"質問への回答に失敗しました: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.getenv('FLASK_ENV') != 'production', host='0.0.0.0', port=port)