from app.config import get_llm
from app.state import InterviewState
from app.tools.llm_json import parser_llm_json
from app.memory.reflection_store import get_recent_reflections

def run_evaluator(state:InterviewState,prompt:str,prefix:str)->dict:
    llm = get_llm()

    question = state["current_question"].get("question","")
    answer = state.get("user_answer")

    reflections = get_recent_reflections(limit=3)
    if reflections:
        reflection_text = "\n".join(
            f"- 提问质量 {r['evaluation_quality']}/10，"
            f"建议：{'; '.join(r['evaluate_suggestions']) if r['evaluate_suggestions'] else '无'}"
            for r in reflections
        )
    else:
        reflection_text = "暂无历史反思"
    

    full_prompt = (prompt + "\n\n面试问题：\n" + question + "\n\n候选人回答：\n" + answer + "\n\n评估反思:\n" + reflection_text)

    response = llm.invoke(full_prompt)
    parsed = parser_llm_json(response.content)

    parsed = {}
    for attempt in range(3):
        response = llm.invoke(full_prompt)
        parsed = parser_llm_json(response.content)
        if parsed:
            break
        print(f"[{prefix}] 第 {attempt+1} 次返回空，重试...")

    parsed.setdefault("score", 0)
    parsed.setdefault("strengths", [])
    parsed.setdefault("weaknesses", [])
    parsed.setdefault("suggestion", "")
    parsed.setdefault("weak_tags", [])

    # evaluations = state.get("evaluations") or []
    # if evaluations:
    #     evaluations[-1][f"{prefix}_score"] = parsed["score"]
    #     evaluations[-1][f"{prefix}_strengths"] = parsed["strengths"]
    #     evaluations[-1][f"{prefix}_weaknesses"] = parsed["weaknesses"]
    #     evaluations[-1][f"{prefix}_suggestion"] = parsed["suggestion"]
    #     evaluations[-1][f"{prefix}_weak_tags"] = parsed["weak_tags"]

    return {
        f"{prefix}_result": parsed,
    }