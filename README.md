# Crawl4AI 网页爬取和AI分析系统

## 项目简介

这是一个基于 Crawl4AI 的智能网页爬取和AI分析系统，集成了现代化的Web界面、数据库存储和MinIO对象存储。系统提供了完整的网页内容抓取、AI智能分析、文件管理和历史记录功能。

## 主要特性

### 🚀 核心功能
- **智能网页爬取**: 支持多种内容源（cleaned_html、raw_html、fit_html）
- **AI智能分析**: 集成多种AI分析模式（内容摘要、关键点提取、结构化数据等）
- **现代化Web界面**: 响应式设计，支持实时操作和结果展示
- **数据持久化**: PostgreSQL数据库存储任务记录和元数据
- **文件存储**: MinIO对象存储管理所有生成的文件
- **历史记录**: 完整的爬取历史和文件管理功能

### 🛠 技术架构
- **后端框架**: FastAPI + Python 3.12
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **对象存储**: MinIO
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **AI集成**: 支持多种LLM提供商（OpenAI、Azure OpenAI、本地LLM、通义千问）

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web 界面      │    │   FastAPI 服务  │    │   PostgreSQL    │
│   (前端)        │◄──►│   (后端API)     │◄──►│   (数据库)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Crawl4AI      │    │   MinIO         │
                       │   (爬取引擎)    │    │   (文件存储)    │
                       └─────────────────┘    └─────────────────┘
```

## 快速开始

### 环境要求
- Python 3.12+
- PostgreSQL 数据库
- MinIO 对象存储服务

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

#### 1. 数据库配置 (`config/database_config.py`)
```python
DATABASE_CONFIG = {
    'host': 'your_postgres_host',
    'port': 5432,
    'database': 'your_database',
    'username': 'your_username',
    'password': 'your_password'
}
```

#### 2. MinIO配置 (`config/minio_config.py`)
```python
MINIO_CONFIG = {
    'endpoint': 'your_minio_host:9000',
    'access_key': 'your_access_key',
    'secret_key': 'your_secret_key',
    'secure': False
}
```

#### 3. AI配置 (`config/ai_config.yaml`)
```yaml
llm_providers:
  openai:
    api_key: "your_openai_api_key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4"
  # 其他提供商配置...
```

### 启动服务

```bash
# 启动服务器（默认端口8000）
python markdown/content_source_server.py

# 指定端口启动
python markdown/content_source_server.py --port 8080

# 指定主机和端口
python markdown/content_source_server.py --host 0.0.0.0 --port 8080
```

### 访问系统

- **Web界面**: http://localhost:8080
- **API文档**: http://localhost:8080/docs
- **API信息**: http://localhost:8080/api

## 功能详解

### 1. 网页爬取功能

#### 支持的内容源类型：
- `cleaned_html`: 清理后的HTML内容（推荐）
- `raw_html`: 原始HTML内容
- `fit_html`: 适配后的HTML内容

#### AI分析模式：
- `content_summary`: 内容摘要
- `key_points`: 关键点提取
- `structured_data`: 结构化数据提取
- `entities`: 实体识别
- `sentiment`: 情感分析

### 2. Web界面功能

#### 主要页面组件：
- **爬取表单**: 输入URL和配置参数
- **实时结果**: 显示爬取进度和结果
- **历史记录**: 查看所有爬取任务
- **文件管理**: 浏览和预览生成的文件

#### 交互特性：
- 响应式设计，支持移动端
- 实时状态更新
- 文件在线预览
- 一键下载功能

### 3. API接口

#### 核心接口：
```
POST /crawl              # 完整爬取和分析
GET  /crawl_simple       # 简化爬取接口
GET  /api/history        # 获取历史记录
GET  /api/files/{task_id} # 获取任务文件
GET  /api/preview/{file_id} # 预览文件内容
```

#### 请求示例：
```bash
# 爬取网页
curl -X POST "http://localhost:8080/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content_source": "cleaned_html",
    "ai_modes": ["content_summary", "key_points"],
    "save_files": true
  }'
