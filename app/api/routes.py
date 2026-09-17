from typing import List, Optional

from fastapi import APIRouter, HTTPException
from openai import BaseModel

from app.memory.sqlite_store import init_db,save_evaluation
from app.state import InterviewState
from app.graph import graph
from app.api.session_store import create_session,get_session,update_session,delete_session
from app.agents.evaluator import evaluator_node


router = APIRouter()

init_db()

class StartRequest(BaseModel):
    jd : str
    resume : str

class QuestionItem(BaseModel):
    question : str
    target : str
    difficulty : Optional[str] = ""
    type : Optional[str] = ""

class StartResponse(BaseModel):
    session_id : str
    jd_keywords : List[str]
    resume_summary : str
    questions : List[QuestionItem]

class AnswerRequest(BaseModel):
    session_id : str
    question_index : int
    answer : str

class AnswerResponse(BaseModel):
    score : int
    strengths : List[str]
    weaknesses : List[str]
    suggestion : str
    weak_tags : List[str]
    is_last : bool

@router.post("/interview/start", response_model=StartResponse)
def start_interview(req : StartRequest):
    state : InterviewState = {
        "messages": [],
        "jd": req.jd,
        "resume": req.resume,
        "jd_keywords": [],
        "match_result": {},
        "questions": [],
        "current_question": {},
        "user_answer": "",
        "evaluations": [],
        "weak_points": [],
        "round": 0,
        "report": "",
    }

    state = graph.invoke(state)

    if not state.get("questions"):
        raise HTTPException(status_code=500,detail="问题生成失败，请重试")

    session_id = create_session(state)

    return StartResponse(session_id=session_id,jd_keywords=state["jd_keywords"],resume_summary= state["match_result"].get("summary",""),questions=[QuestionItem(**q) for q in state["questions"]])

@router.post("/interview/answer",response_model=AnswerResponse)
def answer_question(req : AnswerRequest):
    state = get_session(req.session_id)
    if not state:
        raise HTTPException(status_code=404,detail="回话不存在或已过期")

    questions = state.get("questions") or []
    if req.question_index < 0 or req.question_index > len(questions):
        raise HTTPException(status_code=400,detail="题目编号越界")

    q = questions[req.question_index]
    state["current_question"] = q
    state["user_answer"] = req.answer

    result = evaluator_node(state)
    state["evaluations"] = result["evaluations"]
    state["weak_points"] = result["weak_points"]

    last_eval = state["evaluations"][-1]

    save_evaluation(
        question=last_eval["question"],
        answer=last_eval["answer"],
        score=last_eval["score"],
        strengths=last_eval["strengths"],
        weaknesses=last_eval["weaknesses"],
        suggestion=last_eval["suggestion"],
        weak_tags=last_eval.get("weak_tags", []),
        )

    update_session(req.session_id,state)

    is_last = req.question_index == len(questions) - 1

    return AnswerResponse(score=last_eval["score"],strengths=last_eval["strengths"],weaknesses=last_eval["weaknesses"],suggestion=last_eval["suggestion"],weak_tags=last_eval.get("weak_tags",[]),is_last=is_last)