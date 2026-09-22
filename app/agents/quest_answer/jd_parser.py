import json
from app.state import InterviewState
from app.config import get_llm

JD_PARSER_PROMPT = """ 你是一个招聘JD分析专家。请从以下JD中提取结构化信息，只返回JSON，不要其他内容

返回格式：
{
    "technical_keywords":["技术关键词"],
    "soft_skills":["软技能需求"],
    "bouns":["加分项"],
    "level":应届/初级/中级/高级,
}
"""

def jd_parser_node(state: InterviewState):
    llm = get_llm()
    prompt = JD_PARSER_PROMPT + "\n\nJD内容：\n" + state["jd"]
    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("'''"):
        content = content.split("'''")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "technical_keywords": [],
            "soft_skills": [],
            "bouns": [],
            "level": "未知",
            "raw": content
        }

    return {"jd_keywords":parsed.get("technical_keywords",[])}