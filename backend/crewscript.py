# mvp_course_generator.py
import os
import json
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# 禁用CrewAI遥测，避免SSL连接错误
os.environ["CREWAI_TELEMETRY"] = "false"

# ==================== 1. 配置魔搭API ====================
os.environ["DASHSCOPE_API_KEY"] = "sk-7581f392cad348b5bb60384d15a7a064"
os.environ["OPENAI_API_BASE"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
os.environ["MODEL_NAME"] = "deepseek-v3.2"

print("🚀 魔搭API配置就绪，开始构建生成引擎...")

# ==================== 2. 创建LLM实例（不同任务使用不同温度）===================
# 知识生成：需要准确性和结构化，使用较低温度
llm_knowledge = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    temperature=0.3,
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)

# 测试题生成：需要创造性但保持结构，使用中等温度
llm_test = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    temperature=0.6,
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)

# 示例代码生成：需要实用性和创造性，使用中等温度
llm_example = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    temperature=0.7,
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)

# ==================== 3. 定义数据结构（Pydantic模型）====================
# 注意：这里只定义最核心的字段，后续可扩展
class ChapterHtml(BaseModel):
    chapter_title: str
    learning_objectives: List[str] = []
    html_code: Any = Field(description="完整的HTML教学代码，包含内联CSS和JS")
    core_concepts_demo: str = Field(description="对代码如何演示核心概念的简要说明")

class KnowledgePoint(BaseModel):
    point_title: str
    detailed_explanation: str
    key_terms: List[str] = []

class KnowledgePointsList(BaseModel):
    points: List[KnowledgePoint] = Field(description="知识点列表")

class TestQuestion(BaseModel):
    question_text: str
    question_type: str = "practical"  # practical | quiz
    starter_code: Any = Field(description="学生开始时看到的代码")
    target_output_description: str = Field(description="期望学生实现的功能描述")
    reference_solution: Any = Field(description="完整的参考答案代码")

# ==================== 4. 创建核心Agent（通用角色）====================
# 提示词先保持简洁，后续根据效果调整
frontend_mentor = Agent(
    role="前端教学开发专家",
    goal="根据需求创建清晰、可运行的教学HTML示例",
    backstory="你是一位经验丰富的前端开发者和教师，擅长用最小化的可运行代码片段演示复杂概念。",
    llm=llm_example,  # 使用示例代码生成温度
    verbose=False,
    allow_delegation=False
)

knowledge_expert = Agent(
    role="知识结构化专家",
    goal="将知识图谱和资料转化为结构化的知识点",
    backstory="你是一位知识管理顾问，擅长从复杂信息中提取核心概念并清晰表述。",
    llm=llm_knowledge,  # 使用知识生成温度
    verbose=False,
    allow_delegation=False
)

test_designer = Agent(
    role="编程练习题设计师",
    goal="设计基于代码的实践性测试题",
    backstory="你专长为编程课程设计循序渐进、可实操的编码练习题，注重从已有代码到目标代码的转变。",
    llm=llm_test,  # 使用测试题生成温度
    verbose=False,
    allow_delegation=False
)

# ==================== 4. 创建示例代码生成Agent ====================
example_generator = Agent(
    role="前端示例代码生成专家",
    goal="根据知识图谱内容生成高质量的教学示例代码",
    backstory="你是一位经验丰富的教学设计师，擅长根据知识图谱分析需求并创建实用的前端代码示例。",
    llm=llm_example,  # 使用示例代码生成温度
    verbose=False,
    allow_delegation=False
)

print("✅ 核心Agent创建完成（包含示例代码生成器）")

