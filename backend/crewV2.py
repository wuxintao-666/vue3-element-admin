# crewV2.py - 重构版本，将agent和任务模块化
import os
import json

# 导入自定义模块
from crewaiv2.agents.agent_factory import create_agents
from crewaiv2.tasks.task_factory import create_task_functions
from crewaiv2.utils.json_parser import parse_json_from_text, extract_answer_code_from_structured_json, extract_html_code
from crewaiv2.utils.text_cleaner import clean_escape_chars
from crewaiv2.models.data_models import get_default_example
from crewai import Crew

# 禁用CrewAI遥测，避免SSL连接错误
os.environ["CREWAI_TELEMETRY"] = "false"

# ==================== 1. 配置魔搭API ====================
os.environ["DASHSCOPE_API_KEY"] = "sk-7581f392cad348b5bb60384d15a7a064"
os.environ["OPENAI_API_BASE"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
os.environ["MODEL_NAME"] = "qwen3-max-2026-01-23"

print("🚀 魔搭API配置就绪，开始构建生成引擎...")

# ==================== 2. 创建LLM实例（不同任务使用不同温度）===================
from langchain_openai import ChatOpenAI

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

# ==================== 3. 创建Agent ====================
agents = create_agents(llm_knowledge, llm_test, llm_example)
frontend_mentor = agents['frontend_mentor']
knowledge_expert = agents['knowledge_expert']
test_designer = agents['test_designer']
example_generator = agents['example_generator']

print("✅ 核心Agent创建完成（已模块化）")

# ==================== 4. 创建任务工厂 ====================
task_factory = create_task_functions()

# ==================== 5. 定义示例代码生成任务 ====================
def generate_example_from_knowledge_graph(kg_file, agent):
    """使用AI agent根据知识图谱生成示例代码"""

    try:
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)
    except Exception as e:
        print(f"读取知识图谱失败: {e}")
        return get_default_example()

    # 准备知识图谱摘要 - 按照章节分组
    chapters = {}
    knowledge_points = {}

    # 第一遍：收集所有节点信息
    for node in kg_data.get('nodes', []):
        node_data = node.get('data', {})
        node_type = node_data.get('type')
        node_id = node_data.get('id')
        label = node_data.get('label', '')

        if node_type == 'chapter':
            chapters[node_id] = {
                'label': label,
                'knowledge_points': []
            }
        elif node_type == 'knowledge':
            elements = node_data.get('select_element', [])
            knowledge_points[node_id] = {
                'label': label,
                'elements': elements
            }

    # 第二遍：根据边关系建立章节和知识点的关联
    for edge in kg_data.get('edges', []):
        edge_data = edge.get('data', {})
        source_id = edge_data.get('source')
        target_id = edge_data.get('target')

        # 如果源是章节，目标是知识点，则建立关联
        if source_id in chapters and target_id in knowledge_points:
            kp_info = knowledge_points[target_id]
            chapters[source_id]['knowledge_points'].append(
                f"- {kp_info['label']} (相关元素: {', '.join(kp_info['elements']) if kp_info['elements'] else '无'})"
            )

    # 生成按章节分组的摘要
    summary_lines = []
    for chapter_id, chapter_info in chapters.items():
        summary_lines.append(f"## 章节: {chapter_info['label']}")
        if chapter_info['knowledge_points']:
            summary_lines.extend(chapter_info['knowledge_points'])
        else:
            summary_lines.append("- 暂无具体知识点")

    full_summary = "\n".join(summary_lines)
    print(f"知识图谱摘要：\n{full_summary}")

    # 创建生成全局教学HTML的任务
    example_task = task_factory['create_example_task'](full_summary)
    example_task.agent = agent
    print("task已经构建...")

    # 执行任务
    try:
        example_crew = Crew(
            agents=[agent],
            tasks=[example_task],
            process="sequential",
            verbose=True,
            name="示例HTML生成Crew"
        )

        result = example_crew.kickoff()

        # 提取HTML代码（复用现有的extract_html_code函数）
        example_html = ""
        if result:
            example_html = extract_html_code(str(result))
        #print("HTML代码:"+example_html)
        #print("长度："+str(len(example_html))+"字")

        print("清洗后的html："+repr(example_html))
        # 保存并在默认浏览器打开
        # with open("debug_output.html", "w", encoding="utf-8") as f:
        #     f.write(example_html)
        # 使用动态生成的知识库描述，基于知识图谱内容
        knowledge_base = f"""基于知识图谱的教学内容：

{full_summary}

核心技术栈说明：
- HTML（超文本标记语言）：网页的结构和内容基础
- CSS（层叠样式表）：控制网页的外观和布局
- JavaScript：为网页添加交互功能和动态行为

开发原则：结构、表现、行为分离，提升代码可维护性和用户体验。
"""

        return example_html, knowledge_base

    except Exception as e:
        print(f"生成示例代码失败: {e}")
        return get_default_example()

