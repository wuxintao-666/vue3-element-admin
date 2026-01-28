"""
用户模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), comment="用户昵称")
    gender = Column(String(2), default="0", comment="性别 0:未知 1:男 2:女")
    mobile = Column(String(11), comment="手机号码")
    email = Column(String(50), comment="邮箱")
    avatar = Column(String(255), comment="头像")
    status = Column(Integer, default=1, comment="状态 1:正常 0:禁用")
    recentsignin = Column(DateTime, comment="最近登陆时间")
    createtime = Column(DateTime, default=datetime.now, comment="创建时间")
    updatetime = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True
