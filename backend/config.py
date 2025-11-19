"""
設定と環境変数の管理
"""
from dotenv import load_dotenv
import os
import google.generativeai as genai

# .envファイルから環境変数を読み込む
load_dotenv()

# Google APIキーを設定
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Google Custom Search APIの設定
# 環境変数から読み込む（.envファイルに記載）
# 検索APIキーが明示的に設定されていない場合は、既存のGOOGLE_API_KEYをフォールバックとして使用
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY") or api_key
# Engine IDは環境変数から読み込む
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")


