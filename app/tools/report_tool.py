import os
from datetime import datetime


def generate_report(evaluations: list,weak_points: list,jd_keywords: list,match_result: dict,user_id: str = "default_user",round_history: list = None,) -> str:

    if not evaluations:
        return "暂无评估数据，无法生成报告。"

    round_history = round_history or []

    all_evals = []
    for h in round_history:
        for e in h.get("evaluations", []):
            all_evals.append({**e, "round": h.get("round", 0)})
    for e in evaluations:
        all_evals.append({**e, "round": len(round_history) + 1})

    scores = [e.get("score", 0) for e in all_evals]
    avg_score = sum(scores) / len(scores) if scores else 0
    tech_scores = [e.get("tech_score", 0) for e in all_evals if e.get("tech_score") is not None]
    eng_scores = [e.get("engineering_score", 0) for e in all_evals if e.get("engineering_score") is not None]
    comm_scores = [e.get("communication_score", 0) for e in all_evals if e.get("communication_score") is not None]

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0

    tag_count = {}
    for e in all_evals:
        for tag in (e.get("weak_tags") or []):
            tag = tag.strip()
            if tag:
                tag_count[tag] = tag_count.get(tag, 0) + 1
    sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)

    lines = []
    lines.append("# 面试评估报告")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 用户 ID：`{user_id}`")
    lines.append(f"- 面试轮次：{len(round_history) + 1}")
    lines.append(f"- 评估题数：{len(all_evals)}")
    lines.append("")

    lines.append("## 一、总体得分")
    lines.append("")
    lines.append(f"- 平均分：**{avg_score:.1f} / 10**")
    lines.append(f"- 最高分：{max(scores) if scores else 0}")
    lines.append(f"- 最低分：{min(scores) if scores else 0}")
    lines.append(f"- 技术正确性平均：{avg(tech_scores):.1f}")
    lines.append(f"- 工程实践平均：{avg(eng_scores):.1f}")
    lines.append(f"- 表达逻辑平均：{avg(comm_scores):.1f}")
    lines.append("")

    lines.append("## 二、逐题详情")
    lines.append("")
    for i, e in enumerate(all_evals, 1):
        round_no = e.get("round", 1)
        lines.append(f"### 第 {round_no} 轮 · 第 {i} 题")
        lines.append("")
        lines.append(f"**问题**：{e.get('question', '')}")
        lines.append("")
        lines.append(f"**考察点**：{e.get('target', '未标注')}")
        lines.append("")

        lines.append("**你的回答**：")
        lines.append("")
        answer = e.get("answer", "")
        if answer:
            lines.append(f"> {answer}")
        else:
            lines.append("> （未作答）")
        lines.append("")

        lines.append("**评分明细**：")
        lines.append("")
        lines.append(f"| 维度 | 分数 |")
        lines.append(f"|---|---|")
        lines.append(f"| 技术正确性 | {e.get('tech_score', '-')} / 10 |")
        lines.append(f"| 工程实践 | {e.get('engineering_score', '-')} / 10 |")
        lines.append(f"| 表达逻辑 | {e.get('communication_score', '-')} / 10 |")
        lines.append(f"| **最终得分** | **{e.get('score', '-')} / 10** |")
        lines.append("")

        if e.get("summary"):
            lines.append(f"**综合评语**：{e['summary']}")
            lines.append("")

        strengths = e.get("strengths") or []
        if strengths:
            lines.append("**优点**：")
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")

        weaknesses = e.get("weaknesses") or []
        if weaknesses:
            lines.append("**不足**：")
            for w in weaknesses:
                lines.append(f"- {w}")
            lines.append("")

        if e.get("suggestion"):
            lines.append(f"**改进建议**：{e['suggestion']}")
            lines.append("")

        tags = e.get("weak_tags") or []
        if tags:
            lines.append(f"**弱项标签**：{'、'.join(tags)}")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## 三、弱项频次")
    lines.append("")
    if sorted_tags:
        lines.append("| 弱项标签 | 出现次数 |")
        lines.append("|---|---|")
        for tag, count in sorted_tags:
            lines.append(f"| {tag} | {count} |")
    else:
        lines.append("暂无弱项记录。")
    lines.append("")

    lines.append("## 四、JD 关键词覆盖")
    lines.append("")
    lines.append(f"**JD 要求关键词**：{', '.join(jd_keywords) if jd_keywords else '无'}")
    lines.append("")
    if match_result:
        lines.append(f"**匹配总结**：{match_result.get('summary', '')}")
        lines.append("")
        matched = match_result.get("matched") or []
        partial = match_result.get("partial") or []
        missing = match_result.get("missing") or []
        lines.append(f"- 已匹配：{', '.join(matched) if matched else '无'}")
        lines.append(f"- 部分匹配：{', '.join(partial) if partial else '无'}")
        lines.append(f"- 缺失：{', '.join(missing) if missing else '无'}")
    lines.append("")

    lines.append("## 五、优先改进方向")
    lines.append("")
    if sorted_tags:
        lines.append("按弱项频次从高到低，优先补强：")
        lines.append("")
        for tag, count in sorted_tags[:5]:
            lines.append(f"- **{tag}**（出现 {count} 次）")
    else:
        lines.append("暂无弱项，表现良好。")
    lines.append("")

    return "\n".join(lines)


def save_report(content: str, path: str = "data/report.md") -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path