# ==================== 5. 定义示例代码生成任务 ====================
def generate_example_from_knowledge_graph(kg_file, agent):
    """使用AI agent根据知识图谱生成示例代码"""

    try:
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
    except Exception as e:
        print(f"读取知识图谱失败: {e}")
        return get_default_example()

    # 准备知识图谱摘要
    nodes_summary = []
    for node in kg_data.get('nodes', []):
        node_data = node.get('data', {})
        if node_data.get('type') == 'knowledge':
            label = node_data.get('label', '')
            elements = node_data.get('select_element', [])
            nodes_summary.append(f"- {label} (相关元素: {', '.join(elements) if elements else '无'})")

    knowledge_summary = "\n".join(nodes_summary)
    print(f"知识图谱摘要：\n{knowledge_summary}")
    # 创建生成全局教学HTML的任务
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
        agent=agent,
        expected_output="完整的全局教学HTML代码"
    )
    print("task已经构建...")
    # 执行任务
    try:
        example_crew = Crew(
            agents=[agent],
            tasks=[example_task],
            process="sequential",
            verbose=True,
            name="全局教学HTML生成Crew"
        )

        result = example_crew.kickoff()
  
        # 提取HTML代码（复用现有的extract_html_code函数）
        example_html = ""
        if result:
            example_html = extract_html_code(str(result))
        print("HTML代码:"+example_html)
        print("长度："+str(len(example_html))+"字")
        # 使用固定的知识库描述
        knowledge_base = """
HTML（超文本标记语言）是构建网页的基础。HTML元素由标签、属性和内容组成。
常用标签：<h1>-<h6>标题，<p>段落，<a>链接，<img>图片，<div>容器。
CSS用于样式设计，JavaScript用于交互逻辑。
网页开发遵循结构、表现、行为分离的原则。
"""

        return example_html, knowledge_base

    except Exception as e:
        print(f"生成示例代码失败: {e}")
        return get_default_example()

def get_default_example():
    """获取默认示例"""
    example_html = """<!DOCTYPE html>
<html>
<head>
    <title>示例页面</title>
    <style>body { font-family: Arial; margin: 20px; }</style>
</head>
<body>
    <h1>这是一个示例</h1>
    <p>演示了基本的HTML结构。</p>
    <button onclick="alert('Hello')">点击我</button>
</body>
</html>"""

    knowledge_base = """
HTML（超文本标记语言）是构建网页的基础。HTML元素由标签、属性和内容组成。
常用标签：<h1>-<h6>标题，<p>段落，<a>链接，<img>图片，<div>容器。
CSS用于样式设计，JavaScript用于交互逻辑。
网页开发遵循结构、表现、行为分离的原则。
"""
    return example_html, knowledge_base

# ==================== 5. 单独生成全局教学HTML ====================
def generate_global_html(example_html_ref, knowledge_base_ref):
    """
    生成全局教学HTML，基于知识图谱和HTML示例
    """
    print("🎨 正在生成全局教学HTML...")

    html_task = Task(
        description=f"""基于提供的知识图谱创建完整的教学演示HTML页面。

        知识图谱内容：
        {knowledge_base_ref}

        参考示例风格（但不直接复制）：
        {example_html_ref[:500]}...

        要求：
        - 单个HTML文件，包含内联的<style>和<script>
        - 代码简洁，有清晰的注释
        - 根据知识图谱内容智能选择和演示核心概念
        - 确保代码可直接运行
        - 创建一个综合性的示例页面，展示HTML、CSS、JavaScript的结合使用
        """,
        agent=frontend_mentor,
        expected_output="一个完整的、可运行的HTML文件代码",
        name="生成全局教学HTML"
    )

    # 执行任务
    crew = Crew(
        agents=[frontend_mentor],
        tasks=[html_task],
        process="sequential",
        verbose=True,  # 启用调试信息
        name="全局HTML生成Crew"
    )

    result = crew.kickoff()

    # 提取HTML代码
    global_html = ""
    if result:
        # CrewOutput对象可以直接转换为字符串或访问其属性
        html_output = str(result)
        import re

        # 提取代码块
        html_pattern = r'```html\s*(.*?)\s*```'
        match = re.search(html_pattern, html_output, re.DOTALL)
        if match:
            global_html = match.group(1).strip()
        else:
            code_pattern = r'```\s*(.*?)\s*```'
            match = re.search(code_pattern, html_output, re.DOTALL)
            if match:
                global_html = match.group(1).strip()

    print("✅ 全局教学HTML生成完成")
    return global_html

