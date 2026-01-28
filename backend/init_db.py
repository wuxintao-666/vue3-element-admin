"""
初始化数据库
"""
from sqlalchemy import create_engine, text
from db.database import engine, Base
from db.models import User, Theme
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    """
    创建数据库和所有表
    """
    # 先连接到MySQL服务器，创建数据库
    mysql_admin_url = os.getenv("MYSQL_ADMIN_URL", "mysql+pymysql://root:123456@localhost:3306")
    mysql_engine = create_engine(mysql_admin_url)
    with mysql_engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS vue3_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
        print("数据库 vue3_admin 已创建或已存在")
    
    # 然后创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")

if __name__ == "__main__":
    init_db()
