import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

def get_llm():
    return ChatDeepSeek(
        model="deepseek-chat",
        api_key = os.getenv("DEEPSEEK_API_KEY"),
        temperature=0,
        max_tokens=2048,
        model_kwargs={"response_format": {"type": "json_object"}},
    )