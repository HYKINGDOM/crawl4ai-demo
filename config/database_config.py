"""
数据库配置和连接管理模块
提供PostgreSQL数据库的连接管理和配置
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2 import sql

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_CONFIG = {
    'host': '10.0.203.172',
    'port': 5432,
    'database': 'user_tZGjBb',
    'username': 'user_tZGjBb',
    'password': 'password_fajJed'
}

# SQLAlchemy 基类
Base = declarative_base()

class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化数据库连接"""
        try:
            # 构建数据库连接URL
            database_url = (
                f"postgresql://{DATABASE_CONFIG['username']}:"
                f"{DATABASE_CONFIG['password']}@"
                f"{DATABASE_CONFIG['host']}:"
                f"{DATABASE_CONFIG['port']}/"
                f"{DATABASE_CONFIG['database']}"
            )
            
            # 创建数据库引擎
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # 设置为True可以看到SQL语句
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.SessionLocal:
            raise RuntimeError("数据库连接未初始化")
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("数据库连接测试成功")
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    def drop_tables(self):
        """删除所有表（谨慎使用）"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("数据库表删除成功")
        except Exception as e:
            logger.error(f"数据库表删除失败: {e}")
            raise
    
    def execute_raw_sql(self, sql_query: str, params: dict = None) -> list:
        """执行原始SQL查询"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql_query), params or {})
                if result.returns_rows:
                    return result.fetchall()
                return []
        except Exception as e:
            logger.error(f"SQL查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()

def get_db() -> Session:
    """获取数据库会话的依赖注入函数"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库"""
    try:
        # 测试连接
        if not db_manager.test_connection():
            raise RuntimeError("数据库连接失败")
        
        # 创建表
        db_manager.create_tables()
        
        logger.info("数据库初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

if __name__ == "__main__":
    # 测试数据库连接
    print("测试数据库连接...")
    if db_manager.test_connection():
        print("✅ 数据库连接成功")
    else:
        print("❌ 数据库连接失败")