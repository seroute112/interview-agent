import os

from app.graph import graph
from langgraph.func import S

from app.state import InterviewState
from app.agents.evaluator import evaluator_node
from app.memory.sqlite_store import init_db,save_evaluation,get_evaluation_count,get_weak_points
from app.tools.report_tool import generate_report, save_report

with open("data/sample_jd.txt","r",encoding="utf-8") as f:
    jd_text = f.read()

with open("data/sample_resume.txt","r",encoding="utf-8") as f:
    resume_text = f.read()

if os.path.exists("data/interview.db"):
    os.remove("data/interview.db")

init_db()

state:InterviewState = {
    "message": [],
    "jd": jd_text,
    "resume": resume_text,
    "jd_keywords": [],
    "match_result": {},
    "questions": [],
    "current_questions": {},
    "user_answer": "",
    "evaluations": [],
    "weak_points": [],
    "round": 0,
    "report": ""
}

# 第一步：跑图，自动完成 JD解析 → 简历匹配 → 生成问题
state = graph.invoke(state)

print("JD关键词：", state["jd_keywords"])
print("匹配结果：", state["match_result"].get("summary"))
print()

questions = state.get("questions") or []
print(f"共生成 {len(questions)} 道题")
print()

# 第二步：逐题问答
for i, q in enumerate(questions):
    print("=" * 50)
    print(f"第 {i+1} 题：{q.get('question')}")
    print(f"考察点：{q.get('target')}")
    print("=" * 50)

    answer = input("\n请输入你的答案：\n")
    state["current_question"] = q
    state["user_answer"] = answer

    # 直接调用评估节点，不重新跑整张图
    result = evaluator_node(state)
    state["evaluations"] = result["evaluations"]
    state["weak_points"] = result["weak_points"]
    current_tags = result.get("current_weak_tags", [])

    last_eval = state["evaluations"][-1]
    print()
    print(f"得分：{last_eval['score']} / 10")
    print(f"优点：{last_eval['strengths']}")
    print(f"不足：{last_eval['weaknesses']}")
    print(f"建议：{last_eval['suggestion']}")

    save_evaluation(
        question=last_eval["question"],
        answer=last_eval["answer"],
        score=last_eval["score"],
        strengths=last_eval["strengths"],
        weaknesses=last_eval["weaknesses"],
        suggestion=last_eval["suggestion"],
        weak_tags=current_tags, 
    )
    print()

print("=" * 50)
print("面试结束")
print("累计评估次数：", get_evaluation_count())
print("历史弱项汇总：", get_weak_points())
print("=" * 50)

# 生成报告
report = generate_report(
    evaluations=state["evaluations"],
    weak_points=get_weak_points(),
    jd_keywords=state["jd_keywords"],
    match_result=state["match_result"],
)
report_path = save_report(report)
print(f"面试报告已生成：{report_path}")