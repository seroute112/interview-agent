多智能体 AI 面试模拟与评估系统
基于 LangGraph 的多智能体协作系统，模拟真实面试官完整工作流：读 JD → 看简历 → 找差距 → 提问 → 听回答 → 三维度评估 → 综合 → 反思 → 出报告。
堆料就是量大管饱
# 项目背景
传统模拟面试有两个问题：
找真人成本高，时间难协调
单 Agent 提问不聚焦、不会根据回答追问、不会记录弱项
本项目用多个 Agent 分工协作，让系统像真实面试官一样工作，并且越用越懂你。
# 核心特性
多智能体协作：Supervisor + 多个专业 Agent，动态路由
三维度评估：技术正确性、工程实践、表达逻辑，独立评估后综合
动态出题：根据历史掌握度调整出题权重，弱项多考、强项少考
系统自反思：每轮结束评估提问和评估质量，改进后续策略
两层记忆：SQLite 存结构化掌握度，Mem0 存用户对话历史
统一对话入口：支持模拟面试、简历分析、岗位匹配三种意图
完整工程化：FastAPI 服务化 + Streamlit 界面 + Docker 部署
# 架构
graph TD
    START --> supervisor
    supervisor -->|JD 未解析| jd_parser
    supervisor -->|简历未匹配| resume_matcher
    supervisor -->|需要出题| question_generator
    supervisor -->|待评估| evaluator_tech
    supervisor -->|待综合| summarizer
    supervisor -->|全部完成| reflector
    supervisor -->|结束| END

    jd_parser --> supervisor
    resume_matcher --> supervisor
    question_generator --> supervisor

    evaluator_tech --> evaluator_engineering
    evaluator_engineering --> evaluator_communication
    evaluator_communication --> summarizer
    summarizer --> supervisor
    reflector --> supervisor
# Agent 职责
Agent	职责
Supervisor	LLM 动态决策下一步执行哪个节点，带规则兜底
JD Parser	从 JD 提取技术关键词、软技能、加分项、岗位级别
Resume Matcher	对比简历和 JD，输出匹配点、部分匹配、缺失项
Question Generator	结合掌握度权重、历史弱项、历史反思生成问题
Evaluator Tech	评估技术正确性：概念准确性、有无硬伤
Evaluator Engineering	评估工程实践：场景举例、量化数据、技术选型权衡
Evaluator Communication	评估表达逻辑：结构清晰度、是否答到点上
Summarizer	综合三方评估，输出最终分数和评语
Reflector	评估本轮提问和评估质量，存入 SQLite 供下轮改进
Intent Router	识别用户意图，路由到面试/简历分析/岗位匹配
Resume Analyzer	分析简历结构、技能描述、量化成果
Job Matcher	分析简历和 JD 的匹配度，输出差距和提升建议
# 技术栈
层	技术
编排	LangGraph
Agent 框架	LangChain
大模型	DeepSeek（deepseek-chat）
工具调用	LangChain @tool + Function Calling
结构化存储	SQLite
语义记忆	Mem0
后端	FastAPI + Uvicorn
前端	Streamlit
部署	Docker + Docker Compose
# 快速开始
# 方式一：Docker（推荐）
bash
克隆项目
git clone https://github.com/你的用户名/interview-agent.git
cd interview-agent

配置环境变量
cp .env.example .env
编辑 .env，填入 DEEPSEEK_API_KEY 和 MEM0_API_KEY

启动
docker compose up --build -d
访问：

前端界面：http://localhost:8501

API 文档：http://localhost:8000/docs

停止：

bash
docker compose down
# 方式二：本地运行
bash
创建虚拟环境
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux

安装依赖
pip install -r requirements.txt

配置环境变量
cp .env.example .env
编辑 .env，填入 DEEPSEEK_API_KEY 和 MEM0_API_KEY

启动后端
uvicorn app.api.main:app --reload --port 8000

另开终端，启动前端
streamlit run app/ui/streamlit_app.py
环境变量
# .env 文件内容：

