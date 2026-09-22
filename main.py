# 命令行入口：跑一次完整面试流程

from app.state import InterviewState
from app.graph import graph
from app.memory.sqlite_store import init_db, save_evaluation, get_weak_points, get_evaluation_count
from app.memory.topic_tracker import init_topic_table

# 初始化数据库表
init_db()
init_topic_table()

# 读取样例数据
with open("data/sample_jd.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()

with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
    resume_text = f.read()

# 初始化状态
state: InterviewState = {
    "messages": [],
    "jd": jd_text,
    "resume": resume_text,
    "jd_keywords": [],
    "match_result": {},
    "questions": [],
    "current_question": {},
    "user_answer": "",
    "evaluations": [],
    "weak_points": [],
    "round": 0,
    "round_history": [],
    "report": "",
    # 三个评估结果
    "tech_result": {},
    "engineering_result": {},
    "communication_result": {},
    # 综合结果
    "summary_result": {},
    "reflection_result": {},

    "pending_intent": "",
    "last_intent": "",
    "user_id": "default_user",
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

    answer = input("\n请输入你的答案：\n").strip()
    if not answer:
        print("未检测到回答，跳过本题。")
        continue

    state["current_question"] = q
    state["user_answer"] = answer

    # 跑图触发三个评估 + Summarizer
    state = graph.invoke(state)

    last_eval = state["evaluations"][-1]
    print()
    print(f"技术分：{last_eval.get('tech_score')}")
    print(f"工程分：{last_eval.get('engineering_score')}")
    print(f"表达分：{last_eval.get('communication_score')}")
    print(f"最终分：{last_eval.get('score')} / 10")
    print(f"综合评语：{last_eval.get('summary')}")
    print(f"建议：{last_eval.get('suggestion')}")

    # 存入数据库
    save_evaluation(
        question=last_eval["question"],
        answer=last_eval["answer"],
        score=last_eval["score"],
        strengths=last_eval["strengths"],
        weaknesses=last_eval["weaknesses"],
        suggestion=last_eval["suggestion"],
        weak_tags=last_eval.get("weak_tags", []),
    )

    # 一道题完成后，清空中间状态，避免下一题被误判
    state["tech_result"] = {}
    state["engineering_result"] = {}
    state["communication_result"] = {}
    state["summary_result"] = {}
    state["arbiter_result"] = {}
    state["has_pending_review"] = False
    state["current_question"] = {}
    state["user_answer"] = ""
    print()

print("=" * 50)
print("面试结束")
print("累计评估次数：", get_evaluation_count())
print("历史弱项汇总：", get_weak_points())
print("=" * 50)

# 生成报告
# report = generate_report(
#     evaluations=state["evaluations"],
#     weak_points=get_weak_points(),
#     jd_keywords=state["jd_keywords"],
#     match_result=state["match_result"],
# )
# report_path = save_report(report)
# print(f"面试报告已生成：{report_path}")