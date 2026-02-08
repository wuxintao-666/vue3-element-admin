# task_factory.py - 任务工厂类
from crewai import Task

def create_knowledge_task(chapter_info, knowledge_base_ref):
    """
    创建知识生成任务
    """
    knowledge_task = Task(
        description=f"""您是一位专业的前端开发导师，擅长为零基础学习者讲解前端知识。现在需要根据传入的知识点信息，为学生生成系统化的学习内容。

请根据以下知识点信息生成内容：
{knowledge_base_ref}
知识点ID：{chapter_info.get('id', 'unknown')}
知识点标题：{chapter_info['title']}
涉及的HTML/CSS/JS元素或属性：{', '.join(chapter_info.get('key_concepts', [])) if chapter_info.get('key_concepts') else "无特别指定"}

请编写适合零基础的学习内容，并严格按照以下 JSON 结构返回（不要添加任何额外说明、前后缀或解释文本）：

{{
  "topic_id": "{chapter_info.get('id', 'unknown')}",
  "title": "{chapter_info['title']}",
  "levels": [
    {{
      "level": 1,
      "description": "适合零基础入门，掌握核心概念与基本语法。不少于300字。"
    }},
    {{
      "level": 2,
      "description": "理解知识点常见的场景与组合用法，提升实践能力。不少于300字。"
    }},
    {{
      "level": 3,
      "description": "深入知识点的机制与性能优化，形成系统化认知。不少于300字。"
    }},
    {{
      "level": 4,
      "description": "综合实战与拓展题，必须包含示例代码，不少于300字。"
    }}
  ]
}}

生成要求：
1. 必须返回纯 JSON，不要包含任何额外文本。
2. description 字段中不允许出现标题格式（如"概念：""说明："等）。
3. 每个 description 必须直接以正文开头。
4. 专业术语必须解释清楚，让零基础也能理解。
5. 所有内容必须与前端开发及本知识点相关。
6. Level 4 必须包含完整且可运行的代码示例（HTML/CSS/JS 均可）。
7. 全部内容必须使用中文。
8. 最外层不要有```json```包裹。
        """,
        expected_output="结构化的学习内容 JSON",
        name=f"生成学习内容_{chapter_info['title']}"
    )
    return knowledge_task

