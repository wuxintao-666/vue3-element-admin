"""
知识内容模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeContentBase(BaseModel):
    graph_id: str = Field(..., alias="graphId", description="主题ID")
    topic_id: str = Field(..., description="结点ID")
    description: str = Field(..., description="内容")
    level: int = Field(..., ge=1, le=4, description="难度等级 1:入门 2:基础 3:进阶 4:高级")


class KnowledgeContentCreate(KnowledgeContentBase):
    pass


class KnowledgeContentUpdate(BaseModel):
    graph_id: Optional[str] = Field(None, alias="graphId", description="主题ID")
    topic_id: Optional[str] = Field(None, description="结点ID")
    description: Optional[str] = Field(None, description="内容")
    level: Optional[int] = Field(None, ge=1, le=4, description="难度等级 1:入门 2:基础 3:进阶 4:高级")

    class Config:
        allow_population_by_field_name = True


class KnowledgeContentResponse(BaseModel):
    id: int
    graph_id: str = Field(..., alias="graphId")
    topic_id: str
    description: str
    level: int
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class KnowledgeContentPageQuery(BaseModel):
    """知识内容分页查询参数"""
    level: Optional[int] = None  # 难度等级
    graph_id: Optional[str] = Field(None, alias="graphId")  # 主题ID
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)

    class Config:
        allow_population_by_field_name = True


class KnowledgeContentPageResponse(BaseModel):
    """知识内容分页响应"""
    list: List[KnowledgeContentResponse]
    total: int


class ApiResponse(BaseModel):
    """统一API响应"""
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None