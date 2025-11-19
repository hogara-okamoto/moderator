"""
共通の型定義とデータモデル
"""
from dataclasses import dataclass
from typing import List, Dict

# Messageクラスの定義（main.pyと共通）
@dataclass
class Message:
    content: str
    role: str  # "user", "agent", or "system"

# 議論IDごとの履歴を保持（Session State実装）
# キー: discussion_id (str), 値: List[Message]
_discussion_histories: Dict[str, List[Message]] = {}

def get_discussion_history(discussion_id: str) -> List[Message]:
    """
    議論IDに対応する履歴を取得（存在しない場合は初期化）
    
    Args:
        discussion_id: 議論ID
        
    Returns:
        議論履歴のリスト
    """
    if discussion_id not in _discussion_histories:
        _discussion_histories[discussion_id] = [
            Message(content="（システム）議論を開始します。", role="system")
        ]
    return _discussion_histories[discussion_id]

def set_discussion_history(discussion_id: str, history: List[Message]) -> None:
    """
    議論IDに対応する履歴を設定
    
    Args:
        discussion_id: 議論ID
        history: 議論履歴のリスト
    """
    _discussion_histories[discussion_id] = history

# 後方互換性のため、デフォルトの議論ID "default" の履歴をエクスポート
discussion_history = get_discussion_history("default")


