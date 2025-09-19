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
- **统一配置管理**: 采用YAML格式的统一配置文件，支持配置验证和错误处理

### 🛠 技术架构
- **后端框架**: FastAPI + Python 3.12
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **对象存储**: MinIO
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **AI集成**: 支持多种LLM提供商（OpenAI、Azure OpenAI、本地LLM、通义千问）
- **配置管理**: 统一的YAML配置文件，支持参数验证和类型检查

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
                              │
                              ▼
                       ┌─────────────────┐
                       │  统一配置管理    │
                       │  (YAML配置)     │
                       └─────────────────┘
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

## 🆕 统一配置管理

### 配置文件结构

系统现在使用统一的YAML配置文件 `config/app_config.yaml` 来管理所有配置参数：

```yaml
# 应用基础配置
app:
  name: "Crawl4AI Demo"
  version: "2.0.0"
  description: "智能网页爬取和AI分析系统"
  debug: false

# 服务器配置
server:
  host: "127.0.0.1"
  port: 8080
  workers: 4
  timeout: 30
  reload: false

# PostgreSQL数据库配置
database:
  host: "localhost"
  port: 5432
  name: "crawl4ai_db"
  username: "your_username"
  password: "your_password"
  # 连接池配置
  pool:
    size: 10
    max_overflow: 20
    timeout: 30
    recycle: 3600

# MinIO对象存储配置
minio:
  endpoint: "localhost:9000"
  access_key: "your_access_key"
  secret_key: "your_secret_key"
  secure: false
  region: "us-east-1"
  # 存储桶配置
  buckets:
    default_bucket: "crawl4ai-files"
    markdown_bucket: "crawl4ai-markdown"
    ai_results_bucket: "crawl4ai-ai-results"
    json_bucket: "crawl4ai-json"
  # 上传配置
  upload:
    max_file_size: 104857600  # 100MB
    allowed_extensions: [".md", ".json", ".txt", ".html"]
    auto_create_buckets: true

# AI服务配置
ai:
  default_provider: "qwen"
  # OpenAI配置
  openai:
    api_key: "your_openai_api_key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-3.5-turbo"
    max_tokens: 4000
    temperature: 0.7
  # Azure OpenAI配置
  azure_openai:
    api_key: "your_azure_api_key"
    endpoint: "https://your-resource.openai.azure.com/"
    api_version: "2023-12-01-preview"
    model: "gpt-35-turbo"
  # 本地LLM配置
  local_llm:
    base_url: "http://localhost:11434/v1"
    model: "llama2"
    api_key: "not-needed"
  # 通义千问配置
  qwen:
    api_key: "your_qwen_api_key"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: "qwen-turbo"
  # AI提取配置
  extraction:
    modes:
      content_summary: "请为以下内容生成一个简洁的摘要"
      key_points: "请从以下内容中提取关键要点"
      structured_data: "请将以下内容转换为结构化数据"
    default_mode: "content_summary"
  # 输出配置
  output:
    save_results: true
    format: "markdown"

# 爬取配置
crawl:
  content_sources: ["cleaned_html", "raw_html", "fit_html"]
  default_source: "cleaned_html"
  timeout:
    page_load: 30
    request: 10
    total: 60
  retry:
    max_attempts: 3
    delay: 1

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  files:
    server: "logs/server.log"
    ai_extraction: "logs/ai_extraction.log"
    database: "logs/database.log"
    minio: "logs/minio.log"

# 安全配置
security:
  secret_key: "your-secret-key-here"
  algorithm: "HS256"
  access_token_expire_minutes: 30

# 缓存配置
cache:
  enabled: true
  ttl: 3600  # 1小时
  max_size: 1000

# 监控配置
monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_check_interval: 30
```

### 配置加载器使用

系统提供了统一的配置加载器，支持配置验证和错误处理：

```python
from config.config_loader import config_loader

# 获取完整配置
config = config_loader.get_config()

# 获取特定配置节
db_config = config_loader.get_config('database')
minio_config = config_loader.get_config('minio')

# 获取数据库连接URL
db_url = config_loader.get_database_url()

# 获取MinIO端点
minio_endpoint = config_loader.get_minio_endpoint()
```

### 配置验证功能

系统内置了完善的配置验证机制：

- **参数类型检查**: 验证配置参数的数据类型
- **必填字段验证**: 检查必要配置项是否存在
- **格式验证**: 验证URL、端口号、IP地址等格式
- **范围验证**: 检查数值参数是否在有效范围内
- **依赖关系验证**: 检查配置项之间的依赖关系

配置验证会在系统启动时自动执行，如果发现错误会阻止系统启动并输出详细的错误信息。

### 配置文件迁移

如果你使用的是旧版本的配置文件，请按照以下步骤迁移：

