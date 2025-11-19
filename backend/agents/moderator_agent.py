"""
ルートエージェント（司会者）の実装
"""
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from tools.data_gathering import data_gathering_tool
from tools.sentiment_analysis import sentiment_analysis_tool


# ルートエージェント (司会者) (仕様書 3)
# このエージェントが他のエージェント（ツールとしてラップ）を呼び出すオーケストレーターとなります。
moderator_agent_core = LlmAgent(
    name="ModeratorAgent",
    model="gemini-2.0-flash-exp",
    instruction="""あなたは議論のファシリテーター（司会者）です。
    あなたの目的は、匿名参加者の議論を管理し、客観的なデータに基づき結論に導くことです。

    以下のツール（専門エージェント）を活用できます。
    - DataGatherer: 議論の裏付けとなる客観的データを検索します。
    - SentimentAnalyzer: 議論のトーンや感情を分析します。

    議論の状態（会話履歴）に基づき、次のアクション（質問の提示、データ検索の指示、要約の提示、結論のドラフト作成）を判断してください。
    
    応答は簡潔で、参加者を議論に導くような内容にしてください。
    """,
    tools=[
        FunctionTool(data_gathering_tool),
        FunctionTool(sentiment_analysis_tool),
    ],
)

