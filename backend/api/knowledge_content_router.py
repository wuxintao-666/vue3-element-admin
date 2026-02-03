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
    graphId: Optional[str] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取知识内容分页列表
    """
    try:
        query = db.query(KnowledgeContentModel)

        if level is not None:
            query = query.filter(KnowledgeContentModel.level == level)

        if graphId:
            query = query.filter(KnowledgeContentModel.graph_id == graphId)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        contents = query.order_by(KnowledgeContentModel.create_time.desc()).offset(offset).limit(pageSize).all()

        content_list = [KnowledgeContentResponse.from_orm(content).dict(by_alias=True) for content in contents]

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
        new_content = KnowledgeContentModel(
            graph_id=content_data.graph_id,
            topic_id=content_data.topic_id,
            description=content_data.description,
            level=content_data.level
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
        for key, value in update_fields.items():
            # 处理字段名映射
            if key == "graphId":
                setattr(content, "graph_id", value)
            elif key == "maintainerId":
                setattr(content, "maintainer_id", value)
            else:
                setattr(content, key, value)

        content.update_time = datetime.now()
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
            # 检查是否已存在相同的数据（course_id, node_id, level 组合）
            # 将整数转换为枚举类型进行比较
            from db.models import DifficultyLevelEnum
            level_enum = DifficultyLevelEnum(content_item.level)

            existing = db.query(KnowledgeContentModel).filter(
                KnowledgeContentModel.course_id == course_id,
                KnowledgeContentModel.node_id == content_item.node_id,
                KnowledgeContentModel.level == level_enum
            ).first()

            if existing:
                # 更新现有记录
                existing.title = content_item.title
                existing.description = content_item.description
                existing.updated_at = datetime.now()
                logger.info(f"更新知识内容: course_id={course_id}, node_id={content_item.node_id}, level={content_item.level}")
            else:
                # 创建新记录
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