def extract_html_code(text):
    """从文本中提取HTML代码，支持新的JSON格式"""
    if not text:
        return ""

    import re
    import html
    import json

    # 先解码可能的HTML实体
    decoded_text = html.unescape(text)

    # 首先尝试解析JSON格式（新的测试题格式）
    try:
        # 查找JSON对象
        json_start = decoded_text.find('{')
        json_end = decoded_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = decoded_text[json_start:json_end]
            test_data = json.loads(json_str)

            # 从新的JSON格式中提取答案
            if 'answer' in test_data:
                answer = test_data['answer']
                html_code = answer.get('html', '')
                css_code = answer.get('css', '')
                js_code = answer.get('js', '')

                # 组合成完整的HTML
                full_html = html_code
                if css_code:
                    # 如果有CSS，插入到head中
                    if '<head>' in full_html and '</head>' in full_html:
                        head_end = full_html.find('</head>')
                        full_html = full_html[:head_end] + f'\n<style>\n{css_code}\n</style>\n' + full_html[head_end:]
                    else:
                        full_html = f'<style>\n{css_code}\n</style>\n' + full_html

                if js_code:
                    # 如果有JS，插入到body末尾
                    if '</body>' in full_html:
                        body_end = full_html.find('</body>')
                        full_html = full_html[:body_end] + f'\n<script>\n{js_code}\n</script>\n' + full_html[body_end:]
                    else:
                        full_html += f'\n<script>\n{js_code}\n</script>'

                return full_html.strip()
    except (json.JSONDecodeError, KeyError, ValueError):
        # 如果JSON解析失败，继续使用原来的方法
        pass

    # 回退到原来的方法：提取代码块
    patterns = [
        r'```html\s*(.*?)\s*```',  # 首先尝试html标记的代码块
        r'```\s*(.*?)\s*```',      # 然后尝试普通代码块
    ]

    for pattern in patterns:
        matches = re.findall(pattern, decoded_text, re.DOTALL)
        if matches:
            # 取最后一个匹配（通常是答案代码）
            code = matches[-1].strip()
            # 清理常见的转义序列
            code = code.replace('\\\\n', '\n').replace('\\n', '\n')
            code = code.replace('\\\\t', '\t').replace('\\t', '\t')
            return code

    # 如果没有代码块，直接查找HTML结构
    html_start = decoded_text.find('<!DOCTYPE')
    if html_start == -1:
        html_start = decoded_text.find('<html')

    if html_start != -1:
        html_end = decoded_text.find('</html>', html_start)
        if html_end != -1:
            code = decoded_text[html_start:html_end+7].strip()
            # 清理转义
            code = code.replace('\\\\n', '\n').replace('\\n', '\n')
            code = code.replace('\\\\t', '\t').replace('\\t', '\t')
            return code

    # 返回清理后的文本
    cleaned = decoded_text.replace('\\\\n', '\n').replace('\\n', '\n')
    cleaned = cleaned.replace('\\\\t', '\t').replace('\\t', '\t')
    return cleaned.strip()

def parse_json_from_text(text):
    """从文本中解析JSON对象"""
    if not text:
        return None
    
    # 如果是字符串，尝试解析为JSON
    if isinstance(text, str):
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            try:
                # 查找第一个{和最后一个}
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
            except:
                pass
    
    # 如果已经是字典，直接返回
    elif isinstance(text, dict):
        return text
    
    return None
