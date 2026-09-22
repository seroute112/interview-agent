import json
from app.state import InterviewState
from app.config import get_llm
from app.memory.topic_tracker import update_topic_progress
from app.tools.llm_json import parser_llm_json

EVALUATOR_PROMPT = """你是一个技术面试官。请根据候选人的回答进行评估，只返回JSON，不要其他内容

要求：1. 必须返回所有字段，不能为空，不能省略
2.评分1-10分，要公平公正
3.指出优点，不足与改进建议
4.标记弱项技能，方便后续提问

弱项标签请从以下固定集合中选择，可多选：
["概念不深入", "缺少细节", "缺少场景", "缺少示例", "未作答", "回答无效", "基础知识薄弱", "缺少对比分析"]

返回格式：
{
    "score": 1,
    "strengths":["优点"],
    "weaknesses":["不足"],
    "suggestion":"具体的改进建议",
    "weak_tags":["概念不深入","缺少场景"]
}

"""
def evaluator_node(state: InterviewState):
    llm = get_llm()

    question = state["current_question"].get("question","")
    answer = state.get("user_answer","")

    prompt = (EVALUATOR_PROMPT + "\n\n问题文本:\n" + question + "\n\n候选人答案:\n" + answer)

    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("'''"):
        content = content.split("'''")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end+1]

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "score": 0,
            "strengths":[],
            "weaknesses":[],
            "suggestion":"解析失败",
            "weak_tags":[]
        }

    parsed.setdefault("score",1)
    parsed.setdefault("strengths",[])
    parsed.setdefault("weaknesses",[])
    parsed.setdefault("suggestion","")
    parsed.setdefault("weak_tags",[])

    evaluations = state.get("evaluations","")
    evaluations.append({
        "question":question,
        "answer":answer,
        "score":parsed["score"],
        "strengths":parsed["strengths"],
        "weaknesses":parsed["weaknesses"],
        "suggestion":parsed["suggestion"],
    }) 

    weak_points = state.get("weak_points","")
    weak_points.extend(parsed["weak_tags"])

    target = state["current_question"].get("target","")
    if target:
        topics = [t.strip() for t in target.split(",") if t.strip()]
        for topic in topics:
            update_topic_progress(topic=topic,score=parsed["score"],weak_tags=parsed["weak_tags"],)

    return{"evaluations": evaluations,"weak_points": weak_points,"current_weak_tags": parsed["weak_tags"],}