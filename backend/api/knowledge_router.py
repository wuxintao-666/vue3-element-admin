from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from agents.fast_mind import FastMind
from executor.execution_context import ExecutionContext
from db.database import get_db
from db.models import KGNode, KGEdge, NodeTypeEnum, EdgeTypeEnum, Course
import urllib.parse

knowledge_router = APIRouter()

class ReferenceInfo(BaseModel):
    title: str
    structure: List[Dict[str, Any]]
    text_blocks: List[str]

class KnowledgeExtractRequest(BaseModel):
    reference_url: Optional[str] = None
    reference_info: Optional[ReferenceInfo] = None

class KnowledgeExtractResponse(BaseModel):
    graph: dict
    status: str

class KnowledgeSaveRequest(BaseModel):
    name: str
    graph: dict

class KnowledgeSaveResponse(BaseModel):
    id: str
    name: str
    created_at: str

class KnowledgeSaveToDatabaseRequest(BaseModel):
    course_code: str  # 使用course_code而不是course_id
    name: str
    graph: dict

class KnowledgeSaveToDatabaseResponse(BaseModel):
    course_code: str  # 返回course_code而不是course_id
    name: str
    nodes_count: int
    edges_count: int
    created_at: str

class KnowledgeListItem(BaseModel):
    id: str
    name: str
    created_at: str

class KnowledgeListResponse(BaseModel):
    knowledge_graphs: List[KnowledgeListItem]

