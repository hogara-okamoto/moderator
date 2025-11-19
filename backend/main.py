import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
from dataclasses import dataclass
import time
from dotenv import load_dotenv
import os
from urllib.parse import parse_qs
from i18n import get_message

# .envファイルから環境変数を読み込む
load_dotenv()

# Simple Message class for conversation history
@dataclass
class Message:
    content: str
    role: str  # "user", "agent", or "system"

# --- 前のステップで作成したADKエージェントをインポート ---
# (実際には adk_agents.py ファイルからインポートすることを想定)
try:
    from adk_agents import moderator_agent, discussion_history
except ImportError:
    print("警告: adk_agents.py が見つかりません。ダミーエージェントを使用します。")
    # --- ダミーエージェント（adk_agents.py がない場合のプレースホルダー） ---
    discussion_history = [Message(content="（システム）議論を開始します。", role="system")]
    async def dummy_moderator_agent_send(history):
        last_message = history[-1].content
        response_text = f"（AI司会者）「{last_message}」について承知しました。皆様の意見をどうぞ。"
        yield Message(content=response_text, role="agent")
    
    class DummyAgent:
        def send(self, history):
            return dummy_moderator_agent_send(history)
    moderator_agent = DummyAgent()
    # --- ここまでダミー ---


# --- アプリケーションの初期化 ---
app = FastAPI(
    title="匿名議論ファシリテーションシステム バックエンド",
    description="Google ADKエージェントとWebSocketで連携するAPIサーバー"
)

# --- 4.2. 議論IDの管理 (インメモリでの管理) ---
# (仕様書 4.2 )
# 本番環境では、議論IDごとに状態をRedisやDBで管理します [cite: 4]。
# このスケルトンでは、単一の共有インスタンスを想定します。
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """ 接続中の全クライアントにメッセージをブロードキャスト """
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


# --- 4.2. 投稿頻度制限 (簡易版) ---
# (仕様書 4.2 )
# IPアドレスに基づき、短時間の連続投稿を制限する
RATE_LIMIT_SECONDS = 3 # 3秒に1回まで
last_post_times: Dict[str, float] = {}

# rate_limiter関数は削除（WebSocketエンドポイント内で直接実装）


# --- 4.2. リアルタイム通信 (WebSocket エンドポイント) ---
# (仕様書 4.2 )
@app.websocket("/ws/discussion/{discussion_id}")
async def websocket_endpoint(websocket: WebSocket, discussion_id: str):
    
    await manager.connect(websocket)
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    # クエリパラメータから言語を取得
    # FastAPIのWebSocketでは、クエリパラメータを直接取得できないため、
    # クライアント側から最初のメッセージで言語を送信するか、URLから取得
    # 簡易実装: デフォルトは英語、クライアントが最初に言語を送信する
    lang = 'en'  # デフォルトは英語
    
    print(f"クライアント接続: {client_ip} (議論ID: {discussion_id})")

    # 接続時に現在の議論履歴を送信 (省略可能)
    # for msg in discussion_history:
    #     await websocket.send_text(f"{msg.role}: {msg.content}")

    try:
        while True:
            # 1. フロントエンドから参加者の発言を受信
            data = await websocket.receive_text()
            
            # 言語設定メッセージかどうかを確認（例: "LANG:en"）
            if data.startswith("LANG:"):
                lang = data.split(":")[1]
                if lang not in ['ja', 'en']:
                    lang = 'en'
                print(f"言語設定: {lang}")
                # 言語設定メッセージは処理せず、次のメッセージを待つ
                continue
            
            # 2. 投稿頻度制限のチェック（WebSocket用に修正）
            current_time = time.time()
            last_post = last_post_times.get(client_ip, 0)
            if current_time - last_post < RATE_LIMIT_SECONDS:
                print(f"警告: レートリミット超過 (IP: {client_ip})")
                await websocket.send_text(get_message(lang, "system.rate_limit"))
                continue
            last_post_times[client_ip] = current_time

            # 3. 発言を履歴に追加
            print(f"受信: {data}")
            user_message = Message(content=data, role="user") # 匿名IDはフロント側で付与想定
            discussion_history.append(user_message)
            
            # 4. 発言を全参加者にブロードキャスト 
            await manager.broadcast(f"{user_message.content}") # "参加者 #1: こんにちは" など

            # 5. ADKエージェント（司会者）を呼び出し
            print("ADKエージェント（司会者）を呼び出します...")
            try:
                ai_response_content = ""
                # ADKエージェントのストリーミング応答を処理（言語パラメータを渡す）
                async for chunk in moderator_agent.send(discussion_history, lang=lang):
                    # chunkはMessageオブジェクト
                    if chunk.content:
                        ai_response_content += chunk.content
                        # ストリーミングのままブロードキャストも可能
                        # await manager.broadcast(chunk.content) 
                
                print(f"ADK応答: {ai_response_content}")
                
                # 6. エージェントの応答を履歴に追加し、全参加者にブロードキャスト
                if ai_response_content:
                    ai_message = Message(content=ai_response_content, role="agent")
                    discussion_history.append(ai_message)
                    moderator_prefix = get_message(lang, "moderator")
                    # エージェントの応答にプレフィックスが含まれていない場合は追加
                    if not ai_response_content.startswith(moderator_prefix) and not ai_response_content.startswith("（AI司会者）") and not ai_response_content.startswith("(AI Moderator)"):
                        await manager.broadcast(f"{moderator_prefix}: {ai_message.content}")
                    else:
                        await manager.broadcast(ai_message.content)
                else:
                    print("警告: ADKエージェントからの応答が空です。")

            except Exception as e:
                print(f"ADKエージェント処理エラー: {e}")
                import traceback
                error_traceback = traceback.format_exc()
                print(f"エラー詳細:\n{error_traceback}")
                traceback.print_exc()
                try:
                    await manager.broadcast(get_message(lang, "system.agent_error"))
                except Exception as broadcast_error:
                    print(f"ブロードキャストエラー: {broadcast_error}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"クライアント切断: {client_ip}")
    except Exception as e:
        print(f"WebSocketエラー: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(websocket)


# --- サーバー起動用（デバッグ用） ---
if __name__ == "__main__":
    print("FastAPIサーバーを起動します (http://127.0.0.1:8000)")
    uvicorn.run(app, host="127.0.0.1", port=8000)