from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext

from db.database import get_db
from db.models import User as UserModel, Admin as AdminModel
from schemas.user_schema import UserPageQuery, UserResponse, PageResponse, ApiResponse
from schemas.admin_schema import AdminResponse
from schemas.error_codes import ErrorCodes, ErrorMessages

admin_router = APIRouter(prefix="/api/v1")

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 验证码存储（从auth_router.py导入）
from .auth_router import captcha_store

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
 

class LoginRequest(BaseModel):
    username: str
    password: str
    # 验证码字段
    captcha_key: Optional[str] = None
    captcha_code: Optional[str] = None
    rememberMe: bool = False

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    mobile: Optional[str] = None

class LoginResponse(BaseModel):
    code: str = "00000"
    data: dict
    msg: str = "success"

class RegisterResponse(BaseModel):
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
                "path": "course",
                "component": "system/course/index",
                "name": "Course",
                "meta": {
                    "title": "课程管理",
                    "icon": "el-icon-Reading",
                    "hidden": False,
                    "keepAlive": True,
                    "alwaysShow": False,
                    "params": None,
                },
            },
            {
                "path": "source",
                "component": "Layout",
                "redirect": "/system/source/frontend-learning",
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
                        "path": "frontend-learning",
                        "component": "Layout",
                        "redirect": "/system/source/frontend-learning/theme",
                        "name": "FrontendLearning",
                        "meta": {
                            "title": "前端框架",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                        "children": [
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
                                "path": "test-question",
                                "component": "system/test-question/index",
                                "name": "TestQuestion",
                                "meta": {
                                    "title": "测试题管理",
                                    "icon": "code",
                                    "hidden": False,
                                    "keepAlive": True,
                                    "alwaysShow": False,
                                    "params": None,
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
                        "path": "data-structure",
                        "component": "Layout",
                        "name": "DataStructure",
                        "meta": {
                            "title": "数据结构",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                        "children": [],
                    },
                    {
                        "path": "computer-vision",
                        "component": "Layout",
                        "name": "ComputerVision",
                        "meta": {
                            "title": "机器视觉",
                            "icon": "code",
                            "hidden": False,
                            "keepAlive": True,
                            "alwaysShow": False,
                            "params": None,
                        },
                        "children": [],
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
          
@admin_router.get("/users/profile")
async def get_user_profile():
    """
    获取用户信息 - 符合vue3-element-admin前端要求
    """
    return {
        "code": "00000",
        "data": {
            "userId": 1,
            "username": "admin",
            "nickname": "超级管理员",
            "avatar": "/images/avatar.jpg",
            "roles": ["ROOT"],
            "perms": ["*:*:*"]
        },
        "msg": "success"
    }

@admin_router.get("/users/me")
async def get_current_user(db: Session = Depends(get_db)):
    """
    获取当前登录管理员信息 - 符合vue3-element-admin前端要求
    """
    # 这里应该从token中获取管理员ID，暂时返回默认管理员信息
    # 实际项目中需要从JWT token解析出管理员ID
    admin = db.query(AdminModel).filter(AdminModel.username == "admin").first()

    if admin:
        return {
            "code": "00000",
            "data": {
                "userId": admin.id,
                "username": admin.username,
                "nickname": "系统管理员",
                "avatar": "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
                "roles": ["ADMIN"],
                "perms": [
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
            },
            "msg": "success"
        }
    else:
        # 如果没有找到管理员，返回默认信息
        return {
            "code": "00000",
            "data": {
                "userId": 1,
                "username": "admin",
                "nickname": "系统管理员",
                "avatar": "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
                "roles": ["ADMIN"],
                "perms": ["*:*:*"]
            },
            "msg": "success"
        }

@admin_router.post("/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    管理员登录接口
    """
    try:
        # 验证验证码
        if not login_request.captcha_key or not login_request.captcha_code:
            raise HTTPException(status_code=400, detail=ErrorMessages.CAPTCHA_REQUIRED)

        stored_captcha = captcha_store.get(login_request.captcha_key)
        if not stored_captcha:
            raise HTTPException(status_code=400, detail=ErrorMessages.CAPTCHA_EXPIRED)

        if stored_captcha != login_request.captcha_code.lower():
            raise HTTPException(status_code=400, detail=ErrorMessages.CAPTCHA_ERROR)

        # 验证通过后删除已使用的验证码
        captcha_store.pop(login_request.captcha_key, None)

        # 从管理员表查找用户
        admin = db.query(AdminModel).filter(AdminModel.username == login_request.username).first()

        if not admin:
            raise HTTPException(status_code=401, detail=ErrorMessages.USER_NOT_EXIST)

        # 验证密码
        if not pwd_context.verify(login_request.password, admin.password):
            raise HTTPException(status_code=401, detail=ErrorMessages.USER_PASSWORD_ERROR)

        # 更新最后登录时间
        admin.last_login = datetime.now()
        db.commit()

        # 生成模拟token (实际项目中应该使用JWT)
        access_token = f"admin_token_{admin.id}_{int(datetime.now().timestamp())}"
        refresh_token = f"refresh_token_{admin.id}_{int(datetime.now().timestamp())}"

        return LoginResponse(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            msg="登录成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@admin_router.post("/auth/logout")
async def logout():
    """
    用户登出接口
    """
    return {"code": "00000", "msg": "登出成功"}

@admin_router.post("/auth/register", response_model=RegisterResponse)
async def register(register_request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    try:
        # 检查管理员用户名是否已存在
        existing_admin = db.query(AdminModel).filter(AdminModel.username == register_request.username).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail=ErrorMessages.DATA_ALREADY_EXISTS)

        # 哈希密码
        hashed_password = pwd_context.hash(register_request.password)

        # 创建新管理员
        new_admin = AdminModel(
            username=register_request.username,
            password=hashed_password,
            email=register_request.email,
            mobile=register_request.mobile,
            last_login=datetime.now()
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        return RegisterResponse(
            data={"user_id": new_admin.id},
            msg="注册成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
 