# ==================== 6. 核心函数：生成单个知识点 ====================
def generate_single_knowledge_point(knowledge_point_info, global_html_ref, knowledge_base_ref, main_dir=""):
    """
    生成单个知识点的知识点内容和测试题
    :param knowledge_point_info: 知识点信息字典，如 {"id": "1_1", "label": "HTML元素与结构", "select_element": ["html", "head", "body"]}
    :param global_html_ref: 全局教学HTML参考（字符串）
    :param knowledge_base_ref: 相关知识库摘要（字符串）
    :param main_dir: 主文件夹路径
    :return: 包含本知识点知识点内容和测试题的字典
    """
    print(f"\n🔍 正在生成知识点: {knowledge_point_info['label']} (ID: {knowledge_point_info['id']})")

    # 如果没有传入main_dir，则使用默认的ai_generation_content文件夹
    if not main_dir:
        import time
        timestamp = int(time.time())
        main_dir = os.path.join("ai_generation_content", str(timestamp))

    # 第一步：生成知识点内容
    try:
        # 创建知识点内容生成任务
        
        knowledge_point_task = task_factory['create_knowledge_point_task'](
            knowledge_point_info=knowledge_point_info,
            knowledge_base_ref=knowledge_base_ref
        )
        knowledge_point_task.agent = knowledge_expert
        # 创建Crew并执行任务
        knowledge_point_crew = Crew(
            agents=[knowledge_expert],
            tasks=[knowledge_point_task],
            verbose=True,
            process="sequential",
            name="小节识点内容生成Crew"
        )

        knowledge_result = knowledge_point_crew.kickoff()
        knowledge_output = str(knowledge_result) if knowledge_result else ""
        print(f"✅ 知识点内容生成完成，输出长度: {len(knowledge_output)}")

        # 解析知识点JSON
        if knowledge_output.strip():
            try:
                # 尝试解析为JSON
                import json
                import pprint
                knowledge_json = json.loads(knowledge_output)
                print(f"📋 知识点JSON解析成功，包含键: {list(knowledge_json.keys())}")
                print("📖 知识点JSON键结构:")

                def print_keys_recursive(obj, indent=0, prefix=""):
                    """递归打印JSON的所有键"""
                    indent_str = "  " * indent
                    if isinstance(obj, dict):
                        for key in obj.keys():
                            print(f"{indent_str}{prefix}{key}")
                            if isinstance(obj[key], (dict, list)):
                                print_keys_recursive(obj[key], indent + 1, "")
                    elif isinstance(obj, list) and obj:
                        print(f"{indent_str}[{len(obj)} items]")
                        # 只显示第一个元素的结构作为示例
                        if obj and isinstance(obj[0], (dict, list)):
                            print_keys_recursive(obj[0], indent + 1, "0: ")

                print_keys_recursive(knowledge_json)

            except json.JSONDecodeError:
                print("📝 知识点输出为非JSON格式，尝试提取...")
                try:
                    knowledge_json = extract_html_code.extract_html_code(knowledge_output)
                    if knowledge_json:
                        print("📝 知识点JSON提取成功")
                        import pprint
                        print("📋 知识点JSON结构概览:")
                        def print_keys_recursive(obj, indent=0, prefix=""):
                            indent_str = "  " * indent
                            if isinstance(obj, dict):
                                for key in obj.keys():
                                    print(f"{indent_str}{prefix}{key}")
                                    if isinstance(obj[key], (dict, list)):
                                        print_keys_recursive(obj[key], indent + 1, "")
                            elif isinstance(obj, list) and obj:
                                print(f"{indent_str}[{len(obj)} items]")
                                if obj and isinstance(obj[0], (dict, list)):
                                    print_keys_recursive(obj[0], indent + 1, "0: ")

                        print_keys_recursive(knowledge_json)
                    else:
                        print("❌ 知识点JSON提取失败")
                        knowledge_json = None
                except Exception as parse_error:
                    print(f"❌ 知识点JSON提取错误: {parse_error}")
                    knowledge_json = None
        else:
            print("❌ 知识点输出为空")
            knowledge_json = None

    except Exception as e:
        print(f"❌ 知识点内容任务执行失败: {e}")
        knowledge_output = ""
        knowledge_json = None
    # 保存知识点JSON到单独文件
    import os

    # 使用函数开始处生成的时间戳
    knowledge_dir = os.path.join(main_dir, "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)

    # 文件名格式：knowledge_point_id.json (如 1_1.json)
    knowledge_filename = os.path.join(knowledge_dir, f"{knowledge_point_info['id']}.json")
    try:
        with open(knowledge_filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge_json, f, ensure_ascii=False, indent=2)
        print(f"💾 知识点JSON已保存到: {knowledge_filename}")
    except Exception as save_error:
        print(f"❌ 保存知识点JSON失败: {save_error}")
    # 第二步：生成测试题
    try:
        # 准备测试题生成所需的信息
        levels_description = ""
        if knowledge_json and 'levels' in knowledge_json:
            levels_description = "\n".join([
                f"Level {level['level']}: {level['description'][:100]}..."
                for level in knowledge_json['levels']
            ])
        else:
            levels_description = f"知识点: {knowledge_point_info['label']}"

        # 创建测试题生成任务
        test_task = task_factory['create_knowledge_point_test_task'](
            knowledge_point_info=knowledge_point_info,
            levels_description=levels_description,
            global_html_ref=global_html_ref
        )
        test_task.agent = test_designer
        # 创建Crew并执行任务
        test_crew = Crew(
            agents=[test_designer],
            tasks=[test_task],
            verbose=True,
            process="sequential",
            name="小节测试题生成Crew"
        )

        test_result = test_crew.kickoff()
        test_output = str(test_result) if test_result else ""
        print(f"✅ 测试题生成完成，输出长度: {len(test_output)}")

        # 解析测试题JSON
        if test_output.strip():
            try:
                # 尝试解析为JSON
                import json
                import pprint
                test_json = json.loads(test_output)
                print(f"📋 测试题JSON解析成功，包含键: {list(test_json.keys())}")
                print("📖 测试题JSON键结构:")

                def print_keys_recursive(obj, indent=0, prefix=""):
                    """递归打印JSON的所有键"""
                    indent_str = "  " * indent
                    if isinstance(obj, dict):
                        for key in obj.keys():
                            print(f"{indent_str}{prefix}{key}")
                            if isinstance(obj[key], (dict, list)):
                                print_keys_recursive(obj[key], indent + 1, "")
                    elif isinstance(obj, list) and obj:
                        print(f"{indent_str}[{len(obj)} items]")
                        # 只显示第一个元素的结构作为示例
                        if obj and isinstance(obj[0], (dict, list)):
                            print_keys_recursive(obj[0], indent + 1, "0: ")

                print_keys_recursive(test_json)

            except json.JSONDecodeError:
                print("📝 测试题输出为非JSON格式，尝试提取...")
                try:
                    test_json = extract_html_code.extract_html_code(test_output)
                    if test_json:
                        print("📝 测试题JSON提取成功")
                        import pprint
                        print("📋 测试题JSON结构概览:")
                        def print_keys_recursive(obj, indent=0, prefix=""):
                            indent_str = "  " * indent
                            if isinstance(obj, dict):
                                for key in obj.keys():
                                    print(f"{indent_str}{prefix}{key}")
                                    if isinstance(obj[key], (dict, list)):
                                        print_keys_recursive(obj[key], indent + 1, "")
                            elif isinstance(obj, list) and obj:
                                print(f"{indent_str}[{len(obj)} items]")
                                if obj and isinstance(obj[0], (dict, list)):
                                    print_keys_recursive(obj[0], indent + 1, "0: ")

                        print_keys_recursive(test_json)
                    else:
                        print("❌ 测试题JSON提取失败")
                        test_json = None
                except Exception as parse_error:
                    print(f"❌ 测试题JSON提取错误: {parse_error}")
                    test_json = None
        else:
            print("❌ 测试题输出为空")
            test_json = None

    except Exception as e:
        print(f"❌ 测试题任务执行失败: {e}")
        test_output = ""
        test_json = None

    

    # 保存测试题JSON到单独文件
    import os

    # 使用函数开始处生成的时间戳
    test_dir = os.path.join(main_dir, "test")
    os.makedirs(test_dir, exist_ok=True)

    # 文件名格式：knowledge_point_id.json (如 1_1.json)
    test_filename = os.path.join(test_dir, f"{knowledge_point_info['id']}.json")
    try:
        with open(test_filename, 'w', encoding='utf-8') as f:
            json.dump(test_json, f, ensure_ascii=False, indent=2)
        print(f"💾 测试题JSON已保存到: {test_filename}")
    except Exception as save_error:
        print(f"❌ 保存测试题JSON失败: {save_error}")

    # 返回结果
    return {
        "knowledge_point_id": knowledge_point_info['id'],
        "knowledge_point_title": knowledge_point_info['label'],
        "knowledge_content": knowledge_json,
        "test_content": test_json,
        "answer_code_for_next": ""  # 知识点测试题不传递答案代码
    }

# ==================== 7. 核心函数：生成单个章节（只包含知识点和练习题） ====================
def generate_single_chapter(chapter_info, global_html_ref, knowledge_base_ref, previous_answer_code="", main_dir=""):
    """
    生成单个章节的测试题
    :param chapter_info: 章节信息字典，如 {"title": "HTML基础", "key_concepts": ["标签", "属性"]}
    :param global_html_ref: 全局教学HTML参考（字符串）
    :param knowledge_base_ref: 相关知识库摘要（字符串）
    :param previous_answer_code: 上一章的完整答案代码，用于本章的起始代码
    :param main_dir: 主文件夹路径
    :return: 包含本章测试题的字典
    """
    print(f"\n📖 正在生成章节: {chapter_info['title']}")
    print(f"   起始代码长度: {len(previous_answer_code) if previous_answer_code else 0} 字符")

    # 如果没有传入main_dir，则使用默认的ai_generation_content文件夹
    if not main_dir:
        import time
        timestamp = int(time.time())
        main_dir = os.path.join("ai_generation_content", str(timestamp))

    # 清理起始代码中的转义
    clean_previous = ""
    if previous_answer_code:
        clean_previous = previous_answer_code.replace('\\\\n', '\n').replace('\\n', '\n')
        clean_previous = clean_previous.replace('\\\\t', '\t').replace('\\t', '\t')
        print(f"✅清理后起始代码长度: {len(clean_previous)} 字符")
        print(f"✅清理后起始代码: {clean_previous}")

    # 生成结构化的测试题
    # 构建学习内容描述（基于章节的知识点）
    levels_description = ""
    for i, concept in enumerate(chapter_info.get('key_concepts', []), 1):
        levels_description += f"{i}. {concept}\n"

    if not levels_description:
        levels_description = "基础HTML/CSS/JS开发技能"

    starter_context = "本章是课程起点，学生从空文件开始。" if not clean_previous else f"学生已完成的上一章代码作为基础：\n```html\n{previous_answer_code[:500]}...\n```"

    test_task = task_factory['create_test_task'](chapter_info, levels_description, starter_context, global_html_ref)
    test_task.agent = test_designer

    # 执行测试题生成任务
    print("❓ 执行测试题生成任务...")

    # 为测试题任务创建单独的Crew
    test_crew = Crew(
        agents=[test_designer],
        tasks=[test_task],
        process="sequential",
        verbose=True,
        name="章节测试题生成Crew"
    )

    try:
        test_result = test_crew.kickoff()
        test_output = str(test_result) if test_result else ""
        print(f"✅ 测试题任务完成，输出长度: {len(test_output)}")
        print(f"📝 测试题内容预览: {test_output[:500]}...")

        # 解析测试题输出
        if test_output.strip():
            try:
                import json
                import pprint
                test_json = json.loads(test_output)
                print(f"📋 测试题JSON解析成功，包含键: {list(test_json.keys())}")
                print("📝 测试题JSON键结构:")

                def print_keys_recursive(obj, indent=0, prefix=""):
                    """递归打印JSON的所有键"""
                    indent_str = "  " * indent
                    if isinstance(obj, dict):
                        for key in obj.keys():
                            print(f"{indent_str}{prefix}{key}")
                            if isinstance(obj[key], (dict, list)):
                                print_keys_recursive(obj[key], indent + 1, "")
                    elif isinstance(obj, list) and obj:
                        print(f"{indent_str}[{len(obj)} items]")
                        # 只显示第一个元素的结构作为示例
                        if obj and isinstance(obj[0], (dict, list)):
                            print_keys_recursive(obj[0], indent + 1, "0: ")

                print_keys_recursive(test_json)

                # 保存测试题JSON到单独文件
                import os

                # 使用函数开始处生成的时间戳
                test_dir = os.path.join(main_dir, "test")
                os.makedirs(test_dir, exist_ok=True)

                # 文件名格式：chapter_id.json (如 1_end.json)
                test_filename = os.path.join(test_dir, f"{chapter_info['id']}.json")
                try:
                    with open(test_filename, 'w', encoding='utf-8') as f:
                        json.dump(test_json, f, ensure_ascii=False, indent=2)
                    print(f"💾 测试题JSON已保存到: {test_filename}")
                except Exception as save_error:
                    print(f"❌ 保存测试题JSON失败: {save_error}")

            except json.JSONDecodeError:
                print("📝 测试题输出为非JSON格式")
            except ImportError:
                print("⚠️ pprint模块不可用，使用普通打印")
                print(f"📝 测试题JSON: {test_output[:500]}...")

    except Exception as e:
        print(f"❌ 测试题任务执行失败: {e}")
        test_output = ""


    # 查看test_output
    # print("测试题输出类型2："+type(test_output))
    # print("测试题输出2："+str(test_output))

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
        print(f"   提取的答案代码: {chapter_answer_code}")
        print(f"   提取的答案代码长度: {len(chapter_answer_code)}")

    return {
        "chapter_title": chapter_info["title"],
        "chapter_id": chapter_info["id"],
        "start_html": clean_previous,
        "test_output": test_output,
        "answer_code_for_next": chapter_answer_code
    }

# ==================== 7. 主流程：生成多章节课程 ====================
def main():
    """主生成流程"""
    import time
    start_time = time.time()  # 记录开始时间

    print("\n" + "="*60)
    print("开始生成课程（基于知识图谱）- V2版本")
    print("="*60)

    # 生成时间戳作为文件夹名
    timestamp = int(time.time())
    main_dir = os.path.join("ai_generation_content", str(timestamp))
    os.makedirs(main_dir, exist_ok=True)

    # 第一步：设置知识图谱文件路径
    knowledge_graph_file = "data/knowledge/0adfc7ee-8ae7-42ee-9e06-43e6579189df.json"

    # 第二步：使用AI agent根据知识图谱生成全局教学HTML
    print("🎨 正在根据知识图谱生成全局教学HTML...")
    global_html, knowledge_base = generate_example_from_knowledge_graph(knowledge_graph_file, example_generator)
    print("✅ 全局教学HTML生成完成")

    # 直接保存全局教学HTML为文件
    html_file = os.path.join(main_dir, "example_page.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(global_html)
    print(f"🌐 全局教学HTML已保存至: {html_file}")
    #print("知识库已获取："+knowledge_base)

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
    knowledge_points_list = []  # 新增：存储所有知识点信息的列表

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
            knowledge_point_info = {
                "id": node_id,
                "label": node_label,
                "select_element": node_data.get("select_element", [])
            }
            knowledge_points[node_id] = knowledge_point_info
            knowledge_points_list.append(knowledge_point_info)  # 添加到列表中

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
    # print(f"📊 知识图谱统计:")
    # print(f"   总节点数: {len(knowledge_graph['nodes'])}")
    # print(f"   总边数: {len(knowledge_graph['edges'])}")
    # print(f"   章节节点: {len([n for n in knowledge_graph['nodes'] if n['data']['type'] == 'chapter'])}")
    # print(f"   知识点节点: {len([n for n in knowledge_graph['nodes'] if n['data']['type'] == 'knowledge'])}")

    # print(f"\n📚 解析出的章节:")
    # for i, chapter in enumerate(chapters_to_generate, 1):
    #     print(f"  {i}. {chapter['title']} (ID: {chapter['id']})")
    #     print(f"     关联知识点 ({len(chapter['key_concepts'])} 个):")
    #     for j, concept in enumerate(chapter['key_concepts'], 1):
    #         print(f"       {j}. {concept}")

    # print(f"\n🔗 章节-知识点关联详情:")
    # for chapter_id, knowledge_list in chapter_knowledge_map.items():
    #     chapter_name = next((c['title'] for c in chapters_to_generate if c['id'] == chapter_id), chapter_id)
    #     print(f"  {chapter_name}: {len(knowledge_list)} 个知识点")

    # print(f"\n📚 从知识图谱中解析出 {len(chapters_to_generate)} 个章节:")
    # for i, chapter in enumerate(chapters_to_generate, 1):
    #     print(f"  {i}. {chapter['title']} ({len(chapter['key_concepts'])} 个知识点)")

    # 第五步：并发生成所有知识点
    print(f"\n{'='*60}")
    print("第五步：并发生成所有知识点内容")
    print(f"{'='*60}")

    import concurrent.futures
    import time

    def generate_knowledge_point_with_logging(knowledge_point_info, index, global_html_ref, knowledge_base_ref, main_dir):
        """生成单个知识点并记录日志"""
        print(f"\n{'-'*40}")
        print(f"知识点{index}: {knowledge_point_info['label']} (ID: {knowledge_point_info['id']})")
        print(f"{'-'*40}")

        return generate_single_knowledge_point(
            knowledge_point_info=knowledge_point_info,
            global_html_ref=global_html_ref,
            knowledge_base_ref=knowledge_base_ref,
            main_dir=main_dir
        )

    knowledge_points_results = []
    start_time = time.time()

    # 使用线程池并发执行知识点生成
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(knowledge_points_list), 20)) as executor:
        # 提交所有任务
        future_to_index = {
            executor.submit(generate_knowledge_point_with_logging,
                          knowledge_point, i+1, global_html, knowledge_base, main_dir): i
            for i, knowledge_point in enumerate(knowledge_points_list)
        }

        # 收集结果（按照提交顺序）
        results_dict = {}
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results_dict[index] = result
                print(f"✅ 知识点{index+1}生成完成")
            except Exception as exc:
                print(f"❌ 知识点{index+1}生成失败: {exc}")
                results_dict[index] = None

        # 按原始顺序整理结果
        knowledge_points_results = [results_dict[i] for i in range(len(knowledge_points_list))]

    execution_time = time.time() - start_time
    print(f"\n✅ 共生成 {len([r for r in knowledge_points_results if r is not None])}/{len(knowledge_points_results)} 个知识点")
    print(f"⚡ 并发执行耗时: {execution_time:.2f}秒")

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
            previous_answer_code=previous_answer,
            main_dir=main_dir
        )

        all_results.append(chapter_result)
        previous_answer = chapter_result["answer_code_for_next"]

        print(f"✅ 第{i}章生成完成")
        print(f"   生成答案代码长度: {len(previous_answer)} 字符")
        print(f"   供下一章使用的代码摘要: {previous_answer[:100]}...")

    # 所有结果已分别保存为独立JSON文件，无需额外汇总


    print("\n" + "="*60)
    # 计算总耗时
    end_time = time.time()
    total_time = end_time - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = total_time % 60

    print("🎉 课程生成完成！(V2版本)")
    print(f"📂 所有文件已保存至: {main_dir}")
    print(f"⏱️ 总耗时: {hours:02d}:{minutes:02d}:{seconds:05.2f}")

    print("\n📊 生成摘要:")
    print(f"  知识点数量: {len(knowledge_points_results)}")
    for i, kp in enumerate(knowledge_points_results, 1):
        print(f"    知识点{i}: {kp['knowledge_point_title']} (ID: {kp['knowledge_point_id']})")

    print(f"  章节数量: {len(all_results)}")
    for i, r in enumerate(all_results, 1):
        print(f"    第{i}章: {r['chapter_title']}")
        print(f"      答案代码 → 第{i+1}章起始代码: {'✅' if r['answer_code_for_next'] else '❌ 无代码生成'}")
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