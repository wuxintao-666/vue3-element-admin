from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from db.models import User
from schemas.user_schema import UserPageQuery, UserResponse, PageResponse, ApiResponse

admin_router = APIRouter(prefix="/api/v1")

class Meta(BaseModel):
    title: str
    icon: Optional[str] = ""
    hidden: Optional[bool] = False
    keepAlive: Optional[bool] = True
    alwaysShow: Optional[bool] = False
    params: Optional[dict] = None

class RouteItem(BaseModel):
    path: str
    component: str
    name: Optional[str] = ""
    meta: Optional[Meta] = None
    redirect: Optional[str] = None
    children: Optional[List['RouteItem']] = []

class RouteResponse(BaseModel):
    code: str = "00000"
    data: List[RouteItem]
    msg: str = "success"

class User(BaseModel):
    userId: int
    username: str
    nickname: str
    avatar: str
    roles: List[str]
    perms: List[str]

class UserResponse(BaseModel):
    code: str = "00000"
    data: User
    msg: str = "success"

class LoginRequest(BaseModel):
    username: str
    password: str
    # 暂时保留验证码字段，但不进行验证
    captchaKey: Optional[str] = None
    captchaCode: Optional[str] = None
    rememberMe: bool = False

class LoginResponse(BaseModel):
    code: str = "00000"
    data: dict
    msg: str = "success"