DEEPSEEK_API_KEY=sk-你的密钥
MEM0_API_KEY=m0-你的密钥
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_你的密钥
LANGCHAIN_PROJECT=interview-agent
MEM0_API_KEY 和 LANGCHAIN_API_KEY 可选，不填也能跑，只是没有语义记忆和追踪功能。

# API 接口
POST /interview/start
启动一轮面试。

请求：

json
{
  "jd": "岗位：AI应用开发工程师，要求熟悉 LangChain、RAG、FastAPI",
  "resume": "熟悉 Java、Python、MySQL"
}
响应：

json
{
  "session_id": "abc-123",
  "jd_keywords": ["LangChain", "RAG", "FastAPI"],
  "match_summary": "候选人具备基础但缺乏核心技能",
  "questions": [
    {
      "question": "请描述 RAG 的完整流程",
      "target": "RAG检索",
      "difficulty": "基础",
      "type": "八股"
    }
  ]
}
POST /interview/answer
提交回答，触发三维度评估和综合。

请求：

json
{
  "session_id": "abc-123",
  "question_index": 0,
  "answer": "RAG 先离线将文档切块、向量化..."
}
响应：

json
{
  "tech_score": 9,
  "engineering_score": 6,
  "communication_score": 7,
  "score": 7,
  "summary": "技术理解到位，但缺少工程场景",
  "strengths": ["流程描述完整"],
  "weaknesses": ["没有提到 Rerank"],
  "suggestion": "建议补充实际项目案例",
  "weak_tags": ["缺少场景"],
  "is_last": false
}
POST /interview/next_round
进入下一轮，保留历史，基于弱项生成新题。

POST /interview/report
生成 Markdown 格式的面试报告，包含所有问题、答案、三方分数、弱项频次、改进建议。

POST /chat
统一对话入口，支持模拟面试、简历分析、岗位匹配三种意图。

# 项目结构

interview-agent/
├── app/
│   ├── agents/                          # Agent 实现
│   │   ├── __init__.py
│   │   ├── supervisor.py                # 主管，动态路由
│   │   ├── intent_router.py             # 意图识别
│   │   ├── resume_analyzer.py           # 简历分析
│   │   ├── job_matcher.py               # 岗位匹配
│   │   ├── arbiter.py                   # 仲裁（搁置，未来启用）
│   │   └── quest_answer/                # 面试问答子包
│   │       ├── __init__.py
│   │       ├── jd_parser.py             # JD 解析
│   │       ├── resume_matcher.py        # 简历匹配
│   │       ├── question_generator.py    # 提问
│   │       ├── evaluator_tech.py        # 技术正确性评估
│   │       ├── evaluator_engineering.py # 工程实践评估
│   │       ├── evaluator_communication.py # 表达逻辑评估
│   │       ├── summarizer.py            # 综合评估
│   │       └── reflector.py             # 系统反思
│   ├── api/                             # FastAPI 封装
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── session_store.py
│   ├── memory/                          # 持久化
│   │   ├── __init__.py
│   │   ├── sqlite_store.py              # 评估记录
│   │   ├── topic_tracker.py             # 掌握度追踪
│   │   ├── reflection_store.py          # 系统反思
│   │   └── user_memory.py               # 用户对话记忆（Mem0）
│   ├── tools/                           # 工具
│   │   ├── __init__.py
│   │   ├── llm_json.py                  # JSON 解析
│   │   ├── eval_common.py               # 评估公共逻辑
│   │   ├── report_tool.py               # 报告生成
│   │   └── file_parser.py               # PDF/DOCX 解析
│   ├── ui/
│   │   └── streamlit_app.py             # 前端界面
│   ├── __init__.py
│   ├── config.py                        # LLM 初始化
│   ├── state.py                         # InterviewState 定义
│   └── graph.py                         # LangGraph 组装
├── data/                                # 样例数据、数据库、报告
├── tests/                               # 单元测试
├── Dockerfile                           # 后端镜像
├── Dockerfile.ui                        # 前端镜像
├── docker-compose.yml                   # 容器编排
├── main.py                              # 命令行入口
└── requirements.txt
# 技术决策说明
为什么用多 Agent 而不是单 Agent
单 Agent 把 JD 解析、简历匹配、提问、评估混在一个 prompt 里，职责不清，容易遗漏简历差距点。拆成 Supervisor + Worker 后，每个 Agent 只做一件事，提问 Agent 能明确拿到 missing 技能和历史弱项，针对性更强。

