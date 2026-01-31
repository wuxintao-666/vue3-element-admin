"""
初始化数据库
"""
from sqlalchemy import create_engine, text
from db.database import engine, Base
from db.models import User, Theme, KnowledgeContent, KnowledgeGraph
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    """
    创建数据库和所有表
    """
    try:
        # 先连接到PostgreSQL服务器，创建数据库
        # 注意：CREATE DATABASE 不能在事务中执行，需要使用autocommit
        pg_admin_url = os.getenv("PG_ADMIN_URL", "postgresql://postgres:123456@localhost:5432/postgres")
        pg_engine = create_engine(pg_admin_url, isolation_level="AUTOCOMMIT")
        with pg_engine.connect() as conn:
            conn.execute(text("CREATE DATABASE vue3_admin WITH ENCODING 'UTF8'"))
            print("数据库 vue3_admin 已创建")
    except Exception as e:
        # 如果数据库已存在，会抛出异常，我们忽略它
        if "already exists" in str(e).lower() or "exists" in str(e).lower():
            print("数据库 vue3_admin 已存在")
        else:
            print(f"创建数据库时出错: {e}")
            raise

    # 然后创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")

if __name__ == "__main__":
    init_db()
