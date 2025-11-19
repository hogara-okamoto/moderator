"""
メッセージ変換ユーティリティ
"""
from typing import List
from models import Message


def messages_to_content(history: List[Message]) -> List[dict]:
    """
    Message形式の履歴をgoogle.generativeaiのContent形式（辞書）に変換
    
    Args:
        history: Message形式の会話履歴
        
    Returns:
        Content形式（辞書）の会話履歴
    """
    content_list = []
    for msg in history:
        role_map = {
            "user": "user",
            "agent": "model",
            "system": "user"  # systemメッセージはuserとして扱う
        }
        role = role_map.get(msg.role, "user")
        content_list.append({
            "role": role,
            "parts": [{"text": msg.content}]
        })
    return content_list

