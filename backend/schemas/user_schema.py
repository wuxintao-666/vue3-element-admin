"""
用户模式定义（Pydantic）
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

# 导入统一响应格式
from .base_schema import ApiResponse, PageResponse

class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    gender: Optional[str] = "0"
    mobile: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    status: int = 1

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[int] = None

class UserResponse(UserBase):
    id: int
    recentsignin: Optional[datetime] = None
    createtime: Optional[datetime] = None
    class Config:
        orm_mode = True

class UserPageQuery(BaseModel):
    """用户分页查询参数"""
    keywords: Optional[str] = None  # 关键字（用户名/昵称/手机号）
    status: Optional[int] = None  # 状态
    pageNum: int = 1
    pageSize: int = 10

class PageResponse(BaseModel):
    """分页响应"""
    list: List[UserResponse]
    total: int

# ApiResponse 已移至 base_schema.py
