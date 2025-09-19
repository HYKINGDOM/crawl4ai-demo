"""
数据库模型定义
定义所有数据库表的结构和关系
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from config.database_config import Base

class CrawlTask(Base):
    """爬取任务表"""
    __tablename__ = "crawl_tasks"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键ID")
    
    # 基本信息
    url = Column(String(2048), nullable=False, comment="原网页地址")
    content_source = Column(String(50), default="cleaned_html", comment="内容源类型")
    ai_modes = Column(Text, comment="AI分析模式，JSON格式存储")
    
    # 状态信息
    status = Column(String(20), default="pending", comment="任务状态：pending/processing/completed/failed")
    success = Column(Boolean, default=False, comment="是否成功完成")
    error_message = Column(Text, comment="错误信息")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    started_at = Column(DateTime, comment="开始处理时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    # 内容信息
    markdown_content = Column(Text, comment="生成的Markdown内容")
    ai_results = Column(Text, comment="AI分析结果，JSON格式存储")
    
    # 关联关系
    files = relationship("CrawlFile", back_populates="task", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_crawl_tasks_url', 'url'),
        Index('idx_crawl_tasks_status', 'status'),
        Index('idx_crawl_tasks_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<CrawlTask(id={self.id}, url='{self.url}', status='{self.status}')>"

class CrawlFile(Base):
    """爬取文件表"""
    __tablename__ = "crawl_files"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键ID")
    
    # 关联任务
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=False, comment="关联的爬取任务ID")
    
    # 文件基本信息
    filename = Column(String(255), nullable=False, comment="文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型：markdown/json/ai_result")
    file_size = Column(BigInteger, comment="文件大小（字节）")
    content_type = Column(String(100), comment="MIME类型")
    
    # MinIO存储信息
    minio_bucket = Column(String(100), nullable=False, comment="MinIO存储桶名称")
    minio_object_key = Column(String(500), nullable=False, comment="MinIO对象键")
    minio_url = Column(String(1000), comment="MinIO访问URL")
    
    # 本地存储信息（备份）
    local_path = Column(String(500), comment="本地文件路径")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    uploaded_at = Column(DateTime, comment="上传到MinIO的时间")
    
    # 元数据
    file_metadata = Column(Text, comment="文件元数据，JSON格式存储")
    
    # 关联关系
    task = relationship("CrawlTask", back_populates="files")
    
    # 索引
    __table_args__ = (
        Index('idx_crawl_files_task_id', 'task_id'),
        Index('idx_crawl_files_type', 'file_type'),
        Index('idx_crawl_files_created_at', 'created_at'),
        Index('idx_crawl_files_minio_key', 'minio_object_key'),
    )
    
    def __repr__(self):
        return f"<CrawlFile(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键ID")
    
    # 配置信息
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, comment="配置值")
    config_type = Column(String(20), default="string", comment="配置类型：string/int/float/bool/json")
    description = Column(String(500), comment="配置描述")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_system_config_key', 'config_key'),
    )
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"

class UserSession(Base):
    """用户会话表（可选，用于跟踪用户操作）"""
    __tablename__ = "user_sessions"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键ID")
    
    # 会话信息
    session_id = Column(String(100), unique=True, nullable=False, comment="会话ID")
    user_ip = Column(String(45), comment="用户IP地址")
    user_agent = Column(Text, comment="用户代理字符串")
    
    # 统计信息
    request_count = Column(Integer, default=0, comment="请求次数")
    last_activity = Column(DateTime, default=datetime.utcnow, comment="最后活动时间")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index('idx_user_sessions_session_id', 'session_id'),
        Index('idx_user_sessions_last_activity', 'last_activity'),
    )
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, session_id='{self.session_id}')>"

# 数据库初始化函数
def create_all_tables():
    """创建所有数据库表"""
    from config.database_config import db_manager
    try:
        Base.metadata.create_all(bind=db_manager.engine)
        print("✅ 所有数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return False

def drop_all_tables():
    """删除所有数据库表（谨慎使用）"""
    from config.database_config import db_manager
    try:
        Base.metadata.drop_all(bind=db_manager.engine)
        print("✅ 所有数据库表删除成功")
        return True
    except Exception as e:
        print(f"❌ 数据库表删除失败: {e}")
        return False

if __name__ == "__main__":
    # 测试创建表
    print("创建数据库表...")
    create_all_tables()