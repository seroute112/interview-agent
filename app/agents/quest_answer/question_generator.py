import json
from app.state import InterviewState
from app.config import get_llm
from app.memory.topic_tracker import get_topic_weights
from app.memory.reflection_store import get_recent_reflections

QUESTION_PROMPT = """你是一个技术面试官。请根据候选人的技能差距和历史掌握度生成问题，只返回JSON，不要其他内容

要求：
1. 必须返回所有字段，没有内容时返回空列表 []，不要省略字段
2.问题要覆盖missing和partial里的技能，优先覆盖missing中的技能
3.每个问题带考差点，难度和类型
4.生成5个问题，难度从基础到进阶分布
5.如果提供了历史弱项，优先从历史弱项出题
6.如果给出了历史反思记录，只看提问反思即question_quality和quest_suggestions,请酌情根据反思记录调整问题

返回格式:
{
    "questions":[
    {
        "question":"问题文本",
        "target":"考察的技能点",
        "difficulty":"基础/中级/进阶",
        "type":"八股/项目深挖/场景设计"
    }
    ]
}
"""

def question_generator_node(state: InterviewState):
    llm = get_llm()

    match = state.get("match_result") or {}
    missing = match.get("missing") or []
    partial = match.get("partial") or []
    # weak_points = state.get("weak_points") or get_weak_points()

    # print("本次提问参考的历史弱项：", weak_points)

    topic_weights = get_topic_weights()

    if topic_weights:
        weight_text = "\n".join(f"-{t['topic']}(掌握度:{t['mastery_level']},权重:{t['weight']})" for t in topic_weights)
        for t in topic_weights:
            print(t)
    else:
        weight_text = "暂无记录"

    reflections = get_recent_reflections(limit=3)
    if reflections:
        reflection_text = "\n".join(
            f"- 提问质量 {r['question_quality']}/10，"
            f"建议：{'; '.join(r['quest_suggestions']) if r['quest_suggestions'] else '无'}"
            for r in reflections
        )
    else:
        reflection_text = "暂无历史反思"

    round_history = state.get("round_history") or []
    if round_history:
        last_round = round_history[-1]
        last_evals = last_round.get("evaluations", [])
        weak_questions = [
            e["question"] for e in last_evals
            if e.get("score", 10) < 6
        ]
        history_text = (
            f"上一轮平均分：{last_round.get('avg_score', 0)}\n"
            f"上一轮低分题：{chr(10).join(weak_questions) if weak_questions else '无'}"
        )
    else:
        history_text = "这是第一轮面试"
    
    prompt = (
        QUESTION_PROMPT 
        + "\n\nJD关键词：\n" + ",".join(state["jd_keywords"]) 
        + "\n\n缺失技能：\n" + ",".join(missing) 
        + "\n\n部分匹配技能：\n" + ",".join(partial) 
        # + "\n\n历史弱项：\n" + (",".join(weak_points) if weak_points else "暂无")
        + "\n\n历史考察点掌握情况（按权重降序）：\n" + weight_text
        + "\n\n历史反思建议：\n" + reflection_text
        + "\n\n历史轮次情况：\n" + history_text
        + "\n\n出题规则：\n"
        + "1. 权重 >= 1.5 的考察点优先出题。\n"
        + "2. 权重 <= 0.5 的考察点（已掌握）减少出题。\n"
        + "3. 生成 5 道题。\n"
        + "4. 如果是第二轮或之后，优先针对上一轮的低分题和弱项出题。\n"        
        + "5. 每次最好包含1个全新考察点，即 JD 要求但历史记录里没有的，但是如果其他弱项或者未掌握过多则优先考察弱项。\n"
        
    )

    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("'''"):
        content = content.split("'''")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip

        # 只取 {} 之间的部分
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end+1]

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "questions": [],
            "raw": content
        }

    parsed.setdefault("questions", [])
    return {"questions": parsed["questions"]}