"""
司会者エージェントのラッパー（main.pyとの互換性のため）
【バックアップ】変更前の実装（genai.GenerativeModelを直接使用）
ロールバックする場合は、このファイルの内容をmoderator_agent_wrapper.pyにコピーしてください。
"""
from typing import List, AsyncIterator
import google.generativeai as genai
from models import Message
from utils.context import current_lang
from utils.messages import messages_to_content
from i18n import get_message
from agents.data_gathering_agent import execute_search, process_search_result


class ModeratorAgentWrapper:
    """司会者エージェントのラッパー（main.pyとの互換性のため）"""
    
    def __init__(self, lang: str = "en"):
        self.lang = lang
    
    async def send(self, history: List[Message], lang: str = "en") -> AsyncIterator[Message]:
        """
        会話履歴を受け取り、司会者としての応答を生成
        
        Args:
            history: 会話履歴のリスト
            lang: 言語コード ('ja' または 'en')
            
        Yields:
            Message: 司会者の応答メッセージ
        """
        # 言語設定をコンテキスト変数に設定（data_gathering_toolで使用される）
        current_lang.set(lang)
        
        try:
            # 最後のユーザーメッセージを取得
            if not history:
                yield Message(content=get_message(lang, "moderator.start_discussion"), role="agent")
                return
            
            # 最後のユーザーメッセージを取得
            last_user_message = None
            for msg in reversed(history):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                yield Message(content=get_message(lang, "moderator.start_discussion"), role="agent")
                return
            
            # ADKエージェントを使用（Function CallingをサポートするGeminiモデルを直接使用）
            # システムプロンプトを追加
            system_prompt = get_message(lang, "moderator.system_prompt")
            
            # Function Calling用のツール定義
            tools_config = [
                {
                    "function_declarations": [
                        {
                            "name": "data_gathering_tool",
                            "description": get_message(lang, "moderator.tool_description"),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": get_message(lang, "moderator.tool_query_description")
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                }
            ]
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp", tools=tools_config)
            
            # 履歴メッセージを変換（言語に応じた処理）
            content_history = messages_to_content(history)
            
            # システムプロンプトを履歴の最初に追加（より強調するため）
            system_content = {
                "role": "user",
                "parts": [{"text": system_prompt}]
            }
            
            # 言語指示を最後に追加して、言語設定を明確にする
            lang_reminder = get_message(lang, "moderator.lang_reminder")
            
            # 最後のメッセージに言語指示を追加
            if content_history:
                last_message = content_history[-1]
                if "parts" in last_message and len(last_message["parts"]) > 0:
                    # 最後のメッセージのテキストに言語指示を追加
                    last_text = last_message["parts"][0].get("text", "")
                    last_message["parts"][0]["text"] = last_text + lang_reminder
                else:
                    # 最後のメッセージに言語指示を追加
                    content_history.append({
                        "role": "user",
                        "parts": [{"text": lang_reminder}]
                    })
            else:
                # 履歴が空の場合は言語指示のみを追加
                content_history.append({
                    "role": "user",
                    "parts": [{"text": lang_reminder}]
                })
            
            full_history = [system_content] + content_history
            
            # Function Callingをサポートする応答生成
            try:
                response = await model.generate_content_async(contents=full_history)
            except Exception as e:
                print(f"モデル応答生成エラー: {e}")
                import traceback
                traceback.print_exc()
                # エラー時はフォールバック
                response = None
            
            # Function Callingの処理
            response_text = ""
            function_called = False
            
            if response and hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            # Function Callの検出
                            if hasattr(part, 'function_call') and part.function_call:
                                function_called = True
                                function_name = part.function_call.name
                                # function_call.argsは既に辞書形式
                                try:
                                    function_args = part.function_call.args
                                    if not isinstance(function_args, dict):
                                        function_args = dict(function_args) if hasattr(function_args, '__dict__') else {}
                                except Exception as e:
                                    print(f"Function args取得エラー: {e}")
                                    function_args = {}
                                
                                print(f"Function call detected: {function_name} with args: {function_args}")
                                
                                # data_gathering_toolを呼び出し
                                if function_name == "data_gathering_tool":
                                    query = function_args.get("query", "")
                                    
                                    # データ収集エージェントを使用して検索を実行
                                    search_result_dict = await execute_search(query, lang)
                                    
                                    if search_result_dict["success"]:
                                        search_result = search_result_dict["result"]
                                        
                                        # 関数呼び出しの結果をモデルに送信して続きを生成
                                        # Gemini APIのFunction Callingでは、辞書形式で直接指定するのが正しい方法
                                        function_response_part = {
                                            "function_response": {
                                                "name": function_name,
                                                "response": {"result": search_result}
                                            }
                                        }
                                        
                                        # 関数呼び出しと結果を履歴に追加して続きを生成
                                        # URLを含めるように明示的に指示を追加
                                        url_instruction = get_message(lang, "moderator.url_instruction")
                                        
                                        extended_history = full_history + [
                                            {
                                                "role": "model",
                                                "parts": [part]  # 関数呼び出しを含むpart
                                            },
                                            {
                                                "role": "function",
                                                "parts": [function_response_part]
                                            },
                                            {
                                                "role": "user",
                                                "parts": [{"text": url_instruction}]
                                            }
                                        ]
                                        
                                        final_response = await model.generate_content_async(contents=extended_history)
                                        if final_response and final_response.text:
                                            # 検索結果とAIの応答を処理（URLセクションの追加など）
                                            response_text = process_search_result(search_result, final_response.text, lang)
                                        else:
                                            # モデルが応答を生成できなかった場合は検索結果をそのまま返す
                                            response_text = search_result
                                    else:
                                        # 検索エラー
                                        response_text = search_result_dict["error"]
                            # テキスト応答の処理
                            elif hasattr(part, 'text') and part.text:
                                response_text += part.text
            
            # Function Callがなかった場合、通常のテキスト応答を使用
            if not function_called and not response_text:
                if response and hasattr(response, 'text') and response.text:
                    response_text = response.text
                elif not response_text:
                    response_text = last_user_message
            
            yield Message(content=response_text, role="agent")
            
        except Exception as e:
            print(f"エージェント実行エラー: {e}")
            import traceback
            traceback.print_exc()
            # エラー詳細をログに出力
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"エラー詳細: {error_details}")
            # エラー時のフォールバック応答
            user_messages = [msg for msg in history if msg.role == "user"]
            if user_messages:
                last_message = user_messages[-1].content
                yield Message(
                    content=get_message(lang, "moderator.understand_point", message=last_message),
                    role="agent"
                )
            else:
                yield Message(
                    content=get_message(lang, "moderator.start_discussion"),
                    role="agent"
                )


# エクスポート
moderator_agent = ModeratorAgentWrapper()

