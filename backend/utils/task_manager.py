import uuid
import asyncio
import threading
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import traceback


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskInfo:
    task_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0
    total_steps: int = 1
    current_step: int = 0


class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = threading.Lock()

    def create_task(self, task_func: Callable, *args, **kwargs) -> str:
        """创建一个新任务并返回任务ID"""
        task_id = str(uuid.uuid4())
        
        with self._lock:
            self._tasks[task_id] = TaskInfo(
                task_id=task_id,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        # 在后台执行任务
        future = self._executor.submit(self._execute_task, task_id, task_func, *args, **kwargs)
        
        return task_id

    def _execute_task(self, task_id: str, task_func: Callable, *args, **kwargs):
        """执行任务的内部方法"""
        try:
            # 更新状态为处理中
            with self._lock:
                task_info = self._tasks[task_id]
                task_info.status = TaskStatus.PROCESSING
                task_info.updated_at = datetime.now()

            # 执行任务
            result = task_func(*args, **kwargs)

            # 更新状态为完成
            with self._lock:
                task_info = self._tasks[task_id]
                task_info.status = TaskStatus.COMPLETED
                task_info.result = result
                task_info.updated_at = datetime.now()
                task_info.progress = 100.0

        except Exception as e:
            # 更新状态为失败
            with self._lock:
                task_info = self._tasks[task_id]
                task_info.status = TaskStatus.FAILED
                task_info.error = str(e) + "\n" + traceback.format_exc()
                task_info.updated_at = datetime.now()

    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        with self._lock:
            return self._tasks.get(task_id)

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    def cleanup_old_tasks(self, max_age_minutes: int = 60):
        """清理过期任务"""
        current_time = datetime.now()
        with self._lock:
            old_tasks = [
                task_id for task_id, task_info in self._tasks.items()
                if (current_time - task_info.updated_at).total_seconds() > max_age_minutes * 60
            ]
            for task_id in old_tasks:
                del self._tasks[task_id]
        
        return len(old_tasks)


# 创建全局任务管理器实例
task_manager = TaskManager()