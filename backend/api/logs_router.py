from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from datetime import datetime, timedelta
import random

from schemas.base_schema import ApiResponse
from schemas.error_codes import ErrorCodes, ErrorMessages

logs_router = APIRouter()

class LogEntry(BaseModel):
    task_id: str
    timestamp: str
    files: List[str]
    status: str

class LogsResponse(BaseModel):
    logs: List[LogEntry]


# 访问统计相关的数据模型
class VisitStatsVO(BaseModel):
    """访问统计数据 - 匹配前端期望格式"""
    todayUvCount: int       # 今日访客数(UV)
    totalUvCount: int       # 总访客数
    uvGrowthRate: float     # 访客数同比增长率
    todayPvCount: int       # 今日浏览量(PV)
    totalPvCount: int       # 总浏览量
    pvGrowthRate: float     # 同比增长率


class VisitTrendVO(BaseModel):
    """访问趋势数据 - 匹配前端期望格式"""
    dates: List[str]
    pvList: List[int]  # 浏览量(PV)
    uvList: List[int]  # 访客数(UV)
    ipList: List[int]  # IP数

@logs_router.get("/", response_model=LogsResponse)
async def get_logs():
    """
    日志查询接口
    """
    # 创建日志目录
    logs_dir = os.path.join("data", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    logs = []
    
    # 查找所有任务记录
    tasks_dir = os.path.join("data", "tasks")
    if os.path.exists(tasks_dir):
        for filename in os.listdir(tasks_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(tasks_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        task_data = json.load(f)
                    
                    # 构造日志条目
                    log_entry = LogEntry(
                        task_id=task_data.get("task_id", filename.replace(".json", "")),
                        timestamp=task_data.get("finished_at", task_data.get("created_at", datetime.now().isoformat())),
                        files=["index.html", "style.css"],  # 示例文件
                        status=task_data.get("status", "unknown")
                    )
                    logs.append(log_entry)
                except Exception:
                    continue
    
    # 按时间倒序排列
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    
    return LogsResponse(logs=logs)


@logs_router.get("/visit-stats")
async def get_visit_stats():
    """
    获取访问统计数据 - 返回前端期望的格式
    """
    # 生成模拟数据
    today_uv = random.randint(50, 200)
    total_uv = random.randint(1000, 5000)
    today_pv = random.randint(100, 500)
    total_pv = random.randint(5000, 20000)

    # 计算增长率（模拟数据）
    uv_growth_rate = round(random.uniform(-0.5, 0.8), 2)  # -50% 到 +80%
    pv_growth_rate = round(random.uniform(-0.3, 1.0), 2)  # -30% 到 +100%

    return ApiResponse(
        code="00000",
        data=VisitStatsVO(
            todayUvCount=today_uv,
            totalUvCount=total_uv,
            uvGrowthRate=uv_growth_rate,
            todayPvCount=today_pv,
            totalPvCount=total_pv,
            pvGrowthRate=pv_growth_rate
        ),
        message="success"
    )


@logs_router.get("/visit-trend", response_model=ApiResponse)
async def get_visit_trend(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD")
):
    """
    获取访问趋势数据 - 返回前端期望的格式
    """
    try:
        # 解析日期
        start = datetime.strptime(startDate, "%Y-%m-%d")
        end = datetime.strptime(endDate, "%Y-%m-%d")

        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

        # 初始化数据数组
        dates = []
        pvList = []  # 浏览量
        uvList = []  # 访客数
        ipList = []  # IP数

        # 生成日期范围内的数据
        current_date = start
        while current_date <= end:
            # 生成模拟数据，添加一些随机波动
            base_visits = random.randint(50, 200)
            visits = base_visits + random.randint(-20, 20)
            unique_visitors = int(visits * random.uniform(0.6, 0.9))
            ip_count = int(unique_visitors * random.uniform(0.8, 1.2))  # IP数通常略多于UV

            dates.append(current_date.strftime("%Y-%m-%d"))
            pvList.append(max(1, visits))      # 确保至少有1次访问
            uvList.append(max(1, unique_visitors))
            ipList.append(max(1, ip_count))

            current_date += timedelta(days=1)

        return ApiResponse(
            code="00000",
            data=VisitTrendVO(
                dates=dates,
                pvList=pvList,
                uvList=uvList,
                ipList=ipList
            ),
            message="success"
        )

    except ValueError as e:
        return ApiResponse(
            code=ErrorCodes.PARAM_ERROR,
            data=None,
            message="日期格式错误，请使用YYYY-MM-DD格式"
        )
    except Exception as e:
        return ApiResponse(
            code=ErrorCodes.SYSTEM_ERROR,
            data=None,
            message="获取访问趋势数据失败，请稍后重试"
        )
@logs_router.get("/{task_id}", response_model=LogEntry)
async def get_log_detail(task_id: str):
    """获取指定任务的日志详情"""
    tasks_dir = os.path.join("data", "tasks")
    task_file = os.path.join(tasks_dir, f"{task_id}.json")
    
    if not os.path.exists(task_file):
        raise HTTPException(status_code=404, detail="日志未找到")
    
    with open(task_file, "r", encoding="utf-8") as f:
        task_data = json.load(f)
    
    return LogEntry(
        task_id=task_data.get("task_id", task_id),
        timestamp=task_data.get("finished_at", task_data.get("created_at", datetime.now().isoformat())),
        files=["index.html", "style.css"],  # 示例文件
        status=task_data.get("status", "unknown")
    )

@logs_router.delete("/{task_id}")
async def delete_log(task_id: str):
    """删除指定任务的日志"""
    logs_dir = os.path.join("data", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # 查找并删除匹配的日志文件
    for filename in os.listdir(logs_dir):
        if filename.startswith(f"{task_id}_") and filename.endswith(".txt"):
            filepath = os.path.join(logs_dir, filename)
            os.remove(filepath)
            return {"message": "Log deleted successfully"}

    raise HTTPException(status_code=404, detail="Log not found")


