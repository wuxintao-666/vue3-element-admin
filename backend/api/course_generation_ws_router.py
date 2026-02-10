# course_generation_ws_router.py - 课程生成WebSocket路由
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import json
import uuid
import asyncio
import os
import sys
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewV2 import (
    generate_example_from_knowledge_graph,
    generate_single_knowledge_point,
    generate_single_chapter,
    knowledge_expert,
    test_designer,
    example_generator,
    task_factory
)
from crewaiv2.utils.json_parser import parse_json_from_text, extract_answer_code_from_structured_json
from crewaiv2.utils.text_cleaner import clean_escape_chars

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info("WebSocket连接建立: %s", task_id)
    
    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info("WebSocket连接断开: %s", task_id)
    
    async def send_message(self, message: dict, task_id: str):
        """发送消息到指定连接"""
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_json(message)
            except Exception as e:
                logger.warning("发送消息失败 %s: %s", task_id, e)
                self.disconnect(task_id)

manager = ConnectionManager()


async def generate_course_stream(
    websocket: WebSocket,
    task_id: str,
    knowledge_graph: dict,
    config: dict,
    cancel_event: asyncio.Event,
):
    """生成课程并推送进度"""
    try:
        # 如果已被取消，则直接退出
        if cancel_event.is_set():
            logger.info("课程生成任务已在开始前被取消: %s", task_id)
            return
        # 阶段1: 解析知识图谱
        await manager.send_message({
            "type": "stage_start",
            "task_id": task_id,
            "stage": "parsing",
            "progress": 0,
            "message": "解析知识图谱..."
        }, task_id)
        
        # 从知识图谱中提取章节和知识点
        chapters_to_generate = []
        knowledge_points = {}
        knowledge_points_list = []
        
        for node in knowledge_graph.get("nodes", []):
            node_data = node.get("data", {})
            node_type = node_data.get("type")
            node_id = node_data.get("id")
            node_label = node_data.get("label")
            
            if node_type == "chapter":
                chapters_to_generate.append({
                    "id": node_id,
                    "title": node_label,
                    "key_concepts": []
                })
            elif node_type == "knowledge":
                knowledge_point_info = {
                    "id": node_id,
                    "label": node_label,
                    "select_element": node_data.get("select_element", [])
                }
                knowledge_points[node_id] = knowledge_point_info
                knowledge_points_list.append(knowledge_point_info)
        
        # 建立章节和知识点的关联
        chapter_knowledge_map = {}
        for edge in knowledge_graph.get("edges", []):
            edge_data = edge.get("data", {})
            source = edge_data.get("source")
            target = edge_data.get("target")
            
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
                chapter["key_concepts"] = ["HTML标签", "文档结构", "基本元素"]
        
        # 如果中途被取消，则不再继续后续阶段
        if cancel_event.is_set():
            logger.info("课程生成任务在解析阶段后被取消: %s", task_id)
            return

        await manager.send_message({
            "type": "stage_complete",
            "task_id": task_id,
            "stage": "parsing",
            "progress": 5,
            "message": f"解析完成: {len(chapters_to_generate)}个章节, {len(knowledge_points_list)}个知识点",
            "data": {
                "chapter_count": len(chapters_to_generate),
                "knowledge_point_count": len(knowledge_points_list)
            }
        }, task_id)

        # 阶段2: 生成示例HTML
        await manager.send_message({
            "type": "stage_start",
            "task_id": task_id,
            "stage": "html_generation",
            "progress": 5,
            "message": "开始生成示例HTML..."
        }, task_id)
        
        # 只使用前端直接传入的知识图谱数据：保存到临时JSON文件供生成器读取
        import tempfile

        def _write_knowledge_graph_temp_file() -> str:
            """在线程中写入临时知识图谱JSON文件并返回路径"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(knowledge_graph, f, ensure_ascii=False)
                return f.name

        temp_file = await asyncio.to_thread(_write_knowledge_graph_temp_file)
        
        # 生成全局示例HTML（在线程池中执行，避免阻塞事件循环）
        global_html, knowledge_base = await asyncio.to_thread(
            generate_example_from_knowledge_graph,
            temp_file,
            example_generator
        )
        os.unlink(temp_file)  # 删除临时文件
        
        # 如果在生成示例HTML期间被取消，也直接退出
        if cancel_event.is_set():
            logger.info("课程生成任务在示例HTML阶段后被取消: %s", task_id)
            return

        await manager.send_message({
            "type": "stage_complete",
            "task_id": task_id,
            "stage": "html_generation",
            "progress": 25,
            "message": "示例HTML生成完成",
            "data": {
                "html_preview": global_html[:500] if global_html else "",
                "html_length": len(global_html) if global_html else 0
            }
        }, task_id)
        
        # 阶段3: 并发生成知识点（使用 asyncio 任务并发，可协作式取消）
        await manager.send_message({
            "type": "stage_start",
            "task_id": task_id,
            "stage": "knowledge_generation",
            "progress": 25,
            "message": "开始生成知识点内容..."
        }, task_id)
        
        import time
        
        main_dir = os.path.join("ai_generation_content", task_id)
        os.makedirs(main_dir, exist_ok=True)
        
        knowledge_results = []
        start_time = time.time()

        async def generate_knowledge_point_async(point_info, index):
            """异步包装函数，支持在任务开始前检查取消状态"""
            if cancel_event.is_set():
                logger.info("知识点生成任务在开始前被取消: task_id=%s, index=%s", task_id, index)
                return {"index": index, "error": "cancelled", "success": False}

            try:
                # 将同步的知识点生成函数丢到线程池执行，但任务本身受 asyncio 调度控制
                result = await asyncio.to_thread(
                    generate_single_knowledge_point,
                    point_info,
                    global_html,
                    knowledge_base,
                    main_dir
                )
                return {"index": index, "result": result, "success": True}
            except asyncio.CancelledError:
                # 任务被取消时的协作式退出
                logger.info("知识点生成任务被取消: task_id=%s, index=%s", task_id, index)
                raise
            except Exception as e:
                logger.exception("知识点生成异常 %s: %s", index, e)
                return {"index": index, "error": str(e), "success": False}

        # 创建并发任务
        tasks = [
            asyncio.create_task(generate_knowledge_point_async(point, i))
            for i, point in enumerate(knowledge_points_list)
        ]

        results_dict = {}
        try:
            for task in asyncio.as_completed(tasks):
                if cancel_event.is_set():
                    logger.info("并发知识点生成任务被取消: %s", task_id)
                    # 取消剩余任务
                    for t in tasks:
                        t.cancel()
                    break

                try:
                    result_data = await task
                    index = result_data["index"]
                    results_dict[index] = result_data

                    if result_data.get("success"):
                        # 推送单个知识点完成
                        asyncio.create_task(manager.send_message({
                            "type": "item_complete",
                            "task_id": task_id,
                            "stage": "knowledge_generation",
                            "progress": 25 + int((len(results_dict) / len(knowledge_points_list)) * 40),
                            "message": f"已完成 {len(results_dict)}/{len(knowledge_points_list)} 个知识点",
                            "data": {
                                "item": {
                                    "id": knowledge_points_list[index]["id"],
                                    "title": knowledge_points_list[index]["label"]
                                },
                                "completed": len(results_dict),
                                "total": len(knowledge_points_list)
                            }
                        }, task_id))
                    else:
                        logger.warning("知识点生成失败 %s: %s", index, result_data.get("error"))
                except asyncio.CancelledError:
                    logger.info("知识点生成任务在等待过程中被取消: %s", task_id)
                    break
                except Exception as e:
                    logger.exception("知识点生成任务调度异常: %s", e)
        finally:
            # 确保所有任务都被正确取消/完成
            for t in tasks:
                if not t.done():
                    t.cancel()

        # 按原始顺序整理结果（未完成的索引标记为取消）
        knowledge_results = [
            results_dict.get(i, {"index": i, "error": "cancelled", "success": False})
            for i in range(len(knowledge_points_list))
        ]
        
        # 如果被取消，不再发送阶段完成消息
        if cancel_event.is_set():
            logger.info("课程生成任务在知识点阶段后被取消: %s", task_id)
            return
        
        execution_time = time.time() - start_time
        await manager.send_message({
            "type": "stage_complete",
            "task_id": task_id,
            "stage": "knowledge_generation",
            "progress": 65,
            "message": f"知识点生成完成，耗时 {execution_time:.2f}秒",
            "data": {
                "completed": len([r for r in knowledge_results if r.get("success")]),
                "total": len(knowledge_results),
                "execution_time": execution_time
            }
        }, task_id)
        
        # 阶段4: 顺序生成章节测试题
        await manager.send_message({
            "type": "stage_start",
            "task_id": task_id,
            "stage": "test_generation",
            "progress": 65,
            "message": "开始生成章节测试题..."
        }, task_id)
        
        chapter_results = []
        previous_answer = ""
        
        for i, chapter in enumerate(chapters_to_generate):
            if cancel_event.is_set():
                logger.info("课程生成任务在章节测试阶段被取消: %s", task_id)
                return
            # 推送章节开始
            await manager.send_message({
                "type": "chapter_start",
                "task_id": task_id,
                "stage": "test_generation",
                "progress": 65 + int((i / len(chapters_to_generate)) * 30),
                "message": f"开始生成第{i+1}章: {chapter['title']}",
                "data": {
                    "chapter_id": chapter["id"],
                    "chapter_title": chapter["title"],
                    "current": i + 1,
                    "total": len(chapters_to_generate)
                }
            }, task_id)
            
            try:
                # 构建学习内容描述
                levels_description = ""
                for j, concept in enumerate(chapter.get('key_concepts', []), 1):
                    levels_description += f"{j}. {concept}\n"
                
                if not levels_description:
                    levels_description = "基础HTML/CSS/JS开发技能"
                
                starter_context = "本章是课程起点，学生从空文件开始。" if not previous_answer else f"学生已完成的上一章代码作为基础：\n```html\n{previous_answer[:500]}...\n```"
                
                # 创建测试任务
                test_task = task_factory['create_test_task'](
                    chapter, levels_description, starter_context, global_html
                )
                test_task.agent = test_designer
                
                # 执行测试题生成（放入线程池，避免阻塞事件循环）
                from crewai import Crew
                test_crew = Crew(
                    agents=[test_designer],
                    tasks=[test_task],
                    process="sequential",
                    verbose=False,
                    name=f"章节{chapter['title']}测试题生成Crew"
                )
                
                test_result = await asyncio.to_thread(test_crew.kickoff)
                test_output = str(test_result) if test_result else ""
                
                # 解析测试输出
                test_json = None
                if test_output.strip():
                    test_json = parse_json_from_text(test_output)
                
                # 提取答案代码
                chapter_answer_code = ""
                if test_json:
                    chapter_answer_code = extract_answer_code_from_structured_json(test_json)
                
                # 保存测试题JSON（在线程池中进行磁盘写入）
                if test_json:
                    test_dir = os.path.join(main_dir, "test")
                    os.makedirs(test_dir, exist_ok=True)
                    test_filename = os.path.join(test_dir, f"{chapter['id']}.json")

                    def _write_test_json(path: str, data: dict):
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)

                    await asyncio.to_thread(_write_test_json, test_filename, test_json)
                
                chapter_result = {
                    "chapter_title": chapter["title"],
                    "chapter_id": chapter["id"],
                    "start_html": previous_answer,
                    "test_output": test_output,
                    "test_json": test_json,
                    "answer_code_for_next": chapter_answer_code
                }
                
                chapter_results.append(chapter_result)
                previous_answer = chapter_answer_code
                
                # 推送章节完成
                await manager.send_message({
                    "type": "chapter_complete",
                    "task_id": task_id,
                    "stage": "test_generation",
                    "progress": 65 + int(((i + 1) / len(chapters_to_generate)) * 30),
                    "message": f"第{i+1}章生成完成",
                    "data": {
                        "item": {
                            "id": chapter["id"],
                            "title": chapter["title"],
                            "test": test_json
                        },
                        "completed": i + 1,
                        "total": len(chapters_to_generate)
                    }
                }, task_id)
                
            except Exception as e:
                logger.exception("章节生成失败 %s: %s", chapter.get("title"), e)
                await manager.send_message({
                    "type": "item_error",
                    "task_id": task_id,
                    "stage": "test_generation",
                    "message": f"第{i+1}章生成失败: {str(e)}",
                    "data": {
                        "chapter_id": chapter["id"],
                        "chapter_title": chapter["title"]
                    }
                }, task_id)
        
        # 生成完成，推送完整数据
        # 如果在最终汇总前被取消，则不再发送完成消息
        if cancel_event.is_set():
            logger.info("课程生成任务在完成前被取消: %s", task_id)
            return

        await manager.send_message({
            "type": "generation_complete",
            "task_id": task_id,
            "progress": 100,
            "message": "课程生成完成，等待确认",
            "data": {
                "html": global_html,
                "knowledge_base": knowledge_base,
                "knowledge_points": [
                    r["result"] for r in knowledge_results if r.get("success")
                ],
                "chapters": chapter_results,
                "summary": {
                    "knowledge_count": len([r for r in knowledge_results if r.get("success")]),
                    "chapter_count": len(chapter_results),
                    "main_dir": main_dir
                }
            }
        }, task_id)
        
    except asyncio.CancelledError:
        # 协程被显式取消时，静默退出，不再推送错误消息
        logger.info("课程生成协程被取消: %s", task_id)
        return
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.exception("课程生成失败 %s", task_id)
        await manager.send_message({
            "type": "error",
            "task_id": task_id,
            "message": f"生成失败: {str(e)}",
            "error": error_trace
        }, task_id)


@router.websocket("/ws/generate-course")
async def websocket_generate_course(websocket: WebSocket):
    """课程生成WebSocket端点"""
    task_id = str(uuid.uuid4())
    cancel_event: asyncio.Event = asyncio.Event()
    generation_task: Optional[asyncio.Task] = None
    heartbeat_task: Optional[asyncio.Task] = None

    async def _shutdown_ws(reason: str, send_error: bool = True):
        """
        统一的收尾逻辑：
        - 标记取消
        - 取消后台生成任务
        - 尝试给前端发一条 error（如果连接已断开则会失败，忽略即可）
        - 从连接管理器移除
        """
        logger.warning("_shutdown_ws 调用: task_id=%s, send_error=%s, reason=%s", task_id, send_error, reason)
        cancel_event.set()
        if generation_task is not None:
            generation_task.cancel()
        if heartbeat_task is not None:
            heartbeat_task.cancel()
        if send_error:
            try:
                await manager.send_message({
                    "type": "error",
                    "task_id": task_id,
                    "message": reason
                }, task_id)
            except Exception as send_err:
                # 这里一般是因为连接已经物理关闭，记录日志便于排查
                logger.warning("向前端发送 error 消息失败 task_id=%s: %s", task_id, send_err)
        manager.disconnect(task_id)
    
    try:
        await manager.connect(websocket, task_id)
        
        # 启动后端心跳任务，定期发送 ping 消息，避免长时间无数据导致中间层断开
        async def _heartbeat_loop():
            try:
                while not cancel_event.is_set():
                    await asyncio.sleep(10)  # 心跳间隔（秒）
                    await manager.send_message({
                        "type": "ping",
                        "task_id": task_id,
                        "message": "heartbeat"
                    }, task_id)
            except asyncio.CancelledError:
                # 任务被取消时静默退出
                return

        heartbeat_task = asyncio.create_task(_heartbeat_loop())
        
        # 1. 接收初始请求
        initial_request = await websocket.receive_json()
        
        knowledge_graph = initial_request.get("knowledge_graph")
        config = initial_request.get("config", {})
        
        if not knowledge_graph:
            await manager.send_message({
                "type": "error",
                "task_id": task_id,
                "message": "缺少知识图谱数据"
            }, task_id)
            return

        # 安全/一致性约束：只允许直接传入 knowledge_graph，不允许通过路径读取
        if config.get("knowledge_graph_file"):
            await manager.send_message({
                "type": "error",
                "task_id": task_id,
                "message": "不支持通过 knowledge_graph_file 传入路径，请直接在 knowledge_graph 字段传入图谱数据"
            }, task_id)
            return
        
        # 确认收到请求
        await manager.send_message({
            "type": "request_received",
            "task_id": task_id,
            "message": "请求已接收，开始生成课程..."
        }, task_id)
        
        # 2. 启动生成任务（后台异步）
        generation_task = asyncio.create_task(
            generate_course_stream(websocket, task_id, knowledge_graph, config, cancel_event)
        )
        
        # 3. 等待最终确认消息
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "confirm":
                # 用户确认，保存到数据库
                confirmed_data = message.get("data")
                
                # TODO: 这里可以添加保存到数据库的逻辑
                # await save_confirmed_course(task_id, confirmed_data)
                
                await manager.send_message({
                    "type": "confirmed",
                    "task_id": task_id,
                    "message": "内容已确认，保存成功"
                }, task_id)
                break
                
            elif message.get("type") == "cancel":
                # 用户取消：统一走 shutdown（不发 error，只发 cancelled）
                cancel_event.set()
                if generation_task is not None:
                    generation_task.cancel()
                await manager.send_message({
                    "type": "cancelled",
                    "task_id": task_id,
                    "message": "生成已取消"
                }, task_id)
                manager.disconnect(task_id)
                return
                
    except WebSocketDisconnect:
        # 连接断开：只走这一条逻辑
        logger.warning("捕获 WebSocketDisconnect: task_id=%s", task_id)
        await _shutdown_ws("WebSocket连接已断开，后台生成任务已取消")
    except Exception as e:
        logger.exception("WebSocket错误 %s: %s", task_id, e)
        # 未预料异常：统一走这一条逻辑（尽量把错误发给前端）
        await _shutdown_ws(f"WebSocket错误: {str(e)}", send_error=True)
