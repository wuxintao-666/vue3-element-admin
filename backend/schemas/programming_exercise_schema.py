"""
编程练习题模式定义（Pydantic）
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProgrammingExerciseBase(BaseModel):
    """编程练习题基础模型"""
    course_id: str = Field(..., description="课程编码 (course_code)")
    node_id: str = Field(..., description="知识节点ID")
    title: str = Field(..., description="题目标题")
    description_md: str = Field(..., description="任务描述(Markdown格式)")
    start_code_html: str = Field("", description="起始HTML代码")
    start_code_css: str = Field("", description="起始CSS代码")
    start_code_js: str = Field("", description="起始JavaScript代码")
    checkpoints: List[Dict[str, Any]] = Field(..., description="检查点配置列表")
    answer_html: str = Field(..., description="答案HTML代码")
    answer_css: str = Field("", description="答案CSS代码")
    answer_js: str = Field("", description="答案JavaScript代码")


class ProgrammingExerciseCreate(ProgrammingExerciseBase):
    """创建编程练习题"""
    pass


class ProgrammingExerciseUpdate(BaseModel):
    """更新编程练习题"""
    title: Optional[str] = Field(None, description="题目标题")
    description_md: Optional[str] = Field(None, description="任务描述(Markdown格式)")
    start_code_html: Optional[str] = Field(None, description="起始HTML代码")
    start_code_css: Optional[str] = Field(None, description="起始CSS代码")
    start_code_js: Optional[str] = Field(None, description="起始JavaScript代码")
    checkpoints: Optional[List[Dict[str, Any]]] = Field(None, description="检查点配置列表")
    answer_html: Optional[str] = Field(None, description="答案HTML代码")
    answer_css: Optional[str] = Field(None, description="答案CSS代码")
    answer_js: Optional[str] = Field(None, description="答案JavaScript代码")


class ProgrammingExerciseResponse(BaseModel):
    """编程练习题响应模型"""
    id: int
    course_id: int = Field(..., description="课程ID")
    node_id: str = Field(..., description="知识节点ID")
    title: str
    description_md: str
    start_code_html: str
    start_code_css: str
    start_code_js: str
    checkpoints: List[Dict[str, Any]]
    answer_html: str
    answer_css: str
    answer_js: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ProgrammingExerciseBatchItem(BaseModel):
    """批量保存的单个编程练习题项"""
    node_id: str = Field(..., description="知识节点ID")
    title: str = Field(..., description="题目标题")
    description_md: str = Field(..., description="任务描述(Markdown格式)")
    start_code: Dict[str, str] = Field(..., description="起始代码 {'html': '', 'css': '', 'js': ''}")
    checkpoints: List[Dict[str, Any]] = Field(..., description="检查点配置列表")
    answer: Dict[str, str] = Field(..., description="答案代码 {'html': '', 'css': '', 'js': ''}")


class ProgrammingExerciseBatchSave(BaseModel):
    """批量保存编程练习题的请求"""
    course_id: str = Field(..., description="课程编码 (固定为TEST001)")
    exercises: List[ProgrammingExerciseBatchItem] = Field(..., description="编程练习题列表")


class ProgrammingExercisePageQuery(BaseModel):
    """编程练习题分页查询参数"""
    course_id: Optional[str] = Field(None, description="课程编码")
    node_id: Optional[str] = Field(None, description="知识节点ID")
    pageNum: int = Field(1, gt=0)
    pageSize: int = Field(10, gt=0, le=100)


class ProgrammingExercisePageResponse(BaseModel):
    """编程练习题分页响应"""
    list: List[ProgrammingExerciseResponse]
    total: int


class ApiResponse(BaseModel):
    """统一API响应"""
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None