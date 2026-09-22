import streamlit as st
import httpx
import uuid
import os

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")


if "mode" not in st.session_state:
    st.session_state.mode = "interview"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []
if "round" not in st.session_state:
    st.session_state.round = 1

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

header_left, header_right = st.columns([8, 2])

with header_left:
    if st.session_state.mode == "interview":
        st.title("多智能体面试模拟")
    else:
        st.title("AI 助手")

with header_right:

    st.write("")
    if st.session_state.mode == "interview":
        if st.button("💬 聊天模式", use_container_width=True):
            st.session_state.mode = "chat"
            st.rerun()
    else:
        if st.button("📝 面试模式", use_container_width=True):
            st.session_state.mode = "interview"
            st.rerun()


def render_interview():
    with st.sidebar:
        st.header("输入")
        jd = st.text_area("JD 文本", height=200)
        resume = st.text_area("简历文本", height=200)
        start = st.button("开始面试")

    if start and jd and resume:
        with st.spinner("多 Agent 正在解析 JD 和简历..."):
            resp = httpx.post(
                f"{API_BASE}/interview/start",
                json={"jd": jd, "resume": resume},
                timeout=120.0,
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.questions = data["questions"]
            st.session_state.current_index = 0
            st.session_state.evaluations = []
            st.session_state.round = 1
            st.session_state.match_summary = data.get("match_summary", "")
            st.session_state.jd_keywords = data.get("jd_keywords", [])
        else:
            st.error(f"启动失败：{resp.text}")

    if st.session_state.session_id:
        st.subheader(f"第 {st.session_state.round} 轮")
        st.write(st.session_state.get("match_summary", ""))

        idx = st.session_state.current_index
        questions = st.session_state.questions

        if idx < len(questions):
            q = questions[idx]
            st.subheader(f"第 {idx + 1} / {len(questions)} 题")
            st.markdown(f"**{q['question']}**")
            st.caption(f"考察点：{q.get('target', '')}")

            answer = st.text_area("你的回答", key=f"answer_{idx}")
            if st.button("提交回答"):
                if not answer.strip():
                    st.warning("回答不能为空")
                else:
                    with st.spinner("评估中..."):
                        resp = httpx.post(
                            f"{API_BASE}/interview/answer",
                            json={
                                "session_id": st.session_state.session_id,
                                "question_index": idx,
                                "answer": answer,
                            },
                            timeout=120.0,
                        )
                    if resp.status_code == 200:
                        ev = resp.json()
                        ev["question"] = q["question"]
                        ev["answer"] = answer
                        ev["index"] = idx + 1
                        st.session_state.evaluations.append(ev)
                        st.session_state.current_index += 1
                        st.success(f"得分：{ev['score']} / 10")
                        st.write("**技术分**：", ev.get("tech_score"))
                        st.write("**工程分**：", ev.get("engineering_score"))
                        st.write("**表达分**：", ev.get("communication_score"))
                        st.write("**建议**：", ev.get("suggestion"))
                        st.rerun()
                    else:
                        st.error(f"评估失败：{resp.text}")
        else:
            st.subheader("本轮结束")
            evals = st.session_state.evaluations
            if evals:
                avg = sum(e["score"] for e in evals) / len(evals)
                st.metric("平均分", f"{avg:.1f} / 10")
                for i, e in enumerate(evals, 1):
                    with st.expander(f"第 {e['index']} 题：{e['score']} 分"):
                        st.write("**问题**：", e["question"])
                        st.write("**你的回答**：", e["answer"])
                        st.write("**建议**：", e.get("suggestion"))

            if st.button("继续下一轮"):
                with st.spinner("正在生成本轮题目..."):
                    resp = httpx.post(
                        f"{API_BASE}/interview/next_round",
                        json={"session_id": st.session_state.session_id},
                        timeout=120.0,
                    )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.questions = data["questions"]
                    st.session_state.current_index = 0
                    st.session_state.evaluations = []
                    st.session_state.round = data["round"]
                    st.success(f"进入第 {data['round']} 轮。{data['previous_summary']}")
                    st.rerun()
                else:
                    st.error(f"下一轮启动失败：{resp.text}")

def render_chat():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("输入消息...")
    if user_input:

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("思考中..."):
            resp = httpx.post(
                f"{API_BASE}/chat",
                json={
                    "session_id": st.session_state.chat_session,
                    "user_id": st.session_state.user_id,
                    "message": user_input,
                },
                timeout=120.0,
            )

        if resp.status_code == 200:
            data = resp.json()
            st.session_state.chat_session = data["session_id"]
            reply = data["reply"]

            if data.get("intent") == "interview" and data.get("data", {}).get("questions"):
                st.session_state.questions = data["data"]["questions"]
                st.session_state.current_index = 0
                st.session_state.evaluations = []
                st.session_state.round = 1
                st.session_state.mode = "interview"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
                st.rerun()
            else:
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
                st.rerun()
        else:
            st.error(f"请求失败：{resp.text}")

if st.session_state.mode == "interview":
    render_interview()
else:
    render_chat()