def extract_answer_code_from_structured_json(data):
    """从结构化数据中提取答案代码"""
    if not data:
        print("❌ 数据为空")
        return ""
    
    try:
        # 解析数据
        if isinstance(data, str):
            # 如果是字符串，尝试解析
            json_data = parse_json_from_text(data)
            if not json_data:
                print("❌ 无法从字符串解析JSON")
                return ""
        elif isinstance(data, dict):
            json_data = data
        else:
            print(f"❌ 不支持的数据类型: {type(data)}")
            return ""
        
        # 检查是否包含answer字段
        if "answer" not in json_data:
            # 尝试查找其他可能的字段名
            possible_keys = ["solution", "reference", "code", "result"]
            for key in possible_keys:
                if key in json_data:
                    # 直接返回这个字段的值
                    if isinstance(json_data[key], dict):
                        return build_html_from_code_dict(json_data[key])
                    else:
                        return str(json_data[key])
            
            print("❌ JSON中没有找到answer字段")
            print(f"JSON内容: {json.dumps(json_data, indent=2)[:500]}...")
            return ""
        
        answer = json_data["answer"]
        
        # 如果answer是字符串，直接返回
        if isinstance(answer, str):
            return answer
        
        # 如果answer是字典，提取各部分
        if isinstance(answer, dict):
            return build_html_from_code_dict(answer)
        
        # 其他情况，转换为字符串
        return str(answer)
        
    except Exception as e:
        print(f"❌ 从JSON提取答案代码失败: {e}")
        import traceback
        traceback.print_exc()
        return ""
def build_html_from_code_dict(code_dict):
    """从代码字典构建完整的HTML"""
    if not isinstance(code_dict, dict):
        return str(code_dict)
    
    html_code = code_dict.get("html", "")
    css_code = code_dict.get("css", "")
    js_code = code_dict.get("js", "")
    
    # 如果html_code已经是完整的HTML文档，直接返回
    if html_code.strip().startswith("<!DOCTYPE") or html_code.strip().startswith("<html"):
        # 但可能需要插入CSS和JS
        full_html = html_code
        
        # 插入CSS
        if css_code and "<style>" not in full_html:
            if "</head>" in full_html:
                head_end = full_html.find("</head>")
                full_html = full_html[:head_end] + f"\n<style>\n{css_code}\n</style>" + full_html[head_end:]
            else:
                # 在html标签后添加head
                if "<html" in full_html and ">" in full_html:
                    html_end = full_html.find(">", full_html.find("<html")) + 1
                    full_html = full_html[:html_end] + f"\n<head>\n<style>\n{css_code}\n</style>\n</head>" + full_html[html_end:]
        
        # 插入JS
        if js_code and "<script>" not in full_html:
            if "</body>" in full_html:
                body_end = full_html.find("</body>")
                full_html = full_html[:body_end] + f"\n<script>\n{js_code}\n</script>" + full_html[body_end:]
            else:
                full_html += f"\n<script>\n{js_code}\n</script>"
        
        return full_html
    
    # 构建完整的HTML文档
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>练习页面</title>
"""
    
    if css_code:
        full_html += f"    <style>\n{css_code}\n    </style>\n"
    
    full_html += f"""</head>
<body>
{html_code}
"""
    
    if js_code:
        full_html += f"""    <script>
{js_code}
    </script>
