"""
主题模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 导入统一响应格式
from .base_schema import ApiResponse, PageResponse


class ThemeBase(BaseModel):
    name: str = Field(..., description="主题名称")
    description: str = Field(..., description="主题简介")
    tags: List[str] = Field(..., description="标签数组")
    difficulty: int = Field(..., ge=1, le=3, description="难度 1:初级 2:中级 3:高级")
    status: int = Field(0, ge=0, le=1, description="状态 1:启用 0:禁用")
    entrance_id: str = Field(..., alias="entranceId", description="学习入口节点ID")
    maintainer_id: str = Field(..., alias="maintainerId", description="维护人ID")

    class Config:
        allow_population_by_field_name = True


class ThemeCreate(ThemeBase):
    id: Optional[str] = Field(None, description="主题ID（可选，不提供则自动生成）")


class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, description="主题名称")
    description: Optional[str] = Field(None, description="主题简介")
    tags: Optional[List[str]] = Field(None, description="标签数组")
    difficulty: Optional[int] = Field(None, ge=1, le=3, description="难度 1:初级 2:中级 3:高级")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态 1:启用 0:禁用")
    entrance_id: Optional[str] = Field(None, alias="entranceId", description="学习入口节点ID")
    maintainer_id: Optional[str] = Field(None, alias="maintainerId", description="维护人ID")

    class Config:
        allow_population_by_field_name = True


class ThemeResponse(ThemeBase):
    id: str
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ThemePageQuery(BaseModel):
    """主题分页查询参数"""
    keywords: Optional[str] = None  # 关键字（主题名称）
    status: Optional[int] = None  # 状态
    difficulty: Optional[int] = None  # 难度
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)


class ThemePageResponse(BaseModel):
    """主题分页响应"""
    list: List[ThemeResponse]
    total: int


# ApiResponse 已移至 base_schema.py