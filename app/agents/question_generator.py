import json
from app.state import InterviewState
from app.config import get_llm
from app.memory.sqlite_store import get_weak_points

QUESTION_PROMPT = """你是一个技术面试官。请根据候选人的技能差距生成面试问题，只返回JSON，不要其他内容

要求：
1. 必须返回所有字段，没有内容时返回空列表 []，不要省略字段
2.问题要覆盖missing和partial里的技能，优先覆盖missing中的技能
3.每个问题带考差点，难度和类型
4.生成5个问题，难度从基础到进阶分布
5.如果提供了历史弱项，优先从历史弱项出题

返回格式:
{
    "questions":[
    {
        "question":"问题文本",
        "target":"考察的技能点",
        "difficulty":"基础/中级/进阶",
        "type":"八股/项目深挖/场景设计"
    }
    ]
}

"""

def question_generator_node(state: InterviewState):
    llm = get_llm()

    match = state.get("match_result") or {}
    missing = match.get("missing") or []
    partial = match.get("partial") or []
    weak_points = state.get("weak_points") or get_weak_points()

    print("本次提问参考的历史弱项：", weak_points)

    prompt = QUESTION_PROMPT +"\n\nJD关键词：\n" + ",".join(state["jd_keywords"]) + "\n\n缺失技能：\n" + ",".join(missing) + "\n\n部分匹配技能：\n" + ",".join(partial) +"\n\n历史弱项：\n" + (",".join(weak_points) if weak_points else "暂无")

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
            "questions": [],
            "raw": content
        }

    parsed.setdefault("questions", [])
    return {"questions": parsed["questions"]}