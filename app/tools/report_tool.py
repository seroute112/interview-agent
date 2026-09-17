import os
from datetime import datetime
from app.memory.sqlite_store import get_weak_points

def generate_report(evaluations, weak_points, jd_keywords, match_result):
    if not evaluations:
        return "暂无评估数据，无法生成报告。"

    total_score = sum(e["score"] for e in evaluations)
    avg_score = total_score / len(evaluations)

    # 统计弱项频次
    tag_count = {}
    for tag in weak_points:
        tag_count[tag] = tag_count.get(tag, 0) + 1

    sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)

    lines = []
    lines.append("# 面试评估报告")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## 一、总体得分")
    lines.append("")
    lines.append(f"- 平均分：**{avg_score:.1f} / 10**")
    lines.append(f"- 评估题数：{len(evaluations)}")
    lines.append(f"- 最高分：{max(e['score'] for e in evaluations)}")
    lines.append(f"- 最低分：{min(e['score'] for e in evaluations)}")
    lines.append("")

    lines.append("## 二、逐题详情")
    lines.append("")
    for i, e in enumerate(evaluations, 1):
        lines.append(f"### 第 {i} 题：{e['question']}")
        lines.append("")
        lines.append(f"- 得分：{e['score']} / 10")
        lines.append(f"- 优点：{', '.join(e['strengths']) if e['strengths'] else '无'}")
        lines.append(f"- 不足：{', '.join(e['weaknesses']) if e['weaknesses'] else '无'}")
        lines.append(f"- 建议：{e['suggestion']}")
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
    lines.append(f"JD 要求关键词：{', '.join(jd_keywords)}")
    lines.append("")
    lines.append(f"匹配总结：{match_result.get('summary', '')}")
    lines.append("")

    lines.append("## 五、改进建议")
    lines.append("")
    lines.append("按弱项频次从高到低，优先补强以下方向：")
    lines.append("")
    for tag, count in sorted_tags[:5]:
        lines.append(f"- **{tag}**（出现 {count} 次）")
    lines.append("")

    return "\n".join(lines)


def save_report(content, path="data/report.md"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path