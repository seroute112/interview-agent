from app.config import get_llm
from app.state import InterviewState
from app.tools.llm_json import parser_llm_json
from app.memory.reflection_store import save_reflection

REFLECTOR_PROMPT = """你是一个面试系统质量审核员。请评估本轮面试的系统质量，只返回JSON。

    评估维度：
    1. question_quality：提问质量（1-10分）
    - 问题是否紧扣 JD 和简历差距
    - 难度分布是否合理
    - 是否覆盖了关键考察点
    2. evaluation_quality：评估质量（1-10分）
    - 三方评估是否客观
    - 综合结果是否合理
    - 弱项标签是否有区分度
    3. quest_suggestions：对下一轮面试的提问方面的改进建议（2-4 条字符串）
    4. evaluate_suggestions：对下一轮面试的评估方面的改进建议（2-4 条字符串）

    返回格式：
    {
    "question_quality": 8,
    "evaluation_quality": 7,
    "quest_suggestions": ["建议1", "建议2", "建议3"]
    "evaluate_suggestions": ["建议1", "建议2", "建议3"]
    }
"""

def reflector_node(state:InterviewState):
    llm = get_llm()

    questions = state.get("questions") or []
    evaluations = state.get("evaluations") or []
    jd_keywords = state.get("jd_keywords") or []

    questions_brief = "\n".join(
        f"- {q.get('question', '')}（考察点：{q.get('target', '')}）"
        for q in questions
    )
    evals_brief = "\n".join(
        f"问题文本：{e.get('question','')},回答：{e.get('answer','')}"
        f"- 技术{e.get('tech_score', 0)}/工程{e.get('engineering_score', 0)}"
        f"/表达{e.get('communication_score', 0)}，最终{e.get('score', 0)}"
        f"总结:{e.grt('summary','')}"
        for e in evaluations
    )

    prompt = (
        REFLECTOR_PROMPT
        + f"\n\n本轮 JD 关键词：{', '.join(jd_keywords)}"
        + f"\n\n本轮问题：\n{questions_brief}"
        + f"\n\n本轮评估结果：\n{evals_brief}"
    )
    print(f"\n\n本轮 JD 关键词：{', '.join(jd_keywords)}"+ f"\n\n本轮问题：\n{questions_brief}"+ f"\n\n本轮评估结果：\n{evals_brief}")

    response = llm.invoke(prompt)
    parsed = parser_llm_json(response.content)

    parsed.setdefault("question_quality", 0)
    parsed.setdefault("evaluation_quality", 0)
    parsed.setdefault("quest_suggestions", [])
    parsed.setdefault("evaluate_suggestions", [])

    try:
        save_reflection(parsed, jd_keywords)
        print("反思已存入数据库")
    except Exception as e:
        print(f"存储失败：{e}")

    return {"reflection_result": parsed}