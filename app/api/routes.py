import tempfile
from typing import List, Optional

from altair import NonLayerRepeatSpec
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
import os

from app.memory.sqlite_store import init_db,save_evaluation
from app.state import InterviewState
from app.graph import graph
from app.api.session_store import create_session,get_session,update_session,delete_session
from app.agents.evaluator import evaluator_node
from app.tools.file_parser import parse_file
from app.memory.topic_tracker import init_topic_table
from app.agents.intent_router import classify_intent
from app.agents.resume_analyzer import analyze_resume
from app.agents.job_matcher import match_job
from app.memory.reflection_store import init_reflection_table
from app.memory.user_memory import save_user_message, search_user_memory
from app.tools.report_tool import generate_report


router = APIRouter()

init_db()
init_topic_table()
init_reflection_table()

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

class SessionRequest(BaseModel):
    session_id : str

class NextRoundResponse(BaseModel):
    session_id : str
    round : int
    questions : List[QuestionItem]
    previous_summary : str

class ChatRequest(BaseModel):
    session_id: Optional[str] = NonLayerRepeatSpec
    user_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    intent: str
    reply: str
    data: Optional[dict] = None 

class ReportRequest(BaseModel):
    session_id: str

@router.post("/interview/start", response_model=StartResponse)
def start_interview(req : StartRequest):
    if not req.jd.strip():
        raise HTTPException(status_code=400, detail="JD 不能为空")
    if not req.resume.strip():
        raise HTTPException(status_code=400, detail="简历不能为空")

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
    if not req.answer.strip():
        raise HTTPException(status_code=400, detail="回答不能为空")
    
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

@router.post("/interview/start/upload", response_model=StartResponse)
async def start_interview_upload(jd_file : UploadFile = File(...),resume_file : UploadFile = File(...)):
    """支持txt,docx,pdf文件上传"""
    jd_text = ""
    resume_text = ""

    for file, target in [(jd_file,"jd"),(resume_file,"resume")]:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            text = parse_file(tmp_path)
        finally:
            os.remove(tmp_path)

        if target == "jd":
            jd_text = text
        if target == "resume":
            resume_text = text
    if not jd_text.strip() or not resume_text.strip():
        raise HTTPException(status_code=400,detail="文件解析结果为空，请检查文件内容")

    return start_interview(StartRequest(jd=jd_text,resume=resume_text))

