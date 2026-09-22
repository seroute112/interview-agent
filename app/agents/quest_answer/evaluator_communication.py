from app.state import InterviewState
from app.tools.eval_common import run_evaluator

COMMUNICATION_PROMPT = """你是一个面试沟通能力评估官，专注评估回答的表达与逻辑，只返回JSON。

评判维度：
1. 回答结构是否清晰，有没有分点或分层
2. 是否直接答到问题上，有没有跑题
3. 有没有总结或收尾
4. 语言是否简洁，有没有冗余
5. 如果有评估反思，只看评估反思部分即evaluation_quality和evaluate_suggestions,请根据反思内容酌情修改评估结果

只评估有关面试沟通能力的方面，其他方面是其他面试官的工作。

返回格式：
{
  "score": 8,
  "strengths": ["表达层面的优点"],
  "weaknesses": ["表达层面的不足"],
  "suggestion": "表达层面的改进建议",
  "weak_tags": ["逻辑混乱", "答非所问", "缺少总结"]
}
"""


def evaluator_communication_node(state: InterviewState,):
    return run_evaluator(state, COMMUNICATION_PROMPT,prefix="communication")