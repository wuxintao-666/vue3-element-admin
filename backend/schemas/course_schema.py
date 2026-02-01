"""
课程模式定义（Pydantic）
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    course_code: str = Field(..., description="课程唯一编码")
    course_name: str = Field(..., description="课程名称")
    description: Optional[str] = Field(None, description="课程说明")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_code: Optional[str] = Field(None, description="课程唯一编码")
    course_name: Optional[str] = Field(None, description="课程名称")
    description: Optional[str] = Field(None, description="课程说明")


class CourseResponse(BaseModel):
    id: int
    course_code: str
    course_name: str
    description: Optional[str]
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class CoursePageQuery(BaseModel):
    """课程分页查询参数"""
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)


class CoursePageResponse(BaseModel):
    """课程分页响应"""
    list: List[CourseResponse]
    total: int


class ApiResponse(BaseModel):
    """统一API响应"""
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None