```

### 4. 数据存储

#### 数据库表结构：
- `crawl_tasks`: 爬取任务记录
- `crawl_files`: 文件元数据记录

#### MinIO存储桶：
- `crawl4ai-files`: 通用文件存储
- `crawl4ai-markdown`: Markdown文件
- `crawl4ai-ai-results`: AI分析结果
- `crawl4ai-json`: JSON格式文件

## 开发指南

### 项目结构

```
crawl4ai-demo/
├── config/                 # 配置文件
│   ├── ai_config.yaml     # AI配置
│   ├── database_config.py # 数据库配置
│   └── minio_config.py    # MinIO配置
├── models/                # 数据模型
│   └── database_models.py # 数据库模型
├── utils/                 # 工具模块
│   └── ai_extractor.py    # AI提取器
├── templates/             # HTML模板
│   └── index.html         # 主页模板
├── static/                # 静态资源
│   ├── css/style.css      # 样式文件
│   └── js/app.js          # JavaScript文件
├── markdown/              # 核心服务
│   └── content_source_server.py # 主服务器
├── logs/                  # 日志文件
├── requirements.txt       # 依赖列表
└── README.md             # 项目文档
```

### 扩展开发

#### 添加新的AI分析模式：
1. 在 `config/ai_config.yaml` 中添加新模式配置
2. 在 `utils/ai_extractor.py` 中实现分析逻辑
3. 更新前端界面选项

#### 添加新的存储后端：
1. 在 `config/` 目录创建新的配置文件
2. 实现存储管理器类
3. 在服务器中集成新的存储后端

### 日志和监控

#### 日志文件位置：
- 服务器日志: `logs/server.log`
- AI提取日志: `logs/ai_extraction.log`

#### 日志级别：
- INFO: 正常操作信息
- ERROR: 错误信息
- DEBUG: 调试信息（开发模式）

## 部署指南

### Docker部署

```dockerfile
# Dockerfile示例
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "markdown/content_source_server.py", "--host", "0.0.0.0", "--port", "8080"]
```

### 生产环境配置

#### 1. 使用Gunicorn部署：
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker markdown.content_source_server:app --bind 0.0.0.0:8080
```

#### 2. Nginx反向代理配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
- 检查数据库配置信息
- 确认数据库服务运行状态
- 验证网络连接

#### 2. MinIO连接失败
- 检查MinIO服务状态
- 验证访问密钥配置
- 确认存储桶权限

#### 3. AI分析失败
- 检查API密钥配置
- 验证网络连接
- 查看AI服务配额

### 性能优化

#### 1. 数据库优化
- 添加适当的索引
- 定期清理历史数据
- 使用连接池

#### 2. 存储优化
- 配置MinIO缓存
- 使用CDN加速
- 压缩存储文件

## 贡献指南

### 开发规范
- 遵循SOLID原则
- 保持高内聚低耦合
- 使用中文注释
- 完善错误处理和日志

### 提交规范
- 功能开发使用feature分支
- 提交信息使用中文描述
- 包含完整的测试用例

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 项目讨论区

---

**注意**: 请确保在生产环境中妥善配置安全设置，包括数据库密码、API密钥等敏感信息。

## 功能特性

- 🚀 异步网页抓取
- 📝 智能 Markdown 生成
- 🔧 多种内容源配置
- 💾 自动文件保存
- 🕒 时间戳命名
- 📊 详细日志输出
- 🤖 **AI 智能数据提取**
- 🧠 **多种 LLM 提供商支持**
- 📋 **结构化内容分析**
- ⚙️ **灵活的配置管理**
- 🌐 **HTTP API 服务**
- 📡 **RESTful 接口**
- 🔄 **实时网页处理**

## 项目结构

