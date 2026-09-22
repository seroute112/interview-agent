from app.config import get_llm
from app.tools.llm_json import parser_llm_json

JOB_MATCHER_PROMPT = """你是一个岗位匹配分析师。请对比候选人的简历和目标 JD，只返回JSON。

分析维度：
1. matched：简历已具备且 JD 要求的技能
2. partial：简历沾边但不深入的技能
3. missing：JD 要求但简历未体现的技能
4. match_score：整体匹配度（0-100）
5. summary：一句话总结
6. advice：针对性提升建议（3 条）

返回格式：
{
  "matched": ["技能1", "技能2"],
  "partial": ["技能3"],
  "missing": ["技能4", "技能5"],
  "match_score": 65,
  "summary": "候选人具备基础但缺乏核心技能",
  "advice": ["建议1", "建议2", "建议3"]
}
"""


def match_job(resume_text: str, jd_text: str) -> dict:
    llm = get_llm()

    prompt = (
        JOB_MATCHER_PROMPT
        + f"\n\n简历内容：\n{resume_text}"
        + f"\n\nJD内容：\n{jd_text}"
    )
    response = llm.invoke(prompt)
    parsed = parser_llm_json(response.content)

    parsed.setdefault("matched", [])
    parsed.setdefault("partial", [])
    parsed.setdefault("missing", [])
    parsed.setdefault("match_score", 0)
    parsed.setdefault("summary", "")
    parsed.setdefault("advice", [])

    return parsed