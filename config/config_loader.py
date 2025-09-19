"""
统一配置加载器模块
提供YAML配置文件的加载、验证和管理功能
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 导入配置验证器
from .config_validator import config_validator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = self._get_config_path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """加载YAML配置文件"""
        try:
            config = self.load_config()
            self._config = config
            logger.info(f"配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def _get_config_path(self, config_path: Optional[str] = None) -> Path:
        """获取配置文件的完整路径"""
        if config_path:
            return Path(config_path)
        
        # 默认配置文件路径
        current_dir = Path(__file__).parent
        config_path = current_dir / "app_config.yaml"
        
        if not config_path.exists():
            logger.warning(f"默认配置文件不存在: {config_path}")
        
        return config_path
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"✅ 成功加载配置文件: {self.config_path}")
                
                # 验证配置
                self._validate_config(config or {})
                
                return config or {}
        except FileNotFoundError:
            logger.error(f"❌ 配置文件不存在: {self.config_path}")
            raise ConfigError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            logger.error(f"❌ 配置文件格式错误: {e}")
            raise ConfigError(f"配置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"❌ 加载配置文件时发生未知错误: {e}")
            raise ConfigError(f"加载配置文件失败: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """
        验证配置文件内容
        
        Args:
            config: 配置字典
        """
        try:
            # 使用配置验证器进行验证
            is_valid = config_validator.validate_all(config)
            
            if not is_valid:
                errors = config_validator.get_errors()
                error_msg = "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
                logger.error(error_msg)
                raise ConfigError(error_msg)
            
            # 输出警告信息
            warnings = config_validator.get_warnings()
            if warnings:
                warning_msg = "配置验证警告:\n" + "\n".join(f"  - {warning}" for warning in warnings)
                logger.warning(warning_msg)
                
        except Exception as e:
            if isinstance(e, ConfigError):
                raise
            logger.error(f"配置验证过程中发生错误: {e}")
            raise ConfigError(f"配置验证失败: {e}")
    
    def get_config(self, section: str = None) -> Dict[str, Any]:
        """
        获取配置信息
        
        Args:
            section: 配置节名称，如果为None则返回全部配置
        
        Returns:
            配置字典
        """
        if self._config is None:
            raise RuntimeError("配置文件未加载")
        
        if section is None:
            return self._config
        
        if section not in self._config:
            raise KeyError(f"配置节不存在: {section}")
        
        return self._config[section]
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get_config('database')
    
    def get_minio_config(self) -> Dict[str, Any]:
        """获取MinIO配置"""
        return self.get_config('minio')
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.get_config('ai')
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return self.get_config('app')
    
    def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return self.get_config('server')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get_config('logging')
    
    def get_database_pool_config(self) -> Dict[str, Any]:
        """获取数据库连接池配置"""
        return self.get_nested_config('database.pool', {})
    
    def get_database_url(self) -> str:
        """构建数据库连接URL"""
        db_config = self.get_database_config()
        return (
            f"postgresql://{db_config['username']}:"
            f"{db_config['password']}@"
            f"{db_config['host']}:"
            f"{db_config['port']}/"
            f"{db_config['name']}"
        )
    
    def get_minio_endpoint(self) -> str:
        """获取MinIO端点URL"""
        minio_config = self.get_minio_config()
        protocol = "https" if minio_config.get('secure', False) else "http"
        return f"{protocol}://{minio_config['endpoint']}"
    
    def reload_config(self):
        """重新加载配置文件"""
        logger.info("重新加载配置文件...")
        self._load_config()
    
    def update_config(self, section: str, key: str, value: Any):
        """
        更新配置项（仅在内存中，不写入文件）
        
        Args:
            section: 配置节名称
            key: 配置键
            value: 配置值
        """
        if self._config is None:
            raise RuntimeError("配置文件未加载")
        
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
        logger.info(f"配置项已更新: {section}.{key} = {value}")
    
    def get_nested_config(self, path: str, default: Any = None) -> Any:
        """
        获取嵌套配置项
        
        Args:
            path: 配置路径，使用点号分隔，如 'database.pool.size'
            default: 默认值
        
        Returns:
            配置值
        """
        if self._config is None:
            raise RuntimeError("配置文件未加载")
        
        keys = path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"配置路径不存在: {path}")

# 全局配置加载器实例
config_loader = ConfigLoader()

def get_config(section: str = None) -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    
    Args:
        section: 配置节名称
    
    Returns:
        配置字典
    """
    return config_loader.get_config(section)

def get_database_config() -> Dict[str, Any]:
    """获取数据库配置的便捷函数"""
    return config_loader.get_database_config()

def get_minio_config() -> Dict[str, Any]:
    """获取MinIO配置的便捷函数"""
    return config_loader.get_minio_config()

def get_ai_config() -> Dict[str, Any]:
    """获取AI配置的便捷函数"""
    return config_loader.get_ai_config()

def get_database_url() -> str:
    """获取数据库连接URL的便捷函数"""
    return config_loader.get_database_url()

def get_minio_endpoint() -> str:
    """获取MinIO端点URL的便捷函数"""
    return config_loader.get_minio_endpoint()

if __name__ == "__main__":
    # 测试配置加载器
    try:
        print("🔧 测试配置加载器...")
        
        # 测试加载配置
        print(f"✅ 配置文件路径: {config_loader.config_path}")
        
        # 测试获取各种配置
        app_config = config_loader.get_app_config()
        print(f"✅ 应用名称: {app_config.get('name')}")
        
        db_url = config_loader.get_database_url()
        print(f"✅ 数据库URL: {db_url}")
        
        minio_endpoint = config_loader.get_minio_endpoint()
        print(f"✅ MinIO端点: {minio_endpoint}")
        
        # 测试嵌套配置获取
        pool_size = config_loader.get_nested_config('database.pool.size')
        print(f"✅ 数据库连接池大小: {pool_size}")
        
        print("🎉 配置加载器测试完成")
        
    except Exception as e:
        print(f"❌ 配置加载器测试失败: {e}")