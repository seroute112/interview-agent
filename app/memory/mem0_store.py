from email import message
import os
from mem0 import MemoryClient
from openai import api_key

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            raise ValueError("缺少MEM0_API_KEY环境变量")
        _client = MemoryClient(api_key=api_key)
    return _client

SYSTEM_USER_ID = "interview-agent-system"

def save_reflection(reflection:dict,jd_keywords:list):
    client = _get_client()

    message = [
        {"role":"user","content":f"本轮面试关键词:{",".join(jd_keywords)}"},
        {
            "role":"assistant",
            "content":(
                f"提问质量评分:{reflection.get('question_quality',0)}"
                f"评估质量评分:{reflection.get('evaluation_quality',0)}"
                f"提问改进建议：{';'.join(reflection.get('quest_suggestions',[]))}"
                f"评估改进建议：{';'.join(reflection.get('evaluate_suggestions',[]))}"
            )
        },
    ]

    client.add(message,user_id=SYSTEM_USER_ID)

def search_reflections(query:str,limit:int = 3) -> list:
    client = _get_client()
    try:
        results = client.search(query=query,user_id = SYSTEM_USER_ID,limit=limit)
        return [r["memory"] for r in results if r.get("memory")]
    except Exception as e:
        print(f"Mem0 检索失败：{e}")
        return []