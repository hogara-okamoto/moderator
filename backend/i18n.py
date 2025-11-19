"""
多言語対応のメッセージ定義
"""
import json
from pathlib import Path

# JSONファイルからメッセージを読み込む
def _load_messages():
    """JSONファイルからメッセージを読み込む"""
    json_path = Path(__file__).parent / "i18n" / "messages.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# JSONから読み込んだメッセージと既存のMESSAGESをマージ
JSON_MESSAGES = _load_messages()

MESSAGES = {
    "ja": {
        "system": {
            "discussion_start": "（システム）議論を開始します。",
            "rate_limit": "（システム）発言が早すぎます。少し待ってください。",
            "agent_error": "（システム）AI司会者が応答できませんでした。",
        },
        "moderator": "（AI司会者）",
        "search": {
            "api_not_configured": "検索APIが設定されていません。環境変数を確認してください。",
            "no_results": "に関する検索結果が見つかりませんでした。",
            "error": "に関する検索中にエラーが発生しました:",
            "unexpected_error": "に関する検索中に予期しないエラーが発生しました。",
            "summary_prefix": "に関する検索結果の要約:",
            "reference_urls": "参考URL:",
            "results_prefix": "に関する検索結果:",
        },
    },
    "en": {
        "system": {
            "discussion_start": "(System) Discussion started.",
            "rate_limit": "(System) Message sent too quickly. Please wait a moment.",
            "agent_error": "(System) AI moderator could not respond.",
        },
        "moderator": "(AI Moderator)",
        "search": {
            "api_not_configured": "Search API is not configured. Please check environment variables.",
            "no_results": "No search results found for",
            "error": "An error occurred while searching for",
            "unexpected_error": "An unexpected error occurred while searching.",
            "summary_prefix": "Search results summary for",
            "reference_urls": "Reference URLs:",
            "results_prefix": "Search results for",
        },
    }
}

# JSONから読み込んだメッセージをマージ
for lang in JSON_MESSAGES:
    if lang in MESSAGES:
        MESSAGES[lang].update(JSON_MESSAGES[lang])
    else:
        MESSAGES[lang] = JSON_MESSAGES[lang]

def get_message(lang: str, key: str, **kwargs) -> str:
    """
    言語とキーに基づいてメッセージを取得（プレースホルダー対応）
    
    Args:
        lang: 言語コード ('ja' または 'en')
        key: メッセージキー (例: 'moderator.start_discussion')
        **kwargs: プレースホルダーの値 (例: message="こんにちは")
        
    Returns:
        翻訳されたメッセージ（プレースホルダーが置換されたもの）
    """
    if lang not in MESSAGES:
        lang = "en"  # デフォルトは英語
    
    keys = key.split(".")
    value = MESSAGES[lang]
    for k in keys:
        value = value.get(k, {})
        if not isinstance(value, dict) and k == keys[-1]:
            # プレースホルダーを置換
            if kwargs:
                return value.format(**kwargs)
            return value
    
    # フォールバック: 英語版を返す
    value = MESSAGES["en"]
    for k in keys:
        value = value.get(k, {})
        if not isinstance(value, dict) and k == keys[-1]:
            if kwargs:
                return value.format(**kwargs)
            return value
    
    return key  # 見つからない場合はキーをそのまま返す

