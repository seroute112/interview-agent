from typing import TypedDict , Annotated, List
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    messages: Annotated[List, add_messages]
    jd:str
    resume:str
    jd_keywords:List[str]
    match_result:dict
    questions:List[dict]
    current_question:dict
    user_answer:str
    evaluations:list[dict]
    weak_points:List[str]
      # 流程控制
    round:int
    report:str
    round_history: List[dict]
    # 三个评估 Agent 的结果
    tech_result: dict
    engineering_result: dict
    communication_result: dict
    #总结
    summary_result: dict
    #评估总结
    reflection_result:dict
    #mem0
    pending_intent: str
    last_intent: str
    user_id: str
    # 裁决内容
    # arbiter_result: dict
    # has_pending_review: bool
 