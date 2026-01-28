from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from db.database import get_db
from db.models import KnowledgeContent as KnowledgeContentModel
from schemas.knowledge_content_schema import (
    KnowledgeContentCreate, KnowledgeContentUpdate, KnowledgeContentResponse,
    KnowledgeContentPageQuery, KnowledgeContentPageResponse, ApiResponse
)

knowledge_content_router = APIRouter(prefix="/api/v1/learning-content", tags=["Learning Content"])

# logger
logger = logging.getLogger(__name__)


@knowledge_content_router.get("/", response_model=ApiResponse)
async def get_knowledge_contents(
    level: Optional[int] = None,
    graph_id: Optional[str] = None,
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

        if graph_id:
            query = query.filter(KnowledgeContentModel.graph_id == graph_id)

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
async def get_knowledge_content(content_id: int, db: Session = Depends(get_db)):
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
async def update_knowledge_content(content_id: int, content_data: KnowledgeContentUpdate, db: Session = Depends(get_db)):
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
            if key == "graph_id":
                setattr(content, "graph_id", value)
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