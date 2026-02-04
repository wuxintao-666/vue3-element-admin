from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from db.database import get_db
from db.models import KnowledgeContent as KnowledgeContentModel
from schemas.knowledge_content_schema import (
    KnowledgeContentCreate, KnowledgeContentUpdate, KnowledgeContentResponse,
    KnowledgeContentPageQuery, KnowledgeContentPageResponse, ApiResponse,
    KnowledgeContentBatchSave
)

knowledge_content_router = APIRouter(prefix="/api/v1/learning-content", tags=["Learning Content"])

# logger
logger = logging.getLogger(__name__)


@knowledge_content_router.get("/", response_model=ApiResponse)
async def get_knowledge_contents(
    level: Optional[int] = None,
    courseId: Optional[str] = None,
    nodeId: Optional[str] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取知识内容分页列表
    """
    try:
        # 根据course_code查询课程ID
        course_db_id = None
        if courseId:
            from db.models import Course
            course = db.query(Course).filter(Course.course_code == courseId).first()
            if course:
                course_db_id = course.id

        query = db.query(KnowledgeContentModel)

        if level is not None:
            from db.models import DifficultyLevelEnum
            query = query.filter(KnowledgeContentModel.level == DifficultyLevelEnum(level))

        if course_db_id is not None:
            query = query.filter(KnowledgeContentModel.course_id == course_db_id)

        if nodeId:
            query = query.filter(KnowledgeContentModel.node_id.ilike(f"%{nodeId}%"))

        total = query.count()
        offset = (pageNum - 1) * pageSize
        contents = query.order_by(KnowledgeContentModel.created_at.desc()).offset(offset).limit(pageSize).all()

        # 转换数据格式，添加course_code
        content_list = []
        for content in contents:
            content_dict = KnowledgeContentResponse.from_orm(content).dict(by_alias=True)
            # 添加course_code
            if course_db_id:
                from db.models import Course
                course = db.query(Course).filter(Course.id == content.course_id).first()
                if course:
                    content_dict['course_code'] = course.course_code
            content_list.append(content_dict)

        return ApiResponse(
            code="00000",
            data={
                "list": content_list,
                "total": total
            },
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取知识内容列表失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取知识内容列表失败: {str(e)}"
        )


@knowledge_content_router.get("/{content_id}", response_model=ApiResponse)
async def get_knowledge_content(content_id: str, db: Session = Depends(get_db)):
    """
    获取知识内容详情
    """
    try:
        content = db.query(KnowledgeContentModel).filter(KnowledgeContentModel.id == content_id).first()

        if not content:
            return ApiResponse(
                code="A0001",
                message="知识内容不存在"
            )

        content_data = KnowledgeContentResponse.from_orm(content)
        return ApiResponse(
            code="00000",
            data=content_data.dict(by_alias=True),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取知识内容详情失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取知识内容详情失败: {str(e)}"
        )


@knowledge_content_router.post("/", response_model=ApiResponse)
async def create_knowledge_content(content_data: KnowledgeContentCreate, db: Session = Depends(get_db)):
    """
    创建知识内容
    """
    try:
        # 根据course_code查找课程
        from db.models import Course
        course = db.query(Course).filter(Course.course_code == content_data.course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {content_data.course_id} 不存在"
            )

        # 检查节点是否存在于知识图谱中
        from db.models import KGNode
        node = db.query(KGNode).filter(
            KGNode.course_id == course.id,
            KGNode.id == content_data.node_id
        ).first()

        if not node:
            return ApiResponse(
                code="A0001",
                message=f"节点 '{content_data.node_id}' 在课程 '{content_data.course_id}' 的知识图谱中不存在"
            )

        # 检查是否已存在相同course_id、node_id和level的记录
        from db.models import DifficultyLevelEnum
        existing_content = db.query(KnowledgeContentModel).filter(
            KnowledgeContentModel.course_id == course.id,
            KnowledgeContentModel.node_id == content_data.node_id,
            KnowledgeContentModel.level == DifficultyLevelEnum(content_data.level)
        ).first()

        if existing_content:
            level_names = {1: "入门", 2: "基础", 3: "进阶", 4: "高级"}
            level_name = level_names.get(content_data.level, f"难度{content_data.level}")
            return ApiResponse(
                code="A0001",
                message=f"该课程的节点 '{content_data.node_id}' 已存在{level_name}级别的知识内容，不能重复创建"
            )

        from db.models import DifficultyLevelEnum
        new_content = KnowledgeContentModel(
            course_id=course.id,
            node_id=content_data.node_id,
            title=content_data.title,
            description=content_data.description,
            level=DifficultyLevelEnum(content_data.level)
        )

        db.add(new_content)
        db.commit()
        db.refresh(new_content)

        return ApiResponse(
            code="00000",
            data={"id": new_content.id},
            message="创建成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建知识内容失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"创建知识内容失败: {str(e)}"
        )


@knowledge_content_router.put("/{content_id}", response_model=ApiResponse)
async def update_knowledge_content(content_id: str, content_data: KnowledgeContentUpdate, db: Session = Depends(get_db)):
    """
    更新知识内容
    """
    try:
        content = db.query(KnowledgeContentModel).filter(KnowledgeContentModel.id == content_id).first()

        if not content:
            return ApiResponse(
                code="A0001",
                message="知识内容不存在"
            )

        update_fields = content_data.dict(exclude_unset=True)

        # 准备新的course_id、node_id和level用于验证
        new_course_id = content.course_id
        new_node_id = content.node_id
        new_level = content.level

        for key, value in update_fields.items():
            # 处理字段名映射
            if key == "course_id":
                # 根据course_code查找course_id
                from db.models import Course
                course = db.query(Course).filter(Course.course_code == value).first()
                if course:
                    new_course_id = course.id
                    setattr(content, "course_id", course.id)
                else:
                    return ApiResponse(
                        code="A0001",
                        message=f"课程代码 {value} 不存在"
                    )
            elif key == "node_id":
                new_node_id = value
                setattr(content, key, value)
            elif key == "level":
                # 将整数转换为枚举值
                from db.models import DifficultyLevelEnum
                new_level = DifficultyLevelEnum(value)
                setattr(content, key, new_level)
            else:
                setattr(content, key, value)

        # 检查更新后的节点是否存在于知识图谱中
        from db.models import KGNode
        node = db.query(KGNode).filter(
            KGNode.course_id == new_course_id,
            KGNode.id == new_node_id
        ).first()

        if not node:
            return ApiResponse(
                code="A0001",
                message=f"节点 '{new_node_id}' 在知识图谱中不存在，无法更新"
            )

        # 检查更新后的course_id、node_id和level组合是否与其他记录冲突（排除当前记录）
        if (new_course_id != content.course_id or new_node_id != content.node_id or new_level != content.level):
            existing = db.query(KnowledgeContentModel).filter(
                KnowledgeContentModel.course_id == new_course_id,
                KnowledgeContentModel.node_id == new_node_id,
                KnowledgeContentModel.level == new_level,
                KnowledgeContentModel.id != content_id
            ).first()

            if existing:
                level_names = {1: "入门", 2: "基础", 3: "进阶", 4: "高级"}
                level_name = level_names.get(new_level.value if hasattr(new_level, 'value') else int(new_level), f"难度{new_level}")
                return ApiResponse(
                    code="A0001",
                    message=f"该课程的节点 '{new_node_id}' 已存在{level_name}级别的其他知识内容，无法更新"
                )

        content.updated_at = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="更新成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新知识内容失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"更新知识内容失败: {str(e)}"
        )


@knowledge_content_router.delete("/{content_ids}", response_model=ApiResponse)
async def delete_knowledge_contents(content_ids: str, db: Session = Depends(get_db)):
    """
    删除知识内容（支持批量删除，用逗号分隔）
    """
    try:
        ids = [int(id.strip()) for id in content_ids.split(",")]
        deleted_count = db.query(KnowledgeContentModel).filter(KnowledgeContentModel.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        if deleted_count == 0:
            return ApiResponse(
                code="A0001",
                message="未找到要删除的知识内容"
            )

        return ApiResponse(
            code="00000",
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除知识内容失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除知识内容失败: {str(e)}"
        )


@knowledge_content_router.post("/batch-save", response_model=ApiResponse)
async def batch_save_knowledge_contents(batch_data: KnowledgeContentBatchSave, db: Session = Depends(get_db)):
    """
    批量保存知识点内容
    """
    try:
        # 根据course_code查询对应的course_id
        from db.models import Course as CourseModel
        course = db.query(CourseModel).filter(CourseModel.course_code == batch_data.course_id).first()

        if not course:
            return ApiResponse(
                code="A0001",
                message=f"找不到课程编码为 '{batch_data.course_id}' 的课程"
            )

        course_id = course.id
        saved_count = 0

        for content_item in batch_data.knowledge_contents:
            # 检查节点是否存在于知识图谱中
            from db.models import KGNode
            node = db.query(KGNode).filter(
                KGNode.course_id == course_id,
                KGNode.id == content_item.node_id
            ).first()

            if not node:
                logger.warning(f"跳过不存在的节点: course_id={course_id}, node_id={content_item.node_id}")
                continue

            # 检查是否已存在相同course_id、node_id和level的记录（不允许重复）
            from db.models import DifficultyLevelEnum
            existing = db.query(KnowledgeContentModel).filter(
                KnowledgeContentModel.course_id == course_id,
                KnowledgeContentModel.node_id == content_item.node_id,
                KnowledgeContentModel.level == DifficultyLevelEnum(content_item.level)
            ).first()

            if existing:
                # 记录已存在，跳过重复的记录
                level_names = {1: "入门", 2: "基础", 3: "进阶", 4: "高级"}
                level_name = level_names.get(content_item.level, f"难度{content_item.level}")
                logger.warning(f"跳过已存在的知识内容: course_id={course_id}, node_id={content_item.node_id}, level={level_name}")
                continue
            else:
                # 创建新记录
                level_enum = DifficultyLevelEnum(content_item.level)

                new_content = KnowledgeContentModel(
                    course_id=course_id,
                    node_id=content_item.node_id,
                    title=content_item.title,
                    description=content_item.description,
                    level=level_enum
                )
                db.add(new_content)
                logger.info(f"创建新知识内容: course_id={course_id}, node_id={content_item.node_id}, level={content_item.level}")
                saved_count += 1

        db.commit()

        return ApiResponse(
            code="00000",
            data={
                "saved_count": saved_count,
                "total_items": len(batch_data.knowledge_contents)
            },
            message=f"批量保存成功，共处理 {saved_count} 条记录"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"批量保存知识内容失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"批量保存知识内容失败: {str(e)}"
        )