1. **备份现有配置**: 备份 `config/database_config.py` 和 `config/minio_config.py`
2. **创建新配置文件**: 复制 `config/app_config.yaml` 模板
3. **迁移配置参数**: 将旧配置文件中的参数迁移到新的YAML文件中
4. **验证配置**: 运行系统验证配置是否正确

### 配置最佳实践

1. **环境变量支持**: 敏感信息（如密码、API密钥）建议使用环境变量
2. **配置分层**: 开发、测试、生产环境使用不同的配置文件
3. **版本控制**: 配置文件模板纳入版本控制，实际配置文件排除
4. **定期备份**: 定期备份生产环境的配置文件
5. **权限控制**: 限制配置文件的访问权限，保护敏感信息

### 启动服务

```bash
# 启动服务器（默认端口8080）
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

## 项目结构

```
crawl4ai-demo/
├── config/                          # 配置文件目录
│   ├── app_config.yaml             # 🆕 统一配置文件
│   ├── config_loader.py            # 🆕 配置加载器
│   ├── config_validator.py         # 🆕 配置验证器
│   ├── ai_config.yaml              # AI配置文件（保留兼容）
│   ├── database_config.py          # 数据库配置模块（已更新）
│   └── minio_config.py             # MinIO配置模块（已更新）
├── models/                         # 数据模型
│   └── database_models.py          # 数据库模型定义
├── utils/                          # 工具模块
│   └── ai_extractor.py             # AI提取器核心模块
├── templates/                      # HTML模板
│   └── index.html                  # 主页模板
├── static/                         # 静态资源
│   ├── css/style.css               # 样式文件
│   └── js/app.js                   # JavaScript文件
├── markdown/                       # 核心服务
│   ├── content_source_example.py   # 详细功能演示
│   ├── content_source_short_example.py # 简化功能演示
│   └── content_source_server.py    # HTTP API服务器
├── doc/                            # 输出文件目录
├── logs/                           # 日志文件目录
├── requirements.txt                # 依赖列表
└── README.md                       # 项目文档
```

## 配置系统升级说明

### 🆕 新增功能

1. **统一配置文件**: 所有配置参数集中在 `config/app_config.yaml` 中管理
2. **配置验证器**: 自动验证配置参数的正确性和完整性
3. **类型安全**: 支持配置参数的类型检查和格式验证
4. **错误处理**: 详细的配置错误提示和修复建议
5. **配置加载器**: 提供便捷的配置访问接口

### 🔄 迁移指南

如果你正在从旧版本升级，请按照以下步骤操作：

#### 步骤1: 备份现有配置
```bash
# 备份旧配置文件
cp config/database_config.py config/database_config.py.bak
cp config/minio_config.py config/minio_config.py.bak
```

#### 步骤2: 配置新的统一配置文件
```bash
# 编辑统一配置文件
nano config/app_config.yaml
```

将你的数据库和MinIO配置参数迁移到新的YAML文件中。

#### 步骤3: 验证配置
```bash
# 运行配置验证
python -c "from config.config_loader import config_loader; print('配置验证通过' if config_loader else '配置验证失败')"
```

#### 步骤4: 测试系统
```bash
# 启动服务器测试
python markdown/content_source_server.py --port 8080
```

### ⚠️ 重要提醒

- 新版本的配置系统向后兼容，旧的配置文件仍然可以使用
- 建议逐步迁移到新的统一配置系统以获得更好的管理体验
- 配置验证功能会在系统启动时自动运行，确保配置的正确性
- 如果遇到配置问题，请查看详细的错误日志进行排查

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

### 项目结构说明

#### 配置管理模块
- `config/app_config.yaml`: 统一配置文件，包含所有系统配置
- `config/config_loader.py`: 配置加载器，提供配置访问接口
- `config/config_validator.py`: 配置验证器，确保配置参数正确性
- `config/database_config.py`: 数据库配置模块（已更新为使用统一配置）
- `config/minio_config.py`: MinIO配置模块（已更新为使用统一配置）

#### 核心功能模块
- `models/database_models.py`: 数据库模型定义
- `utils/ai_extractor.py`: AI提取器核心模块
- `markdown/content_source_server.py`: HTTP API服务器

#### 前端资源
- `templates/index.html`: 主页模板
- `static/css/style.css`: 样式文件
- `static/js/app.js`: JavaScript文件

### 配置系统开发

#### 添加新的配置项

1. **在统一配置文件中添加配置项**:
```yaml
# config/app_config.yaml
new_service:
  enabled: true
  endpoint: "http://localhost:3000"
  timeout: 30
```

2. **在配置验证器中添加验证逻辑**:
```python
# config/config_validator.py
def _validate_new_service_config(self, service_config: Dict[str, Any]):
    """验证新服务配置"""
    if 'endpoint' in service_config:
        endpoint = service_config['endpoint']
        if not self._is_valid_url(endpoint):
            self.errors.append(f"新服务端点格式无效: {endpoint}")
