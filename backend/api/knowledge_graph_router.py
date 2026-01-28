from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import uuid

from db.database import get_db
from db.models import KnowledgeGraph as KnowledgeGraphModel
from schemas.knowledge_graph_schema import (
    KnowledgeGraphCreate, KnowledgeGraphUpdate, KnowledgeGraphResponse,
    KnowledgeGraphPageQuery, KnowledgeGraphPageResponse, KnowledgeGraphData,
    ApiResponse
)

knowledge_graph_router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["Knowledge Graph"])

# logger
logger = logging.getLogger(__name__)


@knowledge_graph_router.get("/page", response_model=ApiResponse)
async def get_knowledge_graphs(
    keywords: Optional[str] = None,
    status: Optional[int] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取知识图谱分页列表
    """
    try:
        query = db.query(KnowledgeGraphModel)

        if keywords:
            query = query.filter(KnowledgeGraphModel.name.ilike(f"%{keywords}%"))

        if status is not None:
            query = query.filter(KnowledgeGraphModel.status == status)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        graphs = query.order_by(KnowledgeGraphModel.create_time.desc()).offset(offset).limit(pageSize).all()

        graph_list = [KnowledgeGraphResponse.from_orm(graph).dict(by_alias=True) for graph in graphs]

        return ApiResponse(
            code="00000",
            data={
                "list": graph_list,
                "total": total
            },
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取知识图谱列表失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取知识图谱列表失败: {str(e)}"
        )


@knowledge_graph_router.get("/{graph_id}/form", response_model=ApiResponse)
async def get_knowledge_graph_form(graph_id: str, db: Session = Depends(get_db)):
    """
    获取知识图谱详情（用于表单回显）
    """
    try:
        graph = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id == graph_id).first()

        if not graph:
            return ApiResponse(
                code="A0001",
                message="知识图谱不存在"
            )

        graph_data = KnowledgeGraphResponse.from_orm(graph)
        return ApiResponse(
            code="00000",
            data=graph_data.dict(by_alias=True),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取知识图谱详情失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取知识图谱详情失败: {str(e)}"
        )


@knowledge_graph_router.post("/", response_model=ApiResponse)
async def create_knowledge_graph(graph_data: KnowledgeGraphCreate, db: Session = Depends(get_db)):
    """
    创建知识图谱
    """
    try:
        # 检查ID是否已存在
        existing_graph = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id == graph_data.id).first()
        if existing_graph:
            return ApiResponse(
                code="A0001",
                message="知识图谱ID已存在"
            )

        new_graph = KnowledgeGraphModel(
            id=graph_data.id,
            name=graph_data.name,
            description=graph_data.description,
            tags=graph_data.tags,
            status=graph_data.status,
            maintainer_id=graph_data.maintainer_id
        )

        db.add(new_graph)
        db.commit()
        db.refresh(new_graph)

        return ApiResponse(
            code="00000",
            data={"id": new_graph.id},
            message="创建成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建知识图谱失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"创建知识图谱失败: {str(e)}"
        )


@knowledge_graph_router.put("/{graph_id}", response_model=ApiResponse)
async def update_knowledge_graph(graph_id: str, graph_data: KnowledgeGraphUpdate, db: Session = Depends(get_db)):
    """
    更新知识图谱
    """
    try:
        graph = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id == graph_id).first()

        if not graph:
            return ApiResponse(
                code="A0001",
                message="知识图谱不存在"
            )

        update_fields = graph_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            # 处理字段名映射
            if key == "maintainer_id":
                setattr(graph, "maintainer_id", value)
            else:
                setattr(graph, key, value)

        graph.update_time = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="更新成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新知识图谱失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"更新知识图谱失败: {str(e)}"
        )


@knowledge_graph_router.delete("/{graph_ids}", response_model=ApiResponse)
async def delete_knowledge_graphs(graph_ids: str, db: Session = Depends(get_db)):
    """
    删除知识图谱（支持批量删除，用逗号分隔）
    """
    try:
        ids = [id.strip() for id in graph_ids.split(",")]
        deleted_count = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        if deleted_count == 0:
            return ApiResponse(
                code="A0001",
                message="未找到要删除的知识图谱"
            )

        return ApiResponse(
            code="00000",
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除知识图谱失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除知识图谱失败: {str(e)}"
        )


@knowledge_graph_router.post("/{graph_id}/publish", response_model=ApiResponse)
async def publish_knowledge_graph(graph_id: str, db: Session = Depends(get_db)):
    """
    发布知识图谱
    """
    try:
        graph = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id == graph_id).first()

        if not graph:
            return ApiResponse(
                code="A0001",
                message="知识图谱不存在"
            )

        # 将状态设置为启用
        graph.status = 1
        graph.update_time = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="发布成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"发布知识图谱失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"发布知识图谱失败: {str(e)}"
        )


@knowledge_graph_router.get("/{graph_id}/graph", response_model=ApiResponse)
async def get_knowledge_graph_data(graph_id: str, db: Session = Depends(get_db)):
    """
    获取知识图谱的图数据（节点和边）
    """
    try:
        graph = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.id == graph_id).first()

        if not graph:
            return ApiResponse(
                code="A0001",
                message="知识图谱不存在"
            )

        # 这里应该从相关的节点和边表中获取数据
        # 目前返回空的图数据结构作为示例
        graph_data = KnowledgeGraphData(
            nodes=[],
            edges=[],
            dependent_edges=[]
        )

        return ApiResponse(
            code="00000",
            data=graph_data.dict(),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取知识图谱数据失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取知识图谱数据失败: {str(e)}"
        )