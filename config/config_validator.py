"""
配置验证器模块
提供配置参数的验证、类型检查和错误处理功能
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """配置验证错误异常类"""
    pass

class ConfigValidator:
    """配置验证器类"""
    
    def __init__(self):
        """初始化配置验证器"""
        self.errors = []
        self.warnings = []
    
    def validate_all(self, config: Dict[str, Any]) -> bool:
        """
        验证所有配置项
        
        Args:
            config: 完整配置字典
        
        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            # 验证应用配置
            if 'app' in config:
                self._validate_app_config(config['app'])
            
            # 验证服务器配置
            if 'server' in config:
                self._validate_server_config(config['server'])
            
            # 验证数据库配置
            if 'database' in config:
                self._validate_database_config(config['database'])
            else:
                self.errors.append("缺少数据库配置节 'database'")
            
            # 验证MinIO配置
            if 'minio' in config:
                self._validate_minio_config(config['minio'])
            else:
                self.errors.append("缺少MinIO配置节 'minio'")
            
            # 验证AI配置
            if 'ai' in config:
                self._validate_ai_config(config['ai'])
            
            # 验证爬取配置
            if 'crawl' in config:
                self._validate_crawl_config(config['crawl'])
            
            # 验证日志配置
            if 'logging' in config:
                self._validate_logging_config(config['logging'])
            
            # 输出验证结果
            self._report_validation_results()
            
            return len(self.errors) == 0
            
        except Exception as e:
            logger.error(f"配置验证过程中发生错误: {e}")
            self.errors.append(f"验证过程异常: {str(e)}")
            return False
    
    def _validate_app_config(self, app_config: Dict[str, Any]):
        """验证应用配置"""
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in app_config:
                self.errors.append(f"应用配置缺少必要字段: {field}")
        
        # 验证版本格式
        if 'version' in app_config:
            version = app_config['version']
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                self.warnings.append(f"版本号格式建议使用语义化版本 (x.y.z): {version}")
    
    def _validate_server_config(self, server_config: Dict[str, Any]):
        """验证服务器配置"""
        # 验证端口号
        if 'port' in server_config:
            port = server_config['port']
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.errors.append(f"服务器端口号无效: {port}")
        
        # 验证工作进程数
        if 'workers' in server_config:
            workers = server_config['workers']
            if not isinstance(workers, int) or workers < 1:
                self.errors.append(f"工作进程数无效: {workers}")
        
        # 验证超时时间
        if 'timeout' in server_config:
            timeout = server_config['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                self.errors.append(f"服务器超时时间无效: {timeout}")
    
    def _validate_database_config(self, db_config: Dict[str, Any]):
        """验证数据库配置"""
        required_fields = ['host', 'port', 'name', 'username', 'password']
        for field in required_fields:
            if field not in db_config:
                self.errors.append(f"数据库配置缺少必要字段: {field}")
        
        # 验证端口号
        if 'port' in db_config:
            port = db_config['port']
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.errors.append(f"数据库端口号无效: {port}")
        
        # 验证主机地址
        if 'host' in db_config:
            host = db_config['host']
            if not self._is_valid_host(host):
                self.warnings.append(f"数据库主机地址格式可能有误: {host}")
        
        # 验证连接池配置
        if 'pool' in db_config:
            pool_config = db_config['pool']
            if 'size' in pool_config:
                size = pool_config['size']
                if not isinstance(size, int) or size < 1:
                    self.errors.append(f"数据库连接池大小无效: {size}")
            
            if 'max_overflow' in pool_config:
                overflow = pool_config['max_overflow']
                if not isinstance(overflow, int) or overflow < 0:
                    self.errors.append(f"数据库连接池最大溢出数无效: {overflow}")
    
    def _validate_minio_config(self, minio_config: Dict[str, Any]):
        """验证MinIO配置"""
        required_fields = ['endpoint', 'access_key', 'secret_key']
        for field in required_fields:
            if field not in minio_config:
                self.errors.append(f"MinIO配置缺少必要字段: {field}")
        
        # 验证端点格式
        if 'endpoint' in minio_config:
            endpoint = minio_config['endpoint']
            if not self._is_valid_endpoint(endpoint):
                self.errors.append(f"MinIO端点格式无效: {endpoint}")
        
        # 验证访问密钥
        if 'access_key' in minio_config:
            access_key = minio_config['access_key']
            if not access_key or len(access_key.strip()) == 0:
                self.errors.append("MinIO访问密钥不能为空")
        
        if 'secret_key' in minio_config:
            secret_key = minio_config['secret_key']
            if not secret_key or len(secret_key.strip()) == 0:
                self.errors.append("MinIO密钥不能为空")
        
        # 验证存储桶配置
        if 'buckets' in minio_config:
            buckets = minio_config['buckets']
            if not isinstance(buckets, dict):
                self.errors.append("MinIO存储桶配置必须是字典格式")
            else:
                for bucket_type, bucket_name in buckets.items():
                    if not self._is_valid_bucket_name(bucket_name):
                        self.errors.append(f"MinIO存储桶名称无效: {bucket_name}")
        
        # 验证上传配置
        if 'upload' in minio_config:
            upload_config = minio_config['upload']
            if 'max_file_size' in upload_config:
                max_size = upload_config['max_file_size']
                if not isinstance(max_size, (int, float)) or max_size <= 0:
                    self.errors.append(f"MinIO最大文件大小无效: {max_size}")
    
    def _validate_ai_config(self, ai_config: Dict[str, Any]):
        """验证AI配置"""
        # 验证默认提供商
        if 'default_provider' in ai_config:
            default_provider = ai_config['default_provider']
            available_providers = [key for key in ai_config.keys() if key != 'default_provider' and key != 'extraction']
            if default_provider not in available_providers:
                self.errors.append(f"默认AI提供商 '{default_provider}' 未在配置中定义")
        
        # 验证各个AI提供商配置
        providers = ['openai', 'azure_openai', 'local_llm', 'qwen']
        for provider in providers:
            if provider in ai_config:
                self._validate_ai_provider_config(provider, ai_config[provider])
    
    def _validate_ai_provider_config(self, provider: str, provider_config: Dict[str, Any]):
        """验证AI提供商配置"""
        # 验证API密钥（除了本地LLM）
        if provider != 'local_llm':
            if 'api_key' not in provider_config:
                self.warnings.append(f"{provider} 配置缺少API密钥")
            elif not provider_config['api_key'] or provider_config['api_key'].strip() == "":
                self.warnings.append(f"{provider} API密钥为空")
        
        # 验证基础URL
        if 'base_url' in provider_config:
            base_url = provider_config['base_url']
            if not self._is_valid_url(base_url):
                self.errors.append(f"{provider} 基础URL格式无效: {base_url}")
        
        # 验证模型参数
        if 'max_tokens' in provider_config:
            max_tokens = provider_config['max_tokens']
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                self.errors.append(f"{provider} 最大令牌数无效: {max_tokens}")
        
        if 'temperature' in provider_config:
            temperature = provider_config['temperature']
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                self.errors.append(f"{provider} 温度参数无效: {temperature}")
    
    def _validate_crawl_config(self, crawl_config: Dict[str, Any]):
        """验证爬取配置"""
        # 验证内容源类型
        if 'content_sources' in crawl_config:
            sources = crawl_config['content_sources']
            if not isinstance(sources, list):
                self.errors.append("爬取内容源类型必须是列表格式")
            else:
                valid_sources = ['cleaned_html', 'raw_html', 'fit_html']
                for source in sources:
                    if source not in valid_sources:
                        self.warnings.append(f"未知的内容源类型: {source}")
        
        # 验证超时配置
        if 'timeout' in crawl_config:
            timeout_config = crawl_config['timeout']
            for timeout_type, timeout_value in timeout_config.items():
                if not isinstance(timeout_value, (int, float)) or timeout_value <= 0:
                    self.errors.append(f"爬取{timeout_type}超时时间无效: {timeout_value}")
    
    def _validate_logging_config(self, logging_config: Dict[str, Any]):
        """验证日志配置"""
        # 验证日志级别
        if 'level' in logging_config:
            level = logging_config['level']
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level not in valid_levels:
                self.errors.append(f"日志级别无效: {level}")
        
        # 验证日志文件配置
        if 'files' in logging_config:
            files_config = logging_config['files']
            if not isinstance(files_config, dict):
                self.errors.append("日志文件配置必须是字典格式")
    
    def _is_valid_host(self, host: str) -> bool:
        """验证主机地址格式"""
        # 简单的IP地址或域名验证
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return re.match(ip_pattern, host) is not None or re.match(domain_pattern, host) is not None
    
    def _is_valid_endpoint(self, endpoint: str) -> bool:
        """验证端点格式"""
        # 检查是否包含主机和端口
        if ':' not in endpoint:
            return False
        
        parts = endpoint.split(':')
        if len(parts) != 2:
            return False
        
        host, port = parts
        try:
            port_num = int(port)
            return self._is_valid_host(host) and 1 <= port_num <= 65535
        except ValueError:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_valid_bucket_name(self, bucket_name: str) -> bool:
        """验证MinIO存储桶名称"""
        # MinIO存储桶命名规则
        if not bucket_name or len(bucket_name) < 3 or len(bucket_name) > 63:
            return False
        
        # 只能包含小写字母、数字和连字符
        pattern = r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$'
        return re.match(pattern, bucket_name) is not None
    
    def _report_validation_results(self):
        """报告验证结果"""
        if self.errors:
            logger.error("配置验证发现以下错误:")
            for i, error in enumerate(self.errors, 1):
                logger.error(f"  {i}. {error}")
        
        if self.warnings:
            logger.warning("配置验证发现以下警告:")
            for i, warning in enumerate(self.warnings, 1):
                logger.warning(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("✅ 配置验证通过，所有配置项都正确")
        elif not self.errors:
            logger.info("✅ 配置验证通过，但有一些警告需要注意")
        else:
            logger.error("❌ 配置验证失败，请修复上述错误")
    
    def get_errors(self) -> List[str]:
        """获取验证错误列表"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """获取验证警告列表"""
        return self.warnings.copy()

# 全局配置验证器实例
config_validator = ConfigValidator()

def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置的便捷函数
    
    Args:
        config: 配置字典
    
    Returns:
        验证是否通过
    """
    return config_validator.validate_all(config)

if __name__ == "__main__":
    # 测试配置验证器
    from .config_loader import config_loader
    
    try:
        print("🔍 测试配置验证器...")
        
        # 加载配置
        config = config_loader.get_config()
        
        # 验证配置
        is_valid = validate_config(config)
        
        if is_valid:
            print("🎉 配置验证测试完成 - 配置有效")
        else:
            print("⚠️ 配置验证测试完成 - 配置存在问题")
            
    except Exception as e:
        print(f"❌ 配置验证测试失败: {e}")