```

3. **在配置加载器中添加访问方法**:
```python
# config/config_loader.py
def get_new_service_config(self) -> Dict[str, Any]:
    """获取新服务配置"""
    return self.get_config('new_service')
```

#### 配置验证最佳实践

1. **必填字段验证**: 检查关键配置项是否存在
2. **类型验证**: 确保配置值的数据类型正确
3. **格式验证**: 验证URL、端口号、IP地址等格式
4. **范围验证**: 检查数值是否在合理范围内
5. **依赖验证**: 检查配置项之间的依赖关系

### 扩展开发

#### 添加新的AI分析模式：
1. 在 `config/app_config.yaml` 中添加新模式配置:
```yaml
ai:
  extraction:
    modes:
      new_analysis_mode: "请对以下内容进行新的分析..."
```

2. 在 `utils/ai_extractor.py` 中实现分析逻辑
3. 更新前端界面选项

#### 添加新的存储后端：
1. 在 `config/app_config.yaml` 中添加新存储配置
2. 实现存储管理器类
3. 在服务器中集成新的存储后端
4. 添加相应的配置验证逻辑

### 日志和监控

#### 日志配置
系统使用统一的日志配置，支持多个日志文件：

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  files:
    server: "logs/server.log"
    ai_extraction: "logs/ai_extraction.log"
    database: "logs/database.log"
    minio: "logs/minio.log"
    config: "logs/config.log"
```

#### 日志级别说明：
- **DEBUG**: 详细的调试信息，用于开发和故障排除
- **INFO**: 正常操作信息，记录系统运行状态
- **WARNING**: 警告信息，系统可以继续运行但需要注意
- **ERROR**: 错误信息，系统遇到问题但可以恢复
- **CRITICAL**: 严重错误，系统无法继续运行

#### 监控功能
```yaml
monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_check_interval: 30
```

### 安全最佳实践

#### 配置文件安全
1. **敏感信息保护**: 使用环境变量存储API密钥和密码
2. **文件权限**: 限制配置文件的读写权限
3. **版本控制**: 不要将包含敏感信息的配置文件提交到版本控制系统
4. **配置加密**: 对于高敏感环境，考虑加密配置文件

#### 示例环境变量配置
```bash
# .env 文件
DATABASE_PASSWORD=your_secure_password
MINIO_SECRET_KEY=your_minio_secret
OPENAI_API_KEY=your_openai_key
```

在配置文件中引用：
```yaml
database:
  password: "${DATABASE_PASSWORD}"
minio:
  secret_key: "${MINIO_SECRET_KEY}"
ai:
  openai:
    api_key: "${OPENAI_API_KEY}"
```

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

### 故障排除

### 常见问题及解决方案

#### 配置相关问题

**问题**: 配置文件加载失败
```
ConfigError: 配置文件不存在或无法读取
```
**解决方案**:
1. 检查 `config/app_config.yaml` 文件是否存在
2. 确认文件权限是否正确
3. 验证YAML语法是否正确

**问题**: 配置验证失败
```
ConfigValidationError: 数据库配置验证失败
```
**解决方案**:
1. 检查配置文件中的必填字段是否完整
2. 验证URL格式、端口号等是否正确
3. 查看详细错误信息，修正相应配置项

#### 数据库连接问题

**问题**: PostgreSQL连接失败
```
DatabaseError: 无法连接到数据库
```
**解决方案**:
1. 检查PostgreSQL服务是否运行
2. 验证数据库连接配置（主机、端口、用户名、密码）
3. 确认数据库是否存在
4. 检查网络连接和防火墙设置

**问题**: 数据库连接池耗尽
```
PoolTimeoutError: 连接池超时
```
**解决方案**:
1. 增加连接池大小配置
2. 检查是否有连接泄漏
3. 优化数据库查询性能

#### MinIO存储问题

**问题**: MinIO连接失败
```
MinIOError: 无法连接到MinIO服务
```
**解决方案**:
1. 检查MinIO服务是否运行
2. 验证MinIO连接配置（端点、访问密钥、密钥）
3. 确认存储桶是否存在
4. 检查网络连接

**问题**: 文件上传失败
```
UploadError: 文件上传到MinIO失败
```
**解决方案**:
1. 检查文件大小是否超过限制
2. 验证存储桶权限设置
3. 确认磁盘空间是否充足

#### AI服务问题

**问题**: AI API调用失败
```
AIError: AI服务调用失败
```
**解决方案**:
1. 检查API密钥是否正确
2. 验证网络连接
3. 确认API配额是否充足
4. 检查请求格式是否正确

### 调试技巧

