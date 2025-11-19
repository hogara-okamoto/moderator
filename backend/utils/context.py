"""
コンテキスト変数の管理
"""
from contextvars import ContextVar

# 現在の言語設定を保持するコンテキスト変数
current_lang: ContextVar[str] = ContextVar('current_lang', default='en')

