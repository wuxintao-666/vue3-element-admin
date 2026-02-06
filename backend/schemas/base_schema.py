"""
基础响应模式定义 - 统一所有API响应格式
"""
from typing import Optional, Any, List
from pydantic import BaseModel

# 导入错误码定义
from .error_codes import ErrorCodes, ErrorMessages, get_error_response, get_success_response

class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: str = "00000"
    data: Optional[Any] = None
    message: Optional[str] = "success"

class PageResponse(BaseModel):
    """分页响应格式"""
    code: str = "00000"
    data: Optional[Any] = None
    message: Optional[str] = "success"
    total: int = 0
    page: int = 1
    size: int = 10
    pages: int = 0

class ListResponse(BaseModel):
    """列表响应格式"""
    code: str = "00000"
    data: Optional[List[Any]] = None
    message: Optional[str] = "success"
    total: int = 0