#### 启用调试模式
在配置文件中设置：
```yaml
app:
  debug: true
logging:
  level: "DEBUG"
```

#### 查看日志文件
```bash
# 查看服务器日志
tail -f logs/server.log

# 查看配置加载日志
tail -f logs/config.log

# 查看数据库操作日志
tail -f logs/database.log
```

#### 配置验证测试
```python
# 测试配置验证
from config.config_validator import config_validator
from config.config_loader import config_loader

# 加载并验证配置
config_loader.load_config()
print("配置验证通过")
```

### 性能监控

#### 系统资源监控
```yaml
monitoring:
  enabled: true
  metrics:
    - cpu_usage
    - memory_usage
    - disk_usage
    - network_io
```

#### 数据库性能监控
```yaml
database:
  monitoring:
    slow_query_log: true
    connection_pool_stats: true
    query_timeout: 30
```

#### MinIO性能监控
```yaml
minio:
  monitoring:
    bandwidth_limit: "100MB"
    request_timeout: 30
    health_check_interval: 60
```

### 性能优化

#### 配置优化建议

##### 数据库性能优化
```yaml
database:
  # 连接池优化
  pool:
    min_size: 5          # 最小连接数
    max_size: 20         # 最大连接数
    max_overflow: 10     # 超出最大连接数的额外连接
    pool_timeout: 30     # 获取连接超时时间
    pool_recycle: 3600   # 连接回收时间
  
  # 查询优化
  query:
    timeout: 30          # 查询超时时间
    echo: false          # 是否打印SQL语句
    pool_pre_ping: true  # 连接前预检查
```

##### MinIO存储优化
```yaml
minio:
  # 连接优化
  connection:
    timeout: 30          # 连接超时时间
    retry_attempts: 3    # 重试次数
    retry_delay: 1       # 重试延迟
  
  # 上传优化
  upload:
    chunk_size: 8388608  # 分块上传大小 (8MB)
    max_concurrent: 5    # 最大并发上传数
    compression: true    # 启用压缩
  
  # 存储桶优化
  buckets:
    default_bucket: "crawl4ai-data"
    image_bucket: "crawl4ai-images"
    document_bucket: "crawl4ai-docs"
    versioning: true     # 启用版本控制
```

##### AI服务优化
```yaml
ai:
  # 请求优化
  request:
    timeout: 60          # 请求超时时间
    max_retries: 3       # 最大重试次数
    retry_delay: 2       # 重试延迟
  
  # 缓存优化
  cache:
    enabled: true        # 启用缓存
    ttl: 3600           # 缓存过期时间
    max_size: 1000      # 最大缓存条目数
  
  # 并发控制
  concurrency:
    max_concurrent: 3    # 最大并发请求数
    rate_limit: 60       # 每分钟最大请求数
```

#### 系统性能监控

##### 应用性能指标
```yaml
monitoring:
  performance:
    # 响应时间监控
    response_time:
      warning_threshold: 2000   # 警告阈值(ms)
      critical_threshold: 5000  # 严重阈值(ms)
    
    # 内存使用监控
    memory:
      warning_threshold: 80     # 警告阈值(%)
      critical_threshold: 90    # 严重阈值(%)
    
    # CPU使用监控
    cpu:
      warning_threshold: 70     # 警告阈值(%)
      critical_threshold: 85    # 严重阈值(%)
```

##### 性能调优建议

1. **数据库调优**:
   - 根据并发量调整连接池大小
   - 启用查询缓存和索引优化
   - 定期分析慢查询日志

2. **存储调优**:
   - 使用适当的分块大小进行文件上传
   - 启用压缩减少存储空间
   - 配置合适的存储桶策略

3. **AI服务调优**:
   - 实现请求缓存减少API调用
   - 控制并发请求数避免限流
   - 优化提示词提高响应质量

4. **系统调优**:
   - 启用日志轮转避免磁盘满
   - 配置合适的超时时间
   - 实现健康检查和自动恢复

#### 缓存策略

##### Redis缓存配置（可选）
```yaml
cache:
  redis:
    enabled: false       # 是否启用Redis缓存
    host: "localhost"
    port: 6379
    db: 0
    password: ""
    
    # 缓存策略
    strategies:
      ai_results:
        ttl: 3600        # AI结果缓存1小时
        max_size: 1000   # 最大缓存条目
      
      web_content:
        ttl: 1800        # 网页内容缓存30分钟
        max_size: 500    # 最大缓存条目
```

##### 内存缓存配置
```yaml
cache:
  memory:
    enabled: true        # 启用内存缓存
    max_size: 100        # 最大缓存条目数
    ttl: 1800           # 默认过期时间(秒)
    
    # 缓存清理策略
    cleanup:
      interval: 300      # 清理间隔(秒)
      strategy: "lru"    # 清理策略(lru/fifo)
```

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