```
crawl4ai-demo/
├── config/
│   └── ai_config.yaml                 # AI 配置文件
├── utils/
│   └── ai_extractor.py               # AI 提取器核心模块
├── markdown/
│   ├── content_source_example.py      # 详细的内容源配置演示 + AI 功能
│   ├── content_source_short_example.py # 简化的内容源配置演示 + AI 功能
│   └── content_source_server.py       # HTTP API 服务器
├── doc/                               # 输出文件目录
├── logs/                              # 日志文件目录
└── README.md                          # 项目说明文档
```

## 安装依赖

在运行示例之前，请确保安装了必要的依赖：

```bash
pip install crawl4ai
pip install openai
pip install pyyaml
pip install fastapi
pip install uvicorn
pip install aiohttp
```

## HTTP API 服务

### 启动服务器

```bash
python markdown/content_source_server.py --port 8080
```

服务器启动后，可以通过以下地址访问：
- API 服务：http://localhost:8080
- API 文档：http://localhost:8080/docs

### API 接口

#### 1. 健康检查
```bash
GET /health
```

#### 2. 简单爬取接口（GET）
```bash
GET /crawl_simple?url=https://example.com&ai_modes=content_summary&save_files=true
```

参数说明：
- `url`: 要爬取的网页URL（必需）
- `content_source`: 内容源类型，默认为 "cleaned_html"
- `ai_modes`: AI分析模式，多个模式用逗号分隔，默认为 "content_summary"
- `save_files`: 是否保存文件，默认为 true

#### 3. 完整爬取接口（POST）
```bash
POST /crawl
Content-Type: application/json

{
  "url": "https://example.com",
  "content_source": "cleaned_html",
  "ai_modes": ["content_summary", "key_points"],
  "save_files": true
}
```

### 使用示例

#### 使用 curl 测试 GET 接口：
```bash
curl -X GET "http://localhost:8080/crawl_simple?url=https://httpbin.org/html&ai_modes=content_summary"
```

#### 使用 PowerShell 测试 POST 接口：
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/crawl" -Method POST -ContentType "application/json" -Body '{"url":"https://httpbin.org/html","ai_modes":["content_summary"],"save_files":true}'
```

### 响应格式

API 返回 JSON 格式的响应：

```json
{
  "success": true,
  "url": "https://example.com",
  "timestamp": "2025-09-19T16:38:23.123456",
  "markdown_content": "# 网页标题\n\n网页内容...",
  "ai_results": {
    "content_summary": {
      "success": true,
      "mode": "content_summary",
      "provider": "qwen",
      "result": "内容摘要...",
      "timestamp": "2025-09-19T16:38:35.216788"
    }
  },
  "saved_files": [
    "doc\\server_results_20250919_163823\\markdown_cleaned_html_20250919_163823.md",
    "doc\\server_results_20250919_163823\\ai_content_summary_20250919_163823.md",
    "doc\\server_results_20250919_163823\\complete_results_20250919_163823.json"
  ],
  "error": null
}
```

## 快速开始

### 1. 命令行方式运行

```bash
# 运行完整功能演示
python markdown/content_source_example.py

# 运行简化演示
python markdown/content_source_short_example.py
```

### 2. HTTP API 服务方式

启动 HTTP 服务器：

```bash
# 使用默认配置启动（端口8000）
python markdown/content_source_server.py

# 自定义主机和端口
python markdown/content_source_server.py --host 127.0.0.1 --port 9000
```

服务器启动后，可以通过以下方式访问：

- **API 文档**: http://localhost:8000/docs
- **服务状态**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health

### 3. API 接口使用

#### 简单爬取接口（GET 请求）

```bash
# 基本用法
curl "http://localhost:8000/crawl_simple?url=https://example.com"

# 指定分析模式
curl "http://localhost:8000/crawl_simple?url=https://example.com&ai_modes=structured_data,content_summary,key_points"

