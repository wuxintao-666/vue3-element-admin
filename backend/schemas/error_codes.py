"""
错误码定义 - 统一错误码规范
"""

class ErrorCodes:
    """错误码常量定义"""

    # 成功码
    SUCCESS = "00000"

    # 系统级错误 (A开头)
    SYSTEM_ERROR = "A0001"          # 系统内部错误
    PARAM_ERROR = "A0002"           # 参数错误
    UNAUTHORIZED = "A0003"          # 未授权
    FORBIDDEN = "A0004"             # 权限不足
    NOT_FOUND = "A0005"             # 资源不存在
    METHOD_NOT_ALLOWED = "A0006"    # 请求方法不允许
    TIMEOUT = "A0007"               # 请求超时
    RATE_LIMIT = "A0008"            # 请求频率限制

    # 用户相关错误 (U开头)
    USER_NOT_EXIST = "U0001"        # 用户不存在
    USER_PASSWORD_ERROR = "U0002"   # 密码错误

    # 验证码相关错误 (C开头)
    CAPTCHA_ERROR = "C0001"         # 验证码错误
    CAPTCHA_EXPIRED = "C0002"       # 验证码过期
    CAPTCHA_REQUIRED = "C0003"      # 需要验证码

    # 数据相关错误 (D开头)
    DATA_NOT_FOUND = "D0001"        # 数据不存在
    DATA_ALREADY_EXISTS = "D0002"   # 数据已存在
    DATA_VALIDATION_ERROR = "D0003" # 数据验证错误

    # 文件相关错误 (F开头)
    FILE_UPLOAD_ERROR = "F0001"     # 文件上传错误
    FILE_NOT_ALLOWED = "F0002"      # 文件类型不允许
    FILE_TOO_LARGE = "F0003"        # 文件过大


class ErrorMessages:
    """错误信息常量定义"""

    # 成功信息
    SUCCESS = "操作成功"

    # 系统级错误信息
    SYSTEM_ERROR = "系统内部错误，请稍后重试"
    PARAM_ERROR = "参数错误，请检查输入"
    UNAUTHORIZED = "未授权访问，请先登录"
    FORBIDDEN = "权限不足，无法访问"
    NOT_FOUND = "请求的资源不存在"
    METHOD_NOT_ALLOWED = "请求方法不允许"
    TIMEOUT = "请求超时，请重试"
    RATE_LIMIT = "请求过于频繁，请稍后再试"

    # 用户相关错误信息
    USER_NOT_EXIST = "用户名或密码错误"
    USER_PASSWORD_ERROR = "用户名或密码错误"

    # 验证码相关错误信息
    CAPTCHA_ERROR = "验证码错误"
    CAPTCHA_EXPIRED = "验证码已过期，请重新获取"
    CAPTCHA_REQUIRED = "请输入验证码"

    # 数据相关错误信息
    DATA_NOT_FOUND = "数据不存在"
    DATA_ALREADY_EXISTS = "数据已存在"
    DATA_VALIDATION_ERROR = "数据验证失败"

    # 文件相关错误信息
    FILE_UPLOAD_ERROR = "文件上传失败"
    FILE_NOT_ALLOWED = "文件类型不允许"
    FILE_TOO_LARGE = "文件大小超过限制"


def get_error_response(code: str, custom_message: str = None) -> dict:
    """获取错误响应

    Args:
        code: 错误码
        custom_message: 自定义错误信息，如果不提供则使用默认信息

    Returns:
        错误响应字典
    """
    from .base_schema import ApiResponse

    message = custom_message or getattr(ErrorMessages, code, "未知错误")
    return ApiResponse(code=code, data=None, message=message).dict()


def get_success_response(data: any = None, message: str = None) -> dict:
    """获取成功响应

    Args:
        data: 响应数据
        message: 响应信息，默认"操作成功"

    Returns:
        成功响应字典
    """
    from .base_schema import ApiResponse

    message = message or ErrorMessages.SUCCESS
    return ApiResponse(code=ErrorCodes.SUCCESS, data=data, message=message).dict()