@router.post("/interview/next_round", response_model=NextRoundResponse)
def next_round(req: SessionRequest):
    state = get_session(req.session_id)
    if not state:
        raise HTTPException(status_code=404,detail="回话不存在或已过期")

    questions = state.get("questions") or []
    evaluations = state.get("evaluations") or[]

    if questions and evaluations:
        scores = [e.get("score",0) for e in evaluations]
        avg = round(sum(scores)/len(scores),1) if scores else 0

        history = state.get("round_history") or []
        history.append({
            "round": state.get("round", 1),
            "questions": questions,
            "evaluations": evaluations,
            "avg_score": avg,
        })
        state["round_history"] = history

        previous_summary = (
            f"第 {state.get('round', 1)} 轮共 {len(questions)} 题，"
            f"平均分 {avg}/10。"
            f"薄弱考察点：{', '.join(set(state.get('weak_points') or []))}"
        )

    else:
        previous_summary = "上一轮无有效回答"

    state["round"] = state.get("round", 0) + 1
    state["questions"] = []
    state["evaluations"] = []       # 注意：清空，历史在 round_history 里
    state["current_question"] = {}
    state["user_answer"] = ""
    state["tech_result"] = {}
    state["engineering_result"] = {}
    state["communication_result"] = {}
    state["summary_result"] = {}
    state["reflection_result"] = {}  # 每轮结束后重新反思
    state["arbiter_result"] = {}
    state["has_pending_review"] = False

    state = graph.invoke(state)

    if not state.get("questions"):
        raise HTTPException(status_code=500, detail="下一轮问题生成失败")

    update_session(req.session_id, state)

    return NextRoundResponse(
        session_id=req.session_id,
        round=state["round"],
        questions=[QuestionItem(**q) for q in state["questions"]],
        previous_summary=previous_summary,
    )

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    if req.session_id:
        state = get_session(req.session_id)
        if not state:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        state = {
            "messages": [],
            "jd": "",
            "resume": "",
            "jd_keywords": [],
            "match_result": {},
            "questions": [],
            "current_question": {},
            "user_answer": "",
            "evaluations": [],
            "weak_points": [],
            "round": 0,
            "report": "",
            "tech_result": {},
            "engineering_result": {},
            "communication_result": {},
            "summary_result": {},
            "reflection_result": {},
            "arbiter_result": {},
            "has_pending_review": False,
            "round_history": [],
            "pending_intent": "",
            "last_intent": "",
            "user_id": req.user_id or "default_user",
        }
        session_id = create_session(state)

    user_id = req.user_id or state.get("user_id") or "default_user"
    state["user_id"] = user_id

    history_list = search_user_memory(user_id, req.message, limit=5)
    if history_list:
        history_text = "\n".join(f"- {h}" for h in history_list)
    else:
        history_text = "暂无历史"

    pending = state.get("pending_intent", "")

    if pending == "interview":
        parts = req.message.split("\n\n")
        if len(parts) >= 2:
            state["jd"] = parts[0]
            state["resume"] = "\n\n".join(parts[1:])
            state["pending_intent"] = ""
            state["last_intent"] = "interview"
            state = graph.invoke(state)
            update_session(session_id, state)

            reply = f"已生成 {len(state['questions'])} 道面试题，可以开始答题。"
            save_user_message(user_id, req.message, reply)

            return ChatResponse(
                session_id=session_id,
                intent="interview",
                reply=reply,
                data={"questions": state["questions"]},
            )
        else:
            return ChatResponse(
                session_id=session_id,
                intent="interview",
                reply="请提供 JD 和简历，用两个空行分隔。",
            )

    if pending == "resume_analysis":
        result = analyze_resume(req.message)
        state["resume"] = req.message
        state["pending_intent"] = ""
        state["last_intent"] = "resume_analysis"
        update_session(session_id, state)

        suggestions = "\n".join(f"- {s}" for s in result["suggestions"])
        reply = f"简历分析完成：\n{suggestions}"
        save_user_message(user_id, req.message, reply)

        return ChatResponse(
            session_id=session_id,
            intent="resume_analysis",
            reply=reply,
            data=result,
        )

    if pending == "job_match":
        parts = req.message.split("\n\n")
        if len(parts) >= 2:
            state["jd"] = parts[0]
            state["resume"] = "\n\n".join(parts[1:])
            state["pending_intent"] = ""
            state["last_intent"] = "job_match"
            result = match_job(state["resume"], state["jd"])
            update_session(session_id, state)

            advice = "\n".join(f"- {a}" for a in result["advice"])
            reply = f"匹配度 {result['match_score']}/100。{result['summary']}\n{advice}"
            save_user_message(user_id, req.message, reply)

            return ChatResponse(
                session_id=session_id,
                intent="job_match",
                reply=reply,
                data=result,
            )
        else:
            return ChatResponse(
                session_id=session_id,
                intent="job_match",
                reply="请提供 JD 和简历，用两个空行分隔。",
            )

    intent_result = classify_intent(req.message, history_text)
    intent = intent_result["intent"]

    # ---------- 5. 按意图路由 ----------
    if intent == "interview":
        state["pending_intent"] = "interview"
        update_session(session_id, state)
        reply = "好的，请提供 JD 和简历，用两个空行分隔。"
        save_user_message(user_id, req.message, reply)
        return ChatResponse(session_id=session_id, intent="interview", reply=reply)

    if intent == "resume_analysis":
        if len(req.message) > 100:
            result = analyze_resume(req.message)
            state["resume"] = req.message
            state["last_intent"] = "resume_analysis"
            update_session(session_id, state)

            suggestions = "\n".join(f"- {s}" for s in result["suggestions"])
            reply = f"简历分析完成：\n{suggestions}"
            save_user_message(user_id, req.message, reply)

            return ChatResponse(
                session_id=session_id,
                intent="resume_analysis",
                reply=reply,
                data=result,
            )
        else:
            state["pending_intent"] = "resume_analysis"
            update_session(session_id, state)
            reply = "请把你的简历内容粘贴给我。"
            save_user_message(user_id, req.message, reply)
            return ChatResponse(session_id=session_id, intent="resume_analysis", reply=reply)

    if intent == "job_match":
        state["pending_intent"] = "job_match"
        update_session(session_id, state)
        reply = "请提供 JD 和简历，用两个空行分隔。"
        save_user_message(user_id, req.message, reply)
        return ChatResponse(session_id=session_id, intent="job_match", reply=reply)

    if intent == "continue_previous":
        last = state.get("last_intent", "")

        if last == "resume_analysis" and state.get("resume"):
            result = analyze_resume(state["resume"])
            suggestions = "\n".join(f"- {s}" for s in result["suggestions"])
            reply = f"基于上次简历的进一步分析：\n{suggestions}"
            save_user_message(user_id, req.message, reply)
            return ChatResponse(
                session_id=session_id,
                intent="resume_analysis",
                reply=reply,
                data=result,
            )

        if last == "job_match" and state.get("resume") and state.get("jd"):
            result = match_job(state["resume"], state["jd"])
            advice = "\n".join(f"- {a}" for a in result["advice"])
            reply = f"再次匹配：{result['match_score']}/100。{advice}"
            save_user_message(user_id, req.message, reply)
            return ChatResponse(
                session_id=session_id,
                intent="job_match",
                reply=reply,
                data=result,
            )

        reply = "我这边没有找到可以延续的操作，请告诉我想做什么。"
        save_user_message(user_id, req.message, reply)
        return ChatResponse(session_id=session_id, intent="unknown", reply=reply)

    reply = (
        "未知指令，我可以帮你：\n"
        "- 模拟面试（说\"我想模拟面试\"）\n"
        "- 分析简历（说\"帮我看看简历\"）\n"
        "- 岗位匹配（说\"看看我适不适合这个岗位\"）"
    )
    save_user_message(user_id, req.message, reply)
    return ChatResponse(session_id=session_id, intent="unknown", reply=reply)

@router.post("/interview/report")
def get_report(req: ReportRequest):
    state = get_session(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="会话不存在")

    report = generate_report(
        evaluations=state.get("evaluations") or [],
        weak_points=state.get("weak_points") or [],
        jd_keywords=state.get("jd_keywords") or [],
        match_result=state.get("match_result") or {},
        user_id=state.get("user_id", "default_user"),
        round_history=state.get("round_history") or [],
    )

    return {"report": report}