"""
    
    full_html += "</body>\n</html>"
    
    return full_html
# ==================== 6. 核心函数：生成单个章节（只包含知识点和练习题） ====================
def generate_single_chapter(chapter_info, global_html_ref, knowledge_base_ref, previous_answer_code=""):
    """
    生成单个章节的知识点和练习题
    :param chapter_info: 章节信息字典，如 {"title": "HTML基础", "key_concepts": ["标签", "属性"]}
    :param global_html_ref: 全局教学HTML参考（字符串）
    :param knowledge_base_ref: 相关知识库摘要（字符串）
    :param previous_answer_code: 上一章的完整答案代码，用于本章的起始代码
    :return: 包含本章知识点和练习题的字典
    """
    print(f"\n📖 正在生成章节: {chapter_info['title']}")
    print(f"   起始代码长度: {len(previous_answer_code) if previous_answer_code else 0} 字符")
    # 清理起始代码中的转义
    clean_previous = ""
    if previous_answer_code:
        clean_previous = previous_answer_code.replace('\\\\n', '\n').replace('\\n', '\n')
        clean_previous = clean_previous.replace('\\\\t', '\t').replace('\\t', '\t')
        print(f"✅清理后起始代码长度: {len(clean_previous)} 字符")
        print(f"✅清理后起始代码: {clean_previous}")
    # 任务1：生成结构化的学习内容
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
        agent=knowledge_expert,
        expected_output="结构化的学习内容 JSON",
        name=f"生成学习内容_{chapter_info['title']}"
    )
    
    # 任务2：生成结构化的测试题
    # 构建学习内容描述（基于章节的知识点）
    levels_description = ""
    for i, concept in enumerate(chapter_info.get('key_concepts', []), 1):
        levels_description += f"{i}. {concept}\n"

    if not levels_description:
        levels_description = "基础HTML/CSS/JS开发技能"

    starter_context = "本章是课程起点，学生从空文件开始。" if not clean_previous else f"学生已完成的上一章代码作为基础：\n```html\n{previous_answer_code[:500]}...\n```"

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
        agent=test_designer,
        expected_output="结构化的测试题 JSON",
        name=f"生成测试题_{chapter_info['title']}"
    )

    # 执行本章的Crew（只有知识点和练习题两个任务）
    chapter_crew = Crew(
        agents=[knowledge_expert, test_designer],
        tasks=[knowledge_task, test_task],
        process="sequential",  # 章节内顺序执行
        verbose=True,  # 启用调试信息
        name=f"{chapter_info['title']}章节Crew"
    )
    
    result = chapter_crew.kickoff()
    
    
    knowledge_output = ""
    test_output = ""
    
    # 尝试获取任务的真实输出
    if hasattr(knowledge_task, 'output') and knowledge_task.output:
        # 检查输出类型，可能是字符串或其他对象
        task_output = knowledge_task.output
        if hasattr(task_output, 'raw_output'):
            # 如果是TaskOutput对象，获取原始输出
            knowledge_output = task_output.raw_output
        elif hasattr(task_output, '__str__'):
            knowledge_output = str(task_output)
        else:
            knowledge_output = str(task_output)
    
    if hasattr(test_task, 'output') and test_task.output:
        task_output = test_task.output
        if hasattr(task_output, 'raw_output'):
            test_output = task_output.raw_output
        elif hasattr(task_output, '__str__'):
            test_output = str(task_output)
        else:
            test_output = str(task_output)
    # print(f"✅知识输出: {knowledge_output}")
    # print(f"✅测试输出: {test_output}")

    # 提取本章的参考答案，供下一章使用
    # 编程练习题的参考答案包含了学生应该实现的目标代码
    chapter_answer_code = ""
    if test_output:
        print(f"\n🔍 解析测试输出...")
        print(f"   测试输出前200字符: {test_output[:200]}...")
        
        # 尝试解析JSON
        json_data = parse_json_from_text(test_output)
        if json_data:
            print(f"   ✅ 成功解析JSON")
            chapter_answer_code = extract_answer_code_from_structured_json(json_data)
        else:
            print(f"   ⚠️ 无法解析JSON，尝试直接提取HTML")
            chapter_answer_code = extract_html_code(test_output)
        
        print(f"   提取的答案代码长度: {len(chapter_answer_code)}")
    

    return {
        "chapter_title": chapter_info["title"],
        "start_html": clean_previous,
        "knowledge_output": knowledge_output,
        "test_output": test_output,
        "answer_code_for_next": chapter_answer_code
    }
def clean_escape_chars(text):
    """清理字符串中的转义字符（只清理一次）"""
    if not text:
        return ""
    
    # 只做一次清理，避免叠加
    replacements = [
        ('\\\\n', '\n'),  # 双重转义的换行符
        ('\\n', '\n'),    # 转义的换行符
        ('\\\\t', '\t'),  # 双重转义的制表符
        ('\\t', '\t'),    # 转义的制表符
        ('\\\\"', '"'),   # 双重转义的双引号
        ('\\"', '"'),     # 转义的双引号
        ("\\\\'", "'"),   # 双重转义的单引号
        ("\\'", "'"),     # 转义的单引号
    ]
    
    cleaned = text
    for old, new in replacements:
        cleaned = cleaned.replace(old, new)
    
    return cleaned
# ==================== 7. 主流程：生成多章节课程 ====================
def main():
    """主生成流程"""
    print("\n" + "="*60)
    print("开始生成课程（基于知识图谱）")
    print("="*60)

    # 第一步：设置知识图谱文件路径
    knowledge_graph_file = "data/knowledge/0adfc7ee-8ae7-42ee-9e06-43e6579189df.json"

    # 第二步：使用AI agent根据知识图谱生成全局教学HTML
    print("🎨 正在根据知识图谱生成全局教学HTML...")
    global_html, knowledge_base = generate_example_from_knowledge_graph(knowledge_graph_file, example_generator)
    print("✅ 全局教学HTML生成完成")
    print("知识库已获取："+knowledge_base)
    # 第四步：读取知识图谱文件
    try:
        with open(knowledge_graph_file, 'r', encoding='utf-8') as f:
            knowledge_graph = json.load(f)
    except FileNotFoundError:
        print(f"❌ 知识图谱文件未找到: {knowledge_graph_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ 知识图谱文件解析失败: {e}")
        return

    # 第五步：从知识图谱中提取章节信息
    chapters_to_generate = []
    knowledge_points = {}

    # 解析节点
    for node in knowledge_graph.get("nodes", []):
        node_data = node.get("data", {})
        node_type = node_data.get("type")
        node_id = node_data.get("id")
        node_label = node_data.get("label")

        if node_type == "chapter":
            # 章节节点
            chapters_to_generate.append({
                "id": node_id,
                "title": node_label,
                "key_concepts": []  # 稍后填充
            })
        elif node_type == "knowledge":
            # 知识点节点
            knowledge_points[node_id] = {
                "label": node_label,
                "select_element": node_data.get("select_element", [])
            }

    # 根据边关系建立章节和知识点的关联
    chapter_knowledge_map = {}
    for edge in knowledge_graph.get("edges", []):
        edge_data = edge.get("data", {})
        source = edge_data.get("source")
        target = edge_data.get("target")

        # 如果源是章节，目标是知识点，则建立关联
        if source in [chap["id"] for chap in chapters_to_generate] and target in knowledge_points:
            if source not in chapter_knowledge_map:
                chapter_knowledge_map[source] = []
            chapter_knowledge_map[source].append(knowledge_points[target]["label"])

    # 为每个章节填充关键概念
    for chapter in chapters_to_generate:
        chapter_id = chapter["id"]
        if chapter_id in chapter_knowledge_map:
            chapter["key_concepts"] = chapter_knowledge_map[chapter_id]
        else:
            # 如果没有关联的知识点，使用默认概念
            chapter["key_concepts"] = ["HTML标签", "文档结构", "基本元素"]

    # 调试输出：显示知识图谱解析结果
    print(f"📊 知识图谱统计:")
    print(f"   总节点数: {len(knowledge_graph['nodes'])}")
    print(f"   总边数: {len(knowledge_graph['edges'])}")
    print(f"   章节节点: {len([n for n in knowledge_graph['nodes'] if n['data']['type'] == 'chapter'])}")
    print(f"   知识点节点: {len([n for n in knowledge_graph['nodes'] if n['data']['type'] == 'knowledge'])}")

    print(f"\n📚 解析出的章节:")
    for i, chapter in enumerate(chapters_to_generate, 1):
        print(f"  {i}. {chapter['title']} (ID: {chapter['id']})")
        print(f"     关联知识点 ({len(chapter['key_concepts'])} 个):")
        for j, concept in enumerate(chapter['key_concepts'], 1):
            print(f"       {j}. {concept}")

    print(f"\n🔗 章节-知识点关联详情:")
    for chapter_id, knowledge_list in chapter_knowledge_map.items():
        chapter_name = next((c['title'] for c in chapters_to_generate if c['id'] == chapter_id), chapter_id)
        print(f"  {chapter_name}: {len(knowledge_list)} 个知识点")

    print(f"\n📚 从知识图谱中解析出 {len(chapters_to_generate)} 个章节:")
    for i, chapter in enumerate(chapters_to_generate, 1):
        print(f"  {i}. {chapter['title']} ({len(chapter['key_concepts'])} 个知识点)")

    # 第六步：顺序生成章节，传递代码依赖
    all_results = []
    previous_answer = ""  # 第一章没有起始代码

    for i, chapter in enumerate(chapters_to_generate, 1):
        print(f"\n{'='*50}")
        print(f"第{i}章: {chapter['title']}")
        print(f"   关键概念: {', '.join(chapter['key_concepts'])}")
        print(f"{'='*50}")

        chapter_result = generate_single_chapter(
            chapter_info=chapter,
            global_html_ref=global_html,
            knowledge_base_ref=knowledge_base,
            previous_answer_code=previous_answer
        )

        all_results.append(chapter_result)
        previous_answer = chapter_result["answer_code_for_next"]

        print(f"✅ 第{i}章生成完成")
        print(f"   生成答案代码长度: {len(previous_answer)} 字符")
        print(f"   供下一章使用的代码摘要: {previous_answer[:100]}...")

    # 第七步：保存所有结果
    output_file = "course_generation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # 将结果转换为可序列化的格式
        serializable_results = {
            "global_html": global_html,
            "knowledge_graph_used": knowledge_graph_file,
            "chapters": []
        }

        for r in all_results:
            # 清理转义字符
            clean_start_html = clean_escape_chars(r["start_html"])
            clean_knowledge = clean_escape_chars(r["knowledge_output"])
            clean_test = clean_escape_chars(r["test_output"])
            clean_answer = clean_escape_chars(r["answer_code_for_next"])

            serializable_results["chapters"].append({
                "chapter": r["chapter_title"],
                "start_html": clean_start_html,
                "knowledge_preview": clean_knowledge[:500] + "..." if len(clean_knowledge) > 500 else clean_knowledge,
                "test_preview": clean_test[:800] + "..." if len(clean_test) > 800 else clean_test,
                "answer_code_summary": clean_answer
            })

        # 使用ensure_ascii=False确保中文和特殊字符正确显示
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)

    # 单独保存全局教学HTML为文件
    html_file = "generated_global_demo.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(global_html)
    print(f"🌐 全局教学HTML已保存至: {html_file}")

    print("\n" + "="*60)
    print("🎉 课程生成完成！")
    print(f"📁 结果已保存至: {output_file}")
    print(f"🌐 示例代码已保存至: {html_file}")
    print("\n📊 生成摘要:")
    for i, r in enumerate(all_results, 1):
        print(f"  第{i}章: {r['chapter_title']}")
        print(f"    答案代码 → 第{i+1}章起始代码: {'✅' if r['answer_code_for_next'] else '❌ 无代码生成'}")
    print("="*60)

# ==================== 8. 运行脚本 ====================
if __name__ == "__main__":
    # 简单异常处理，避免因小错误中断
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行出错: {type(e).__name__}: {e}")
        print("\n💡 建议检查:")
        print("1. API密钥是否正确且有效")
        print("2. 网络连接是否正常")
        print("3. 魔搭平台服务状态")
        import traceback
        traceback.print_exc()