@admin_router.get("/menus/routes", response_model=RouteResponse)
async def get_routes():
    """
    获取用户权限路由 - 符合vue3-element-admin前端要求
    """
    routes_data = [
    {
        "path": "/system",
        "component": "Layout",
        "redirect": "/system/user",
        "name": "/system",
        "meta": {
            "title": "系统管理",
            "icon": "system",
            "hidden": False,
            "alwaysShow": False,
            "params": None,
        },
        "children": [
            {
                "path": "user",
                "component": "system/user/index",
                "name": "User",
                "meta": {
                    "title": "用户管理",
                    "icon": "el-icon-User",
                    "hidden": False,
                    "keepAlive": True,
                    "alwaysShow": False,
                    "params": None,
                },
            },
            {
                "path": "source",
                "component": "Layout",
                "redirect": "/system/source/theme",
                "name": "Role",
                "meta": {
                    "title": "教学资源管理",
                    "icon": "cascader",
                    "hidden": False,
                    "keepAlive": True,
                    "alwaysShow": False,
                    "params": None,
                },
                "children": [
                    {
                        "path": "theme",
                        "component": "system/theme/index",
                        "name": "Resource",
                        "meta": {
                            "title": "主题资源管理",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "learning-content",
                        "component": "system/learning-content/index",
                        "name": "LearningContent",
                        "meta": {
                            "title": "知识点管理",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "knowledge-graph",
                        "component": "system/knowledge-graph/index",
                        "name": "KnowledgeGraph",
                        "meta": {
                            "title": "知识图谱管理",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                        },
                    },
                    {
                        "path": "content-generator",
                        "component": "system/content-generator/index",
                        "name": "ContentGenerator",
                        "meta": {
                            "title": "学习内容生成界面",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                ],
            },
            {
                "path": "ai",
                "component": "Layout",
                "name": "ai",
                "meta": {
                    "title": "ai管理",
                    "icon": "menu",
                    "hidden": False,
                    "alwaysShow": False,
                    "params": None,
                },
                "children": [
                    {
                        "path": "ai-attribute",
                        "component": "system/ai/attribute/index",
                        "name": "ai-attribute",
                        "meta": {
                            "title": "AI属性配置",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "codegen1",
                        "component": "system/ai/prompt/index",
                        "name": "Codegen1",
                        "meta": {
                            "title": "提示词工程",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "codegen2",
                        "component": "system/ai/finetune/index",
                        "name": "Codegen2",
                        "meta": {
                            "title": "ai-调参",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                ],
            },
            {
                "path": "static-analysisg",
                "component": "Layout",
                "name": "static-analysisg",
                "meta": {
                    "title": "数据分析及可视化",
                    "icon": "el-icon-Star",
                    "hidden": False,
                    "alwaysShow": False,
                    "params": None,
                },
                "children": [
                    {
                        "path": "user-draw",
                        "component": "system/user-draw/index",
                        "name": "user-draw",
                        "meta": {
                            "title": "用户画像分析",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "codegenq",
                        "component": "system/course-analyse/index",
                        "name": "Codegenq",
                        "meta": {
                            "title": "课程数据统计",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "codegenw",
                        "component": "system/test-result/index",
                        "name": "Codegenw",
                        "meta": {
                            "title": "测试结果统计",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                    {
                        "path": "codegene",
                        "component": "system/ai/massageAnalyse",
                        "name": "Codegene",
                        "meta": {
                            "title": "ai对话分析",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                    },
                ],
            },
            {
                "path": "test-data",
                "component": "system/test-data/index",
                "name": "test-data",
                "meta": {
                    "title": "编程题库与测试用例",
                    "icon": "el-icon-MagicStick",
                    "hidden": False,
                    "alwaysShow": False,
                    "params": None,
                },
            },
        ],
        "msg": "一切ok",
    },
]

    return RouteResponse(data=[RouteItem(**route) for route in routes_data])
          
@admin_router.get("/users/profile", response_model=UserResponse)
async def get_user_profile():
    """
    获取用户信息 - 符合vue3-element-admin前端要求
    """
    user_data = User(
        userId=1,
        username="admin",
        nickname="超级管理员",
        avatar="/images/avatar.jpg",
        roles=["ROOT"],
        perms=["*:*:*"]
    )
    
    return UserResponse(data=user_data)

@admin_router.get("/users/me", response_model=UserResponse)
async def get_current_user():
    """
    获取当前登录用户信息 - 符合vue3-element-admin前端要求
    """
    # 模拟当前登录用户信息
    user_data = User(
        userId=2,
        username="admin",
        nickname="系统管理员",
        avatar="https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
        roles=["ADMIN"],
        perms=[
            "sys:user:query",
            "sys:user:add",
            "sys:user:edit",
            "sys:user:delete",
            "sys:user:import",
            "sys:user:export",
            "sys:user:reset-password",

            "sys:role:query",
            "sys:role:add",
            "sys:role:edit",
            "sys:role:delete",

            "sys:dept:query",
            "sys:dept:add",
            "sys:dept:edit",
            "sys:dept:delete",

            "sys:menu:query",
            "sys:menu:add",
            "sys:menu:edit",
            "sys:menu:delete",

            "sys:dict:query",
            "sys:dict:add",
            "sys:dict:edit",
            "sys:dict:delete",
            "sys:dict:delete",

            "sys:dict-item:query",
            "sys:dict-item:add",
            "sys:dict-item:edit",
            "sys:dict-item:delete",

            "sys:notice:query",
            "sys:notice:add",
            "sys:notice:edit",
            "sys:notice:delete",
            "sys:notice:revoke",
            "sys:notice:publish",

            "sys:config:query",
            "sys:config:add",
            "sys:config:update",
            "sys:config:delete",
            "sys:config:refresh",
        ]
    )
    
    return UserResponse(data=user_data)

@admin_router.post("/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """
    用户登录接口
    """
    # 未来可以在这里添加验证码验证逻辑
    # 暂时跳过验证码验证，只验证用户名和密码
    
    # 简单的验证，实际项目中需要连接数据库验证密码
    if login_request.username == "admin" and login_request.password == "123456":
        # 生成模拟token
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        return LoginResponse(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            msg="登录成功"
        )
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

@admin_router.post("/auth/logout")
async def logout():
    """
    用户登出接口
    """
    return {"code": "00000", "msg": "登出成功"}

@admin_router.get("/users/page")
async def get_users_page(
    pageNum: int = 1,
    pageSize: int = 10,
    keywords: Optional[str] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户分页列表
    
    参数:
        pageNum: 页码（从1开始）
        pageSize: 每页数量
        keywords: 关键字搜索（用户名/昵称/手机号）
        status: 用户状态（1:正常 0:禁用）
    """
    try:
        # 构建查询条件
        query = db.query(User)
        
        # 关键字搜索
        if keywords:
            query = query.filter(
                (User.username.ilike(f"%{keywords}%")) |
                (User.nickname.ilike(f"%{keywords}%")) |
                (User.mobile.ilike(f"%{keywords}%"))
            )
        
        # 状态过滤
        if status is not None:
            query = query.filter(User.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (pageNum - 1) * pageSize
        users = query.offset(offset).limit(pageSize).all()
        
        # 转换为响应对象
        user_list = [UserResponse.from_orm(user) for user in users]
        
        return {
            "code": "00000",
            "data": {
                "list": user_list,
                "total": total
            },
            "message": "获取成功"
        }
    except Exception as e:
        return {
            "code": "A0001",
            "message": f"获取用户列表失败: {str(e)}"
        }

@admin_router.get("/users/{user_id}/form")
async def get_user_form(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户详情
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                "code": "A0001",
                "message": "用户不存在"
            }
        
        return {
            "code": "00000",
            "data": UserResponse.from_orm(user),
            "message": "获取成功"
        }
    except Exception as e:
        return {
            "code": "A0001",
            "message": f"获取用户详情失败: {str(e)}"
        }

@admin_router.post("/users")
async def create_user(user_data: dict, db: Session = Depends(get_db)):
    """
    创建用户
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.get("username")).first()
        if existing_user:
            return {
                "code": "A0001",
                "message": "用户名已存在"
            }
        
        # 创建新用户
        new_user = User(
            username=user_data.get("username"),
            password=user_data.get("password"),  # 实际应该进行加密处理
            nickname=user_data.get("nickname"),
            gender=user_data.get("gender", "0"),
            mobile=user_data.get("mobile"),
            email=user_data.get("email"),
            avatar=user_data.get("avatar"),
            status=user_data.get("status", 1)
        )
        
        db.add(new_user)
        db.commit()
        
        return {
            "code": "00000",
            "message": "创建成功"
        }
    except Exception as e:
        db.rollback()
        return {
            "code": "A0001",
            "message": f"创建用户失败: {str(e)}"
        }

@admin_router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    """
    更新用户
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                "code": "A0001",
                "message": "用户不存在"
            }
        
        # 更新用户信息
        for key, value in user_data.items():
            if value is not None and key != "id":
                setattr(user, key, value)
        
        user.updatetime = datetime.now()
        db.commit()
        
        return {
            "code": "00000",
            "message": "更新成功"
        }
    except Exception as e:
        db.rollback()
        return {
            "code": "A0001",
            "message": f"更新用户失败: {str(e)}"
        }

@admin_router.delete("/users/{user_ids}")
async def delete_users(user_ids: str, db: Session = Depends(get_db)):
    """
    删除用户（支持批量删除，用逗号分隔）
    """
    try:
        # 解析用户ID列表
        ids = [int(id.strip()) for id in user_ids.split(",")]
        
        # 删除用户
        db.query(User).filter(User.id.in_(ids)).delete()
        db.commit()
        
        return {
            "code": "00000",
            "message": "删除成功"
        }
    except Exception as e:
        db.rollback()
        return {
            "code": "A0001",
            "message": f"删除用户失败: {str(e)}"
        }

@admin_router.post("/users/{user_id}/reset-password")
async def reset_password(user_id: int, password_data: dict, db: Session = Depends(get_db)):
    """
    重置用户密码
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                "code": "A0001",
                "message": "用户不存在"
            }
        
        # 更新密码（实际应该进行加密处理）
        user.password = password_data.get("password")
        user.updatetime = datetime.now()
        db.commit()
        
        return {
            "code": "00000",
            "message": "重置成功"
        }
    except Exception as e:
        db.rollback()
        return {
            "code": "A0001",
            "message": f"重置密码失败: {str(e)}"
        }