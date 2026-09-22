from app.state import InterviewState
from app.tools.eval_common import run_evaluator

ENGINEERING_PROMPT = """你是一个资深工程师面试官，专注评估回答的工程实践，只返回JSON。

评判维度：
1. 有没有结合实际场景举例
2. 有没有量化数据或具体参数
3. 有没有讨论技术选型的权衡取舍
4. 有没有提到踩坑经验或边界情况
5. 如果有评估反思，只看评估反思部分即evaluation_quality和evaluate_suggestions,请根据反思内容酌情修改评估结果

只评估工程实践方面的内容，其他方面是其他面试官的工作。

返回格式：
{
  "score": 8,
  "strengths": ["工程视角的优点"],
  "weaknesses": ["工程视角的不足"],
  "suggestion": "工程层面的改进建议",
  "weak_tags": ["缺少场景", "缺少量化数据"]
}

"""

def evaluator_engineering_node(state:InterviewState):
    print("2")
    return run_evaluator(state,ENGINEERING_PROMPT,prefix="engineering")