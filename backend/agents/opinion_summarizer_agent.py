"""
意見要約エージェントの実装
"""
from google.adk.agents.llm_agent import LlmAgent

# 意見要約エージェント (仕様書 3)
# (このエージェントはツールを持たず、LLMの推論能力で要約を行う)
opinion_summarizer_agent = LlmAgent(
    name="OpinionSummarizer",
    model="gemini-2.0-flash-exp",
    instruction="""あなたは議論の要約家です。
    入力された会話履歴全体を分析し、以下の点を抽出・整理してください。
    1. 主要な論点
    2. 各論点に対する賛成意見と反対意見
    3. 未解決のギャップや疑問点""",
)

