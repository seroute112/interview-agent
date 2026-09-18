from app.agents.evaluator import evaluator_node
from tests.test_jd_parser import make_state

def test_evaluator_returns_valid_score():
    state = make_state()
    state["current_question"] = {
        "question": "什么是RAG？",
        "target": "RAG",
    }
    state["user_answer"] = "RAG是检索增强生成，先检索相关文档再让大模型生成答案。"

    result = evaluator_node(state)
    evaluations = result["evaluations"]
    assert len(evaluations) == 1

    last = evaluations[-1]
    assert 1 <= last["score"] <= 10
    assert isinstance(last["strengths"], list)
    assert isinstance(last["weaknesses"], list)
    assert isinstance(last["suggestion"], str)