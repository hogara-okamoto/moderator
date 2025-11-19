"""
データ収集エージェントの実装
"""
from typing import Dict, Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from tools.data_gathering import data_gathering_tool
from i18n import get_message

# データ収集エージェント (仕様書 3)
data_gathering_agent = LlmAgent(
    name="DataGatheringAgent",
    model="gemini-2.0-flash-exp",  # モデル名を文字列で指定
    instruction="あなたはデータ収集の専門家です。依頼されたクエリに基づき、data_gathering_toolを使って客観的な情報を検索・要約してください。",
    tools=[FunctionTool(data_gathering_tool)],
)


async def execute_search(query: str, lang: str = "en") -> Dict[str, Any]:
    """
    検索を実行し、結果を処理する
    
    Args:
        query: 検索クエリ
        lang: 言語コード ('ja' または 'en')
        
    Returns:
        検索結果を含む辞書:
        {
            "success": bool,
            "result": str,  # 検索結果のテキスト
            "error": str | None  # エラーメッセージ（エラー時のみ）
        }
    """
    if not query:
        return {
            "success": False,
            "result": None,
            "error": get_message(lang, "moderator.search_query_not_specified")
        }
    
    try:
        print(f"検索を実行します: {query}")
        search_result = await data_gathering_tool(query)
        print(f"検索結果（最初の300文字）: {search_result[:300] if search_result else 'None'}...")
        print(f"検索結果（最後の300文字）: {search_result[-300:] if search_result and len(search_result) > 300 else 'None'}...")
        
        return {
            "success": True,
            "result": search_result,
            "error": None
        }
    except Exception as e:
        print(f"検索実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "result": None,
            "error": get_message(lang, "moderator.search_error", error=str(e))
        }


def process_search_result(search_result: str, ai_response_text: str, lang: str = "en") -> str:
    """
    検索結果とAIの応答を処理し、URLセクションが含まれているか確認して追加する
    
    Args:
        search_result: 検索結果のテキスト
        ai_response_text: AIが生成した応答テキスト
        lang: 言語コード ('ja' または 'en')
        
    Returns:
        処理済みの応答テキスト
    """
    # 検索結果にURLが含まれているが、応答に含まれていない場合は追加
    if "🔗" in search_result or "参考URL" in search_result or "Reference URLs" in search_result:
        # URLセクションを抽出
        url_section_start = search_result.find("━━━━━━━━")
        if url_section_start != -1:
            url_section = search_result[url_section_start:]
            
            # AIの応答に既にURLセクションが含まれているかチェック
            # 「━━━━━━━━」と「参考URL」（または「Reference URLs」）の両方が含まれていれば、既に含まれていると判断
            response_has_url_section = (
                "━━━━━━━━" in ai_response_text and 
                ("参考URL" in ai_response_text or "Reference URLs" in ai_response_text)
            )
            
            if not response_has_url_section:
                # URLセクションが含まれていない場合のみ追加
                return ai_response_text + "\n\n" + url_section
            else:
                # 既に含まれている場合はそのまま
                return ai_response_text
        else:
            return ai_response_text
    else:
        return ai_response_text

