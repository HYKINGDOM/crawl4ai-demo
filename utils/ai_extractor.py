"""
AI数据提取器 - 集成多种LLM提供商进行智能数据提取
"""

import json
import yaml
import logging
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import os

class AIExtractor:
    """AI数据提取器类，支持多种LLM提供商"""
    
    def __init__(self, config_path: str = None):
        """
        初始化AI提取器
        
        Args:
            config_path: 配置文件路径，如果为None则自动查找
        """
        # 如果没有指定配置文件路径，则自动查找
        if config_path is None:
            # 获取当前文件的目录
            current_dir = Path(__file__).parent
            # 查找项目根目录下的配置文件
            project_root = current_dir.parent
            config_path = project_root / "config" / "ai_config.yaml"
        
        self.config_path = str(config_path)
        self.logger = self._setup_logging()  # 先设置日志
        self.config = self._load_config()    # 再加载配置
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                self.logger.warning(f"⚠️ 配置文件不存在: {config_path}")
                self.logger.info("🔧 使用默认配置")
                return self._get_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"✅ 成功加载配置文件: {config_path}")
                return config
        except Exception as e:
            self.logger.error(f"❌ 加载配置文件失败: {e}")
            self.logger.info("🔧 使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "llm": {
                "default_provider": "openai",
                "openai": {
                    "api_key": "",
                    "model": "gpt-3.5-turbo",
                    "base_url": "https://api.openai.com/v1",
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                "azure_openai": {
                    "api_key": "",
                    "endpoint": "",
                    "api_version": "2024-02-15-preview",
                    "deployment_name": "",
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                "local_llm": {
                    "base_url": "http://localhost:11434",
                    "model": "llama2",
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                "qwen": {
                    "api_key": "",
                    "model": "qwen-turbo",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "temperature": 0.1,
                    "max_tokens": 4000
                }
            },
            "extraction": {
                "default_mode": "structured_data",
                "prompts": {
                    "structured_data": "请从以下内容中提取结构化数据，以JSON格式返回：\n\n{content}",
                    "summary": "请总结以下内容的主要观点：\n\n{content}",
                    "keywords": "请从以下内容中提取关键词：\n\n{content}",
                    "entities": "请从以下内容中提取实体（人名、地名、组织等）：\n\n{content}",
                    "sentiment": "请分析以下内容的情感倾向：\n\n{content}"
                },
                "max_content_length": 8000
            },
            "output": {
                "save_results": True,
                "output_format": "json",
                "filename_pattern": "ai_analysis_{timestamp}_{mode}.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ai_extraction.log"
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志记录"""
        logger = logging.getLogger("AIExtractor")
        logger.setLevel(logging.INFO)
        
        # 如果已经有处理器，则不重复添加
        if logger.handlers:
            return logger
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建文件处理器
        log_file = log_dir / "ai_extraction.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _build_prompt(self, content: str, mode: str) -> str:
        """
        构建提示词
        
        Args:
            content: 要处理的内容
            mode: 提取模式
            
        Returns:
            构建好的提示词
        """
        # 获取提示词模板
        prompts = self.config.get("extraction", {}).get("prompts", {})
        
        # 根据模式选择提示词模板
        if mode == "structured_data":
            template = prompts.get("structured_data", 
                "请从以下内容中提取结构化数据，包括标题、关键信息、数据等：\n\n{content}")
        elif mode == "content_summary":
            template = prompts.get("content_summary", 
                "请对以下内容进行总结，提取主要观点和核心信息：\n\n{content}")
        elif mode == "key_points":
            template = prompts.get("key_points", 
                "请从以下内容中提取关键点，以列表形式呈现：\n\n{content}")
        elif mode == "entities":
            template = prompts.get("entities", 
                "请从以下内容中识别和提取实体信息（人名、地名、机构名等）：\n\n{content}")
        elif mode == "sentiment":
            template = prompts.get("sentiment", 
                "请分析以下内容的情感倾向和态度：\n\n{content}")
        else:
            template = "请分析以下内容：\n\n{content}"
        
        # 限制内容长度，避免超出API限制
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            self.logger.info(f"内容过长，已截取前{max_content_length}个字符")
        
        return template.format(content=content)

    async def extract_with_openai(self, content: str, mode: str = "structured_data") -> Dict[str, Any]:
        """
        使用OpenAI进行数据提取
        
        Args:
            content: 要提取的内容
            mode: 提取模式
            
        Returns:
            提取结果
        """
        try:
            openai_config = self.config.get("openai", {})
            api_key = openai_config.get("api_key")
            base_url = openai_config.get("base_url", "https://api.openai.com/v1")
            model = openai_config.get("model", "gpt-3.5-turbo")
            
            if not api_key or api_key == "your-openai-api-key-here":
                self.logger.warning("OpenAI API密钥未配置，跳过AI提取")
                return {"error": "API密钥未配置"}
            
            # 获取提示词模板
            prompt_template = self.config.get("extraction", {}).get("prompts", {}).get(mode, "")
            if not prompt_template:
                prompt_template = "请分析以下内容：\n{content}"
            
            prompt = prompt_template.format(content=content[:4000])  # 限制内容长度
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": openai_config.get("max_tokens", 2000),
                "temperature": openai_config.get("temperature", 0.1)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        self.logger.info(f"OpenAI提取成功，模式: {mode}")
                        return {
                            "success": True,
                            "mode": mode,
                            "provider": "openai",
                            "result": ai_response,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"OpenAI API请求失败: {response.status} - {error_text}")
                        return {"error": f"API请求失败: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"OpenAI提取过程中发生错误: {e}")
            return {"error": str(e)}
    
    async def extract_with_local_llm(self, content: str, mode: str = "structured_data") -> Dict[str, Any]:
        """
        使用本地LLM进行数据提取（如Ollama）
        
        Args:
            content: 要提取的内容
            mode: 提取模式
            
        Returns:
            提取结果
        """
        try:
            local_config = self.config.get("local_llm", {})
            base_url = local_config.get("base_url", "http://localhost:11434")
            model = local_config.get("model", "llama2")
            
            # 获取提示词模板
            prompt_template = self.config.get("extraction", {}).get("prompts", {}).get(mode, "")
            if not prompt_template:
                prompt_template = "请分析以下内容：\n{content}"
            
            prompt = prompt_template.format(content=content[:4000])  # 限制内容长度
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": local_config.get("temperature", 0.1),
                    "num_predict": local_config.get("max_tokens", 2000)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result.get("response", "")
                        
                        self.logger.info(f"本地LLM提取成功，模式: {mode}")
                        return {
                            "success": True,
                            "mode": mode,
                            "provider": "local_llm",
                            "result": ai_response,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"本地LLM请求失败: {response.status} - {error_text}")
                        return {"error": f"本地LLM请求失败: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"本地LLM提取过程中发生错误: {e}")
            return {"error": str(e)}
    
    async def extract_with_qwen(self, content: str, mode: str = "structured_data") -> Dict[str, Any]:
        """
        使用通义千问进行数据提取
        
        Args:
            content: 要提取的内容
            mode: 提取模式
            
        Returns:
            提取结果
        """
        try:
            qwen_config = self.config.get("qwen", {})
            api_key = qwen_config.get("api_key")
            base_url = qwen_config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            model = qwen_config.get("model", "qwen-plus")
            
            if not api_key or api_key == "your-qwen-api-key-here":
                self.logger.warning("QWEN API密钥未配置，跳过AI提取")
                return {"error": "API密钥未配置"}
            
            # 获取提示词模板
            prompt_template = self.config.get("extraction", {}).get("prompts", {}).get(mode, "")
            if not prompt_template:
                prompt_template = "请分析以下内容：\n{content}"
            
            prompt = prompt_template.format(content=content[:4000])  # 限制内容长度
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": qwen_config.get("max_tokens", 2000),
                "temperature": qwen_config.get("temperature", 0.1)
            }
            
            # 确保URL格式正确
            if not base_url.endswith("/chat/completions"):
                if base_url.endswith("/"):
                    base_url = base_url + "chat/completions"
                else:
                    base_url = base_url + "/chat/completions"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        self.logger.info(f"QWEN提取成功，模式: {mode}")
                        return {
                            "success": True,
                            "mode": mode,
                            "provider": "qwen",
                            "result": ai_response,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"QWEN API请求失败: {response.status} - {error_text}")
                        return {"error": f"API请求失败: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"QWEN提取过程中发生错误: {e}")
            return {"error": str(e)}
    
    async def extract(self, content: str, mode: str = None, provider: str = None) -> Dict[str, Any]:
        """
        执行AI数据提取
        
        Args:
            content: 要提取的内容
            mode: 提取模式，如果为None则使用默认模式
            provider: LLM提供商，如果为None则使用默认提供商
            
        Returns:
            提取结果
        """
        if not mode:
            mode = self.config.get("extraction", {}).get("default_mode", "structured_data")
        
        if not provider:
            provider = self.config.get("default_provider", "openai")
        
        self.logger.info(f"🚀 开始AI提取 - 提供商: {provider}, 模式: {mode}, 内容长度: {len(content)}")
        
        # 根据提供商选择相应的提取方法
        if provider == "openai":
            result = await self.extract_with_openai(content, mode)
        elif provider == "local_llm":
            result = await self.extract_with_local_llm(content, mode)
        elif provider == "qwen":
            result = await self.extract_with_qwen(content, mode)
        else:
            error_msg = f"❌ 不支持的提供商: {provider}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # 记录提取结果
        if result.get("success"):
            self.logger.info(f"✅ AI提取成功 - 提供商: {provider}, 模式: {mode}")
        else:
            self.logger.error(f"❌ AI提取失败 - 提供商: {provider}, 错误: {result.get('error', '未知错误')}")
        
        return result
    
    def save_result(self, result: Dict[str, Any], filename: str = None) -> str:
        """
        保存提取结果到文件
        
        Args:
            result: 提取结果
            filename: 文件名，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                mode = result.get("mode", "unknown")
                filename = f"ai_extract_{mode}_{timestamp}.json"
            
            # 确保文件名以.json结尾
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"提取结果已保存到: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return ""
    
    def get_available_modes(self) -> List[str]:
        """获取可用的提取模式列表"""
        return list(self.config.get("extraction", {}).get("prompts", {}).keys())
    
    def get_available_providers(self) -> List[str]:
        """获取可用的LLM提供商列表"""
        providers = []
        
        # 检查各个提供商的配置
        if "openai" in self.config and self.config["openai"].get("api_key"):
            providers.append("openai")
        
        if "azure_openai" in self.config and self.config["azure_openai"].get("api_key"):
            providers.append("azure_openai")
            
        if "local_llm" in self.config:
            providers.append("local_llm")
            
        if "qwen" in self.config and self.config["qwen"].get("api_key"):
            providers.append("qwen")
        
        self.logger.info(f"📋 可用的LLM提供商: {providers}")
        return providers