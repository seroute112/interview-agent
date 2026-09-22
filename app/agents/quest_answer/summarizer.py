from app.config import get_llm
from app.state import InterviewState
from app.tools.llm_json import parser_llm_json
from app.memory.topic_tracker import update_topic_progress

SUMMARIZER_PROMPT = """你是一个面试评估总结专家。三位面试官从不同角度评估了同一份回答：
- 面试官A：技术正确性
- 面试官B：工程实践
- 面试官C：表达与逻辑

请综合三方评估，输出最终分数和评语。

要求：
1. 取三方平均分（四舍五入）作为最终分数。
2. 综合三方的 strengths、weaknesses、suggestion，不要简单拼接,请自己评估后进行总结。
3. 合并三方的 weak_tags，去重。
4. 请以 JSON 格式返回，只返回 JSON，不要其他内容,必须返回所有字段。

返回格式：
{
  "final_score": 7,
  "summary": "一句话综合评语",
  "strengths": ["综合后的优点"],
  "weaknesses": ["综合后的不足"],
  "suggestion": "综合后的改进建议",
  "weak_tags": ["去重后的弱项标签"]
}
"""

def summarizer_node(state: InterviewState):
    print("4")
    llm = get_llm()

    question = state["current_question"].get("question","")
    answer = state.get("user_answer","")
    evaluations = state.get("evaluations") or []
    last_eval = evaluations[-1] if evaluations else {}

    tech = state.get("tech_result") or {}
    engineering = state.get("engineering_result") or {}
    communication = state.get("communication_result") or {}

    content =  (
        f"\n\n面试问题：\n{question}"
        + f"\n\n候选人回答：\n{answer}"
        + f"\n\n【技术正确性】分：{last_eval.get('tech_score', 0)}"
        + f"\n优点：{last_eval.get('tech_strengths', [])}"
        + f"\n不足：{last_eval.get('tech_weaknesses', [])}"
        + f"\n建议：{last_eval.get('tech_suggestion', '')}"
        + f"\n\n【工程实践】分：{last_eval.get('engineering_score', 0)}"
        + f"\n优点：{last_eval.get('engineering_strengths', [])}"
        + f"\n不足：{last_eval.get('engineering_weaknesses', [])}"
        + f"\n建议：{last_eval.get('engineering_suggestion', '')}"
        + f"\n\n【表达逻辑】分：{last_eval.get('communication_score', 0)}"
        + f"\n优点：{last_eval.get('communication_strengths', [])}"
        + f"\n不足：{last_eval.get('communication_weaknesses', [])}"
        + f"\n建议：{last_eval.get('communication_suggestion', '')}"
    )

    response = llm.invoke(SUMMARIZER_PROMPT + content)
    parsed = parser_llm_json(response.content)

    parsed.setdefault("final_score", 0)
    parsed.setdefault("summary", "")
    parsed.setdefault("strengths", [])
    parsed.setdefault("weaknesses", [])
    parsed.setdefault("suggestion", "")
    parsed.setdefault("weak_tags", [])

    evaluations = state.get("evaluations",[])
    evaluations.append({
        "question":question,
        "answer":answer,
        "tech_score": tech.get("score", 0),
        "engineering_score": engineering.get("score", 0),
        "communication_score": communication.get("score", 0),
        "score":parsed["final_score"],
        "summary": parsed["summary"],
        "strengths":parsed["strengths"],
        "weaknesses":parsed["weaknesses"],
        "suggestion":parsed["suggestion"],
        "weak_tags": parsed["weak_tags"],
    }) 

    weak_points = state.get("weak_points") or []
    weak_points.extend(parsed["weak_tags"])
    
    target = state["current_question"].get("target","")
    if target:
        topics = [t.strip() for t in target.split(",") if t.strip()]
        for topic in topics:
            update_topic_progress(topic=topic,score=parsed["final_score"],weak_tags=parsed["weak_tags"],)

    return {"summary_result": parsed,"evaluations": evaluations,"weak_points": weak_points,}