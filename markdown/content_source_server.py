"""
HTTP服务器 - 提供网页爬取和AI分析的API接口
支持通过HTTP接口调用网页爬取和AI提取功能
集成MinIO存储和PostgreSQL数据库
"""
import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, HttpUrl
import uvicorn

# 添加utils目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from utils.ai_extractor import AIExtractor
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

# 导入数据库和存储配置
from config.database_config import db_manager, get_db, init_database
from config.minio_config import minio_manager
from models.database_models import CrawlTask, CrawlFile


class CrawlRequest(BaseModel):
    """爬取请求模型"""
    url: HttpUrl
    content_source: str = "cleaned_html"  # cleaned_html, raw_html, fit_html
    ai_modes: list[str] = ["structured_data", "content_summary", "key_points"]
    save_files: bool = True


class CrawlResponse(BaseModel):
    """爬取响应模型"""
    success: bool
    url: str
    timestamp: str
    markdown_content: Optional[str] = None
    ai_results: Optional[Dict[str, Any]] = None
    storage_info: Optional[Dict[str, Any]] = None  # 替换saved_files
    error: Optional[str] = None


class ContentSourceServer:
    """网页内容爬取和AI分析HTTP服务器"""
    
    def __init__(self, port: int = 8000, host: str = "0.0.0.0"):
        """
        初始化服务器
        
        Args:
            port: 服务器端口
            host: 服务器主机地址
        """
        self.port = port
        self.host = host
        
        # 设置日志
        self.logger = self._setup_logging()
        self.logger.info(f"🔧 初始化ContentSourceServer，端口: {port}, 主机: {host}")
        
        # 创建FastAPI应用
        self.app = FastAPI(
            title="Crawl4AI HTTP服务器",
            description="提供网页爬取和AI分析的API接口，集成MinIO存储和PostgreSQL数据库",
            version="2.0.0"
        )
        
        # 初始化AI提取器
        self.logger.info("🤖 初始化AI提取器...")
        self.ai_extractor = AIExtractor()
        
        # 设置模板和静态文件
        self.logger.info("📁 设置模板和静态文件...")
        self.templates = Jinja2Templates(directory="templates")
        
        # 初始化数据库和存储
        self.logger.info("💾 初始化数据库和存储...")
        self._init_database_and_storage()
        
        # 设置路由
        self.logger.info("🛣️ 设置API路由...")
        self._setup_routes()
        
        # 挂载静态文件
        self.logger.info("📂 挂载静态文件...")
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        
        self.logger.info("✅ ContentSourceServer初始化完成")
        
    def _init_database_and_storage(self):
        """初始化数据库和MinIO存储"""
        try:
            # 初始化数据库
            init_database()
            self.logger.info("✅ 数据库初始化成功")
            
            # MinIO存储桶在初始化时已经创建，这里只需要测试连接
            if minio_manager.test_connection():
                self.logger.info("✅ MinIO存储连接成功")
            else:
                raise Exception("MinIO连接测试失败")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库或存储初始化失败: {str(e)}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        logger = logging.getLogger("ContentSourceServer")
        logger.setLevel(logging.INFO)
        
        # 如果已经有处理器，则不重复添加
        if logger.handlers:
            return logger
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建文件处理器
        log_file = log_dir / "server.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/")
        async def root(request: Request):
            """主页 - 返回Web界面"""
            return self.templates.TemplateResponse("index.html", {"request": request})
        
        @self.app.get("/api")
        async def api_info():
            """API信息 - 服务器状态"""
            return {
                "service": "网页爬取和AI分析服务",
                "status": "运行中",
                "version": "1.0.0",
                "endpoints": {
                    "/crawl": "POST - 爬取网页并进行AI分析",
                    "/crawl_simple": "GET - 简单爬取接口（URL参数）",
                    "/health": "GET - 健康检查",
                    "/providers": "GET - 获取可用的AI提供商",
                    "/modes": "GET - 获取可用的AI分析模式",
                    "/api/history": "GET - 获取爬取历史记录",
                    "/api/files/{task_id}": "GET - 获取任务文件列表",
                    "/api/preview/{file_id}": "GET - 预览文件内容"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查接口"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "ai_providers": self.ai_extractor.get_available_providers(),
                "ai_modes": self.ai_extractor.get_available_modes()
            }
        
        @self.app.get("/providers")
        async def get_providers():
            """获取可用的AI提供商"""
            return {
                "providers": self.ai_extractor.get_available_providers(),
                "default_provider": self.ai_extractor.config.get("llm", {}).get("default_provider", "openai")
            }
        
        @self.app.get("/modes")
        async def get_modes():
            """获取可用的AI分析模式"""
            return {
                "modes": self.ai_extractor.get_available_modes(),
                "default_mode": self.ai_extractor.config.get("extraction", {}).get("default_mode", "structured_data")
            }
        
        @self.app.post("/crawl", response_model=CrawlResponse)
        async def crawl_and_analyze(request: CrawlRequest):
            """
            爬取网页并进行AI分析（完整功能）
            
            Args:
                request: 爬取请求参数
                
            Returns:
                爬取和分析结果
            """
            return await self._process_crawl_request(
                url=str(request.url),
                content_source=request.content_source,
                ai_modes=request.ai_modes,
                save_files=request.save_files
            )
        
        @self.app.get("/crawl_simple", response_model=CrawlResponse)
        async def crawl_simple(
            url: str = Query(..., description="要爬取的网页URL"),
            content_source: str = Query("cleaned_html", description="内容源类型"),
            ai_modes: str = Query("content_summary", description="AI分析模式（逗号分隔）"),
            save_files: bool = Query(True, description="是否保存文件")
        ) -> CrawlResponse:
            """
            简单爬取接口（GET请求，URL参数）
            
            Args:
                url: 要爬取的网页URL
                content_source: 内容源类型
                ai_modes: AI分析模式（逗号分隔）
                save_files: 是否保存文件
                
            Returns:
                爬取和分析结果
            """
            # 解析AI模式
            modes_list = [mode.strip() for mode in ai_modes.split(",") if mode.strip()]
            
            return await self._process_crawl_request(
                url=url,
                content_source=content_source,
                ai_modes=modes_list,
                save_files=save_files
            )
        
        @self.app.get("/api/history")
        async def get_crawl_history(
            limit: int = Query(50, description="返回记录数量限制"),
            offset: int = Query(0, description="偏移量")
        ):
            """获取爬取历史记录"""
            try:
                with get_db() as db:
                    # 查询爬取任务记录
                    tasks = db.query(CrawlTask).order_by(CrawlTask.created_at.desc()).offset(offset).limit(limit).all()
                    
                    history = []
                    for task in tasks:
                        # 获取任务关联的文件数量
                        file_count = db.query(CrawlFile).filter(CrawlFile.task_id == task.id).count()
                        
                        history.append({
                            "id": task.id,
                            "url": task.url,
                            "content_source": task.content_source,
                            "ai_modes": task.ai_modes.split(",") if task.ai_modes else [],
                            "status": task.status,
                            "created_at": task.created_at.isoformat(),
                            "file_count": file_count
                        })
                    
                    return {
                        "success": True,
                        "data": history,
                        "total": len(history)
                    }
                    
            except Exception as e:
                self.logger.error(f"获取历史记录失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")
        
        @self.app.get("/api/files/{task_id}")
        async def get_task_files(task_id: int):
            """获取指定任务的文件列表"""
            try:
                with get_db() as db:
                    # 查询任务信息
                    task = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
                    if not task:
                        raise HTTPException(status_code=404, detail="任务不存在")
                    
                    # 查询任务关联的文件
                    files = db.query(CrawlFile).filter(CrawlFile.task_id == task_id).all()
                    
                    file_list = []
                    for file in files:
                        file_list.append({
                            "id": file.id,
                            "filename": file.filename,
                            "file_type": file.file_type,
                            "file_size": file.file_size,
                            "minio_bucket": file.minio_bucket,
                            "minio_path": file.minio_path,
                            "created_at": file.created_at.isoformat()
                        })
                    
                    return {
                        "success": True,
                        "task": {
                            "id": task.id,
                            "url": task.url,
                            "content_source": task.content_source,
                            "created_at": task.created_at.isoformat()
                        },
                        "files": file_list
                    }
                    
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"获取任务文件失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"获取任务文件失败: {str(e)}")
        
        @self.app.get("/api/preview/{file_id}")
        async def preview_file(file_id: int):
            """预览文件内容"""
            try:
                with get_db() as db:
                    # 查询文件信息
                    file = db.query(CrawlFile).filter(CrawlFile.id == file_id).first()
                    if not file:
                        raise HTTPException(status_code=404, detail="文件不存在")
                    
                    # 从MinIO获取文件内容
                    try:
                        file_content = minio_manager.get_file_content(file.minio_bucket, file.minio_path)
                        
                        # 根据文件类型处理内容
                        if file.file_type in ['markdown', 'json', 'txt']:
                            # 文本文件直接返回内容
                            content = file_content.decode('utf-8')
                        else:
                            # 其他文件类型返回base64编码
                            import base64
                            content = base64.b64encode(file_content).decode('utf-8')
                        
                        return {
                            "success": True,
                            "file": {
                                "id": file.id,
                                "filename": file.filename,
                                "file_type": file.file_type,
                                "file_size": file.file_size,
                                "content": content,
                                "is_text": file.file_type in ['markdown', 'json', 'txt']
                            }
                        }
                        
                    except Exception as e:
                        self.logger.error(f"从MinIO获取文件内容失败: {str(e)}")
                        raise HTTPException(status_code=500, detail=f"获取文件内容失败: {str(e)}")
                    
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"预览文件失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"预览文件失败: {str(e)}")
    
    async def _process_crawl_request(
        self,
        url: str,
        content_source: str = "cleaned_html",
        ai_modes: list[str] = None,
        save_files: bool = True
    ) -> CrawlResponse:
        """
        处理爬取请求的核心逻辑
        
        Args:
            url: 要爬取的网页URL
            content_source: 内容源类型
            ai_modes: AI分析模式列表
            save_files: 是否保存文件
            
        Returns:
            爬取和分析结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self.logger.info(f"🚀 开始处理爬取请求 - URL: {url}")
            
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise HTTPException(status_code=400, detail="无效的URL格式")
            
            # 设置默认AI模式
            if ai_modes is None:
                ai_modes = ["structured_data", "content_summary"]
            
            # 验证AI模式
            available_modes = self.ai_extractor.get_available_modes()
            invalid_modes = [mode for mode in ai_modes if mode not in available_modes]
            if invalid_modes:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无效的AI分析模式: {invalid_modes}，可用模式: {available_modes}"
                )
            
            # 创建Markdown生成器
            markdown_generator = DefaultMarkdownGenerator(content_source=content_source)
            config = CrawlerRunConfig(markdown_generator=markdown_generator)
            
            # 执行网页爬取
            self.logger.info(f"📄 开始爬取网页 - 内容源: {content_source}")
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=config)
                
                if not result.success:
                    raise HTTPException(status_code=500, detail=f"网页爬取失败: {result.error_message}")
                
                markdown_content = result.markdown
                self.logger.info(f"✅ 网页爬取成功 - 内容长度: {len(markdown_content)}")
            
            # 执行AI分析
            ai_results = {}
            if ai_modes:
                self.logger.info(f"🤖 开始AI分析 - 模式: {ai_modes}")
                for mode in ai_modes:
                    try:
                        ai_result = await self.ai_extractor.extract(markdown_content, mode=mode)
                        ai_results[mode] = ai_result
                        self.logger.info(f"✅ AI分析完成 - 模式: {mode}")
                    except Exception as e:
                        self.logger.error(f"❌ AI分析失败 - 模式: {mode}, 错误: {str(e)}")
                        ai_results[mode] = {
                            "success": False,
                            "error": str(e),
                            "mode": mode
                        }
            
            # 保存文件到MinIO和数据库
            storage_info = {}
            if save_files:
                storage_info = await self._save_results(
                    url=url,
                    timestamp=timestamp,
                    markdown_content=markdown_content,
                    ai_results=ai_results,
                    content_source=content_source
                )
            
            self.logger.info(f"🎉 请求处理完成 - URL: {url}")
            
            return CrawlResponse(
                success=True,
                url=url,
                timestamp=timestamp,
                markdown_content=markdown_content,
                ai_results=ai_results,
                storage_info=storage_info
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"❌ 处理请求失败 - URL: {url}, 错误: {str(e)}")
            return CrawlResponse(
                success=False,
                url=url,
                timestamp=timestamp,
                error=str(e)
            )
    
    async def _save_results(
        self,
        url: str,
        timestamp: str,
        markdown_content: str,
        ai_results: Dict[str, Any],
        content_source: str
    ) -> Dict[str, Any]:
        """
        保存爬取和分析结果到MinIO和数据库
        
        Args:
            url: 原始URL
            timestamp: 时间戳
            markdown_content: Markdown内容
            ai_results: AI分析结果
            content_source: 内容源类型
            
        Returns:
            包含文件信息和数据库记录的字典
        """
        try:
            # 创建临时目录保存文件
            temp_dir = Path("temp") / f"server_results_{timestamp}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            saved_files = []
            minio_urls = []
            
            # 1. 保存Markdown文件到临时目录
            markdown_filename = f"markdown_{content_source}_{timestamp}.md"
            markdown_file = temp_dir / markdown_filename
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(f"# 网页爬取结果\n\n")
                f.write(f"**URL:** {url}\n\n")
                f.write(f"**爬取时间:** {timestamp}\n\n")
                f.write(f"**内容源:** {content_source}\n\n")
                f.write("---\n\n")
                f.write(markdown_content)
            
            # 上传Markdown文件到MinIO
            markdown_minio_url = minio_manager.upload_file(
                str(markdown_file), 
                "crawl4ai-markdown", 
                markdown_filename
            )
            if markdown_minio_url:
                minio_urls.append({
                    "type": "markdown",
                    "filename": markdown_filename,
                    "url": markdown_minio_url,
                    "size": os.path.getsize(markdown_file)
                })
                self.logger.info(f"💾 已上传Markdown文件到MinIO: {markdown_minio_url}")
            
            # 2. 保存AI分析结果
            for mode, result in ai_results.items():
                if result.get("success"):
                    ai_filename = f"ai_{mode}_{timestamp}.md"
                    ai_file = temp_dir / ai_filename
                    with open(ai_file, 'w', encoding='utf-8') as f:
                        f.write(f"# AI分析结果 - {mode}\n\n")
                        f.write(f"**URL:** {url}\n\n")
                        f.write(f"**分析时间:** {timestamp}\n\n")
                        f.write(f"**分析模式:** {mode}\n\n")
                        f.write(f"**AI提供商:** {result.get('provider', 'unknown')}\n\n")
                        f.write("---\n\n")
                        f.write(result.get("content", ""))
                    
                    # 上传AI分析文件到MinIO
                    ai_minio_url = minio_manager.upload_file(
                        str(ai_file), 
                        "crawl4ai-ai-results", 
                        ai_filename
                    )
                    if ai_minio_url:
                        minio_urls.append({
                            "type": f"ai_{mode}",
                            "filename": ai_filename,
                            "url": ai_minio_url,
                            "size": os.path.getsize(ai_file)
                        })
                        self.logger.info(f"💾 已上传AI分析文件到MinIO: {ai_minio_url}")
            
            # 3. 保存完整结果JSON
            json_filename = f"complete_results_{timestamp}.json"
            json_file = temp_dir / json_filename
            complete_results = {
                "url": url,
                "timestamp": timestamp,
                "content_source": content_source,
                "markdown_content": markdown_content,
                "ai_results": ai_results,
                "minio_files": minio_urls
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(complete_results, f, ensure_ascii=False, indent=2)
            
            # 上传JSON文件到MinIO
            json_minio_url = minio_manager.upload_file(
                str(json_file), 
                "crawl4ai-json", 
                json_filename
            )
            if json_minio_url:
                minio_urls.append({
                    "type": "json",
                    "filename": json_filename,
                    "url": json_minio_url,
                    "size": os.path.getsize(json_file)
                })
                self.logger.info(f"💾 已上传完整结果JSON到MinIO: {json_minio_url}")
            
            # 4. 保存记录到数据库
            db_record_id = await self._save_to_database(url, timestamp, content_source, minio_urls)
            
            # 5. 清理临时文件
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                "database_id": db_record_id,
                "minio_files": minio_urls,
                "total_files": len(minio_urls)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 保存文件失败: {str(e)}")
            return {"error": str(e)}
    
    async def _save_to_database(self, url: str, timestamp: str, content_source: str, minio_files: list) -> Optional[int]:
        """保存爬取任务和文件记录到数据库"""
        try:
            db = next(get_db())
            
            # 创建爬取任务记录
            crawl_task = CrawlTask(
                url=url,
                content_source=content_source,
                status="completed",
                created_at=datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            )
            db.add(crawl_task)
            db.commit()
            db.refresh(crawl_task)
            
            # 创建文件记录
            for file_info in minio_files:
                crawl_file = CrawlFile(
                    task_id=crawl_task.id,
                    filename=file_info["filename"],
                    file_type=file_info["type"],
                    file_size=file_info["size"],
                    minio_url=file_info["url"],
                    file_metadata={"content_source": content_source}
                )
                db.add(crawl_file)
            
            db.commit()
            self.logger.info(f"💾 已保存数据库记录，任务ID: {crawl_task.id}")
            return crawl_task.id
            
        except Exception as e:
            self.logger.error(f"❌ 保存数据库记录失败: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    def run(self):
        """启动服务器"""
        try:
            self.logger.info(f"🚀 启动网页爬取和AI分析服务器")
            self.logger.info(f"📡 服务器地址: http://{self.host}:{self.port}")
            self.logger.info(f"📚 API文档: http://{self.host}:{self.port}/docs")
            self.logger.info(f"🔧 可用AI提供商: {self.ai_extractor.get_available_providers()}")
            self.logger.info(f"🎯 可用AI模式: {self.ai_extractor.get_available_modes()}")
            
            # 添加启动前的日志
            self.logger.info("🔄 正在启动Uvicorn服务器...")
            
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except Exception as e:
            self.logger.error(f"❌ 服务器启动失败: {str(e)}")
            raise


def main():
    """主函数"""
    import argparse
    
    # 从统一配置获取默认值
    from config.config_loader import config_loader
    
    try:
        # 加载配置
        config_loader.load_config()
        server_config = config_loader.get_server_config()
        default_host = server_config.get('host', '0.0.0.0')
        default_port = server_config.get('port', 8080)
    except Exception as e:
        print(f"⚠️ 无法加载配置文件，使用默认值: {e}")
        default_host = '0.0.0.0'
        default_port = 8080
    
    parser = argparse.ArgumentParser(description="网页爬取和AI分析HTTP服务器")
    parser.add_argument("--host", default=default_host, help="服务器主机地址")
    parser.add_argument("--port", type=int, default=default_port, help="服务器端口")
    
    args = parser.parse_args()
    
    # 创建并启动服务器
    server = ContentSourceServer(host=args.host, port=args.port)
    server.run()


if __name__ == "__main__":
    main()