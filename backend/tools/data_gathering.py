"""
データ収集ツールの実装
"""
import requests
import google.generativeai as genai
from config import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
from utils.context import current_lang
from i18n import get_message

async def data_gathering_tool(query: str) -> str:
    """
    議論中の主張や論点に関する客観的な最新情報をインターネットで検索します。
    
    Args:
        query: 検索クエリ（例：「リモートワーク 生産性 最新調査」）
        
    Returns:
        検索結果の要約。
    """
    # コンテキスト変数から現在の言語を取得（ModeratorAgentWrapper.send()で設定される）
    lang = current_lang.get()  # デフォルトは'en'（ContextVarの初期化時に設定済み）
    if lang not in ['ja', 'en']:
        lang = 'en'  # デフォルトは英語
    
    print(f"Tool: data_gathering_tool 呼び出し (Query: {query}, Lang: {lang})")
    
    # Google Custom Search APIが設定されていない場合はフォールバック
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        print("警告: Google Custom Search APIの設定がありません。環境変数 GOOGLE_SEARCH_API_KEY と GOOGLE_SEARCH_ENGINE_ID を設定してください。")
        api_not_configured_msg = get_message(lang, "search.api_not_configured")
        if lang == 'ja':
            return f"「{query}」に関する検索結果：[{api_not_configured_msg}]"
        else:
            return f"Search results for \"{query}\": [{api_not_configured_msg}]"
    
    try:
        # Google Custom Search APIを呼び出し
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
            "q": query,
            "num": 5,  # 最大5件の結果を取得
        }
        
        # 言語に応じて検索結果の言語を指定（オプション）
        # lrパラメータ: lang_ja (日本語), lang_en (英語)
        if lang == 'ja':
            params["lr"] = "lang_ja"
        else:
            params["lr"] = "lang_en"
        
        print(f"Google Custom Search APIを呼び出します: {url}")
        print(f"パラメータ: key={GOOGLE_SEARCH_API_KEY[:10]}..., cx={GOOGLE_SEARCH_ENGINE_ID}, q={query}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"API応答ステータス: {response.status_code}")
        
        # エラーレスポンスの詳細を確認
        if response.status_code != 200:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = f" - {error_data}"
                print(f"エラーレスポンス詳細: {error_data}")
            except:
                error_detail = f" - {response.text}"
                print(f"エラーレスポンステキスト: {response.text[:500]}")
            
            print(f"Google Custom Search API エラー: {response.status_code} {error_detail}")
            
            # 403エラーの場合、より詳細なメッセージを返す
            if response.status_code == 403:
                error_msg_ja = f"【検索エラー】Google Custom Search APIへのアクセスが拒否されました（403エラー）。\n\n考えられる原因:\n1. APIキーにCustom Search APIの権限がない\n2. APIキーが無効または期限切れ\n3. Custom Search Engine IDが間違っている\n4. APIキーの使用制限に達している\n\n環境変数 GOOGLE_SEARCH_API_KEY と GOOGLE_SEARCH_ENGINE_ID を確認してください。\n\nエラー詳細: {error_detail}"
                error_msg_en = f"【Search Error】Access to Google Custom Search API was denied (403 error).\n\nPossible causes:\n1. API key does not have Custom Search API permission\n2. API key is invalid or expired\n3. Custom Search Engine ID is incorrect\n4. API key usage limit reached\n\nPlease check environment variables GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID.\n\nError details: {error_detail}"
                error_response = error_msg_ja if lang == 'ja' else error_msg_en
                print(f"エラーメッセージを返します: {error_response[:200]}...")
                return error_response
        
        response.raise_for_status()
        
        data = response.json()
        
        # 検索結果を解析
        if "items" not in data or len(data["items"]) == 0:
            no_results_msg = get_message(lang, "search.no_results")
            if lang == 'ja':
                return f"「{query}」{no_results_msg}"
            else:
                return f"{no_results_msg} \"{query}\"."
        
        # 検索結果を要約
        results_summary = []
        bullet_point = "・" if lang == 'ja' else "•"
        for item in data["items"][:5]:  # 最大5件まで
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results_summary.append(f"{bullet_point}{title}\n  {snippet}\n  URL: {link}")
        
        summary_text = "\n\n".join(results_summary)
        
        # Geminiを使って検索結果を要約（オプション）
        # より簡潔で議論に役立つ情報を抽出
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            # 言語に応じたプロンプト
            if lang == 'ja':
                prompt = f"""以下の検索結果を、議論の参考になるように簡潔に要約してください。
検索クエリ: {query}

検索結果:
{summary_text}

要約では、主要な事実、統計、最新の情報を強調してください。日本語で応答してください。"""
            else:
                prompt = f"""Please summarize the following search results concisely to be useful for discussion.
Search query: {query}

Search results:
{summary_text}

In the summary, emphasize key facts, statistics, and the latest information. Respond in English."""
            
            summary_response = await model.generate_content_async(prompt)
            if summary_response and summary_response.text:
                summary_prefix = get_message(lang, "search.summary_prefix")
                reference_urls = get_message(lang, "search.reference_urls")
                
                # URLをより目立つ形で表示（最大5件）
                url_items = data["items"][:5]
                url_section = ""
                if lang == 'ja':
                    url_section = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📎 {reference_urls}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    for idx, item in enumerate(url_items, 1):
                        title = item.get('title', '')
                        link = item.get('link', '')
                        if title and link:
                            url_section += f"\n【情報源 {idx}】\n📌 {title}\n🔗 {link}\n"
                        elif link:
                            url_section += f"\n【情報源 {idx}】\n🔗 {link}\n"
                else:
                    url_section = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📎 {reference_urls}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    for idx, item in enumerate(url_items, 1):
                        title = item.get('title', '')
                        link = item.get('link', '')
                        if title and link:
                            url_section += f"\n【Source {idx}】\n📌 {title}\n🔗 {link}\n"
                        elif link:
                            url_section += f"\n【Source {idx}】\n🔗 {link}\n"
                
                if lang == 'ja':
                    return f"「{query}」{summary_prefix}\n\n{summary_response.text}{url_section}"
                else:
                    return f"{summary_prefix} \"{query}\":\n\n{summary_response.text}{url_section}"
        except Exception as e:
            print(f"要約生成エラー: {e}")
            # 要約に失敗した場合は生の検索結果を返す
            pass
        
        # 要約に失敗した場合や要約が生成されなかった場合は生の検索結果を返す
        results_prefix = get_message(lang, "search.results_prefix")
        reference_urls = get_message(lang, "search.reference_urls")
        
        # URLをより目立つ形で表示
        url_items = data["items"][:5]
        url_section = ""
        if lang == 'ja':
            url_section = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📎 {reference_urls}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for idx, item in enumerate(url_items, 1):
                title = item.get('title', '')
                link = item.get('link', '')
                if title and link:
                    url_section += f"\n【情報源 {idx}】\n📌 {title}\n🔗 {link}\n"
                elif link:
                    url_section += f"\n【情報源 {idx}】\n🔗 {link}\n"
        else:
            url_section = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📎 {reference_urls}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for idx, item in enumerate(url_items, 1):
                title = item.get('title', '')
                link = item.get('link', '')
                if title and link:
                    url_section += f"\n【Source {idx}】\n📌 {title}\n🔗 {link}\n"
                elif link:
                    url_section += f"\n【Source {idx}】\n🔗 {link}\n"
        
        if lang == 'ja':
            return f"「{query}」{results_prefix}:\n\n{summary_text}{url_section}"
        else:
            return f"{results_prefix} \"{query}\":\n\n{summary_text}{url_section}"
        
    except requests.exceptions.RequestException as e:
        print(f"検索API呼び出しエラー: {e}")
        import traceback
        traceback.print_exc()
        error_msg = get_message(lang, "search.error")
        error_response = f"「{query}」{error_msg} {str(e)}" if lang == 'ja' else f"{error_msg} \"{query}\": {str(e)}"
        print(f"エラーレスポンスを返します: {error_response[:200]}...")
        return error_response
    except Exception as e:
        print(f"予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        unexpected_error_msg = get_message(lang, "search.unexpected_error")
        error_response = f"「{query}」{unexpected_error_msg}" if lang == 'ja' else f"{unexpected_error_msg}"
        print(f"エラーレスポンスを返します: {error_response[:200]}...")
        return error_response

