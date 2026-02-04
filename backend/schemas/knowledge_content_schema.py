"""
知识内容模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeContentBase(BaseModel):
    course_id: str = Field(..., description="课程编码 (course_code)，将自动转换为课程ID")
    node_id: str = Field(..., description="节点ID")
    title: str = Field(..., description="内容标题")
    description: str = Field(..., description="内容描述")
    level: int = Field(..., ge=1, le=4, description="难度等级 1:入门 2:基础 3:进阶 4:高级")


class KnowledgeContentCreate(KnowledgeContentBase):
    pass


class KnowledgeContentUpdate(BaseModel):
    course_id: Optional[str] = Field(None, description="课程编码")
    node_id: Optional[str] = Field(None, description="节点ID")
    title: Optional[str] = Field(None, description="内容标题")
    description: Optional[str] = Field(None, description="内容描述")
    level: Optional[int] = Field(None, ge=1, le=4, description="难度等级 1:入门 2:基础 3:进阶 4:高级")

    class Config:
        allow_population_by_field_name = True


class KnowledgeContentResponse(BaseModel):
    id: str
    course_id: str
    course_code: Optional[str] = None  # 额外添加的字段
    node_id: str
    title: str
    description: str
    level: int
    created_at: Optional[datetime] = Field(None, alias="created_at")
    updated_at: Optional[datetime] = Field(None, alias="updated_at")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class KnowledgeContentPageQuery(BaseModel):
    """知识内容分页查询参数"""
    level: Optional[int] = None  # 难度等级
    courseId: Optional[str] = None  # 课程编码
    nodeId: Optional[str] = None  # 节点ID
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)

    class Config:
        allow_population_by_field_name = True


class KnowledgeContentPageResponse(BaseModel):
    """知识内容分页响应"""
    list: List[KnowledgeContentResponse]
    total: int


class KnowledgeContentBatchItem(BaseModel):
    """批量保存的单个知识内容项"""
    node_id: str = Field(..., description="知识图谱结点ID")
    level: int = Field(..., ge=1, le=4, description="难度等级 1:入门 2:基础 3:进阶 4:高级")
    title: str = Field(..., description="内容标题")
    description: str = Field(..., description="内容正文")


class KnowledgeContentBatchSave(BaseModel):
    """批量保存知识内容的请求"""
    course_id: str = Field(..., description="课程编码 (course_code)，将自动转换为课程ID")
    knowledge_contents: List[KnowledgeContentBatchItem] = Field(..., description="知识内容列表")


class ApiResponse(BaseModel):
    """统一API响应"""
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None