# data_models.py - 数据模型定义
from pydantic import BaseModel, Field

class ChapterHtml(BaseModel):
    chapter_title: str
    learning_objectives: list = []
    html_code: str = Field(description="完整的HTML教学代码，包含内联CSS和JS")
    core_concepts_demo: str = Field(description="对代码如何演示核心概念的简要说明")

class KnowledgePoint(BaseModel):
    point_title: str
    detailed_explanation: str
    key_terms: list = []

class KnowledgePointsList(BaseModel):
    points: list = Field(description="知识点列表")

class TestQuestion(BaseModel):
    question_text: str
    question_type: str = "practical"  # practical | quiz
    starter_code: str = Field(description="学生开始时看到的代码")
    target_output_description: str = Field(description="期望学生实现的功能描述")
    reference_solution: str = Field(description="完整的参考答案代码")

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