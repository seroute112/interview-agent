from app.agents.resume_matcher import resume_matcher_node
from tests.test_jd_parser import make_state

def test_resume_matcher_returns_all_fields():
    state = make_state(
        jd="岗位：AI开发工程师，要求熟悉Python、LangChain、RAG。",
        resume="熟悉Java、Python、MySQL。",
    )
    state["jd_keywords"] = ["Python", "LangChain", "RAG"]
    result = resume_matcher_node(state)
    match = result["match_result"]

    assert "matched" in match
    assert "partial" in match
    assert "missing" in match
    assert isinstance(match["matched"], list)
    assert isinstance(match["partial"], list)
    assert isinstance(match["missing"], list)