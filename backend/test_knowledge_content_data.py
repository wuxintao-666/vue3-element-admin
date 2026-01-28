"""
根据现有主题生成测试知识点数据
每个主题生成3个知识点，每个知识点包含4个等级
"""
from sqlalchemy.orm import sessionmaker
from db.database import engine
from db.models import Theme, KnowledgeContent
import uuid
from datetime import datetime

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 获取所有启用的主题
    themes = db.query(Theme).filter(Theme.status == 1).all()

    if not themes:
        print("没有找到启用的主题，请先运行 test_theme_data.py")
        exit(1)

    print(f"找到 {len(themes)} 个启用的主题")

    # 为每个主题定义知识点模板
    knowledge_templates = {
        "Python编程基础": [
            {
                "title": "Python语法基础",
                "levels": {
                    1: "了解Python的基本语法规则，包括缩进、注释、变量命名等",
                    2: "掌握数据类型（数字、字符串、列表、字典）和基本运算",
                    3: "熟练使用控制结构（if语句、循环）和函数定义",
                    4: "理解面向对象编程基础和模块导入机制"
                }
            },
            {
                "title": "数据处理与文件操作",
                "levels": {
                    1: "学习文件读写的基本方法和异常处理",
                    2: "掌握字符串和列表的高级操作技巧",
                    3: "使用字典和集合进行数据处理",
                    4: "学习数据序列化和JSON格式处理"
                }
            },
            {
                "title": "Python标准库应用",
                "levels": {
                    1: "熟悉常用标准库模块（os, sys, datetime）",
                    2: "掌握字符串格式化和正则表达式",
                    3: "学习文件系统操作和路径处理",
                    4: "使用标准库解决实际编程问题"
                }
            }
        ],
        "前端开发入门": [
            {
                "title": "HTML基础结构",
                "levels": {
                    1: "掌握HTML基本标签和文档结构",
                    2: "学习表单元素和语义化标签",
                    3: "理解HTML5新特性和API",
                    4: "创建语义化和可访问的HTML文档"
                }
            },
            {
                "title": "CSS样式设计",
                "levels": {
                    1: "学习CSS选择器和基本样式属性",
                    2: "掌握盒模型和布局技术",
                    3: "使用Flexbox和Grid进行高级布局",
                    4: "实现响应式设计和CSS动画效果"
                }
            },
            {
                "title": "JavaScript交互",
                "levels": {
                    1: "理解JavaScript基本语法和数据类型",
                    2: "掌握DOM操作和事件处理",
                    3: "学习异步编程和AJAX技术",
                    4: "使用现代JavaScript特性和框架基础"
                }
            }
        ],
        "机器学习算法": [
            {
                "title": "监督学习算法",
                "levels": {
                    1: "理解监督学习的基本概念和分类",
                    2: "掌握线性回归和逻辑回归算法",
                    3: "学习决策树和随机森林算法",
                    4: "应用支持向量机和神经网络"
                }
            },
            {
                "title": "无监督学习算法",
                "levels": {
                    1: "理解聚类和降维的基本概念",
                    2: "掌握K-means聚类算法",
                    3: "学习主成分分析（PCA）",
                    4: "应用高级聚类和降维技术"
                }
            },
            {
                "title": "模型评估与优化",
                "levels": {
                    1: "学习交叉验证和模型评估指标",
                    2: "理解过拟合和欠拟合问题",
                    3: "掌握特征选择和特征工程",
                    4: "应用模型调优和集成学习方法"
                }
            }
        ],
        "数据库设计与优化": [
            {
                "title": "关系型数据库设计",
                "levels": {
                    1: "理解数据库设计的基本原则",
                    2: "掌握ER模型和规范化理论",
                    3: "设计高效的数据库表结构",
                    4: "实现数据库约束和完整性"
                }
            },
            {
                "title": "SQL查询优化",
                "levels": {
                    1: "掌握基本SQL查询语句",
                    2: "学习索引原理和索引设计",
                    3: "优化复杂查询和子查询",
                    4: "使用执行计划分析查询性能"
                }
            },
            {
                "title": "数据库性能调优",
                "levels": {
                    1: "理解数据库性能指标",
                    2: "学习查询优化和索引优化",
                    3: "掌握数据库连接池和缓存",
                    4: "实施高可用和备份策略"
                }
            }
        ],
        "移动应用开发": [
            {
                "title": "React Native基础",
                "levels": {
                    1: "理解React Native开发环境搭建",
                    2: "掌握基本组件和布局",
                    3: "学习状态管理和数据流",
                    4: "实现导航和路由管理"
                }
            },
            {
                "title": "Flutter开发入门",
                "levels": {
                    1: "了解Dart语言基础语法",
                    2: "掌握Flutter Widget系统",
                    3: "学习状态管理和Provider模式",
                    4: "实现Material Design和Cupertino设计"
                }
            },
            {
                "title": "跨平台应用优化",
                "levels": {
                    1: "理解平台差异和适配策略",
                    2: "学习性能优化和内存管理",
                    3: "掌握热更新和版本管理",
                    4: "实施应用上架和发布流程"
                }
            }
        ]
    }

    total_inserted = 0

    # 为每个主题生成知识点
    for theme in themes:
        theme_name = theme.name
        theme_id = theme.id

        print(f"\n处理主题: {theme_name} (ID: {theme_id[:8]}...)")

        # 获取该主题的知识点模板
        # 创建主题名称到模板的映射
        theme_template_mapping = {
            "Python编程基础": "Python编程基础",
            "前端开发入门": "前端开发入门",
            "机器学习算法": "机器学习算法",
            "数据库设计与优化": "数据库设计与优化",
            "移动应用开发": "移动应用开发"
        }

        template_key = theme_template_mapping.get(theme_name)
        if not template_key or template_key not in knowledge_templates:
            print(f"  跳过 - 没有找到 {theme_name} 的匹配模板")
            print(f"  映射关系: {theme_template_mapping}")
            continue

        knowledge_points = knowledge_templates[template_key]
        print(f"  使用模板: {template_key}")
        theme_inserted = 0

        # 为每个知识点生成4个等级的内容
        for kp_template in knowledge_points:
            for level in range(1, 5):  # 1-4级
                try:
                    # 生成唯一的topic_id
                    topic_id = f"{theme_name.lower().replace(' ', '_')}_{kp_template['title'].lower().replace(' ', '_')}_level_{level}"

                    # 检查是否已存在
                    existing_content = db.query(KnowledgeContent).filter(
                        KnowledgeContent.graph_id == theme_id,
                        KnowledgeContent.topic_id == topic_id
                    ).first()

                    if existing_content:
                        print(f"  跳过 - 知识点已存在: {topic_id}")
                        continue

                    # 创建知识点内容
                    content = KnowledgeContent(
                        id=str(uuid.uuid4()),
                        graph_id=theme_id,
                        topic_id=topic_id,
                        description=kp_template['levels'][level],
                        level=level
                    )

                    db.add(content)
                    theme_inserted += 1
                    print(f"  添加知识点: {kp_template['title']} - {level}级")

                except Exception as e:
                    print(f"  处理知识点时出错: {e}")
                    continue

        print(f"  为主题 {theme_name} 插入了 {theme_inserted} 个知识点")
        total_inserted += theme_inserted

    # 提交所有更改
    db.commit()
    print(f"\n🎉 成功插入 {total_inserted} 个知识点!")

    # 显示统计信息
    all_contents = db.query(KnowledgeContent).all()
    print(f"\n📊 数据库统计:")
    print(f"  总知识点数量: {len(all_contents)}")

    # 按主题分组统计
    theme_stats = {}
    for content in all_contents:
        theme = db.query(Theme).filter(Theme.id == content.graph_id).first()
        theme_name = theme.name if theme else content.graph_id[:8]
        if theme_name not in theme_stats:
            theme_stats[theme_name] = 0
        theme_stats[theme_name] += 1

    print("  各主题知识点数量:")
    for theme_name, count in theme_stats.items():
        print(f"    {theme_name}: {count} 个")

    # 按等级统计
    level_stats = {}
    for content in all_contents:
        level = content.level
        if level not in level_stats:
            level_stats[level] = 0
        level_stats[level] += 1

    print("  各等级知识点数量:")
    level_names = {1: "初级", 2: "基础", 3: "进阶", 4: "高级"}
    for level in sorted(level_stats.keys()):
        print(f"    {level_names.get(level, f'{level}级')}: {level_stats[level]} 个")

except Exception as e:
    print(f"插入测试数据失败: {e}")
    db.rollback()

finally:
    db.close()