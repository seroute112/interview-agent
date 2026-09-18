import json
from app.state import InterviewState
from app.config import get_llm

MATCHER_PROMPT = """你是一个JD与简历匹配分析专家。请对比候选人的简历与目标JD，输出结构化匹配结果，只返回JSON，不要其他内容

要求：
1. 必须返回所有字段，没有内容时返回空列表 []，不要省略字段。

返回格式：
{
    "matched":["简历中已具备且JD中要求的技能"],
    "partial":["简历中沾边但不深入的技能"],s
    "missing":["JD要求但简历中未体现的技能"]
    "summary":"一句话总结匹配度",
}
"""

def resume_matcher_node(state: InterviewState):
    llm = get_llm()
    prompt = MATCHER_PROMPT + "\n\nJD内容：\n" + state["jd"] +"\n\nJD关键词：\n" + ",".join(state["jd_keywords"]) + "\n\n简历内容：\n" + state["resume"]
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
            "matched": [],
            "partial": [],
            "missing": [],
            "summary": "未知",
            "raw": content
        }

    return {"match_result": parsed}