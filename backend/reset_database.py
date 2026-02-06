"""
重置数据库 - 删除所有表并重新创建
用于数据库结构更新时使用
"""
from db.database import engine, Base
from sqlalchemy import MetaData, text

def reset_database():
    """
    删除所有表并重新创建
    """
    try:
        print("开始重置数据库...")

        # 获取所有表名
        meta = MetaData()
        meta.reflect(bind=engine)

        # 删除所有表（按依赖关系倒序删除）
        tables_to_drop = [
            'programming_exercise',
            'knowledge_content',
            'kg_edge',
            'kg_node',
            'course',
            'users',
            'admins'
        ]

        with engine.connect() as conn:
            # 禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

            # 删除表
            for table_name in tables_to_drop:
                if table_name in meta.tables:
                    print(f"删除表: {table_name}")
                    conn.execute(text(f"DROP TABLE {table_name}"))
                    conn.commit()

            # 重新启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        print("所有表已删除")

        # 重新创建所有表
        print("重新创建所有表...")
        Base.metadata.create_all(bind=engine)
        print("所有表创建成功")

        # 验证表结构
        meta = MetaData()
        meta.reflect(bind=engine)

        print("\n当前数据库中的表:")
        for table_name in meta.tables:
            table = meta.tables[table_name]
            print(f"\n表: {table_name}")
            for column in table.columns:
                print(f"  {column.name}: {column.type} {'(主键)' if column.primary_key else ''}")

    except Exception as e:
        print(f"重置数据库失败: {e}")
        raise

if __name__ == "__main__":
    reset_database()