# 指定内容源类型
curl "http://localhost:8000/crawl_simple?url=https://example.com&content_source=cleaned_html"
```

#### 完整功能接口（POST 请求）

```bash
curl -X POST "http://localhost:8000/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "content_source": "cleaned_html",
       "ai_modes": ["structured_data", "content_summary", "key_points"],
       "save_files": true
     }'
```

#### 获取系统信息

```bash
# 获取可用的 AI 提供商
curl "http://localhost:8000/providers"

# 获取可用的分析模式
curl "http://localhost:8000/modes"
```

## AI 配置设置

### 1. 配置文件说明

项目使用 `config/ai_config.yaml` 文件管理 AI 相关配置：

```yaml
# LLM 提供商配置
providers:
  openai:
    api_key: "your-openai-api-key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-3.5-turbo"
    
  local_llm:
    base_url: "http://localhost:11434/v1"
    model: "llama2"
    api_key: "not-needed"

# 默认使用的提供商
default_provider: "openai"

# AI 提取模式配置
extraction_modes:
  content_summary:
    prompt: "请为以下内容生成一个简洁的摘要..."
  key_points:
    prompt: "请从以下内容中提取关键要点..."
```

### 2. 支持的 LLM 提供商

- **OpenAI**: GPT-3.5/GPT-4 系列模型
- **本地 LLM**: 通过 Ollama 等本地服务
- **其他兼容 OpenAI API 的服务**

### 3. 配置步骤

1. 复制配置文件模板
2. 填入你的 API 密钥
3. 选择合适的模型
4. 根据需要调整提示词

## 使用方法

### 基础网页抓取 + AI 分析

```bash
# 运行详细演示（包含完整的 AI 功能）
python markdown/content_source_example.py