def create_test_task(chapter_info, levels_description, starter_context, global_html_ref):
    """
    创建测试题生成任务
    """
    test_task = Task(
        description=f"""你是一名资深的HTML编程出题专家，请基于以下信息为学生生成测试题和配套答案。
【核心目标】：
设计一个逐步构建的系列测试题，最终目标是让学生逐步完成一个与全局教学HTML相似的完整项目。

【知识点标题】:
{chapter_info['title']}

【学习内容】:
{levels_description}

【起始代码】：
{starter_context}

【项目目标参考（全局教学HTML）】：
{global_html_ref}...

【本章设计原则】：
1. **渐进式构建**：本章的测试题应该基于学生已有的代码（起始代码），并逐步向全局教学HTML的目标代码靠拢
2. **增量开发**：不要重新设计整个页面，而是在现有基础上添加新功能或改进现有功能
3. **目标导向**：参考全局教学HTML中的相关部分，思考如何在本章实现其中的一部分功能
4. **适度挑战**：每章增加适量的新知识点，避免一次性引入太多内容

【生成要求】:
1. 你的输出必须是一个**合法的 JSON 对象**，不能包含 Markdown 代码块、注释或额外解释。
2. JSON 开头必须是 {{，结尾必须是 }}。
3. JSON 字段必须包含：
   - topic_id（值为 "{chapter_info.get('id', 'unknown')}"）
   - title（测试题标题）
   - description_md（任务描述，Markdown 格式，分步骤说明）
   - start_code（起始代码，如果是第一章则为空，否则应为上一章的答案代码，包含 html/css/js 的字典）
   - checkpoints（列表，包含验证规则）
   - answer（答案部分，包含完整的解答代码,请基于起始代码进行扩展，不要重新设计整个页面。主要任务是在现有基础上添加新功能）

4. 题目内容必须贴合"学习内容"
5. 每个测试题至少包含 **3 个检查点**，覆盖不同类型（元素存在性、文本内容、位置/层级结构）。
6. 任务要贴近真实网页开发场景，例如"个人网站介绍页""新闻文章页面"等。
【检查点类型定义】:
- **`assert_element`**: 检查元素是否存在。必需字段：`selector`, `assertion_type` (值为 "exists")
- **`assert_style`**: 检查元素样式。必需字段：`selector`, `css_property`, `assertion_type` ("equals", "contains", "greater_than", "less_than"), `value`
- **`assert_attribute`**: 检查元素属性。必需字段：`selector`, `attribute`, `assertion_type` ("exists", "equals", "contains"), `value` (可选)
- **`assert_text_content`**: 检查文本内容。必需字段：`selector`, `assertion_type` ("equals", "contains", "matches_regex"), `value`
- **`interaction_and_assert`**: 交互后断言。必需字段：`action_selector`, `action_type` ("click", "hover", "type_text"), `assertion` (嵌套断言对象)
- **`custom_script`**: 自定义脚本。必需字段：script

【答案部分要求】:
- **`html`**: 完整的解答HTML代码
- **`css`**: 完整的解答CSS样式代码（如果没有css代码，请设为空字符串""）
- **`js`**: 完整的解答JavaScript代码（如果没有JavaScript代码，请设为空字符串""）

【输出格式示例】（请严格遵循此结构，根据实际内容替换）:
{{
  "topic_id": "{chapter_info.get('id', 'unknown')}",
  "title": "创建个人博客页面",
  "description_md": "## 任务描述\\n请创建一个个人博客页面，要求如下：\\n\\n1. 使用HTML5语义化标签\\n2. 添加导航菜单\\n3. 创建内容区域\\n4. 添加页脚信息\\n\\n## 具体要求\\n- 必须有header、nav、main、footer标签\\n- 导航菜单至少包含3个链接\\n- 主要内容区域至少包含一个h2标题和两个段落",
  "start_code": {{
    "html": "<!DOCTYPE html>\\\\n<html lang=\\"zh-CN\\">\\\\n<head>\\\\n    <meta charset=\\"UTF-8\\">\\\\n    <title>我的网站</title>\\\\n</head>\\\\n<body>\\\\n    <div>这是一个简单的页面</div>\\\\n</body>\\\\n</html>",
    "css": "",
    "js": ""
  }},
  "checkpoints": [
    {{
      "name": "检查header元素",
      "type": "assert_element",
      "selector": "header",
      "assertion_type": "exists",
      "feedback": "请添加一个header元素作为页面头部"
    }},
    {{
      "name": "检查导航链接数量",
      "type": "assert_element",
      "selector": "nav a",
      "assertion_type": "count_greater_than",
      "value": 2,
      "feedback": "导航菜单应至少包含3个链接"
    }},
    {{
      "name": "检查h2标题内容",
      "type": "assert_text_content",
      "selector": "main h2",
      "assertion_type": "contains",
      "value": "博客",
      "feedback": "主要内容区域应包含一个含有'博客'文字的h2标题"
    }}
  ],
  "answer": {{
    "html": "<!DOCTYPE html>\\\\n<html lang=\\"zh-CN\\">\\\\n<head>\\\\n    <meta charset=\\"UTF-8\\">\\\\n    <meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1.0\\">\\\\n    <title>我的个人博客</title>\\\\n</head>\\\\n<body>\\\\n    <header>\\\\n        <h1>我的技术博客</h1>\\\\n    </header>\\\\n    \\\\n    <nav>\\\\n        <a href=\\"#\\">首页</a>\\\\n        <a href=\\"#about\\">关于我</a>\\\\n        <a href=\\"#contact\\">联系方式</a>\\\\n    </nav>\\\\n    \\\\n    <main>\\\\n        <h2>我的技术博客</h2>\\\\n        <p>这里分享我的学习心得和技术经验。</p>\\\\n        <p>专注于前端开发、JavaScript和现代Web技术。</p>\\\\n    </main>\\\\n    \\\\n    <footer>\\\\n        <p>© 2023 我的博客</p>\\\\n    </footer>\\\\n</body>\\\\n</html>",
    "css": "body {{ font-family: Arial, sans-serif; margin: 20px; }}",
    "js": ""
  }}
}}

请基于学习内容中的知识点设计测试题和配套答案，确保题目内容宽泛且实用，适合初学者练习。答案部分要包含完整、正确的代码，能够通过所有检查点。

        """,
        expected_output="结构化的测试题 JSON",
        name=f"生成测试题_{chapter_info['title']}"
    )
    return test_task

def create_example_task(knowledge_summary):
    """
    创建示例代码生成任务
    """
    example_task = Task(
        description=f"""请根据以下知识图谱信息生成一个完整的全局教学HTML页面。

【知识图谱摘要】:
{knowledge_summary}

【字数控制要求】：
1. 总有效教学内容（用户可见文本）控制在 800-1500 字之间
2. 代码注释约占整体内容的 20-30%
3. 结构分布建议：
   - HTML结构代码：40%
   - CSS样式代码：30%
   - JavaScript代码：15%
   - 注释说明：15%

【具体控制方法】：
1. 如果内容过长，请精简重复示例
2. 如果内容过短，请增加实用案例
3. 保持核心知识点覆盖完整
4. 确保代码简洁，避免冗余

请先估算字数，生成后检查是否符合要求。

【生成要求】:
1. 创建一个完整的HTML页面，包含DOCTYPE、html、head、body等基本结构
2. 根据知识图谱中的所有知识点，创建一个综合性的教学演示页面
3. 页面应该包含结构、表现、行为分离的完整示例
4. 为每个知识模块创建相应的演示区域，用注释说明这是哪个知识点的演示
5. 添加现代化的CSS样式，使页面美观、专业且易于理解
6. 包含适当的JavaScript交互功能，展示动态行为
7. 页面应该是一个完整的、可运行的教学演示，适合作为课程的全局展示
【输出格式】:
直接输出完整的HTML代码，不要包含任何额外的说明或代码块标记。
""",
        expected_output="完整的全局教学HTML代码"
    )
    return example_task

def create_task_functions():
    """
    创建任务工厂实例
    """
    return {
        'create_knowledge_task': create_knowledge_task,
        'create_test_task': create_test_task,
        'create_example_task': create_example_task
    }