#!/usr/bin/env python3
"""
创建测试课程数据
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.db.database import SessionLocal
from backend.db.models import Course

def create_test_course():
    db = SessionLocal()
    try:
        # 检查是否已存在测试课程
        existing_course = db.query(Course).filter(Course.course_code == "TEST001").first()
        if existing_course:
            print(f"测试课程已存在: {existing_course.course_name} (ID: {existing_course.id})")
            return existing_course.id

        # 创建测试课程
        test_course = Course(
            course_code="TEST001",
            course_name="测试课程",
            description="用于测试知识图谱保存功能的课程"
        )

        db.add(test_course)
        db.commit()
        db.refresh(test_course)

        print(f"✅ 测试课程创建成功: {test_course.course_name} (ID: {test_course.id})")
        return test_course.id

    except Exception as e:
        db.rollback()
        print(f"❌ 创建测试课程失败: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    course_id = create_test_course()
    if course_id:
        print(f"可以使用课程ID: {course_id} 进行测试")