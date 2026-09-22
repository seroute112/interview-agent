from app.config import get_llm
from app.tools.llm_json import parser_llm_json

INTENT_PROMPT = """你是一个意图识别器。请结合用户历史，判断当前输入的意图，只返回JSON。

用户历史操作：{history}

当前输入：{message}

可选意图：
- interview：用户想模拟面试、想练面试、想出题
- resume_analysis：用户想分析简历、优化简历、看简历问题
- job_match：用户想做岗位匹配、看自己适不适合某岗位
- continue_previous：延续上一次操作，比如"再优化一下""根据刚才的继续""再来一次"
- unknown：无法识别

判断规则：
1. 如果当前输入语义模糊，但历史里最近一次操作是简历分析，且用户说"优化一下"之类，判为 continue_previous
2. 如果当前输入明确提到面试、练题，判为 interview
3. 如果当前输入明确提到简历、优化，判为 resume_analysis
4. 如果当前输入明确提到岗位、匹配、适不适合，判为 job_match

返回格式：
{
  "intent": "interview",
  "confidence": 0.9,
  "reason": "用户明确说想模拟面试"
}
"""


def classify_intent(message: str, history: str = "") -> dict:
    llm = get_llm()

    prompt = (
        INTENT_PROMPT
        .replace("{history}", history if history else "暂无历史")
        .replace("{message}", message)
    )

    response = llm.invoke(prompt)
    parsed = parser_llm_json(response.content)

    parsed.setdefault("intent", "unknown")
    parsed.setdefault("confidence", 0.0)
    parsed.setdefault("reason", "")

    valid_intents = ["interview", "resume_analysis", "job_match", "continue_previous", "unknown"]
    if parsed["intent"] not in valid_intents:
        parsed["intent"] = "unknown"

    return parsed