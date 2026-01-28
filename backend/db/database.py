"""
数据库配置和连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# MySQL数据库配置
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/vue3_admin"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=False  # 是否打印SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """
    依赖注入：获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
