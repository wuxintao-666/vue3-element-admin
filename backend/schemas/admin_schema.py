"""
管理员模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AdminBase(BaseModel):
    username: str
    email: Optional[str] = None
    mobile: Optional[str] = None

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_super_admin: Optional[int] = None
    status: Optional[int] = None

class AdminResponse(AdminBase):
    id: int
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminPageQuery(BaseModel):
    """管理员分页查询参数"""
    username: Optional[str] = None
    nickname: Optional[str] = None
    status: Optional[int] = None
    pageNum: int = 1
    pageSize: int = 10