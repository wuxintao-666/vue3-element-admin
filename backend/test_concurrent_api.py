#!/usr/bin/env python3
"""
测试后端API的并发处理能力
"""
import asyncio
import aiohttp
import time
import json
from typing import List, Dict

async def test_single_request(session: aiohttp.ClientSession, request_id: int, knowledge_node: Dict) -> Dict:
    """测试单个API请求"""
    url = "http://localhost:8000/api/learning/generate-knowledge-point"
    start_time = time.time()

    try:
        async with session.post(url, json=knowledge_node) as response:
            result = await response.json()
            end_time = time.time()
            duration = end_time - start_time

            if response.status == 200:
                return {
                    "request_id": request_id,
                    "status": "success",
                    "duration": duration,
                    "data": result
                }
            else:
                return {
                    "request_id": request_id,
                    "status": "error",
                    "duration": duration,
                    "error": result
                }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        return {
            "request_id": request_id,
            "status": "exception",
            "duration": duration,
            "error": str(e)
        }

async def test_concurrent_requests(num_requests: int = 5):
    """测试并发请求"""
    print(f"开始测试 {num_requests} 个并发请求...")

    # 测试数据
    test_knowledge_node = {
        "id": "test_1",
        "label": "测试HTML基础",
        "type": "knowledge",
        "select_element": ["html", "head", "body"]
    }

    # 创建多个测试数据（稍微修改以区分）
    test_data = []
    for i in range(num_requests):
        data = test_knowledge_node.copy()
        data["id"] = f"test_{i+1}"
        data["label"] = f"测试HTML基础_{i+1}"
        test_data.append(data)

    async with aiohttp.ClientSession() as session:
        start_time = time.time()

        # 并发执行所有请求
        tasks = [
            test_single_request(session, i+1, data)
            for i, data in enumerate(test_data)
        ]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_duration = end_time - start_time

        # 分析结果
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] != "success"]

        print("\n=== 测试结果 ===")
        print(f"总请求数: {num_requests}")
        print(f"成功数: {len(successful)}")
        print(f"失败数: {len(failed)}")
        print(f"总耗时: {total_duration:.2f}秒")
        if successful:
            avg_duration = sum(r['duration'] for r in successful) / len(successful)
            print(f"平均响应时间: {avg_duration:.2f}秒")
        print(f"并发效率: {total_duration / max(r['duration'] for r in results):.2f}x")

        if failed:
            print("\n失败的请求:")
            for fail in failed:
                print(f"  请求 {fail['request_id']}: {fail['status']} - {fail.get('error', 'Unknown error')}")

        return results

if __name__ == "__main__":
    # 测试不同数量的并发请求
    for num_requests in [3, 5, 8]:
        print(f"\n{'='*50}")
        print(f"测试 {num_requests} 个并发请求")
        print(f"{'='*50}")
        asyncio.run(test_concurrent_requests(num_requests))