为什么三个评估 Agent 而不是一个
LLM 单次评分方差大，一个 Agent 打 8 分还是 5 分，取决于当次采样。拆成三个正交维度——技术正确性、工程实践、表达逻辑——从不同角度评估，信息增量更大，还能精准定位用户的短板类型。

为什么用 SQLite 存掌握度和反思
掌握度和反思是结构化数据（分数、标签、时间），需要按时间排序、聚合、过滤。SQLite 一行 SQL 搞定，不需要语义检索。用 Mem0 反而会丢失结构化字段。

为什么用 Mem0 存用户对话
用户对话是非结构化数据，需要语义检索。用户说"优化一下上次那个"，SQLite 做不到，Mem0 可以从历史里找到"上次那个"是什么。

为什么 Arbiter 搁置
三个评估是不同角度，分差大是正常现象（技术 9 分、表达 3 分是真实画像），不是评估冲突。用同一个 LLM 做仲裁只会得到和稀泥的结果。未来接入第二家模型（Qwen/GLM）做二轮独立评估后，才需要真正的仲裁。

# 已知限制
Session 存内存：session_store.py 用字典存 session，重启服务会丢失。生产环境应换 Redis。
单用户假设：SQLite 无并发控制，多用户同时写会锁库。生产环境应换 PostgreSQL。
同模型仲裁无意义：Arbiter 已搁置，等接入第二家模型再启用。
PDF 解析质量不稳定：扫描版 PDF 可能提取为空，建议用 DOCX 或 TXT。

# 未来规划
1.Critic 全局审查与打回机制
Reflector 升级为全局复审：负责审查每轮的评估和提问质量，结果存入数据库全局保存，供后续所有会话参考。
新增 Critic 节点：独立审查每个功能节点的输出，检查是否符合各自 prompt 的约束、是否违反全局规则。
每个节点后跑 Critic：JD 解析、简历匹配、提问、三个评估、综合，每个节点执行完都经过 Critic 检查。
不符合要求立即打回重做：Critic 发现问题时，将节点退回重做，并带上具体的修改要求，避免错误向下游传播。
2.为提问和评估 Agent 建资料库
提问资料库：收集高质量面试题、标准考察点、常见追问路径，让提问 Agent 基于资料库出题，而不是凭空生成。
评估资料库：收集优秀回答范例、评分标准、常见扣分点，让三个评估 Agent 有客观参照，减少主观偏差。
技术选型：用 RAG + 向量数据库（Chroma 或 Milvus），支持语义检索。
3.前端界面优化
从指令式升级为对话式：不限于按钮和固定输入框，支持自然多轮对话。
上下文感知：用户中途切换话题（面试 → 简历分析 → 面试）时，能保留上下文，不用重新提供资料。
界面优化：消息气泡、Markdown 渲染、代码块高亮、流式输出。
4.双模型独立评估 + 仲裁
接入第二家模型（Qwen 或 GLM），与 DeepSeek 分别对同一份回答独立评估。
差异检测：两家模型的评分差异超过阈值（如 2 分）时，触发仲裁流程。
审判 Agent：由第三个模型或规则逻辑综合双方评估，给出最终分数和裁决理由。
解决同模型仲裁无意义的问题：不同模型有不同的训练数据和偏好，独立评估才有信息增量。
# 运行测试
bash
pytest tests/ -v
命令行模式
不启动 FastAPI 和 Streamlit，直接跑：

bash
python main.py
会依次执行 JD 解析、简历匹配、提问、逐题问答、评估、报告。

# License
MIT

如果有帮助，欢迎 Star。项目仍在迭代中，欢迎提 Issue 和 PR。