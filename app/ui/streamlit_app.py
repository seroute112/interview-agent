import streamlit as st
import os
import sys

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.memory.sqlite_store import init_db,save_evaluation
from app.graph import graph
from app.agents.evaluator import evaluator_node

init_db()
## 这个是不使用FastAPI的版本
st.set_page_config(page_title="AI 面试系统",layout="wide")
st.title("多智能体面试模拟与评估系统")

if "state" not in st.session_state:
    st.session_state.state = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

with st.sidebar:
    st.header("输入")
    jd = st.text_area("JD 文本",height=200)
    resume = st.text_area("简历文本",height=200)
    start = st.button("开始面试")

if jd and resume and start:
    state = { "message": [],"jd": jd,"resume": resume,
            "jd_keywords": [],"match_result": {},"questions": [],
            "current_questions": {},"user_answer": "","evaluations": [],
            "weak_points": [],"round": 0,"report": ""
    }
    with st.spinner("正在解析JD与简历"):
        state = graph.invoke(state)

    st.session_state.state = state
    st.session_state.questions = state.get("questions",[])
    st.session_state.current_index = 0
    st.session_state.evaluations = []

if st.session_state.state:
    state = st.session_state.state
    questions = st.session_state.questions
    idx = st.session_state.current_index

    st.subheader("匹配分析结果")
    st.write(state["match_result"].get("summary",""))

    if idx < len(questions):
        q = questions[idx]
        st.subheader(f"第{idx+1}/{len(questions)}题")
        st.markdown(f"**{q['question']}**")
        st.caption(f"考察点:{q.get('target','')}")

        answer = st.text_area("你的回答",key = f"answer_{idx}")
        if st.button("提交回答"):
            if not answer.strip():
                st.warning("回答不能为空")
            else:
                state["current_question"] = q
                state["user_answer"] = answer
                with st.spinner("批改ing"):
                    result = evaluator_node(state)

                state["evaluations"] = result["evaluations"]
                state["weak_points"] = result["weak_points"]

                last = state["evaluations"][-1]
                save_evaluation(question= q["question"],answer=answer,score=last["score"],strengths=last["strengths"],weaknesses=last["weaknesses"],suggestion=last["suggestion"],weak_tags=last.get("weak_tags",[]),)

                st.session_state.state = state
                st.session_state.evaluations = state["evaluations"]
                st.session_state.current_index += 1

                st.success(f"得分:{last['score']}/10")
                st.write(f"优点：{last['strengths']}")
                st.write(f"缺点：{last['weaknesses']}")
                st.write(f"建议：{last['suggestion']}")
                st.rerun()
    else:
        st.header("面试结束")
        evals = st.session_state.evaluations
        if eval:
            avg = sum(e["score"] for e in evals)/len(evals)
            st.write(f"平均分:{avg:.1f}/10")
            for i,e in enumerate(evals,1):
                with st.expander(f"第{i}题得分:{e['score']}/10"):
                    st.write(f"问题：{e['question']}")
                    st.write(f"回答：{e['answer']}")
                    st.write(f"建议：{e['suggestion']}")

