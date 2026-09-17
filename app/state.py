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
    round:int
    report:str