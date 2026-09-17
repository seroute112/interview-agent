from typing import Literal
from app.state import InterviewState
from langchain_core.messages import SystemMessage,HumanMessage


SUPERVISOR_PROMPT = """ 你是一个面试流程调度器，请根据当前状态，选择下一步执行哪个节点

    可选节点：
    - jd_parser : 解析JD关键词
    - resume_matcher : 匹配简历与JD
    - question_generator : 面试问题生成
    - evaluator : 评估用户回答的面试问题
    - _end_ : 流程结束 

    判断规则：
    1.如果jd_keywords为空,返回jd_parser
    2.如果match_result为空,返回resume_matcher
    3.如果questions为空,返回question_generator
    4.如果current_question有值,且user_answer有值,且evaluations 数量小于 questions ,返回evaluator
    5.如果evaluations 数量等于 questions,返回_end_
    6.只返回节点名字，不需要其他内容
"""

def supervisor_node(state: InterviewState):
    if not state.get("jd_keywords"):
        return {"messages":[{"role":"assistant","content":"jd_parser"}]}
    if not state.get("match_result"):
        return {"messages":[{"role":"assistant","content":"resume_matcher"}]}
    if not state.get("questions"):
            return {"messages":[{"role":"assistant","content":"question_generator"}]}

    questions = state.get("questions") or []
    evaluations = state.get("evaluations") or []

    if len(evaluations) < len(questions):
         if state.get("current_question") and state.get("user_answer"):
              return {"messages":[{"role":"assistant","content":"evaluator"}]}
         else:
              return {"messages":[{"role":"assistant","content":"_end_"}]}

    return {"messages": [{"role": "assistant", "content": "__end__"}]}

def router(state: InterviewState) -> Literal["jd_parser","resume_matcher","question_generator","question_generator","evaluator","__end__"]:
    last = state["messages"][-1].content.strip().lower()

    if "jd_parser" in last:
        return "jd_parser"
    if "resume_matcher" in last:
        return "resume_matcher"
    if "question_generator" in last:
        return "question_generator"
    if "evaluator" in last:
        return "evaluator"
    
    return "__end__"