from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, BigInteger, ForeignKey, ForeignKeyConstraint, Enum as SQLEnum
from db.database import Base


class GenderEnum(int, Enum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class UserStatusEnum(int, Enum):
    OFFLINE = 0
    ONLINE = 1


class DifficultyLevelEnum(int, Enum):
    BEGINNER = 1
    BASIC = 2
    ADVANCED = 3
    EXPERT = 4


class NodeTypeEnum(str, Enum):
    CHAPTER = "chapter"
    KNOWLEDGE = "knowledge"


class EdgeTypeEnum(str, Enum):
    STRUCTURAL = "structural"
    DEPENDENCY = "dependency"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码哈希")
    gender = Column(SQLEnum(GenderEnum), default=GenderEnum.UNKNOWN, comment="性别")
    mobile = Column(String(20), comment="手机号码")
    email = Column(String(100), comment="邮箱")
    status = Column(SQLEnum(UserStatusEnum), default=UserStatusEnum.ONLINE, comment="状态")
    recent_signin = Column(DateTime, comment="最近登陆时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True


class KnowledgeContent(Base):
    __tablename__ = "knowledge_content"

    id = Column(Integer, primary_key=True, autoincrement=True)

    course_id = Column(BigInteger, nullable=False, comment="课程ID")
    node_id = Column(String(50), nullable=False, comment="知识图谱结点ID")


    title = Column(String(255), comment="内容标题")
    description = Column(Text, nullable=False, comment="内容正文")

    level = Column(
        SQLEnum(DifficultyLevelEnum),
        nullable=False,
        comment="难度等级"
    )

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

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
    course_code = Column(String(50), unique=True, index=True, comment="课程唯一编码")
    course_name = Column(String(255), nullable=False, comment="课程名称")
    description = Column(Text, comment="课程说明")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True


class KGNode(Base):
    __tablename__ = "kg_node"

    id = Column(String(50), primary_key=True, comment="节点ID")
    course_id = Column(BigInteger, ForeignKey("course.id"), primary_key=True, comment="所属课程")
    label = Column(String(255), nullable=False, comment="节点名称")
    type = Column(SQLEnum(NodeTypeEnum), nullable=False, comment="节点类型")
    select_element = Column(JSON, comment="关联的HTML元素")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    class Config:
        from_attributes = True


class KGEdge(Base):
    __tablename__ = "kg_edge"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="边ID")
    course_id = Column(BigInteger, ForeignKey("course.id"), nullable=False, comment="所属课程")
    source_id = Column(String(50), nullable=False, comment="起点节点")
    target_id = Column(String(50), nullable=False, comment="终点节点")
    edge_type = Column(SQLEnum(EdgeTypeEnum), nullable=False, comment="边类型")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        ForeignKeyConstraint(
            ["course_id", "source_id"],
            ["kg_node.course_id", "kg_node.id"]
        ),
        ForeignKeyConstraint(
            ["course_id", "target_id"],
            ["kg_node.course_id", "kg_node.id"]
        ),
    )

    class Config:
        from_attributes = True


class ProgrammingExercise(Base):
    """编程练习题表"""
    __tablename__ = "programming_exercise"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="练习题ID")

    # 关联到知识节点 (course_id + node_id)
    course_id = Column(BigInteger, nullable=False, comment="课程ID")
    node_id = Column(String(50), nullable=False, comment="知识节点ID")

    # 题目基本信息
    title = Column(String(255), nullable=False, comment="题目标题")
    description_md = Column(Text, nullable=False, comment="任务描述(Markdown格式)")

    # 起始代码
    start_code_html = Column(Text, default="", comment="起始HTML代码")
    start_code_css = Column(Text, default="", comment="起始CSS代码")
    start_code_js = Column(Text, default="", comment="起始JavaScript代码")

    # 检查点配置 (JSON格式存储)
    checkpoints = Column(JSON, nullable=False, comment="检查点配置列表")

    # 答案代码
    answer_html = Column(Text, nullable=False, comment="答案HTML代码")
    answer_css = Column(Text, default="", comment="答案CSS代码")
    answer_js = Column(Text, default="", comment="答案JavaScript代码")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        ForeignKeyConstraint(
            ["course_id", "node_id"],
            ["kg_node.course_id", "kg_node.id"]
        ),
    )

    class Config:
        from_attributes = True

