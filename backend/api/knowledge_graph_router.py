from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from db.database import get_db
from db.models import Course, KGNode, KGEdge, EdgeTypeEnum, NodeTypeEnum
from schemas.knowledge_graph_schema import KnowledgeGraphData, ApiResponse

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


@knowledge_graph_router.get("/course/{course_id}/graph", response_model=ApiResponse)
async def get_knowledge_graph_by_course(course_id: str, db: Session = Depends(get_db)):
    """
    根据课程ID获取知识图谱的图数据（节点和边）
    """
    try:
        # 根据course_id查找课程
        course = db.query(Course).filter(Course.course_code == course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {course_id} 不存在"
            )

        course_db_id = course.id

        # 获取该课程的所有节点
        nodes = db.query(KGNode).filter(KGNode.course_id == course_db_id).all()
        # 获取该课程的所有边
        edges = db.query(KGEdge).filter(KGEdge.course_id == course_db_id).all()

        # 按照 save_to_database 的格式构造返回数据
        nodes_data = []
        for node in nodes:
            node_dict = {
                "data": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type.value,  # 转换为字符串
                    "select_element": node.select_element or []
                }
            }
            nodes_data.append(node_dict)

        # 分离普通边和依赖边
        regular_edges_data = []
        dependent_edges_data = []

        for edge in edges:
            edge_dict = {
                "data": {
                    "source": edge.source_id,
                    "target": edge.target_id
                }
            }

            if edge.edge_type == EdgeTypeEnum.STRUCTURAL:
                regular_edges_data.append(edge_dict)
            elif edge.edge_type == EdgeTypeEnum.DEPENDENCY:
                dependent_edges_data.append(edge_dict)

        graph_data = KnowledgeGraphData(
            nodes=nodes_data,
            edges=regular_edges_data,
            dependent_edges=dependent_edges_data
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


@knowledge_graph_router.delete("/course/{course_id}/delete", response_model=ApiResponse)
async def delete_course_knowledge_graph(course_id: str, db: Session = Depends(get_db)):
    """
    删除指定课程的所有知识图谱数据（节点和边）
    """
    try:
        # 根据course_id查找课程
        course = db.query(Course).filter(Course.course_code == course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {course_id} 不存在"
            )

        course_db_id = course.id

        # 删除该课程的所有边数据（由于外键约束，必须先删除边）
        deleted_edges = db.query(KGEdge).filter(KGEdge.course_id == course_db_id).delete()
        # 删除该课程的所有节点数据
        deleted_nodes = db.query(KGNode).filter(KGNode.course_id == course_db_id).delete()

        # 提交事务
        db.commit()

        return ApiResponse(
            code="00000",
            data={
                "deleted_nodes": deleted_nodes,
                "deleted_edges": deleted_edges
            },
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除知识图谱数据失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除知识图谱数据失败: {str(e)}"
        )


@knowledge_graph_router.post("/course/{course_id}/import", response_model=ApiResponse)
async def import_knowledge_graph(course_id: str, import_data: dict, db: Session = Depends(get_db)):
    """
    导入知识图谱数据（JSON格式）
    """
    try:
        # 根据course_id查找课程
        course = db.query(Course).filter(Course.course_code == course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {course_id} 不存在"
            )

        course_db_id = course.id

        # 验证导入数据格式
        if not isinstance(import_data, dict):
            raise HTTPException(status_code=400, detail="数据格式错误：期望JSON对象")

        nodes = import_data.get("nodes", [])
        edges = import_data.get("edges", [])
        dependent_edges = import_data.get("dependent_edges", [])

        if not isinstance(nodes, list) or not isinstance(edges, list) or not isinstance(dependent_edges, list):
            raise HTTPException(status_code=400, detail="数据格式错误：nodes、edges、dependent_edges必须是数组")

        # 删除现有数据
        db.query(KGEdge).filter(KGEdge.course_id == course_db_id).delete()
        db.query(KGNode).filter(KGNode.course_id == course_db_id).delete()

        nodes_count = 0
        edges_count = 0

        # 导入节点数据
        for node_data in nodes:
            if not isinstance(node_data, dict) or "data" not in node_data:
                continue

            node_info = node_data["data"]
            if not all(key in node_info for key in ["id", "label", "type"]):
                continue

            # 验证节点类型
            node_type_str = node_info["type"]
            if node_type_str not in ["chapter", "knowledge"]:
                continue

            node = KGNode(
                id=node_info["id"],
                course_id=course_db_id,
                label=node_info["label"],
                type=NodeTypeEnum(node_type_str),
                select_element=node_info.get("select_element", [])
            )
            db.add(node)
            nodes_count += 1

        # 提交节点数据
        db.flush()

        # 导入普通边数据
        for edge_data in edges:
            if not isinstance(edge_data, dict) or "data" not in edge_data:
                continue

            edge_info = edge_data["data"]
            if not all(key in edge_info for key in ["source", "target"]):
                continue

            source_id = edge_info["source"]
            target_id = edge_info["target"]

            # 验证节点是否存在
            source_node = db.query(KGNode).filter(
                KGNode.course_id == course_db_id,
                KGNode.id == source_id
            ).first()
            target_node = db.query(KGNode).filter(
                KGNode.course_id == course_db_id,
                KGNode.id == target_id
            ).first()

            if not source_node or not target_node:
                continue

            edge = KGEdge(
                course_id=course_db_id,
                source_id=source_id,
                target_id=target_id,
                edge_type=EdgeTypeEnum.STRUCTURAL
            )
            db.add(edge)
            edges_count += 1

        # 导入依赖边数据
        for edge_data in dependent_edges:
            if not isinstance(edge_data, dict) or "data" not in edge_data:
                continue

            edge_info = edge_data["data"]
            if not all(key in edge_info for key in ["source", "target"]):
                continue

            source_id = edge_info["source"]
            target_id = edge_info["target"]

            # 验证节点是否存在
            source_node = db.query(KGNode).filter(
                KGNode.course_id == course_db_id,
                KGNode.id == source_id
            ).first()
            target_node = db.query(KGNode).filter(
                KGNode.course_id == course_db_id,
                KGNode.id == target_id
            ).first()

            if not source_node or not target_node:
                continue

            edge = KGEdge(
                course_id=course_db_id,
                source_id=source_id,
                target_id=target_id,
                edge_type=EdgeTypeEnum.DEPENDENCY
            )
            db.add(edge)
            edges_count += 1

        # 提交事务
        db.commit()

        return ApiResponse(
            code="00000",
            data={
                "nodes_count": nodes_count,
                "edges_count": edges_count
            },
            message="导入成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"导入知识图谱数据失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"导入知识图谱数据失败: {str(e)}"
        )