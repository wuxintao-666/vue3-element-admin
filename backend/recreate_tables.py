"""
重新创建知识点内容表（修改id字段类型）
"""
from sqlalchemy import create_engine, text, MetaData
from db.database import engine
from db.models import KnowledgeContent
import os
from dotenv import load_dotenv

load_dotenv()

def recreate_knowledge_content_table():
    """
    删除并重新创建knowledge_contents表
    """
    try:
        # 使用MetaData来删除表
        meta = MetaData()
        meta.reflect(bind=engine)

        # 检查表是否存在
        if 'knowledge_contents' in meta.tables:
            print("删除现有的knowledge_contents表...")
            # 删除表
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE knowledge_contents"))
                conn.commit()
            print("表已删除")

        # 重新创建表
        print("重新创建knowledge_contents表...")
        KnowledgeContent.__table__.create(engine)
        print("表创建成功")

        # 验证表结构
        meta = MetaData()
        meta.reflect(bind=engine)
        knowledge_contents_table = meta.tables['knowledge_contents']

        print("\n新表结构:")
        for column in knowledge_contents_table.columns:
            print(f"  {column.name}: {column.type} {'(主键)' if column.primary_key else ''}")

    except Exception as e:
        print(f"重新创建表失败: {e}")

if __name__ == "__main__":
    recreate_knowledge_content_table()