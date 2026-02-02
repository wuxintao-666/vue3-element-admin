#!/usr/bin/env python3
"""
测试知识图谱保存到数据库的API
"""

try:
    import requests
    import json
except ImportError as e:
    print(f"❌ 缺少必要的模块: {e}")
    print("请运行: pip install requests")
    exit(1)

# 测试数据
test_data = {
    "course_code": "TEST001",  
    "name": "测试知识图谱",
    "graph": {
        "nodes": [
            {
                "data": {
                    "id": "node1",
                    "label": "HTML基础",
                    "type": "chapter",
                    "select_element": ["html", "head", "body"]
                }
            },
            {
                "data": {
                    "id": "node2",
                    "label": "标题标签",
                    "type": "knowledge",
                    "select_element": ["h1", "h2", "h3"]
                }
            }
        ],
        "edges": [
            {
                "data": {
                    "source": "node1",
                    "target": "node2"
                }
            }
        ],
        "dependent_edges": [
            {
                "data": {
                    "source": "node1",
                    "target": "node2"
                }
            }
        ]
    }
}

def test_server_connection():
    """测试服务器连接"""
    url = "http://localhost:8000"
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ 服务器连接正常: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("请确保后端服务器正在运行 (python backend/main.py)")
        return False

def test_save_to_database():
    """测试保存到数据库功能"""
    url = "http://localhost:8000/api/knowledge/save_to_database"

    print("📤 发送请求数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print("\n" + "="*50)

    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 保存成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ 保存失败! 状态码: {response.status_code}")
            try:
                error_detail = response.json()
                print("错误详情:")
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print("错误内容:")
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == "__main__":
    print("🔍 开始测试知识图谱保存到数据库功能")
    print("="*50)

    # 1. 测试服务器连接
    if not test_server_connection():
        exit(1)

    print("\n" + "="*50)

    # 2. 测试保存功能
    test_save_to_database()