# 运行简化演示（快速体验 AI 功能）
python markdown/content_source_short_example.py
```

### AI 功能特性

#### 1. 智能内容分析
- **内容摘要**: 自动生成网页内容的简洁摘要
- **关键点提取**: 识别并提取内容中的重要信息点
- **结构化数据提取**: 将非结构化内容转换为结构化数据

#### 2. 多模式提取
- **content_summary**: 生成内容摘要
- **key_points**: 提取关键要点
- **structured_data**: 结构化数据提取
- **custom**: 自定义提取模式

#### 3. 灵活的 LLM 集成
- 支持多种 LLM 提供商
- 可配置的模型参数
- 自定义提示词模板
- 错误处理和重试机制

## 三种内容源模式对比

| 模式 | 描述 | 适用场景 | AI 分析效果 |
|------|------|----------|-------------|
| **cleaned_html** | 清理后的HTML（默认） | 一般网页内容提取 | ⭐⭐⭐⭐⭐ 最佳 |
| **raw_html** | 原始HTML | 需要保留完整结构 | ⭐⭐⭐ 良好 |
| **fit_html** | 适配HTML | 结构化数据提取 | ⭐⭐⭐⭐ 优秀 |

## 输出文件说明

### 命令行方式输出

运行脚本后，会在 `doc/crawl_results_YYYYMMDD_HHMMSS/` 目录下生成以下文件：

```
crawl_results_20240101_120000/
├── markdown_default_20240101_120000.md      # 默认模式生成的 Markdown
├── markdown_raw_20240101_120000.md          # 原始 HTML 模式
├── markdown_fit_20240101_120000.md          # 适配 HTML 模式
├── ai_content_summary_20240101_120000.md    # AI 内容摘要
├── ai_key_points_20240101_120000.md         # AI 关键点提取
└── ai_structured_data_20240101_120000.md    # AI 结构化数据
```

### HTTP API 方式输出

通过 API 调用时，会在 `doc/server_results_YYYYMMDD_HHMMSS/` 目录下生成：

```
server_results_20240101_120000/
├── markdown_cleaned_html_20240101_120000.md  # Markdown 内容
├── ai_structured_data_20240101_120000.md     # AI 分析结果
├── ai_content_summary_20240101_120000.md     # AI 摘要
├── ai_key_points_20240101_120000.md          # AI 关键点
└── complete_results_20240101_120000.json     # 完整结果 JSON
```

## API 响应格式

### 成功响应示例

```json
{
  "success": true,
  "url": "https://example.com",
  "timestamp": "20240101_120000",
  "markdown_content": "# 网页标题\n\n网页内容...",
  "ai_results": {
    "structured_data": {
      "success": true,
      "content": "提取的结构化数据...",
      "provider": "qwen",
      "model": "qwen-turbo",
      "mode": "structured_data"
    },
    "content_summary": {
      "success": true,
      "content": "内容摘要...",
      "provider": "qwen",
      "model": "qwen-turbo", 
      "mode": "content_summary"
    }
  },
  "saved_files": [
    "path/to/markdown_file.md",
    "path/to/ai_result.md"
  ]
}
```

### 错误响应示例

```json
{
  "success": false,
  "url": "https://example.com",
  "timestamp": "20240101_120000",
  "error": "网页爬取失败: 连接超时"
```

## 技术特性

### 核心功能
- ✅ 异步网页抓取，提高处理效率
- ✅ 智能 Markdown 转换，保持内容结构
- ✅ 多种内容源配置，适应不同需求
- ✅ AI 智能分析，提取有价值信息
- ✅ 自动文件保存，便于结果管理
- ✅ 时间戳命名，避免文件覆盖
- 🌐 HTTP API 服务，支持远程调用
- 📡 RESTful 接口设计，易于集成

### AI 增强功能
- 🤖 **多 LLM 支持**: OpenAI、本地模型、通义千问等
- 🧠 **智能提取**: 内容摘要、关键点识别
- 📊 **结构化分析**: 将内容转换为结构化数据
- ⚙️ **配置驱动**: 通过 YAML 文件灵活配置
- 🔄 **错误恢复**: 完善的异常处理机制
- 📝 **详细日志**: 完整的处理过程记录

### 编码特性
- 🌐 完整的 UTF-8 支持，处理中文内容无障碍
- 📁 智能目录管理，自动创建时间戳文件夹
- 🛡️ 健壮的错误处理，确保程序稳定运行
- 📊 详细的统计信息，了解处理结果
- 🔧 模块化设计，易于扩展和维护
- 📂 有序文件组织，按时间戳分类存储
- 🚀 异步处理架构，提升并发性能

## 注意事项

### AI 功能使用前提
1. **API 密钥配置**: 确保在 `config/ai_config.yaml` 中正确配置了 LLM 提供商的 API 密钥
2. **网络连接**: AI 功能需要稳定的网络连接（使用在线 LLM 服务时）
3. **模型可用性**: 确认所配置的 LLM 模型服务正常运行

### HTTP 服务使用注意
1. **端口占用**: 确保指定端口未被其他程序占用
2. **防火墙设置**: 如需外部访问，请配置防火墙规则
3. **并发限制**: 服务器支持并发请求，但建议控制并发数量
4. **文件存储**: 长期运行需定期清理生成的文件

### 性能优化建议
- 对于大量内容处理，建议使用本地 LLM 以降低 API 调用成本
- 可根据内容类型选择最适合的内容源模式
- 每次运行会创建新的时间戳文件夹，便于结果管理和版本对比
- 定期清理 `doc/` 目录下的旧文件夹以节省存储空间
- HTTP 服务建议使用反向代理（如 Nginx）进行生产部署

### 故障排除
- 如果 AI 功能无法正常工作，请检查配置文件中的 API 密钥和服务地址
- 网络连接问题可能导致 AI 分析失败，程序会继续执行基础功能
- 查看控制台输出的详细日志信息以诊断问题
- HTTP 服务启动失败时，检查端口占用和权限问题

## 许可证

本项目仅用于学习和演示目的。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

*最后更新：2025年1月*