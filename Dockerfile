# 后端 API 镜像
FROM docker.m.daocloud.io/library/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 换清华镜像源，加速 pip 安装（国内服务器）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 先复制依赖文件，利用 Docker 分层缓存
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建 data 目录（挂载点）
RUN mkdir -p data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]