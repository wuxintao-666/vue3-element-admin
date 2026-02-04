import os
from dotenv import load_dotenv

def load_config():
    """
    加载环境配置
    """
    load_dotenv()
    
    config = {
        "MODELSCOPE_API_KEY": os.getenv("MODELSCOPE_API_KEY", "ms-d4a3ae0f-503a-41d9-a963-1a4ddc5b3bad"),
        "MODELSCOPE_BASE_URL": os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1"),
        "FAST_MODEL": os.getenv("FAST_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        "SLOW_MODEL": os.getenv("SLOW_MODEL", "deepseek-ai/DeepSeek-V3.2"),
        "EXECUTOR_MODEL": os.getenv("EXECUTOR_MODEL", "deepseek-ai/DeepSeek-V3.2"),
        "TEST_COURSE_ID": os.getenv("TEST_COURSE_ID", "TEST001"),
    }
    
    return config