from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from sqlalchemy import func
from passlib.context import CryptContext
import io
import csv
from fastapi.responses import StreamingResponse

from db.database import get_db
from db.models import User as UserModel
from schemas.user_schema import UserCreate, UserUpdate, UserResponse, PageResponse, ApiResponse

user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])

# logger
logger = logging.getLogger(__name__)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordData(BaseModel):
    password: str


@user_router.get("/page")
async def get_users_page(
    request: Request,
    pageNum: int = 1,
    pageSize: int = 10,
    keywords: Optional[str] = None,
    status: Optional[int] = None,
    createTime: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户分页列表
    """
    try:
        query = db.query(UserModel)

        # log raw incoming query for debugging
        #logger.info("raw_query: %s", request.url.query)
        #logger.info("parsed_query_params: %s", dict(request.query_params))
        # FastAPI may not bind repeated query params to a List in some cases;
        # if createTime is empty, attempt to read all repeated params manually.
        if not createTime:
            try:
                create_time_list = request.query_params.getlist("createTime")
                if create_time_list:
                    #logger.info("createTime fallback from query_params.getlist: %s", create_time_list)
                    createTime = create_time_list
            except Exception as e:
                logger.info("Failed to read createTime from request.query_params.getlist: %s", e)

        if keywords:
            query = query.filter(
                (UserModel.username.ilike(f"%{keywords}%")) |
                (UserModel.nickname.ilike(f"%{keywords}%")) |
                (UserModel.mobile.ilike(f"%{keywords}%"))
            )
        #logger.info("createTime: %s", createTime)
        # 创建时间范围过滤，createTime 期望为 [start, end]，格式 YYYY-MM-DD
        if createTime and len(createTime) == 2:
            try:
                # 按日期比较数据库中的日期部分，避免时区/时间部分导致的匹配问题
                start_date = datetime.strptime(createTime[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(createTime[1], "%Y-%m-%d").date()
                #logger.info("Applying createTime filter: %s <= date(createtime) <= %s", start_date, end_date)
                
                query = query.filter(func.date(UserModel.createtime) >= start_date,
                                     func.date(UserModel.createtime) <= end_date)
            except Exception:
                # 如果解析失败，则忽略时间过滤
                logger.info("Failed to parse createTime filter: %s", createTime)
                pass

        if status is not None:
            query = query.filter(UserModel.status == status)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        users = query.offset(offset).limit(pageSize).all()

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


@user_router.get("/{user_id}/form")
async def get_user_form(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户详情
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()

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


@user_router.post("/")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    创建用户
    """
    try:
        existing_user = db.query(UserModel).filter(UserModel.username == user_data.username).first()
        if existing_user:
            return {
                "code": "A0001",
                "message": "用户名已存在"
            }

        hashed_password = pwd_context.hash(user_data.password)

        new_user = UserModel(
            username=user_data.username,
            password=hashed_password,
            nickname=user_data.nickname,
            gender=user_data.gender or "0",
            mobile=user_data.mobile,
            email=user_data.email,
            avatar=user_data.avatar,
            status=user_data.status if user_data.status is not None else 1
        )

        db.add(new_user)
        db.commit()
        # 刷新以获取自增 ID 等数据库字段
        db.refresh(new_user)

        return {
            "code": "00000",
            "data": {"id": new_user.id},
            "message": "创建成功"
        }
    except Exception as e:
        db.rollback()
        return {
            "code": "A0001",
            "message": f"创建用户失败: {str(e)}"
        }


@user_router.put("/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            return {
                "code": "A0001",
                "message": "用户不存在"
            }

        update_fields = user_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
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


@user_router.delete("/{user_ids}")
async def delete_users(user_ids: str, db: Session = Depends(get_db)):
    """
    删除用户（支持批量删除，用逗号分隔）
    """
    try:
        ids = [int(id.strip()) for id in user_ids.split(",")]
        db.query(UserModel).filter(UserModel.id.in_(ids)).delete(synchronize_session=False)
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


@user_router.post("/{user_id}/reset-password")
async def reset_password(user_id: int, password_data: PasswordData, db: Session = Depends(get_db)):
    """
    重置用户密码
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            return {
                "code": "A0001",
                "message": "用户不存在"
            }

        user.password = pwd_context.hash(password_data.password)
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


@user_router.get("/export")
async def export_users(
    request: Request,
    keywords: Optional[str] = None,
    status: Optional[int] = None,
    createTime: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    导出用户（CSV），支持关键字和状态过滤
    """
    try:
        query = db.query(UserModel)

        if keywords:
            query = query.filter(
                (UserModel.username.ilike(f"%{keywords}%")) |
                (UserModel.mobile.ilike(f"%{keywords}%"))
            )
        if status is not None:
            query = query.filter(UserModel.status == status)

        # Fallback: read repeated params if FastAPI didn't bind createTime
        if not createTime:
            try:
                create_time_list = request.query_params.getlist("createTime")
                if create_time_list:
                    logger.info("createTime fallback for export from query_params.getlist: %s", create_time_list)
                    createTime = create_time_list
            except Exception as e:
                logger.info("Failed to read createTime for export from request.query_params.getlist: %s", e)

        # 创建时间范围过滤（同查询接口）
        if createTime and len(createTime) == 2:
            try:
                start_date = datetime.strptime(createTime[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(createTime[1], "%Y-%m-%d").date()
                logger.info("Applying createTime filter on export: %s <= date(createtime) <= %s", start_date, end_date)
                try:
                    sample_dates = [r[0] for r in db.query(UserModel.createtime).order_by(UserModel.id).limit(5).all()]
                    logger.info("Sample createtime values for export (first 5 rows): %s", sample_dates)
                except Exception as sample_err:
                    logger.info("Failed to fetch sample createtime values for export: %s", sample_err)

                query = query.filter(func.date(UserModel.createtime) >= start_date,
                                     func.date(UserModel.createtime) <= end_date)
            except Exception:
                pass

        users = query.all()

        # 生成 CSV 到内存
        output = io.StringIO()
        writer = csv.writer(output)
        # 表头
        writer.writerow(["id", "username", "nickname", "mobile", "email", "gender", "status", "recentsignin", "createtime"])
        for u in users:
            writer.writerow([
                u.id,
                u.username,
                u.nickname or "",
                u.mobile or "",
                u.email or "",
                u.gender or "",
                u.status,
                u.recentsignin.isoformat() if u.recentsignin else "",
                u.createtime.isoformat() if u.createtime else ""
            ])

        output.seek(0)
        filename = "users_export.csv"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return StreamingResponse(iter([output.getvalue().encode("utf-8")]), media_type="text/csv", headers=headers)
    except Exception as e:
        return {
            "code": "A0001",
            "message": f"导出用户失败: {str(e)}"
        }

