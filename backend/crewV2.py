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
os.environ["MODEL_NAME"] = "deepseek-v3.2"

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
    example_task = task_factory['create_example_task'](knowledge_summary)
    example_task.agent = agent
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
    knowledge_task = task_factory['create_knowledge_task'](chapter_info, knowledge_base_ref)
    knowledge_task.agent = knowledge_expert

    # 任务2：生成结构化的测试题
    # 构建学习内容描述（基于章节的知识点）
    levels_description = ""
    for i, concept in enumerate(chapter_info.get('key_concepts', []), 1):
        levels_description += f"{i}. {concept}\n"

    if not levels_description:
        levels_description = "基础HTML/CSS/JS开发技能"

    starter_context = "本章是课程起点，学生从空文件开始。" if not clean_previous else f"学生已完成的上一章代码作为基础：\n```html\n{previous_answer_code[:500]}...\n```"

    test_task = task_factory['create_test_task'](chapter_info, levels_description, starter_context, global_html_ref)
    test_task.agent = test_designer

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

# ==================== 7. 主流程：生成多章节课程 ====================
def main():
    """主生成流程"""
    print("\n" + "="*60)
    print("开始生成课程（基于知识图谱）- V2版本")
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
    output_file = "course_generation_results_v2.json"
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

            print(f"\n🔍 解析章节 '{r['chapter_title']}' 的输出...")

            # 解析knowledge_output为JSON对象
            knowledge_json = parse_json_from_text(clean_knowledge)
            if knowledge_json and isinstance(knowledge_json, dict):
                print(f"✅ 知识输出解析成功: {type(knowledge_json)}，包含键: {list(knowledge_json.keys())}")
            else:
                print(f"⚠️ 知识输出解析失败，使用原始字符串")
                knowledge_json = clean_knowledge

            # 解析test_output为JSON对象
            test_json = parse_json_from_text(clean_test)
            if test_json and isinstance(test_json, dict):
                print(f"✅ 测试输出解析成功: {type(test_json)}，包含键: {list(test_json.keys())}")
            else:
                print(f"⚠️ 测试输出解析失败，使用原始字符串")
                test_json = clean_test

            serializable_results["chapters"].append({
                "chapter": r["chapter_title"],
                "start_html": clean_start_html,
                "knowledge_preview": knowledge_json,
                "test_preview": test_json,
                "answer_code_summary": clean_answer
            })

        # 使用ensure_ascii=False确保中文和特殊字符正确显示
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)

    # 单独保存全局教学HTML为文件
    html_file = "generated_global_demo_v2.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(global_html)
    print(f"🌐 全局教学HTML已保存至: {html_file}")

    print("\n" + "="*60)
    print("🎉 课程生成完成！(V2版本)")
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