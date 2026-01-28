from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import uuid

from db.database import get_db
from db.models import Theme as ThemeModel
from schemas.theme_schema import (
    ThemeCreate, ThemeUpdate, ThemeResponse,
    ThemePageQuery, ThemePageResponse, ApiResponse
)

theme_router = APIRouter(prefix="/api/v1/themes", tags=["Themes"])

# logger
logger = logging.getLogger(__name__)


@theme_router.get("/page", response_model=ApiResponse)
async def get_themes_page(
    keywords: Optional[str] = None,
    status: Optional[int] = None,
    difficulty: Optional[int] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取主题分页列表
    """
    try:
        query = db.query(ThemeModel)

        if keywords:
            query = query.filter(ThemeModel.name.ilike(f"%{keywords}%"))

        if status is not None:
            query = query.filter(ThemeModel.status == status)

        if difficulty is not None:
            query = query.filter(ThemeModel.difficulty == difficulty)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        themes = query.order_by(ThemeModel.create_time.desc()).offset(offset).limit(pageSize).all()

        theme_list = [ThemeResponse.from_orm(theme).dict(by_alias=True) for theme in themes]

        return ApiResponse(
            code="00000",
            data={
                "list": theme_list,
                "total": total
            },
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取主题列表失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取主题列表失败: {str(e)}"
        )


@theme_router.get("/{theme_id}/form", response_model=ApiResponse)
async def get_theme_form(theme_id: str, db: Session = Depends(get_db)):
    """
    获取主题详情（用于表单回显）
    """
    try:
        theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()

        if not theme:
            return ApiResponse(
                code="A0001",
                message="主题不存在"
            )

        theme_data = ThemeResponse.from_orm(theme)
        return ApiResponse(
            code="00000",
            data=theme_data.dict(by_alias=True),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取主题详情失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取主题详情失败: {str(e)}"
        )


@theme_router.post("/", response_model=ApiResponse)
async def create_theme(theme_data: ThemeCreate, db: Session = Depends(get_db)):
    """
    创建主题
    """
    try:
        # 如果没有提供ID，自动生成UUID
        theme_id = theme_data.id if theme_data.id else str(uuid.uuid4())

        # 检查主题ID是否已存在
        existing_theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
        if existing_theme:
            return ApiResponse(
                code="A0001",
                message="主题ID已存在"
            )

        new_theme = ThemeModel(
            id=theme_id,
            name=theme_data.name,
            description=theme_data.description,
            tags=theme_data.tags,
            difficulty=theme_data.difficulty,
            status=theme_data.status,
            entrance_id=theme_data.entrance_id,
            maintainer_id=theme_data.maintainer_id
        )

        db.add(new_theme)
        db.commit()
        db.refresh(new_theme)

        return ApiResponse(
            code="00000",
            data={"id": new_theme.id},
            message="创建成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建主题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"创建主题失败: {str(e)}"
        )


@theme_router.put("/{theme_id}", response_model=ApiResponse)
async def update_theme(theme_id: str, theme_data: ThemeUpdate, db: Session = Depends(get_db)):
    """
    更新主题
    """
    try:
        theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()

        if not theme:
            return ApiResponse(
                code="A0001",
                message="主题不存在"
            )

        update_fields = theme_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            # 处理字段名映射（Pydantic使用snake_case，数据库使用snake_case）
            if key == "entrance_id":
                setattr(theme, "entrance_id", value)
            elif key == "maintainer_id":
                setattr(theme, "maintainer_id", value)
            else:
                setattr(theme, key, value)

        theme.update_time = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="更新成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新主题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"更新主题失败: {str(e)}"
        )


@theme_router.delete("/{theme_ids}", response_model=ApiResponse)
async def delete_themes(theme_ids: str, db: Session = Depends(get_db)):
    """
    删除主题（支持批量删除，用逗号分隔）
    """
    try:
        ids = [id.strip() for id in theme_ids.split(",")]
        deleted_count = db.query(ThemeModel).filter(ThemeModel.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        if deleted_count == 0:
            return ApiResponse(
                code="A0001",
                message="未找到要删除的主题"
            )

        return ApiResponse(
            code="00000",
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除主题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除主题失败: {str(e)}"
        )


@theme_router.post("/{theme_id}/publish", response_model=ApiResponse)
async def publish_theme(theme_id: str, db: Session = Depends(get_db)):
    """
    发布主题
    """
    try:
        theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()

        if not theme:
            return ApiResponse(
                code="A0001",
                message="主题不存在"
            )

        # 这里可以添加发布逻辑，比如状态变更、通知等
        # 目前简单地将状态设置为启用
        theme.status = 1
        theme.update_time = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="发布成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"发布主题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"发布主题失败: {str(e)}"
        )


@theme_router.post("/{theme_id}/disable", response_model=ApiResponse)
async def disable_theme(theme_id: str, db: Session = Depends(get_db)):
    """
    停用主题
    """
    try:
        theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()

        if not theme:
            return ApiResponse(
                code="A0001",
                message="主题不存在"
            )

        # 将状态设置为禁用
        theme.status = 0
        theme.update_time = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="停用成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"停用主题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"停用主题失败: {str(e)}"
        )