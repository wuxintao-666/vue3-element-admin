# agent_factory.py - Agent工厂类
from crewai import Agent

def create_agents(llm_knowledge, llm_test, llm_example):
    """
    创建所有需要的Agent
    :param llm_knowledge: 知识生成LLM
    :param llm_test: 测试题生成LLM
    :param llm_example: 示例代码生成LLM
    :return: 包含所有Agent的字典
    """

    # 前端教学开发专家
    frontend_mentor = Agent(
        role="前端教学开发专家",
        goal="根据需求创建清晰、可运行的教学HTML示例",
        backstory="你是一位经验丰富的前端开发者和教师，擅长用最小化的可运行代码片段演示复杂概念。",
        llm=llm_example,  # 使用示例代码生成温度
        verbose=False,
        allow_delegation=False
    )

    # 知识结构化专家
    knowledge_expert = Agent(
        role="知识结构化专家",
        goal="将知识图谱和资料转化为结构化的知识点",
        backstory="你是一位知识管理顾问，擅长从复杂信息中提取核心概念并清晰表述。",
        llm=llm_knowledge,  # 使用知识生成温度
        verbose=False,
        allow_delegation=False
    )

    # 编程练习题设计师
    test_designer = Agent(
        role="编程练习题设计师",
        goal="设计基于代码的实践性测试题",
        backstory="你专长为编程课程设计循序渐进、可实操的编码练习题，注重从已有代码到目标代码的转变。",
        llm=llm_test,  # 使用测试题生成温度
        verbose=False,
        allow_delegation=False
    )

    # 前端示例代码生成专家
    example_generator = Agent(
        role="前端示例代码生成专家",
        goal="根据知识图谱内容生成高质量的教学示例代码",
        backstory="你是一位经验丰富的教学设计师，擅长根据知识图谱分析需求并创建实用的前端代码示例。",
        llm=llm_example,  # 使用示例代码生成温度
        verbose=False,
        allow_delegation=False
    )

    return {
        'frontend_mentor': frontend_mentor,
        'knowledge_expert': knowledge_expert,
        'test_designer': test_designer,
        'example_generator': example_generator
    }