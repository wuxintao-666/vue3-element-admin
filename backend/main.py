import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.upload_router import upload_router
from api.prd_router import prd_router
from api.knowledge_router import knowledge_router
from api.executor_router import executor_router
from api.preview_router import preview_router
from api.logs_router import logs_router
from api.learning_router import learning_router
from api.test_router import test_router  # 添加这一行
from api.admin_router import admin_router  # 添加管理系统API路由
from api.user_router import user_router  # 用户管理单独路由
from api.auth_router import auth_router  # 添加认证API路由
from api.course_router import course_router  # 课程管理路由
#from api.theme_router import theme_router  # 主题管理路由
from api.knowledge_content_router import knowledge_content_router  # 知识内容管理路由
from api.programming_exercise_router import programming_exercise_router  # 编程练习题管理路由
from api.test_question_router import test_question_router  # 测试题管理路由
#from api.knowledge_graph_router import knowledge_graph_router  # 知识图谱管理路由
from db.database import Base, engine
import os

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # 暴露Content-Disposition头部，用于文件下载
)

# 注册路由
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(prd_router, prefix="/api/prd", tags=["PRD"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(executor_router, prefix="/api/execute", tags=["Executor"])
app.include_router(preview_router, prefix="/api/preview", tags=["Preview"])
app.include_router(logs_router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(learning_router, prefix="/api/learning", tags=["Learning"])
app.include_router(test_router, prefix="/api/test", tags=["Test"])  # 添加这一行
# 添加用户管理路由（前端用户管理页面使用）
app.include_router(user_router)

# 添加管理系统API路由
app.include_router(admin_router)

# 添加认证API路由
app.include_router(auth_router)

# 添加主题管理路由
#app.include_router(theme_router)

# 添加知识内容管理路由
app.include_router(knowledge_content_router)

# 添加编程练习题管理路由
app.include_router(programming_exercise_router)
app.include_router(test_question_router)

# 添加知识图谱管理路由
from api.knowledge_graph_router import knowledge_graph_router
app.include_router(knowledge_graph_router)

# 添加课程管理路由
app.include_router(course_router)

# 添加静态文件服务
# 设置静态文件目录路径
STATIC_DIR = os.path.join("data", "results", "project", "src")
if os.path.exists(STATIC_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/api/src", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return {"message": "SCOT-Web Backend API"}

if __name__ == "__main__":
    import uvicorn
    # 使用多线程模式提高并发处理能力
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=1,  # 使用1个worker进程
        loop="asyncio",  # 使用asyncio事件循环
        access_log=True,
        log_level="info",
        # 优化并发性能
        server_header=False,
        date_header=False,
        # 限制请求体大小，避免大文件上传问题
        limit_concurrency=100,  # 限制并发连接数
        backlog=2048  # 监听队列长度
    )