"""
用户模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
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


class KnowledgeContent(Base):
    __tablename__ = "knowledge_contents"

    id = Column(String(50), primary_key=True, index=True, comment="知识点ID")
    graph_id = Column(String(50), nullable=False, comment="主题ID")
    topic_id = Column(String(100), nullable=False, comment="结点ID")
    description = Column(Text, nullable=False, comment="内容")
    level = Column(Integer, nullable=False, comment="难度等级 1:入门 2:基础 3:进阶 4:高级")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True


class KnowledgeGraph(Base):
    __tablename__ = "knowledge_graphs"

    id = Column(String(50), primary_key=True, index=True, comment="知识图谱ID")
    name = Column(String(200), nullable=False, comment="知识图谱名称")
    description = Column(Text, nullable=False, comment="知识图谱简介")
    tags = Column(JSON, nullable=False, comment="标签数组")
    status = Column(Integer, default=1, nullable=False, comment="状态 1:启用 0:禁用")
    maintainer_id = Column(String(50), nullable=False, comment="维护人ID")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True


class Theme(Base):
    __tablename__ = "themes"

    id = Column(String(50), primary_key=True, index=True, comment="主题ID")
    name = Column(String(100), nullable=False, comment="主题名称")
    description = Column(Text, nullable=False, comment="主题简介")
    tags = Column(JSON, nullable=False, comment="标签数组")
    difficulty = Column(Integer, nullable=False, comment="难度 1:初级 2:中级 3:高级")
    status = Column(Integer, default=1, nullable=False, comment="状态 1:启用 0:禁用")
    entrance_id = Column(String(50), nullable=False, comment="学习入口节点ID")
    maintainer_id = Column(String(50), nullable=False, comment="维护人ID")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True
