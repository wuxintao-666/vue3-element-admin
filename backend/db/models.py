"""
用户模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, BigInteger, ForeignKey, ForeignKeyConstraint
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
    __tablename__ = "knowledge_content"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    course_id = Column(BigInteger, nullable=False, comment="课程ID")
    node_id = Column(String(50), nullable=False, comment="知识图谱结点ID")

    content_type = Column(
        String(50),
        nullable=False,
        comment="内容类型: concept/example/exercise/summary"
    )

    title = Column(String(255), comment="内容标题")
    description = Column(Text, nullable=False, comment="内容正文")

    level = Column(
        Integer,
        nullable=False,
        comment="难度等级 1入门 2基础 3进阶 4高级"
    )

    sort_order = Column(Integer, default=0, comment="内容顺序")

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        ForeignKeyConstraint(
            ["course_id", "node_id"],
            ["kg_node.course_id", "kg_node.id"]
        ),
    )

    class Config:
        from_attributes = True


class Course(Base):
    __tablename__ = "course"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="课程ID")
    course_code = Column(String(50), unique=True, comment="课程唯一编码")
    course_name = Column(String(255), nullable=False, comment="课程名称")
    description = Column(Text, comment="课程说明")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    class Config:
        from_attributes = True


class KGNode(Base):
    __tablename__ = "kg_node"

    id = Column(String(50), primary_key=True, comment="节点ID")
    course_id = Column(BigInteger, ForeignKey("course.id"), primary_key=True, comment="所属课程")
    label = Column(String(255), nullable=False, comment="节点名称")
    type = Column(String(50), nullable=False, comment="节点类型 chapter/knowledge")
    select_element = Column(JSON, comment="关联的HTML元素")
    sort_order = Column(Integer, comment="节点顺序")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    class Config:
        from_attributes = True


class KGEdge(Base):
    __tablename__ = "kg_edge"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="边ID")
    course_id = Column(BigInteger, ForeignKey("course.id"), nullable=False, comment="所属课程")
    source_id = Column(String(50), nullable=False, comment="起点节点")
    target_id = Column(String(50), nullable=False, comment="终点节点")
    edge_type = Column(String(50), nullable=False, comment="边类型 structural/dependency")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    class Config:
        from_attributes = True

