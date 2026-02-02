#!/usr/bin/env python3
"""
删除测试课程及相关数据
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.db.database import SessionLocal
from backend.db.models import Course, KGNode, KGEdge

def delete_test_course():
    db = SessionLocal()
    try:
        # 根据course_code查找课程
        course = db.query(Course).filter(Course.course_code == "TEST001").first()

        if not course:
            print("❌ 课程 TEST001 不存在")
            return False

        print(f"找到课程: {course.course_name} (ID: {course.id})")

        # 统计相关数据
        nodes_count = db.query(KGNode).filter(KGNode.course_id == course.id).count()
        edges_count = db.query(KGEdge).filter(KGEdge.course_id == course.id).count()

        print(f"相关数据: {nodes_count} 个节点, {edges_count} 条边")

        # 删除边数据（由于外键约束，必须先删除边）
        deleted_edges = db.query(KGEdge).filter(KGEdge.course_id == course.id).delete()
        print(f"已删除 {deleted_edges} 条边")

        # 删除节点数据
        deleted_nodes = db.query(KGNode).filter(KGNode.course_id == course.id).delete()
        print(f"已删除 {deleted_nodes} 个节点")

        # 删除课程
        db.delete(course)
        print("已删除课程")

        # 提交事务
        db.commit()

        print("✅ 级联删除完成！")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ 删除失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = delete_test_course()
    if success:
        print("\n提示: 如果需要重新创建测试课程，请运行:")
        print("python create_test_course.py")