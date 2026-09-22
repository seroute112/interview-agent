import os
from mem0 import MemoryClient

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            raise ValueError("缺少 MEM0_API_KEY 环境变量")
        _client = MemoryClient(api_key=api_key)
    return _client


def save_user_message(user_id: str, user_msg: str, assistant_msg: str):
    client = _get_client()
    messages = [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ]
    client.add(messages, user_id=user_id)


def search_user_memory(user_id: str, query: str, limit: int = 5) -> list:
    client = _get_client()
    try:
        results = client.search(query=query, user_id=user_id, limit=limit)
        return [r["memory"] for r in results if r.get("memory")]
    except Exception as e:
        print(f"用户记忆检索失败：{e}")
        return []