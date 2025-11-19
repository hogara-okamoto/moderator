# ロールバック手順

## 概要

`moderator_agent_wrapper.py`を`moderator_agent_core`（ADK実装）を使うように変更しました。
うまくいかない場合は、以下の手順でロールバックできます。

## ロールバック方法

### 方法1: バックアップファイルから復元

```bash
cd /home/hogara/projects/moderator/backend/agents
cp moderator_agent_wrapper.backup.py moderator_agent_wrapper.py
```

### 方法2: 手動でコピー

1. `moderator_agent_wrapper.backup.py`を開く
2. 内容をすべてコピー
3. `moderator_agent_wrapper.py`を開く
4. 内容をすべて削除して、コピーした内容を貼り付け

## 変更内容

### 変更前（バックアップ）
- `genai.GenerativeModel`を直接使用
- Function Callingを手動実装
- 検索結果処理を手動実装

### 変更後（現在）
- `moderator_agent_core`（ADKの`LlmAgent`）を使用
- ADKが自動的にFunction Callingを処理
- コードが簡潔になった

## 確認方法

ロールバック後、以下のコマンドで動作確認：

```bash
cd /home/hogara/projects/moderator/backend
python -m pytest  # テストがある場合
# または
python main.py  # サーバーを起動してテスト
```

## 注意事項

- バックアップファイル（`.backup.py`）は削除しないでください
- ロールバック後も、新しい実装を試したい場合は再度変更できます

