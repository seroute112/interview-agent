import httpx
import streamlit as st
import os
import sys

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.memory.sqlite_store import init_db,save_evaluation
from app.graph import graph
from app.agents.evaluator import evaluator_node

API_BASE = "http://127.0.0.1:8000"
## 这个是使用FastAPI的版本
st.set_page_config(page_title="AI 面试系统",layout="wide")
st.title("多智能体面试模拟与评估系统")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
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
    with st.spinner("正在解析JD与简历"):
        resp = httpx.post(
            f"{API_BASE}/interview/start",
            json={"jd" : jd, "resume" : resume},
            timeout=120.0,
        )
    if resp.status_code == 200:
        data = resp.json()
        st.session_state.session_id = data["session_id"]
        st.session_state.questions = data["questions"]
        st.session_state.current_index = 0
        st.session_state.evaluations = []
        st.session_state.jd_keywords = data.get("jd_keywords",[])
        st.session_state.resume_summary = data.get("resume_summary",[])
    else:
        st.error(f"启动失败:{resp.text}")

if st.session_state.session_id:
    st.subheader("匹配分析结果")
    st.write(st.session_state.get("resume_summary",""))

    idx = st.session_state.current_index
    questions = st.session_state.questions

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
                with st.spinner("批改ing"):
                    resp = httpx.post(
                        f"{API_BASE}/interview/answer",
                        json={"session_id" : st.session_state.session_id,"question_index" : idx,"answer" : answer},
                        timeout=120.0,
                    )
                if resp.status_code == 200:
                    ev = resp.json()
                    ev["question"] = q["question"]
                    ev["answer"] = answer
                    st.session_state.evaluations.append(ev)

                    st.success(f"得分:{ev['score']}/10")
                    st.write(f"优点：{ev['strengths']}")
                    st.write(f"缺点：{ev['weaknesses']}")
                    st.write(f"建议：{ev['suggestion']}")

                    st.session_state.current_index += 1
                    st.rerun()
                else:
                    st.error(f"评估失败：{resp.text}")
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

