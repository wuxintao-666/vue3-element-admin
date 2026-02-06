"""
测试访问统计和访问趋势API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_visit_stats():
    """测试访问统计API"""
    print("测试访问统计API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/logs/visit-stats")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"总访问量: {data.get('total_visits')}")
            print(f"独立访客: {data.get('unique_visitors')}")
            print(f"平均会话时长: {data.get('avg_session_duration')}秒")
            print(f"跳出率: {data.get('bounce_rate')}")
            print(f"设备统计: {data.get('device_stats')}")
        else:
            print(f"❌ API调用失败: {response.text}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_visit_trend():
    """测试访问趋势API"""
    print("\n测试访问趋势API...")
    try:
        params = {
            "startDate": "2026-02-01",
            "endDate": "2026-02-07"
        }
        response = requests.get(f"{BASE_URL}/api/v1/logs/visit-trend", params=params)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"数据点数量: {data.get('total')}")
            trend_data = data.get('data', [])
            if trend_data:
                print("前3个数据点:")
                for item in trend_data[:3]:
                    print(f"  {item['date']}: 访问量{item['visits']}, 独立访客{item['unique_visitors']}")
        else:
            print(f"❌ API调用失败: {response.text}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_visit_stats()
    test_visit_trend()