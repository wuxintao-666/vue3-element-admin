from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from db.models import Course as CourseModel
from schemas.course_schema import (
    CourseCreate, CourseUpdate, CourseResponse,
    CoursePageQuery, CoursePageResponse, ApiResponse as CourseApiResponse
)

logger = logging.getLogger(__name__)

course_router = APIRouter(prefix="/api/v1/course")

# ===== 课程管理接口 =====

@course_router.post("", response_model=CourseApiResponse)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """
    创建课程
    """
    try:
        # 检查课程编码是否已存在
        existing_course = db.query(CourseModel).filter(CourseModel.course_code == course.course_code).first()
        if existing_course:
            return CourseApiResponse(code="A0001", message="课程编码已存在")

        # 创建新课程
        db_course = CourseModel(**course.dict())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)

        return CourseApiResponse(
            data=CourseResponse.from_orm(db_course).dict(),
            message="课程创建成功"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建课程失败: {str(e)}")


@course_router.get("", response_model=CourseApiResponse)
async def get_course_list(
    courseCode: str = None,
    courseName: str = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取课程列表（分页）
    """
    try:
        query = db.query(CourseModel)
        logger.info(f"courseCode: {courseCode}")
        logger.info(f"courseName: {courseName}")
        # 添加筛选条件
        if courseCode:
            query = query.filter(CourseModel.course_code.like(f"%{courseCode}%"))
        if courseName:
            query = query.filter(CourseModel.course_name.like(f"%{courseName}%"))

        # 分页查询
        total = query.count()
        courses = query.offset((pageNum - 1) * pageSize).limit(pageSize).all()

        return CourseApiResponse(
            data=CoursePageResponse(
                list=[CourseResponse.from_orm(course) for course in courses],
                total=total
            ).dict(),
            message="获取课程列表成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程列表失败: {str(e)}")


@course_router.get("/{course_id}", response_model=CourseApiResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取课程详情
    """
    try:
        course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return CourseApiResponse(code="A0002", message="课程不存在")

        return CourseApiResponse(
            data=CourseResponse.from_orm(course).dict(),
            message="获取课程成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程失败: {str(e)}")


@course_router.put("/{course_id}", response_model=CourseApiResponse)
async def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)):
    """
    更新课程信息
    """
    try:
        # 检查课程是否存在
        course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return CourseApiResponse(code="A0002", message="课程不存在")

        # 检查课程编码是否与其他课程冲突
        if course_update.course_code:
            existing_course = db.query(CourseModel).filter(
                CourseModel.course_code == course_update.course_code,
                CourseModel.id != course_id
            ).first()
            if existing_course:
                return CourseApiResponse(code="A0001", message="课程编码已存在")

        # 更新课程信息
        update_data = course_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        db.commit()
        db.refresh(course)

        return CourseApiResponse(
            data=CourseResponse.from_orm(course).dict(),
            message="课程更新成功"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新课程失败: {str(e)}")


@course_router.delete("/{course_id}", response_model=CourseApiResponse)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    删除课程
    """
    try:
        # 检查课程是否存在
        course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            return CourseApiResponse(code="A0002", message="课程不存在")

        # 删除课程
        db.delete(course)
        db.commit()

        return CourseApiResponse(message="课程删除成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除课程失败: {str(e)}")