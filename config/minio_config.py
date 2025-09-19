"""
MinIO对象存储配置和管理模块
提供MinIO存储服务的连接管理和文件操作功能
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, BinaryIO
from minio import Minio
from minio.error import S3Error
from urllib.parse import urljoin
import hashlib
import json

# 导入统一配置加载器
from .config_loader import config_loader

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinIOManager:
    """MinIO存储管理器类"""
    
    def __init__(self):
        """初始化MinIO管理器"""
        self.client = None
        # 从统一配置文件获取MinIO配置
        self.minio_config = config_loader.get_minio_config()
        self.base_url = config_loader.get_minio_endpoint()
        self._initialize_client()
        self._ensure_buckets_exist()
    
    def _initialize_client(self):
        """初始化MinIO客户端"""
        try:
            self.client = Minio(
                endpoint=self.minio_config['endpoint'],
                access_key=self.minio_config['access_key'],
                secret_key=self.minio_config['secret_key'],
                secure=self.minio_config.get('secure', False),
                region=self.minio_config.get('region', 'us-east-1')
            )
            logger.info("MinIO客户端初始化成功")
        except Exception as e:
            logger.error(f"MinIO客户端初始化失败: {e}")
            raise
    
    def _ensure_buckets_exist(self):
        """确保所有必要的存储桶存在"""
        try:
            # 从配置文件获取存储桶配置
            bucket_config = self.minio_config.get('buckets', {})
            for bucket_name in bucket_config.values():
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logger.info(f"创建存储桶: {bucket_name}")
                else:
                    logger.info(f"存储桶已存在: {bucket_name}")
        except Exception as e:
            logger.error(f"创建存储桶失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试MinIO连接"""
        try:
            # 尝试列出存储桶
            buckets = self.client.list_buckets()
            logger.info(f"MinIO连接测试成功，找到 {len(buckets)} 个存储桶")
            return True
        except Exception as e:
            logger.error(f"MinIO连接测试失败: {e}")
            return False
    
    def upload_file(self, 
                   file_path: str, 
                   object_name: str, 
                   bucket_name: str = None,
                   content_type: str = None) -> Tuple[bool, str, dict]:
        """
        上传文件到MinIO
        
        Args:
            file_path: 本地文件路径
            object_name: MinIO对象名称
            bucket_name: 存储桶名称，默认使用default_bucket
            content_type: 文件MIME类型
        
        Returns:
            (成功标志, MinIO URL, 文件信息)
        """
        if bucket_name is None:
            bucket_config = self.minio_config.get('buckets', {})
            bucket_name = bucket_config.get('default', 'crawl4ai-files')
        
        try:
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            
            # 自动检测content_type
            if content_type is None:
                if file_path.endswith('.md'):
                    content_type = 'text/markdown'
                elif file_path.endswith('.json'):
                    content_type = 'application/json'
                elif file_path.endswith('.txt'):
                    content_type = 'text/plain'
                else:
                    content_type = 'application/octet-stream'
            
            # 上传文件
            result = self.client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
            
            # 构建访问URL
            file_url = f"{self.base_url}/{bucket_name}/{object_name}"
            
            # 文件信息
            file_info = {
                'bucket': bucket_name,
                'object_key': object_name,
                'size': file_size,
                'content_type': content_type,
                'etag': result.etag,
                'url': file_url,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"文件上传成功: {file_path} -> {file_url}")
            return True, file_url, file_info
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return False, "", {}
    
    def upload_content(self, 
                      content: str, 
                      object_name: str, 
                      bucket_name: str = None,
                      content_type: str = 'text/plain') -> Tuple[bool, str, dict]:
        """
        上传文本内容到MinIO
        
        Args:
            content: 文本内容
            object_name: MinIO对象名称
            bucket_name: 存储桶名称
            content_type: 内容MIME类型
        
        Returns:
            (成功标志, MinIO URL, 文件信息)
        """
        if bucket_name is None:
            bucket_config = self.minio_config.get('buckets', {})
            bucket_name = bucket_config.get('default', 'crawl4ai-files')
        
        try:
            # 将内容转换为字节
            content_bytes = content.encode('utf-8')
            content_size = len(content_bytes)
            
            # 创建内存中的文件对象
            from io import BytesIO
            content_stream = BytesIO(content_bytes)
            
            # 上传内容
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=content_stream,
                length=content_size,
                content_type=content_type
            )
            
            # 构建访问URL
            file_url = f"{self.base_url}/{bucket_name}/{object_name}"
            
            # 文件信息
            file_info = {
                'bucket': bucket_name,
                'object_key': object_name,
                'size': content_size,
                'content_type': content_type,
                'etag': result.etag,
                'url': file_url,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"内容上传成功: {object_name} -> {file_url}")
            return True, file_url, file_info
            
        except Exception as e:
            logger.error(f"内容上传失败: {e}")
            return False, "", {}
    
    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> bool:
        """
        从MinIO下载文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: MinIO对象名称
            file_path: 本地保存路径
        
        Returns:
            成功标志
        """
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"文件下载成功: {bucket_name}/{object_name} -> {file_path}")
            return True
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return False
    
    def get_file_content(self, bucket_name: str, object_name: str) -> Optional[str]:
        """
        获取文件内容（文本文件）
        
        Args:
            bucket_name: 存储桶名称
            object_name: MinIO对象名称
        
        Returns:
            文件内容字符串
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            content = response.read().decode('utf-8')
            response.close()
            response.release_conn()
            return content
        except Exception as e:
            logger.error(f"获取文件内容失败: {e}")
            return None
    
    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """
        删除MinIO中的文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: MinIO对象名称
        
        Returns:
            成功标志
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"文件删除成功: {bucket_name}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def list_files(self, bucket_name: str, prefix: str = "") -> List[dict]:
        """
        列出存储桶中的文件
        
        Args:
            bucket_name: 存储桶名称
            prefix: 对象名称前缀
        
        Returns:
            文件信息列表
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            files = []
            for obj in objects:
                file_info = {
                    'object_name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                    'etag': obj.etag,
                    'url': f"{self.base_url}/{bucket_name}/{obj.object_name}"
                }
                files.append(file_info)
            return files
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    def generate_presigned_url(self, 
                              bucket_name: str, 
                              object_name: str, 
                              expires: timedelta = timedelta(hours=1)) -> Optional[str]:
        """
        生成预签名URL（用于临时访问）
        
        Args:
            bucket_name: 存储桶名称
            object_name: MinIO对象名称
            expires: 过期时间
        
        Returns:
            预签名URL
        """
        try:
            url = self.client.presigned_get_object(bucket_name, object_name, expires)
            return url
        except Exception as e:
            logger.error(f"生成预签名URL失败: {e}")
            return None
    
    def get_file_info(self, bucket_name: str, object_name: str) -> Optional[dict]:
        """
        获取文件信息
        
        Args:
            bucket_name: 存储桶名称
            object_name: MinIO对象名称
        
        Returns:
            文件信息字典
        """
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            file_info = {
                'object_name': object_name,
                'size': stat.size,
                'last_modified': stat.last_modified.isoformat() if stat.last_modified else None,
                'etag': stat.etag,
                'content_type': stat.content_type,
                'metadata': stat.metadata,
                'url': f"{self.base_url}/{bucket_name}/{object_name}"
            }
            return file_info
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None

# 全局MinIO管理器实例
minio_manager = MinIOManager()

def get_bucket_for_file_type(file_type: str) -> str:
    """根据文件类型获取对应的存储桶"""
    # 从统一配置文件获取存储桶配置
    minio_config = config_loader.get_minio_config()
    bucket_config = minio_config.get('buckets', {})
    
    bucket_mapping = {
        'markdown': bucket_config.get('markdown', 'crawl4ai-markdown'),
        'json': bucket_config.get('json', 'crawl4ai-json'),
        'ai_result': bucket_config.get('ai_results', 'crawl4ai-ai-results')
    }
    return bucket_mapping.get(file_type, bucket_config.get('default', 'crawl4ai-files'))

def generate_object_key(filename: str, task_id: int = None, timestamp: str = None) -> str:
    """生成MinIO对象键"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if task_id:
        return f"task_{task_id}/{timestamp}/{filename}"
    else:
        return f"{timestamp}/{filename}"

if __name__ == "__main__":
    # 测试MinIO连接
    print("测试MinIO连接...")
    if minio_manager.test_connection():
        print("✅ MinIO连接成功")
        
        # 列出所有存储桶
        try:
            buckets = minio_manager.client.list_buckets()
            print(f"📦 找到 {len(buckets)} 个存储桶:")
            for bucket in buckets:
                print(f"  - {bucket.name} (创建时间: {bucket.creation_date})")
        except Exception as e:
            print(f"❌ 列出存储桶失败: {e}")
    else:
        print("❌ MinIO连接失败")