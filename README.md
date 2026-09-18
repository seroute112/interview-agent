# 多智能体求职面试模拟与评估系统

基于 LangGraph 的多智能体协作系统，根据简历和目标 JD 自动生成针对性面试问题，评估回答，记录弱项，并生成面试报告。

## 项目背景

传统模拟面试要么找真人成本高，要么单 Agent 提问不聚焦、不会根据回答追问、不会记录弱项。本项目用多个 Agent 分工协作，模拟真实面试官的完整工作流。

## 架构

graph TD
    START --> supervisor
    supervisor -->|jd_keywords 为空| jd_parser
    supervisor -->|match_result 为空| resume_matcher
    supervisor -->|questions 为空| question_generator
    supervisor -->|有待评估回答| evaluator
    supervisor -->|全部完成| END

    jd_parser --> supervisor
    resume_matcher --> supervisor
    question_generator --> supervisor
    evaluator --> supervisor

Agent	          职责
Supervisor	    根据当前状态决定下一步执行哪个节点
JD 解析	        从 JD 提取技术关键词、软技能、加分项、岗位级别
简历匹配	      对比简历和 JD，输出匹配点、部分匹配、缺失项
提问	          针对缺失技能和历史弱项生成面试问题
评估	          对回答打分，给出优点、不足、改进建议和弱项标签

技术栈
编排：LangGraph
模型：DeepSeek（deepseek-chat）
工具：LangChain @tool
持久化：SQLite
接口：FastAPI + Uvicorn
报告：Markdown

## 快速开始
1. 安装依赖
bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
2. 配置 API Key
在项目根目录创建 .env:

DEEPSEEK_API_KEY=sk-你的密钥

3. 命令行运行
bash
python main.py
4. 启动 API 服务
bash
uvicorn app.api.main:app --reload --port 8000
打开 http://127.0.0.1:8000/docs 查看 Swagger 文档。

API 示例
启动面试
bash
curl -X POST http://127.0.0.1:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{"jd": "岗位JD文本", "resume": "简历文本"}'
返回：

json
{
  "session_id": "xxx",
  "jd_keywords": ["LangChain", "RAG", "FastAPI"],
  "resume_summary": "...",
  "questions": [
    {"question": "...", "target": "...", "difficulty": "基础", "type": "八股"}
  ]
}
提交回答
bash
curl -X POST http://127.0.0.1:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "question_index": 0, "answer": "你的回答"}'
返回：

json
{
  "score": 6,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestion": "...",
  "weak_tags": ["概念不深入"],
  "is_last": false
}
## 项目结构
text
interview-agent/
├── app/
│   ├── agents/          # 每个 Agent 一个文件
│   ├── api/             # FastAPI 封装
│   ├── memory/          # SQLite 持久化
│   ├── tools/           # 报告生成等工具
│   ├── config.py        # LLM 初始化
│   ├── state.py         # InterviewState 定义
│   └── graph.py         # LangGraph 组装
├── data/                # 样例数据、数据库、报告
├── main.py              # 命令行入口
└── requirements.txt