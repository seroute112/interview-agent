from app.config import get_llm
from app.agents.quest_answer.evaluator_tech import evaluator_tech_node
from app.agents.quest_answer.evaluator_engineering import evaluator_engineering_node
from app.agents.quest_answer.evaluator_communication import evaluator_communication_node
from app.state import InterviewState
from app.tools.llm_json import parser_llm_json

ARBITER_PROMPT = """你是一个资深技术面试仲裁官。三位面试官对同一份回答评分差异较大，请独立裁决。

要求：
1. 独立判断，参考三方理由但要有自己的技术判断。
2. 给出 1-10 分的最终分数和裁决理由。

返回格式：
{
  "final_score": 7,
  "reason": "裁决理由"
}
"""