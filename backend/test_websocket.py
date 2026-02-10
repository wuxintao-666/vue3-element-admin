# test_websocket.py - WebSocket API 测试脚本
import asyncio
import websockets
import json
import sys

# 终端颜色（ANSI 转义码）
RESET = "\033[0m"
GREEN = "\033[92m"   # 成功
YELLOW = "\033[93m"  # 阶段 / 进度
RED = "\033[91m"     # 错误
CYAN = "\033[96m"    # 心跳 / 其他


async def test_websocket():
    """测试WebSocket连接和消息推送"""
    uri = "ws://localhost:8000/ws/generate-course"
    
    print("🔌 正在连接到 WebSocket 服务器...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 连接成功！")
            
            # 准备测试数据（2 章，每章 3 个知识点的知识图谱）
            test_knowledge_graph = {
                "nodes": [
                    # 章节 1
                    {
                        "data": {
                            "id": "1_end",
                            "type": "chapter",
                            "label": "HTML 基础"
                        }
                    },
                    # 章节 1 的 3 个知识点
                    {
                        "data": {
                            "id": "1_1",
                            "type": "knowledge",
                            "label": "HTML 文档结构",
                            "select_element": ["html", "head", "body"]
                        }
                    },
                    {
                        "data": {
                            "id": "1_2",
                            "type": "knowledge",
                            "label": "常见块级元素与行内元素",
                            "select_element": ["div", "span", "p"]
                        }
                    },
                    {
                        "data": {
                            "id": "1_3",
                            "type": "knowledge",
                            "label": "文本与列表标签",
                            "select_element": ["h1", "h2", "ul", "li"]
                        }
                    },
                    # 章节 2
                    {
                        "data": {
                            "id": "2_end",
                            "type": "chapter",
                            "label": "CSS 基础"
                        }
                    },
                    # 章节 2 的 3 个知识点
                    {
                        "data": {
                            "id": "2_1",
                            "type": "knowledge",
                            "label": "选择器与基本样式",
                            "select_element": ["selector", "color", "font-size"]
                        }
                    },
                    {
                        "data": {
                            "id": "2_2",
                            "type": "knowledge",
                            "label": "盒模型与边距",
                            "select_element": ["margin", "padding", "border"]
                        }
                    },
                    {
                        "data": {
                            "id": "2_3",
                            "type": "knowledge",
                            "label": "布局：flex 基础",
                            "select_element": ["display", "flex", "justify-content", "align-items"]
                        }
                    }
                ],
                "edges": [
                    # 章节 1 与其 3 个知识点的关联
                    {"data": {"source": "1_end", "target": "1_1"}},
                    {"data": {"source": "1_end", "target": "1_2"}},
                    {"data": {"source": "1_end", "target": "1_3"}},
                    # 章节 2 与其 3 个知识点的关联
                    {"data": {"source": "2_end", "target": "2_1"}},
                    {"data": {"source": "2_end", "target": "2_2"}},
                    {"data": {"source": "2_end", "target": "2_3"}}
                ]
            }
            # 发送初始请求
            initial_request = {
                "knowledge_graph": test_knowledge_graph,
                "config": {}
            }
            
            print("\n📤 发送初始请求...")
            await websocket.send(json.dumps(initial_request))
            print("✅ 请求已发送")
            
            # 接收消息
            print("\n📥 等待服务器响应...")
            print("=" * 60)
            
            message_count = 0
            while True:
                try:
                    # 设置超时，避免无限等待
                    message = await asyncio.wait_for(websocket.recv(), timeout=300.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    msg_type = data.get("type", "unknown")
                    progress = data.get("progress", 0)
                    stage = data.get("stage", "")
                    msg_text = data.get("message", "")
                    
                    # 根据消息类型选择颜色
                    if msg_type == "generation_complete":
                        color = GREEN
                    elif msg_type in ("stage_start", "stage_complete", "item_complete", "confirmed", "cancelled"):
                        color = YELLOW
                    elif msg_type == "error":
                        color = RED
                    elif msg_type == "ping":
                        color = CYAN
                    else:
                        color = RESET

                    # 更简洁的一行输出，便于查看整体进度
                    stage_str = f", stage={stage}" if stage else ""
                    print(f"\n{color}[{message_count}] type={msg_type}{stage_str}, progress={progress}%, msg={msg_text}{RESET}")
                    # 同时输出一份截断后的原始数据，方便调试后端payload结构
                    try:
                        payload_preview = json.dumps(data, ensure_ascii=False)
                        if len(payload_preview) > 400:
                            payload_preview = payload_preview[:400] + "...(truncated)"
                        print(f"    raw: {payload_preview}")
                    except Exception:
                        # 万一序列化失败就忽略
                        pass
                    
                    # 如果是生成完成，等待用户确认
                    if msg_type == "generation_complete":
                        summary = data.get("data", {}).get("summary", {}) or {}
                        print("\n" + "=" * 60)
                        print("✅ 课程生成完成！"
                              f" 知识点: {summary.get('knowledge_count', 0)},"
                              f" 章节: {summary.get('chapter_count', 0)}")
                        print("=" * 60)
                        
                        # 模拟用户确认
                        print("\n📤 发送确认消息...")
                        confirm_message = {
                            "type": "confirm",
                            "data": data.get("data", {})
                        }
                        await websocket.send(json.dumps(confirm_message))
                        print("✅ 确认消息已发送")
                        
                        # 等待确认响应
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        confirm_data = json.loads(response)
                        print(f"\n✅ 收到确认响应: {confirm_data.get('message')}")
                        break
                    
                    # 如果是错误，退出
                    if msg_type == "error":
                        print(f"\n❌ 生成失败: {data.get('message')}")
                        if 'error' in data:
                            print(f"   错误详情: {data['error'][:200]}...")
                        break
                    
                except asyncio.TimeoutError:
                    print("\n⏱️ 等待超时，可能生成时间较长...")
                    print("   继续等待...")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("\n🔌 连接已关闭")
                    break
                    
    except ConnectionRefusedError:
        print("❌ 无法连接到服务器，请确保服务器已启动")
        print("   启动命令: python main.py 或 uvicorn main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🧪 WebSocket API 测试")
    print("=" * 60)
    asyncio.run(test_websocket())
