import re
import json

def parser_llm_json(content:str) -> dict:
    content = content.replace("\ufeff", "")

    # 去掉零宽字符（U+200B ~ U+200F, U+2028 ~ U+202F, U+205F, U+FEFF）
    content = re.sub(r"[\u200b-\u200f\u2028-\u202f\u205f\ufeff]", "", content)

    # 中文引号替换成英文引号
    content = content.replace("“", '"').replace("”", '"')
    content = content.replace("‘", "'").replace("’", "'")

    # 中文冒号替换成英文冒号（只在键值对里出现，全局替换风险低）
    # 如果发现误伤，可以注释掉这行
    content = content.replace("：", ":")

    # 去掉控制字符（保留 \n \t \r）
    content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", content)

    content = content.strip()
    if content.startswith("'''"):
        content = content.split("'''")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    if content.endswith("'''"):
        content = content[:-3].strip()

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end+1]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("=== LLM JSON 解析失败，原始返回 ===")
        print(repr(content))
        print("===================================")
        return {}