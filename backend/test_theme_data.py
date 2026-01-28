"""
生成测试主题数据
"""
from sqlalchemy.orm import sessionmaker
from db.database import engine
from db.models import Theme
import uuid
from datetime import datetime

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 生成测试主题数据
    test_themes = [
        {
            "id": str(uuid.uuid4()),
            "name": "Python编程基础",
            "description": "学习Python编程语言的基础知识，包括语法、数据类型、控制结构等核心概念。",
            "tags": ["python", "编程基础", "后端开发"],
            "difficulty": 1,
            "status": 1,
            "entrance_id": "python_basic_001",
            "maintainer_id": "user_admin"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "前端开发入门",
            "description": "掌握HTML、CSS、JavaScript的基础知识，学习构建现代Web界面的技能。",
            "tags": ["html", "css", "javascript", "前端开发"],
            "difficulty": 1,
            "status": 1,
            "entrance_id": "frontend_basic_001",
            "maintainer_id": "user_admin"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "机器学习算法",
            "description": "深入理解机器学习的核心算法，包括监督学习、无监督学习和强化学习。",
            "tags": ["机器学习", "算法", "AI", "数据科学"],
            "difficulty": 3,
            "status": 1,
            "entrance_id": "ml_algorithms_001",
            "maintainer_id": "user_admin"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "数据库设计与优化",
            "description": "学习关系型数据库的设计原则、索引优化、查询性能调优等高级技能。",
            "tags": ["数据库", "SQL", "性能优化", "系统架构"],
            "difficulty": 2,
            "status": 1,
            "entrance_id": "database_design_001",
            "maintainer_id": "user_admin"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "移动应用开发",
            "description": "使用React Native和Flutter等框架开发跨平台移动应用程序。",
            "tags": ["移动开发", "React Native", "Flutter", "跨平台"],
            "difficulty": 2,
            "status": 1,
            "entrance_id": "mobile_dev_001",
            "maintainer_id": "user_admin"
        }
    ]

    inserted_count = 0
    for theme_data in test_themes:
        try:
            # 检查主题ID是否已存在
            existing_theme = db.query(Theme).filter(Theme.id == theme_data["id"]).first()
            if existing_theme:
                print(f"主题 {theme_data['name']} 已存在，跳过")
                continue

            # 创建主题对象
            theme = Theme(
                id=theme_data["id"],
                name=theme_data["name"],
                description=theme_data["description"],
                tags=theme_data["tags"],
                difficulty=theme_data["difficulty"],
                status=theme_data["status"],
                entrance_id=theme_data["entrance_id"],
                maintainer_id=theme_data["maintainer_id"]
            )

            db.add(theme)
            inserted_count += 1
            print(f"准备插入主题: {theme_data['name']}")

        except Exception as e:
            print(f"处理主题 {theme_data['name']} 时出错: {e}")
            continue

    # 提交所有更改
    db.commit()
    print(f"\n成功插入 {inserted_count} 个主题!")

    # 显示插入的主题
    all_themes = db.query(Theme).all()
    print(f"\n数据库中现在共有 {len(all_themes)} 个主题:")
    difficulty_map = {1: "初级", 2: "中级", 3: "高级"}
    status_map = {0: "禁用", 1: "启用"}

    for theme in all_themes:
        print(f"ID: {theme.id}")
        print(f"  名称: {theme.name}")
        print(f"  难度: {difficulty_map.get(theme.difficulty, '未知')}")
        print(f"  状态: {status_map.get(theme.status, '未知')}")
        print(f"  标签: {', '.join(theme.tags)}")
        print()

except Exception as e:
    print(f"插入测试数据失败: {e}")
    db.rollback()

finally:
    db.close()