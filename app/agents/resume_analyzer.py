from app.config import get_llm
from app.tools.llm_json import parser_llm_json

RESUME_ANALYZER_PROMPT = """你是一个简历优化专家。请分析以下简历，只返回JSON。

分析维度：
1. structure：结构是否清晰（教育、技能、项目、荣誉是否完整）
2. skill_description：技能描述是否具体，有没有"熟悉/了解"滥用
3. quantified_results：项目经历有没有量化成果
4. suggestions：3-5 条具体改进建议

返回格式：
{
  "structure": {"score": 7, "comment": "结构基本完整"},
  "skill_description": {"score": 6, "comment": "技能描述偏笼统"},
  "quantified_results": {"score": 4, "comment": "缺少量化数据"},
  "suggestions": ["建议1", "建议2", "建议3"]
}
"""


def analyze_resume(resume_text: str) -> dict:
    llm = get_llm()

    prompt = RESUME_ANALYZER_PROMPT + f"\n\n简历内容：\n{resume_text}"
    response = llm.invoke(prompt)
    parsed = parser_llm_json(response.content)

    parsed.setdefault("structure", {"score": 0, "comment": ""})
    parsed.setdefault("skill_description", {"score": 0, "comment": ""})
    parsed.setdefault("quantified_results", {"score": 0, "comment": ""})
    parsed.setdefault("suggestions", [])

    return parsed