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

【JSON Schema要求】：
响应必须严格遵循此schema：
{{
  "type": "object",
  "properties": {{
    "topic_id": {{"type": "string"}},
    "title": {{"type": "string"}},
    "levels": {{
      "type": "array",
      "items": {{
        "type": "object",
        "properties": {{
          "level": {{"type": "integer", "enum": [1,2,3,4]}},
          "description": {{"type": "string"}}
        }}
      }}
    }}
  }},
  "required": ["topic_id", "title", "levels"]
}}

【关键格式要求】：
1. **必须返回纯JSON格式**，不要包含任何额外文本、注释、```json```标记或代码块
2. **description字段必须使用Markdown格式**，以支持后续渲染
3. **每个description必须包含以下Markdown元素**：
   - 使用`**加粗**`强调关键术语
   - 使用`- `创建列表项
   - 使用`1. `创建有序列表
   - 使用`>` 添加引用说明
   - 使用反引号包裹`代码片段`或```代码块```
4. **Level 4必须包含完整可运行的代码示例**，使用```html/css/javascript标记语言
5. **description字符串中的换行符必须使用`\\n`表示**，以确保JSON解析正确

【内容要求】：
1. 每个description不少于300字
2. Level 1：适合零基础入门，掌握核心概念与基本语法
3. Level 2：理解知识点常见的场景与组合用法，提升实践能力
4. Level 3：深入知识点的机制与性能优化，形成系统化认知
5. Level 4：综合实战与拓展题，必须包含完整代码示例

【Markdown渲染指导】：
- 使用空行分隔段落（在JSON中用`\\n\\n`表示空行）
- 重要概念使用**加粗**突出
- 代码示例必须使用```代码块格式
- 步骤说明使用1. 2. 3. 有序列表
- 关键要点使用- 无序列表

【JSON字符串转义要求】：
在JSON字符串中必须正确转义：
- 换行符：`\\n`
- 回车符：`\\r`  
- 制表符：`\\t`
- 双引号：`\\"`
- 反斜杠：`\\\\`
- Unicode转义：`\\uXXXX` (对于特殊字符)

【禁止项】：
1. 不要在任何字段中使用"概念："、"说明："等标题格式
2. 不要使用HTML标签，只使用Markdown语法
3. 不要在最外层包裹```json```标记
4. 不要添加"输出："、"JSON："等前缀
5. 不要在JSON字符串中使用未转义的双引号

