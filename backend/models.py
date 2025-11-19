"""
共通の型定義とデータモデル
"""
from dataclasses import dataclass
from typing import List

# Messageクラスの定義（main.pyと共通）
@dataclass
class Message:
    content: str
    role: str  # "user", "agent", or "system"

# 議論履歴を保持（議論IDごとに管理する場合は後で拡張）
discussion_history: List[Message] = [
    Message(content="（システム）議論を開始します。", role="system")
]


