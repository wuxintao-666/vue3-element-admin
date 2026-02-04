from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from db.database import get_db
from db.models import ProgrammingExercise as ProgrammingExerciseModel, Course as CourseModel
from schemas.programming_exercise_schema import (
    ProgrammingExerciseCreate, ProgrammingExerciseUpdate, ProgrammingExerciseResponse,
    ProgrammingExercisePageQuery, ProgrammingExercisePageResponse, ApiResponse,
    ProgrammingExerciseBatchSave
)

programming_exercise_router = APIRouter(prefix="/api/v1/programming-exercises", tags=["Programming Exercises"])

# logger
logger = logging.getLogger(__name__)


@programming_exercise_router.get("/", response_model=ApiResponse)
async def get_programming_exercises(
    course_id: Optional[str] = None,
    node_id: Optional[str] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取编程练习题分页列表
    """
    try:
        query = db.query(ProgrammingExerciseModel)

        if course_id:
            # 根据course_code查找course_id
            course = db.query(CourseModel).filter(CourseModel.course_code == course_id).first()
            if course:
                query = query.filter(ProgrammingExerciseModel.course_id == course.id)

        if node_id:
            query = query.filter(ProgrammingExerciseModel.node_id == node_id)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        exercises = query.order_by(ProgrammingExerciseModel.created_at.desc()).offset(offset).limit(pageSize).all()

        exercise_list = [ProgrammingExerciseResponse.from_orm(exercise).dict(by_alias=True) for exercise in exercises]

        return ApiResponse(
            code="00000",
            data={
                "list": exercise_list,
                "total": total
            },
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取编程练习题列表失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取编程练习题列表失败: {str(e)}"
        )


@programming_exercise_router.get("/{exercise_id}", response_model=ApiResponse)
async def get_programming_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """
    获取编程练习题详情
    """
    try:
        exercise = db.query(ProgrammingExerciseModel).filter(ProgrammingExerciseModel.id == exercise_id).first()

        if not exercise:
            return ApiResponse(
                code="A0001",
                message="编程练习题不存在"
            )

        exercise_data = ProgrammingExerciseResponse.from_orm(exercise)
        return ApiResponse(
            code="00000",
            data=exercise_data.dict(by_alias=True),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取编程练习题详情失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取编程练习题详情失败: {str(e)}"
        )


@programming_exercise_router.post("/", response_model=ApiResponse)
async def create_programming_exercise(exercise_data: ProgrammingExerciseCreate, db: Session = Depends(get_db)):
    """
    创建编程练习题
    """
    try:
        # 根据course_code查询对应的course_id
        course = db.query(CourseModel).filter(CourseModel.course_code == exercise_data.course_id).first()

        if not course:
            return ApiResponse(
                code="A0001",
                message=f"找不到课程编码为 '{exercise_data.course_id}' 的课程"
            )

        course_id = course.id

        new_exercise = ProgrammingExerciseModel(
            course_id=course_id,
            node_id=exercise_data.node_id,
            title=exercise_data.title,
            description_md=exercise_data.description_md,
            start_code_html=exercise_data.start_code_html,
            start_code_css=exercise_data.start_code_css,
            start_code_js=exercise_data.start_code_js,
            checkpoints=exercise_data.checkpoints,
            answer_html=exercise_data.answer_html,
            answer_css=exercise_data.answer_css,
            answer_js=exercise_data.answer_js
        )

        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)

        return ApiResponse(
            code="00000",
            data={"id": new_exercise.id},
            message="创建成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建编程练习题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"创建编程练习题失败: {str(e)}"
        )


@programming_exercise_router.put("/{exercise_id}", response_model=ApiResponse)
async def update_programming_exercise(exercise_id: int, exercise_data: ProgrammingExerciseUpdate, db: Session = Depends(get_db)):
    """
    更新编程练习题
    """
    try:
        exercise = db.query(ProgrammingExerciseModel).filter(ProgrammingExerciseModel.id == exercise_id).first()

        if not exercise:
            return ApiResponse(
                code="A0001",
                message="编程练习题不存在"
            )

        update_fields = exercise_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(exercise, key, value)

        exercise.updated_at = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="更新成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新编程练习题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"更新编程练习题失败: {str(e)}"
        )


@programming_exercise_router.delete("/{exercise_ids}", response_model=ApiResponse)
async def delete_programming_exercises(exercise_ids: str, db: Session = Depends(get_db)):
    """
    删除编程练习题（支持批量删除，用逗号分隔）
    """
    try:
        ids = [int(id.strip()) for id in exercise_ids.split(",")]
        deleted_count = db.query(ProgrammingExerciseModel).filter(ProgrammingExerciseModel.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        if deleted_count == 0:
            return ApiResponse(
                code="A0001",
                message="未找到要删除的编程练习题"
            )

        return ApiResponse(
            code="00000",
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除编程练习题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除编程练习题失败: {str(e)}"
        )


@programming_exercise_router.post("/batch-save", response_model=ApiResponse)
async def batch_save_programming_exercises(batch_data: ProgrammingExerciseBatchSave, db: Session = Depends(get_db)):
    """
    批量保存编程练习题
    """
    try:
        # 验证course_id必须是TEST001
        if batch_data.course_id != "TEST001":
            return ApiResponse(
                code="A0001",
                message="课程编码必须是TEST001"
            )

        # 根据course_code查询对应的course_id
        course = db.query(CourseModel).filter(CourseModel.course_code == batch_data.course_id).first()

        if not course:
            return ApiResponse(
                code="A0001",
                message=f"找不到课程编码为 '{batch_data.course_id}' 的课程"
            )

        course_id = course.id
        saved_count = 0

        for exercise_item in batch_data.exercises:
            # 检查是否已存在相同的数据（course_id, node_id 组合）
            existing = db.query(ProgrammingExerciseModel).filter(
                ProgrammingExerciseModel.course_id == course_id,
                ProgrammingExerciseModel.node_id == exercise_item.node_id
            ).first()

            start_code = exercise_item.start_code
            answer = exercise_item.answer

            if existing:
                # 更新现有记录
                existing.title = exercise_item.title
                existing.description_md = exercise_item.description_md
                existing.start_code_html = start_code.get('html', '')
                existing.start_code_css = start_code.get('css', '')
                existing.start_code_js = start_code.get('js', '')
                existing.checkpoints = exercise_item.checkpoints
                existing.answer_html = answer.get('html', '')
                existing.answer_css = answer.get('css', '')
                existing.answer_js = answer.get('js', '')
                existing.updated_at = datetime.now()
                logger.info(f"更新编程练习题: course_id={course_id}, node_id={exercise_item.node_id}")
            else:
                # 创建新记录
                new_exercise = ProgrammingExerciseModel(
                    course_id=course_id,
                    node_id=exercise_item.node_id,
                    title=exercise_item.title,
                    description_md=exercise_item.description_md,
                    start_code_html=start_code.get('html', ''),
                    start_code_css=start_code.get('css', ''),
                    start_code_js=start_code.get('js', ''),
                    checkpoints=exercise_item.checkpoints,
                    answer_html=answer.get('html', ''),
                    answer_css=answer.get('css', ''),
                    answer_js=answer.get('js', '')
                )
                db.add(new_exercise)
                logger.info(f"创建新编程练习题: course_id={course_id}, node_id={exercise_item.node_id}")

            saved_count += 1

        db.commit()

        return ApiResponse(
            code="00000",
            data={
                "saved_count": saved_count,
                "total_items": len(batch_data.exercises)
            },
            message=f"批量保存成功，共处理 {saved_count} 条记录"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"批量保存编程练习题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"批量保存编程练习题失败: {str(e)}"
        )