【示例结构参考】：
{{
  "topic_id": "1_1",
  "title": "HTML基础",
  "levels": [
    {{
      "level": 1,
      "description": "HTML是网页的骨架，用于定义网页内容的结构。**标签**是HTML的基本构建块...\\n\\n关键特性包括：\\n- 标签由尖括号包围\\n- 大多数标签成对出现\\n- 标签可以包含属性\\n\\n> 注意：HTML不负责样式，只负责结构。"
    }},
    {{
      "level": 2,
      "description": "在实际开发中，HTML需要与CSS和JavaScript配合使用...\\n\\n常用组合模式：\\n1. 使用`<div>`创建容器\\n2. 添加CSS类名控制样式\\n3. 通过id属性供JavaScript操作\\n\\n**语义化标签**如`<header>`、`<nav>`、`<main>`等能提高代码可读性..."
    }},
    {{
      "level": 3,
      "description": "深入了解HTML的解析机制和性能优化...\\n\\n**DOM树构建过程**：\\n- 浏览器解析HTML字节流\\n- 构建DOM节点树\\n- 应用CSS样式\\n- 计算布局和绘制\\n\\n优化建议：\\n- 减少嵌套层级\\n- 避免使用废弃标签\\n- 合理使用异步加载..."
    }},
    {{
      "level": 4,
      "description": "综合实战：创建一个完整的用户注册表单\\n\\n```html\\n<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>用户注册</title>\\n    <style>\\n        /* CSS样式 */\\n        .form-container {{ margin: 20px; }}\\n    </style>\\n</head>\\n<body>\\n    <form id=\\"registerForm\\">\\n        <label for=\\"username\\">用户名：</label>\\n        <input type=\\"text\\" id=\\"username\\" required>\\n    </form>\\n    <script>\\n        // JavaScript验证\\n        document.querySelector('#registerForm').addEventListener('submit', function(e) {{\\n            e.preventDefault();\\n            console.log('表单提交');\\n        }});\\n    </script>\\n</body>\\n</html>\\n```\\n\\n代码说明：\\n1. 使用`<form>`元素包裹表单\\n2. `required`属性确保必填项\\n3. JavaScript添加表单验证逻辑..."
    }}
  ]
}}
  现在请直接返回JSON格式的响应，不要包含任何其他内容。""",
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
设计一个逐步构建的系列测试题，最终目标是让学生逐步完成一个与示例HTML相似的完整项目。

【知识点标题】:
{chapter_info['title']}

【学习内容】:
{levels_description}

【起始代码】：
{starter_context}

【项目目标参考（示例HTML）】：
{global_html_ref}...

【本章设计原则】：
1. **渐进式构建**：本章的测试题应该基于学生已有的代码（起始代码），并逐步向示例HTML的目标代码靠拢
2. **增量开发**：不要重新设计整个页面，而是在现有基础上添加新功能或改进现有功能
3. **目标导向**：参考示例HTML中的相关部分，思考如何在本章实现其中的一部分功能
4. **适度挑战**：每章增加适量的新知识点，避免一次性引入太多内容

【输出格式要求】：
1. **必须返回纯JSON格式**，直接以 {{ 开头，以 }} 结尾
2. **不要包含任何Markdown代码块标记**（如```json```）
3. **不要包含任何额外解释、注释或说明文本**

【JSON字段规范】：
- `topic_id`: 固定值为 "{chapter_info.get('id', 'unknown')}"
- `title`: 测试题标题（纯文本）
- `description_md`: 任务描述，**必须使用Markdown格式**，支持换行、列表、代码块等
- `start_code`: 起始代码（字典类型，包含html、css、js三个键值）
- `checkpoints`: 检查点列表（字典类型，每个检查点是一个对象）
- `answer`: 答案部分（字典类型，包含html、css、js三个键值）

【Markdown格式要求】：
`description_md` 字段必须使用以下Markdown语法：
- 使用 `##`、`###` 创建标题
- 使用 `-` 或 `1.` 创建列表
- 使用 `**加粗**` 或 `*斜体*` 强调文本
- 使用反引号包裹 `代码片段`
- 使用 ```语言 代码块``` 格式化代码示例
- 使用空行分隔段落

【JSON字符串转义要求】：
在JSON字符串中必须正确转义：
- 换行符：`\\n`
- 回车符：`\\r`  
- 制表符：`\\t`
- 双引号：`\\"`
- 反斜杠：`\\\\`
- Unicode转义：`\\uXXXX` (对于特殊字符)


【检查点设计】：
至少包含3个检查点，类型包括：
1. **元素存在性检查**（assert_element）
2. **内容/属性检查**（assert_text_content 或 assert_attribute）
3. **样式/布局检查**（assert_style）或 **交互检查**（interaction_and_assert）

【答案设计原则】：
1. 基于起始代码进行扩展，不要重新设计整个页面
2. 添加的功能应该对应本章学习内容
3. 代码必须能通过所有检查点验证

【严格的JSON输出指令】：
1. 你的响应必须是且仅是一个有效的JSON对象
2. 不要在最外层添加任何文本，包括"```json"标记
3. 不要添加类似"这是你要的JSON："的前缀
4. 确保JSON语法正确，可以立即被 `JSON.loads()` 解析
5. 题目内容必须贴合"学习内容"
6. 每个测试题至少包含 **3 个检查点**，覆盖不同类型（元素存在性、文本内容、位置/层级结构）。
7. 任务要贴近真实网页开发场景，例如"个人网站介绍页""新闻文章页面"等。

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

【JSON Schema要求】：
响应必须严格遵循此schema：
{{
  "type": "object",
  "properties": {{
    "topic_id": {{"type": "string"}},
    "title": {{"type": "string"}},
    "description_md": {{"type": "string"}},
    "start_code": {{
      "type": "object",
      "properties": {{
        "html": {{"type": "string"}},
        "css": {{"type": "string"}},
        "js": {{"type": "string"}}
      }},
      "required": ["html", "css", "js"]
    }},
    "checkpoints": {{
      "type": "array",
      "items": {{
        "type": "object",
        "properties": {{
          "name": {{"type": "string"}},
          "type": {{"type": "string", "enum": ["assert_element", "assert_style", "assert_attribute", "assert_text_content", "interaction_and_assert", "custom_script"]}},
          "selector": {{"type": "string"}},
          "assertion_type": {{"type": "string"}},
          "value": {{}},  // 可选字段
          "css_property": {{"type": "string"}},  // 可选字段
          "attribute": {{"type": "string"}},     // 可选字段
          "action_selector": {{"type": "string"}}, // 可选字段
          "action_type": {{"type": "string"}},   // 可选字段
          "assertion": {{}}, // 可选字段
          "script": {{"type": "string"}},        // 可选字段
          "feedback": {{"type": "string"}}
        }},
        "required": ["name", "type", "assertion_type", "feedback"]
      }}
    }},
    "answer": {{
      "type": "object",
      "properties": {{
        "html": {{"type": "string"}},
        "css": {{"type": "string"}},
        "js": {{"type": "string"}}
      }},
      "required": ["html", "css", "js"]
    }}
  }},
  "required": ["topic_id", "title", "description_md", "start_code", "checkpoints", "answer"]
}}

【输出格式示例】（请严格遵循此结构，根据实际内容替换）:
{{
  "topic_id": "{chapter_info.get('id', 'unknown')}",
  "title": "创建个人博客页面",
  "description_md": "## 任务描述\\n请创建一个个人博客页面，要求如下：\\n\\n1. 使用HTML5语义化标签\\n2. 添加导航菜单\\n3. 创建内容区域\\n4. 添加页脚信息\\n\\n## 具体要求\\n- 必须有header、nav、main、footer标签\\n- 导航菜单至少包含3个链接\\n- 主要内容区域至少包含一个h2标题和两个段落",
  "start_code": {{
    "html": "<!DOCTYPE html>\\n<html lang=\\"zh-CN\\">\\n<head>\\n    <title>测试</title>\\n</head>",
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
    "html": "<!DOCTYPE html>\\n<html lang=\\"zh-CN\\">\\n<head>\\n    <meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1.0\\">\\n    <title>答案</title>\\n</head>",
    "css": "",
    "js": ""
  }}
}}

请基于学习内容中的知识点设计测试题和配套答案，确保题目内容宽泛且实用，适合初学者练习。答案部分要包含完整、正确的代码，能够通过所有检查点。


现在请直接返回JSON格式的响应，不要包含任何其他内容。""",
        expected_output="结构化的测试题 JSON",
        name=f"生成测试题_{chapter_info['title']}"
    )
    return test_task

