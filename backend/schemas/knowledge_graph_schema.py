"""
知识图谱模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeGraphBase(BaseModel):
    name: str = Field(..., description="知识图谱名称")
    description: str = Field(..., description="知识图谱简介")
    tags: List[str] = Field(..., description="标签数组")
    status: int = Field(0, ge=0, le=1, description="状态 1:启用 0:禁用")
    maintainer_id: str = Field(..., alias="maintainerId", description="维护人ID")


class KnowledgeGraphCreate(KnowledgeGraphBase):
    id: str = Field(..., description="知识图谱ID")


class KnowledgeGraphUpdate(BaseModel):
    name: Optional[str] = Field(None, description="知识图谱名称")
    description: Optional[str] = Field(None, description="知识图谱简介")
    tags: Optional[List[str]] = Field(None, description="标签数组")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态 1:启用 0:禁用")
    maintainer_id: Optional[str] = Field(None, alias="maintainerId", description="维护人ID")

    class Config:
        allow_population_by_field_name = True


class KnowledgeGraphResponse(KnowledgeGraphBase):
    id: str
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class KnowledgeGraphPageQuery(BaseModel):
    """知识图谱分页查询参数"""
    keywords: Optional[str] = None  # 关键字（名称）
    status: Optional[int] = None  # 状态
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)


class KnowledgeGraphPageResponse(BaseModel):
    """知识图谱分页响应"""
    list: List[KnowledgeGraphResponse]
    total: int


# 图谱数据相关模型
class KnowledgeGraphNode(BaseModel):
    data: dict


class KnowledgeGraphEdge(BaseModel):
    data: dict


class KnowledgeGraphData(BaseModel):
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]
    dependent_edges: List[KnowledgeGraphEdge]


class ApiResponse(BaseModel):
    """统一API响应"""
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None