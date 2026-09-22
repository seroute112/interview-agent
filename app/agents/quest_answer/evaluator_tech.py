from app.state import InterviewState
from app.tools.eval_common import run_evaluator

TECH_PROMPT = """你是一个技术面试官，专注评估回答的技术正确性，只返回JSON。

评判维度：
1. 技术概念是否准确
2. 有没有事实性错误
3. 原理描述是否清晰
4. 如果有评估反思，只看评估反思部分即evaluation_quality和evaluate_suggestions,请根据反思内容酌情修改评估结果

只评估技术方面的内容，其他方面是其他面试官的工作。

返回格式：
{
  "score": 8,
  "strengths": ["技术点准确的地方"],
  "weaknesses": ["技术错误或遗漏的地方"],
  "suggestion": "技术层面的改进建议",
  "weak_tags": ["概念不深入", "缺少细节"]
}

"""

def evaluator_tech_node(state:InterviewState):
    print("1")
    # evaluations = state.get("evaluations") or []
    # evaluations.append({
    #     "question": state["current_question"].get("question", ""),
    #     "answer": state.get("user_answer", ""),
    # })
    # state["evaluations"] = evaluations
    return run_evaluator(state,TECH_PROMPT,prefix="tech")