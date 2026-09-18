from app.agents.jd_parser import jd_parser_node

def make_state(jd="", resume=""):
    return {
        "messages": [],
        "jd": jd,
        "resume": resume,
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

def test_jd_parser_returns_keywords():
    state = make_state(jd="岗位：AI开发工程师，要求熟悉Python、LangChain、RAG、FastAPI。")
    result = jd_parser_node(state)
    assert isinstance(result["jd_keywords"], list)
    assert len(result["jd_keywords"]) > 0

def test_jd_parser_keywords_not_empty_string():
    state = make_state(jd="岗位：后端开发，要求熟悉Java、Spring、MySQL。")
    result = jd_parser_node(state)
    for kw in result["jd_keywords"]:
        assert isinstance(kw, str)
        assert kw.strip() != ""