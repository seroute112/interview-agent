from typing import Literal
from app.state import InterviewState
from app.config import get_llm

SUPERVISOR_PROMPT = """ 你是一个面试流程调度器，请根据当前状态，选择下一步执行哪个节点
    请以 JSON 格式返回，例如 {"node": "jd_parser"}。

    可选节点：
    - jd_parser : 解析JD关键词
    - resume_matcher : 匹配简历与JD
    - question_generator : 面试问题生成
    - evaluator_tech : 开始评估用户回答的面试问题
    - _end_ : 流程结束 

    当前状态：
    - JD关键词：{jd_keywords}
    - 匹配结果：{match_result}
    - 已生成问题数：{question_count}
    - 已回答数：{answer_count}
    - 是否有待评估回答：{has_pending_answer}

    判断规则,请按顺序判断，如果有符合条件的节点立即停止判断，然后返回节点名字：
    1.如果jd_keywords为空,返回jd_parser
    2.如果match_result为空,返回resume_matcher
    3.如果questions为空,返回question_generator
    4.如果has_pending_answer 为 True,返回evaluator_tech
    5.如果has_pending_answer 为 False ，且answer_count不为0，且 reflection_result 为空，则返回reflector
    6.如果 reflection_result 有值 → __end__
    7.只返回节点名字，不需要其他内容
"""

def router(state: InterviewState) -> Literal["jd_parser","resume_matcher","question_generator","question_generator","evaluator_tech","reflector","__end__"]:
    last = state["messages"][-1].content.strip().lower()

    if "jd_parser" in last:
        return "jd_parser"
    if "resume_matcher" in last:
        return "resume_matcher"
    if "question_generator" in last:
        return "question_generator"
    if "evaluator_tech" in last:
        return "evaluator_tech"
    if "reflector" in last:
        return "reflector"
    
    return "__end__"

def supervisor_node(state: InterviewState):
    llm = get_llm()

    jd_keywords = state.get("jd_keywords") or []
    match_result = state.get("match_result") or {}
    questions = state.get("questions") or []
    evaluations = state.get("evaluations") or []
    current_question = state.get("current_question") or {}
    user_answer = state.get("user_answer") or ""
    summary_result = state.get("summary_result") or ""
    reflection_result = state.get("reflection_result") or {}

    has_pending_answer = bool(current_question and user_answer) and not summary_result
    print(has_pending_answer)

    prompt = (
        SUPERVISOR_PROMPT
        .replace("{jd_keywords}", ", ".join(jd_keywords) if jd_keywords else "空")
        .replace("{match_result}", str(match_result) if match_result else "空")
        .replace("{question_count}", str(len(questions)))
        .replace("{answer_count}", str(len(evaluations)))
        .replace("{has_pending_answer}", "是" if has_pending_answer else "否")
    )

    response = llm.invoke(prompt)
    decision = response.content.strip().lower()

    valid_nodes = ["jd_parser", "resume_matcher", "question_generator", "evaluator_tech","reflector", "__end__"]
    matched = None
    for node in valid_nodes:
        if node in decision:
            matched = node
            break

    if not matched:
        if not jd_keywords:
            matched = "jd_parser"
        elif not match_result:
            matched = "resume_matcher"
        elif not questions:
            matched = "question_generator"
        elif has_pending_answer:
            matched = "evaluator_tech"
        elif not reflection_result:
            matched = "reflector"
        else:
            matched = "__end__"

    return {"messages": [{"role": "assistant", "content": matched}]}