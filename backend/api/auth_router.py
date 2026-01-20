from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import random
import string
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import hashlib
import time

auth_router = APIRouter(prefix="/api/v1")

class CaptchaResponse(BaseModel):
    code: str = "00000"
    data: dict
    msg: str = "success"

class CaptchaInfo(BaseModel):
    captcha_key: str
    captcha_image: str  # base64编码的图片

def generate_captcha_text(length: int = 4) -> str:
    """生成随机验证码文本"""
    chars = string.ascii_uppercase + string.digits
    # 避免容易混淆的字符
    chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(random.choice(chars) for _ in range(length))

def create_captcha_image(text: str) -> str:
    """创建验证码图片并返回base64编码"""
    # 创建图像
    width, height = 120, 40
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 字体（如果没有字体文件，使用默认字体）
    try:
        font = ImageFont.truetype("arial.ttf", 25)
    except IOError:
        font = ImageFont.load_default()

    # 绘制文字 - 使用textbbox替代已废弃的textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)), font=font)

    # 添加干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)), width=1)

    # 将图片转换为base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# 模拟存储验证码的简单方式（实际项目中应该使用Redis等缓存）
captcha_store = {}

from pydantic import Field

class CaptchaInfoResponse(BaseModel):
    captchaKey: str = Field(alias='captcha_key')
    captchaBase64: str = Field(alias='captcha_image')
    class Config:
        allow_population_by_field_name = True  # 允许用 Python 字段名初始化

class CaptchaResponseFinal(BaseModel):
    code: str = "00000"
    data: CaptchaInfoResponse
    msg: str = "success"

@auth_router.get("/auth/captcha", response_model=CaptchaResponseFinal)
async def get_captcha():
    """
    获取验证码
    """
    # 生成验证码文本
    captcha_text = generate_captcha_text()
    
    # 生成唯一的key
    captcha_key = hashlib.md5(f"{captcha_text}{time.time()}".encode()).hexdigest()
    
    # 保存验证码文本（实际项目中应设置过期时间）
    captcha_store[captcha_key] = captcha_text.lower()
    
    # 创建验证码图片
    captcha_image = create_captcha_image(captcha_text)
    
    # 实际项目中应该清理过期的验证码
    if len(captcha_store) > 100:
        # 清理最老的一些验证码（这里简化处理，实际应按时间清理）
        keys_to_remove = list(captcha_store.keys())[:20]
        for key in keys_to_remove:
            captcha_store.pop(key, None)
    
    captcha_info = CaptchaInfoResponse(
        captcha_key=captcha_key,
        captcha_image=captcha_image
    )
    
    return CaptchaResponseFinal(
        data=captcha_info
    )

# 为了方便测试，添加一个获取存储的验证码的方法
@auth_router.get("/auth/captcha/{captcha_key}")
async def get_stored_captcha(captcha_key: str):
    captcha_text = captcha_store.get(captcha_key)
    if captcha_text:
        return {"code": "00000", "data": captcha_text, "msg": "success"}
    else:
        return {"code": "404", "data": None, "msg": "验证码不存在或已过期"}