"""
SlowMind：将用户的模糊需求生成详细方案（PRD）
拓展：生成多套方案供用户选择
"""
import re
import json
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from openai import OpenAI
from typing import Dict, Any, Optional
from utils.prompts import (
    get_slow_mind_prompt_from_html,
    get_website_analysis_prompt,
    get_knowledge_points_prompt_from_html,
    get_knowledge_points_prompt,
    generate_demo_site_prompt,
    generate_learning_content_prompt,
    generate_test_task_prompt
)
from executor.execution_context import ExecutionContext
from utils.logger import logger  # 添加日志导入


class SlowMind:
    """
    慢思考智能体：负责复杂任务的深度分析与生成
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.client = context.get_client("slow")
        self.model = context.get_model("slow")
        # 创建线程池用于并发处理AI请求
        self.executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix="ai_worker")

    async def _run_in_thread(self, func, *args, **kwargs):
        """
        在线程池中运行同步函数，避免阻塞异步事件循环
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    def generate_prd_from_html(self, html_content: str, user_goal: str = "") -> str:
        """
        生成PRD文档
        :param user_goal: 用户输入的详细需求  
        :param html_content: 用户上传的HTML内容
        :return: PRD文档内容
        """
        logger.info("开始生成PRD文档，内容长度: %d", len(html_content))
        prompt = get_slow_mind_prompt_from_html(html_content, user_goal)

        print("正在分析上传的网页内容，生成结构化 PRD 文档...\n")
        logger.debug("发送请求到模型: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        plan = response.choices[0].message.content.strip()
        logger.info("AI响应成功，内容长度: %d", len(plan))

        # 生成唯一ID并保存 PRD 到文件
        prd_id = str(uuid.uuid4())
        save_path = os.path.join("data", "prd", f"{prd_id}.txt")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(plan)
        logger.info("PRD文档已保存到: %s", save_path)
        return plan

    def generate_prd_from_url(self, url: str, user_goal: str = "") -> str:
        """
        生成PRD文档（从URL）
        :param url: 用户输入的URL
        :param user_goal: 用户输入的详细需求
        :return: PRD文档内容
        """
        logger.info("开始从URL生成PRD文档: %s", url)
        prompt = get_slow_mind_prompt_from_html(url, user_goal)

        print("正在分析网页URL，生成结构化 PRD 文档...\n")
        logger.debug("发送请求到模型: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        plan = response.choices[0].message.content.strip()
        logger.info("AI响应成功，内容长度: %d", len(plan))
        return plan

    def extract_knowledge_from_html(self, html_content: str) -> str:
        """
        从HTML内容中提取知识图谱
        :param html_content: HTML内容
        :return: 知识图谱JSON字符串
        """
        logger.info("开始从HTML内容中提取知识图谱，内容长度: %d", len(html_content))
        prompt = get_knowledge_points_prompt_from_html(html_content)

        print("正在分析HTML内容，提取知识图谱...\n")
        logger.debug("发送请求到模型: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        knowledge_graph = response.choices[0].message.content.strip()
        logger.info("知识图谱提取成功，内容长度: %d", len(knowledge_graph))
        
        # 生成唯一ID并保存知识图谱到文件
        kg_id = str(uuid.uuid4())
        save_path = os.path.join("data", "knowledge", f"{kg_id}.txt")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(knowledge_graph)
        logger.info("知识图谱已保存到: %s", save_path)
        return knowledge_graph

    def extract_knowledge_from_context(self, context: str) -> str:
        """
        从上下文内容中提取知识图谱
        :param context: 上下文内容（如PRD文档等）
        :return: 知识图谱JSON字符串
        """
        logger.info("开始从上下文提取知识图谱，内容长度: %d", len(context))
        prompt = get_knowledge_points_prompt(context)

        print("正在分析上下文，提取知识图谱...\n")
        logger.debug("发送请求到模型: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        knowledge_graph = response.choices[0].message.content.strip()
        logger.info("知识图谱提取成功，内容长度: %d", len(knowledge_graph))
        return knowledge_graph

    def generate_demo_site(self, prd_doc: str, knowledge_graph: str) -> str:
        """
        生成演示网站
        :param prd_doc: PRD文档内容
        :param knowledge_graph: 知识图谱内容
        :return: 生成的HTML代码
        """
        logger.info("开始生成演示网站，PRD长度: %d, 知识图谱长度: %d", len(prd_doc), len(knowledge_graph))
        prompt = generate_demo_site_prompt(prd_doc, knowledge_graph)

        print("正在根据PRD文档和知识图谱生成演示网站...\n")
        logger.debug("发送请求到模型: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        html_code = response.choices[0].message.content.strip()
        logger.info("演示网站生成成功，代码长度: %d", len(html_code))
        return html_code

    async def generate_learning_content(self, html_content: str) -> str:
        """
        生成学习内容
        :param html_content: HTML内容
        :return: 学习内容
        """
        logger.info("开始生成学习内容，内容长度: %d", len(html_content))
        prompt = generate_learning_content_prompt(html_content)

        print("正在生成学习内容...\n")
        logger.debug("发送请求到模型: %s", self.model)

        # 在线程池中执行同步的AI调用，避免阻塞异步事件循环
        create_completion = partial(
            self.client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        response = await self._run_in_thread(create_completion)
        learning_content = response.choices[0].message.content.strip()
        logger.info("学习内容生成成功，内容长度: %d", len(learning_content))
        return learning_content

    async def generate_test_tasks(self, topic_info: dict, learning_content: dict = None) -> str:
        """
        生成测试任务
        :param topic_info: 知识点信息
        :param learning_content: 学习内容
        :return: 测试任务
        """
        logger.info("开始生成测试任务，知识点: %s", topic_info.get("label", ""))
        logger.info("学习内容: %s", learning_content)
        prompt = generate_test_task_prompt(topic_info, learning_content)

        print("正在生成测试任务...\n")
        logger.debug("发送请求到模型: %s", self.model)

        # 在线程池中执行同步的AI调用，避免阻塞异步事件循环
        create_completion = partial(
            self.client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "enable_thinking": False
            }
        )
        response = await self._run_in_thread(create_completion)
        raw = response.choices[0].message.content.strip()
        logger.info("测试任务生成成功，内容长度: %d", len(raw))
        # 提取 JSON 部分（防止有 Markdown 包裹或截断）
        json_match = re.search(r'```(?:json)?\s*({.*})\s*```', raw, re.DOTALL)
        if json_match:
            raw_json = json_match.group(1)
        else:
            raw_json = raw  # 尝试直接解析

        try:
            test_tasks_dict = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.error("解析测试任务 JSON 失败，返回空任务")
            test_tasks_dict = {"tasks": [], "count": 0}

        return test_tasks_dict