def create_knowledge_point_task(knowledge_point_info, knowledge_base_ref):
    """
    创建单个知识点的内容生成任务
    """
    knowledge_point_task = Task(
        description=f"""您是一位专业的前端开发导师，擅长为零基础学习者讲解前端知识。现在需要根据传入的知识点信息，为学生生成系统化的学习内容。

请根据以下知识点信息生成内容：
{knowledge_base_ref}
知识点ID：{knowledge_point_info.get('id', 'unknown')}
知识点标题：{knowledge_point_info['label']}
涉及的HTML/CSS/JS元素或属性：{', '.join(knowledge_point_info.get('select_element', [])) if knowledge_point_info.get('select_element') else "无特别指定"}

请编写适合零基础的学习内容，并严格按照以下 JSON 结构返回（不要添加任何额外说明、前后缀或解释文本）：

【JSON Schema要求】：
响应必须严格遵循此schema：
{{
  "type": "object",
  "properties": {{
    "topic_id": {{"type": "string"}},
    "title": {{"type": "string"}},
    "levels": {{
      "type": "array",
      "items": {{
        "type": "object",
        "properties": {{
          "level": {{"type": "integer", "enum": [1,2,3,4]}},
          "description": {{"type": "string"}}
        }}
      }}
    }}
  }},
  "required": ["topic_id", "title", "levels"]
}}

【关键格式要求】：
1. **必须返回纯JSON格式**，不要包含任何额外文本、注释、```json```标记或代码块
2. **description字段必须使用Markdown格式**，以支持后续渲染
3. **每个description必须包含以下Markdown元素**：
   - 使用`**加粗**`强调关键术语
   - 使用`- `创建列表项
   - 使用`1. `创建有序列表
   - 使用`>` 添加引用说明
   - 使用反引号包裹`代码片段`或```代码块```
4. **Level 4必须包含完整可运行的代码示例**，使用```html/css/javascript标记语言
5. **description字符串中的换行符必须使用`\\n`表示**，以确保JSON解析正确

【内容要求】：
1. 每个description不少于300字
2. Level 1：适合零基础入门，掌握核心概念与基本语法
3. Level 2：理解知识点常见的场景与组合用法，提升实践能力
4. Level 3：深入知识点的机制与性能优化，形成系统化认知
5. Level 4：综合实战与拓展题，必须包含完整代码示例

【Markdown渲染指导】：
- 使用空行分隔段落（在JSON中用`\\n\\n`表示空行）
- 重要概念使用**加粗**突出
- 代码示例必须使用```代码块格式
- 步骤说明使用1. 2. 3. 有序列表
- 关键要点使用- 无序列表

【JSON字符串转义要求】：
在JSON字符串中必须正确转义：
- 换行符：`\\n`
- 回车符：`\\r`  
- 制表符：`\\t`
- 双引号：`\\"`
- 反斜杠：`\\\\`
- Unicode转义：`\\uXXXX` (对于特殊字符)

【禁止项】：
1. 不要在任何字段中使用"概念："、"说明："等标题格式
2. 不要使用HTML标签，只使用Markdown语法
3. 不要在最外层包裹```json```标记
4. 不要添加"输出："、"JSON："等前缀
5. 不要在JSON字符串中使用未转义的双引号

【示例结构参考】：
{{
  "topic_id": "1_1",
  "title": "HTML基础",
  "levels": [
    {{
      "level": 1,
      "description": "HTML是网页的骨架，用于定义网页内容的结构。**标签**是HTML的基本构建块...\\n\\n关键特性包括：\\n- 标签由尖括号包围\\n- 大多数标签成对出现\\n- 标签可以包含属性\\n\\n> 注意：HTML不负责样式，只负责结构。"
    }},
    {{
      "level": 2,
      "description": "在实际开发中，HTML需要与CSS和JavaScript配合使用...\\n\\n常用组合模式：\\n1. 使用`<div>`创建容器\\n2. 添加CSS类名控制样式\\n3. 通过id属性供JavaScript操作\\n\\n**语义化标签**如`<header>`、`<nav>`、`<main>`等能提高代码可读性..."
    }},
    {{
      "level": 3,
      "description": "深入了解HTML的解析机制和性能优化...\\n\\n**DOM树构建过程**：\\n- 浏览器解析HTML字节流\\n- 构建DOM节点树\\n- 应用CSS样式\\n- 计算布局和绘制\\n\\n优化建议：\\n- 减少嵌套层级\\n- 避免使用废弃标签\\n- 合理使用异步加载..."
    }},
    {{
      "level": 4,
      "description": "综合实战：创建一个完整的用户注册表单\\n\\n```html\\n<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>用户注册</title>\\n    <style>\\n        /* CSS样式 */\\n        .form-container {{ margin: 20px; }}\\n    </style>\\n</head>\\n<body>\\n    <form id=\\"registerForm\\">\\n        <label for=\\"username\\">用户名：</label>\\n        <input type=\\"text\\" id=\\"username\\" required>\\n    </form>\\n    <script>\\n        // JavaScript验证\\n        document.querySelector('#registerForm').addEventListener('submit', function(e) {{\\n            e.preventDefault();\\n            console.log('表单提交');\\n        }});\\n    </script>\\n</body>\\n</html>\\n```\\n\\n代码说明：\\n1. 使用`<form>`元素包裹表单\\n2. `required`属性确保必填项\\n3. JavaScript添加表单验证逻辑..."
    }}
  ]
}}
  现在请直接返回JSON格式的响应，不要包含任何其他内容。""",
        expected_output="""结构化的学习内容 JSON"""
    )

    return knowledge_point_task

