import logging
import os
from datetime import datetime

# 创建logs目录
logs_dir = os.path.join("data", "logs")
os.makedirs(logs_dir, exist_ok=True)

# 创建logger
logger = logging.getLogger("scot-web")
logger.setLevel(logging.DEBUG)

# 文件日志已被禁用
# log_filename = os.path.join(logs_dir, f"scot-web-{datetime.now().strftime('%Y%m%d')}.log")
# file_handler = logging.FileHandler(log_filename, encoding='utf-8')
# file_handler.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# file_handler.setFormatter(formatter)  # 文件处理器已被禁用
console_handler.setFormatter(formatter)

# 添加处理器到logger
# logger.addHandler(file_handler)  # 禁用文件日志记录
logger.addHandler(console_handler)