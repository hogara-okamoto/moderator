"""
感情分析エージェントの実装
"""
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from tools.sentiment_analysis import sentiment_analysis_tool

# 感情分析エージェント (仕様書 3)
sentiment_analyzer_agent = LlmAgent(
    name="SentimentAnalyzer",
    model="gemini-2.0-flash-exp",
    instruction="あなたは感情分析の専門家です。入力されたテキストをsentiment_analysis_toolを使って分析し、結果を報告してください。",
    tools=[FunctionTool(sentiment_analysis_tool)],
)