@knowledge_router.post("/extract", response_model=KnowledgeExtractResponse)
async def extract_knowledge(extract_request: KnowledgeExtractRequest):
    """
    从参考网站URL或参考信息中提取知识点
    
    参数：
    - reference_url: 参考网站URL
    - reference_info: 参考信息
    """
    try:
        # 初始化AI执行上下文
        context = ExecutionContext()
        fast_mind = FastMind(context)
        
        # 根据提供的参数提取知识点
        if extract_request.reference_url:
            # 基于URL提取知识点
            knowledge_data = fast_mind.extract_knowledge_points(extract_request.reference_url)
        else:
            raise HTTPException(status_code=422, detail="必须提供参考URL或参考信息")
        
        return KnowledgeExtractResponse(
            graph=knowledge_data,
            status="success"
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识点提取失败: {str(e)}")

@knowledge_router.post("/save", response_model=KnowledgeSaveResponse)
async def save_knowledge_graph(knowledge_data: KnowledgeSaveRequest):
    """保存知识点图谱"""
    # 创建知识点目录
    knowledge_dir = os.path.join("data", "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    
    # 生成唯一ID
    knowledge_id = str(uuid.uuid4())
    file_path = os.path.join(knowledge_dir, f"{knowledge_id}.json")
    
    # 创建知识点数据
    knowledge_record = {
        "id": knowledge_id,
        "name": knowledge_data.name,
        "graph": knowledge_data.graph,
        "created_at": datetime.now().isoformat()
    }
    
    # 保存到文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_record, f, ensure_ascii=False, indent=2)
    
    return KnowledgeSaveResponse(
        id=knowledge_id,
        name=knowledge_data.name,
        created_at=knowledge_record["created_at"]
    )

@knowledge_router.post("/save_to_database", response_model=KnowledgeSaveToDatabaseResponse)
async def save_knowledge_graph_to_database(
    knowledge_data: KnowledgeSaveToDatabaseRequest,
    db: Session = Depends(get_db)
):
    """
    将知识图谱保存到数据库（kg_node 和 kg_edge 表）
    """
    try:
        course_code = knowledge_data.course_code
        graph_data = knowledge_data.graph

        # 根据course_code查找课程
        course = db.query(Course).filter(Course.course_code == course_code).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"课程代码 {course_code} 不存在")

        course_id = course.id

        # 删除该课程原有的节点和边数据
        db.query(KGEdge).filter(KGEdge.course_id == course_id).delete()
        db.query(KGNode).filter(KGNode.course_id == course_id).delete()

        nodes_count = 0
        edges_count = 0

        # 保存节点数据
        if "nodes" in graph_data and graph_data["nodes"]:
            for idx, node_data in enumerate(graph_data["nodes"]):
                # 验证节点类型
                node_type_str = node_data["data"]["type"]
                if node_type_str not in ["chapter", "knowledge"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"无效的节点类型: {node_type_str}，只允许 'chapter' 或 'knowledge'"
                    )

                node = KGNode(
                    id=node_data["data"]["id"],
                    course_id=course_id,
                    label=node_data["data"]["label"],
                    type=NodeTypeEnum(node_type_str),
                    select_element=node_data["data"].get("select_element", [])
                )
                db.add(node)
                nodes_count += 1
                print(f"准备插入节点: course_id={course_id}, id={node_data['data']['id']}, label={node_data['data']['label']}")

        # 在插入边之前，先提交节点数据，确保节点存在于数据库中
        db.flush()
        print(f"节点数据已刷新到数据库，共 {nodes_count} 个节点")

        # 保存普通边数据
        if "edges" in graph_data and graph_data["edges"]:
            for edge_data in graph_data["edges"]:
                source_id = edge_data["data"]["source"]
                target_id = edge_data["data"]["target"]

                # 验证源节点和目标节点是否存在
                source_node = db.query(KGNode).filter(
                    KGNode.course_id == course_id,
                    KGNode.id == source_id
                ).first()
                target_node = db.query(KGNode).filter(
                    KGNode.course_id == course_id,
                    KGNode.id == target_id
                ).first()

                if not source_node:
                    raise HTTPException(
                        status_code=400,
                        detail=f"源节点不存在: course_id={course_id}, node_id={source_id}"
                    )
                if not target_node:
                    raise HTTPException(
                        status_code=400,
                        detail=f"目标节点不存在: course_id={course_id}, node_id={target_id}"
                    )

                print(f"准备插入普通边: course_id={course_id}, source={source_id}, target={target_id}")
                edge = KGEdge(
                    course_id=course_id,
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=EdgeTypeEnum.STRUCTURAL  # 普通边
                )
                db.add(edge)
                edges_count += 1

        # 保存依赖边数据
        if "dependent_edges" in graph_data and graph_data["dependent_edges"]:
            for edge_data in graph_data["dependent_edges"]:
                source_id = edge_data["data"]["source"]
                target_id = edge_data["data"]["target"]

                # 验证源节点和目标节点是否存在
                source_node = db.query(KGNode).filter(
                    KGNode.course_id == course_id,
                    KGNode.id == source_id
                ).first()
                target_node = db.query(KGNode).filter(
                    KGNode.course_id == course_id,
                    KGNode.id == target_id
                ).first()

                if not source_node:
                    raise HTTPException(
                        status_code=400,
                        detail=f"源节点不存在: course_id={course_id}, node_id={source_id}"
                    )
                if not target_node:
                    raise HTTPException(
                        status_code=400,
                        detail=f"目标节点不存在: course_id={course_id}, node_id={target_id}"
                    )

                print(f"准备插入依赖边: course_id={course_id}, source={source_id}, target={target_id}")
                edge = KGEdge(
                    course_id=course_id,
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=EdgeTypeEnum.DEPENDENCY  # 依赖边
                )
                db.add(edge)
                edges_count += 1

        # 提交事务
        db.commit()

        return KnowledgeSaveToDatabaseResponse(
            course_code=course_code,
            name=knowledge_data.name,
            nodes_count=nodes_count,
            edges_count=edges_count,
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存知识图谱到数据库失败: {str(e)}")

@knowledge_router.get("/", response_model=KnowledgeListResponse)
async def list_knowledge_graphs():
    """获取知识点图谱列表"""
    knowledge_dir = os.path.join("data", "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    
    knowledge_graphs = []
    if os.path.exists(knowledge_dir):
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(knowledge_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        knowledge_data = json.load(f)
                        knowledge_graphs.append(KnowledgeListItem(
                            id=knowledge_data["id"],
                            name=knowledge_data["name"],
                            created_at=knowledge_data["created_at"]
                        ))
                except Exception:
                    continue
    
    return KnowledgeListResponse(knowledge_graphs=knowledge_graphs)

@knowledge_router.get("/{knowledge_id}")
async def get_knowledge_graph(knowledge_id: str):
    """获取指定知识点图谱详情"""
    file_path = os.path.join("data", "knowledge", f"{knowledge_id}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="知识点图谱未找到")
    
    with open(file_path, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)
    
    return knowledge_data

@knowledge_router.delete("/{knowledge_id}")
async def delete_knowledge_graph(knowledge_id: str):
    """删除指定知识点图谱"""
    file_path = os.path.join("data", "knowledge", f"{knowledge_id}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="知识点图谱未找到")
    
    os.remove(file_path)
    
    return {"message": "知识点图谱删除成功"}

@knowledge_router.get("/download/{knowledge_id}")
async def download_knowledge_graph(knowledge_id: str):
    """下载指定知识点图谱"""
    file_path = os.path.join("data", "knowledge", f"{knowledge_id}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="知识点图谱未找到")
    
    # 获取知识图谱名称用于文件名
    with open(file_path, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)
    
    # 使用URL编码处理文件名，避免特殊字符导致的编码问题
    filename = f"{knowledge_data['name']}.json"
    return FileResponse(path=file_path, filename=filename)