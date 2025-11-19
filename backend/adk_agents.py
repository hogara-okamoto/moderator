"""
Google ADKエージェント群の実装（後方互換性のための再エクスポート）
仕様書に基づくエージェント群:
1. ルートエージェント（ModeratorAgent）- 司会者
2. データ収集エージェント（DataGatheringAgent）
3. 意見要約エージェント（OpinionSummarizer）
4. 感情分析エージェント（SentimentAnalyzer）

注意: このファイルは後方互換性のために残されています。
各エージェントは個別のファイルに分割されています:
- agents/moderator_agent.py: ルートエージェント
- agents/data_gathering_agent.py: データ収集エージェント
- agents/opinion_summarizer_agent.py: 意見要約エージェント
- agents/sentiment_analyzer_agent.py: 感情分析エージェント
"""

# 後方互換性のため、新しい場所からインポートして再エクスポート
from models import Message, discussion_history
from agents import (
    moderator_agent,
    moderator_agent_core,
    ModeratorAgentWrapper,
    data_gathering_agent,
    opinion_summarizer_agent,
    sentiment_analyzer_agent,
)

# エクスポート（後方互換性のため）
__all__ = [
    "Message",
    "discussion_history",
    "moderator_agent",
    "moderator_agent_core",
    "ModeratorAgentWrapper",
    "data_gathering_agent",
    "opinion_summarizer_agent",
    "sentiment_analyzer_agent",
]