def create_knowledge_point_test_task(knowledge_point_info, levels_description, global_html_ref):
    """
    创建单个知识点的测试题生成任务
    """
    test_task = Task(
        description=f"""你是一名资深的HTML编程出题专家，请基于以下信息为学生生成测试题和配套答案。

【核心目标】：
设计一个针对特定知识点的测试题，帮助学生巩固对该知识点的理解和应用。

【知识点信息】:
ID: {knowledge_point_info.get('id', 'unknown')}
标题: {knowledge_point_info['label']}
相关元素: {', '.join(knowledge_point_info.get('select_element', [])) if knowledge_point_info.get('select_element') else "无特别指定"}

【学习内容】:
{levels_description}


【输出格式要求】：
1. **必须返回纯JSON格式**，直接以 {{ 开头，以 }} 结尾
2. **不要包含任何Markdown代码块标记**（如```json```）
3. **不要包含任何额外解释、注释或说明文本**

【JSON字段规范】：
- `topic_id`: 固定值为 "{knowledge_point_info.get('id', 'unknown')}"
- `title`: 测试题标题（纯文本）
- `description_md`: 任务描述，**必须使用Markdown格式**，支持换行、列表、代码块等
- `start_code`: 起始代码（为空字符串""）
- `checkpoints`: 检查点列表（字典类型，每个检查点是一个对象）
- `answer`: 答案部分（字典类型，包含html、css、js三个键值）

【Markdown格式要求】：
`description_md` 字段必须使用以下Markdown语法：
- 使用 `##`、`###` 创建标题
- 使用 `-` 或 `1.` 创建列表
- 使用 `**加粗**` 或 `*斜体*` 强调文本
- 使用反引号包裹 `代码片段`
- 使用 ```语言 代码块``` 格式化代码示例
- 使用空行分隔段落

【代码字段要求】：
`start_code` 和 `answer` 中的字符串必须：
1. **必须使用正确的JSON转义字符**：
   - 换行符：`\\n`（JSON中显示为`\n`）
   - 双引号：`\"`（JSON中显示为`"`）
   - 反斜杠：`\\`（JSON中显示为`\`）
2. 保持代码缩进结构

【检查点设计】：
至少包含3个检查点，类型包括：
1. **元素存在性检查**（assert_element）
2. **内容/属性检查**（assert_text_content 或 assert_attribute）
3. **样式/布局检查**（assert_style）或 **交互检查**（interaction_and_assert）

【答案设计原则】：
1. 基于起始代码进行扩展，不要重新设计整个页面
2. 添加的功能应该对应本章学习内容
3. 代码必须能通过所有检查点验证

【严格的JSON输出指令】：
1. 你的响应必须是且仅是一个有效的JSON对象
2. 不要在最外层添加任何文本，包括"```json"标记
3. 不要添加类似"这是你要的JSON："的前缀
4. 确保JSON语法正确，可以立即被 `JSON.loads()` 解析
5. 题目内容必须贴合"学习内容"
6. 每个测试题至少包含 **3 个检查点**，覆盖不同类型（元素存在性、文本内容、位置/层级结构）。
7. 任务要贴近真实网页开发场景，例如"个人网站介绍页""新闻文章页面"等。

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

【JSON字符串转义要求】：
在JSON字符串中必须正确转义：
- 换行符：`\\n`
- 回车符：`\\r`  
- 制表符：`\\t`
- 双引号：`\\"`
- 反斜杠：`\\\\`
- Unicode转义：`\\uXXXX` (对于特殊字符)

【JSON Schema要求】：
响应必须严格遵循此schema：
{{
  "type": "object",
  "properties": {{
    "topic_id": {{"type": "string"}},
    "title": {{"type": "string"}},
    "description_md": {{"type": "string"}},
    "start_code": {{
      "type": "object",
      "properties": {{
        "html": {{"type": "string"}},
        "css": {{"type": "string"}},
        "js": {{"type": "string"}}
      }},
      "required": ["html", "css", "js"]
    }},
    "checkpoints": {{
      "type": "array",
      "items": {{
        "type": "object",
        "properties": {{
          "name": {{"type": "string"}},
          "type": {{"type": "string", "enum": ["assert_element", "assert_style", "assert_attribute", "assert_text_content", "interaction_and_assert", "custom_script"]}},
          "selector": {{"type": "string"}},
          "assertion_type": {{"type": "string"}},
          "value": {{}},  // 可选字段
          "css_property": {{"type": "string"}},  // 可选字段
          "attribute": {{"type": "string"}},     // 可选字段
          "action_selector": {{"type": "string"}}, // 可选字段
          "action_type": {{"type": "string"}},   // 可选字段
          "assertion": {{}}, // 可选字段
          "script": {{"type": "string"}},        // 可选字段
          "feedback": {{"type": "string"}}
        }},
        "required": ["name", "type", "assertion_type", "feedback"]
      }}
    }},
    "answer": {{
      "type": "object",
      "properties": {{
        "html": {{"type": "string"}},
        "css": {{"type": "string"}},
        "js": {{"type": "string"}}
      }},
      "required": ["html", "css", "js"]
    }}
  }},
  "required": ["topic_id", "title", "description_md", "start_code", "checkpoints", "answer"]
}}

【输出格式示例】（请严格遵循此结构，根据实际内容替换）:
{{
  "topic_id": "{knowledge_point_info.get('id', 'unknown')}",
  "title": "创建个人博客页面",
  "description_md": "## 任务描述\\n请创建一个个人博客页面，要求如下：\\n\\n1. 使用HTML5语义化标签\\n2. 添加导航菜单\\n3. 创建内容区域\\n4. 添加页脚信息\\n\\n## 具体要求\\n- 必须有header、nav、main、footer标签\\n- 导航菜单至少包含3个链接\\n- 主要内容区域至少包含一个h2标题和两个段落",
  "start_code": {{
    "html": "",
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
    "html": "<!DOCTYPE html>\\n<html lang=\\"zh-CN\\">\\n<head>\\n    <meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1.0\\">\\n    <title>答案</title>\\n</head>",
    "css": "",
    "js": ""
  }}
}}

请基于学习内容中的知识点设计测试题和配套答案，确保题目内容宽泛且实用，适合初学者练习。答案部分要包含完整、正确的代码，能够通过所有检查点。

现在请直接返回JSON格式的响应，不要包含任何其他内容。""",
        expected_output="""结构化的测试题 JSON"""
    )

    return test_task

def create_example_task(knowledge_summary):
    """
    创建示例代码生成任务
    """
    example_task = Task(
        description=f"""请根据以下学习路径信息生成一个完整的示例html页面。

【知识图谱摘要】:
{knowledge_summary}

【字数控制要求】：
1. 总有效教学内容（用户可见文本）控制在 100-200 字之间
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
【生成要求】
 我只需要HTML代码，不要任何其他内容。
 请生成一个完整的、可独立运行的HTML文件，要求：
  1. 包含完整的HTML5文档结构
  2. 所有CSS写在<style>标签内
  3. 所有JavaScript写在<script>标签内
  4. 代码简洁高效，无冗余
  5. 输出时不要包含任何注释、解释或markdown标记

立即开始输出HTML代码，从<!DOCTYPE html>开始：
""",
        expected_output="完整的html代码"
    )
    return example_task

def create_task_functions():
    """
    创建任务工厂实例
    """
    return {
        'create_knowledge_task': create_knowledge_task,
        'create_test_task': create_test_task,
        'create_example_task': create_example_task,
        'create_knowledge_point_task': create_knowledge_point_task,
        'create_knowledge_point_test_task': create_knowledge_point_test_task
    }