# Schema 架构说明

## 📋 概述

所有API响应格式已统一使用 `base_schema.py` 中的标准响应类，错误码规范统一使用 `error_codes.py`。

## 🏗️ 架构设计

### 1. 基础响应类 (`base_schema.py`)

```python
from schemas.base_schema import ApiResponse, PageResponse, ListResponse

# 通用API响应
response = ApiResponse(code="00000", data=my_data, message="success")

# 分页响应
page_response = PageResponse(
    code="00000",
    data=items,
    message="success",
    total=100,
    page=1,
    size=10,
    pages=10
)

# 列表响应
list_response = ListResponse(
    code="00000",
    data=items,
    message="success",
    total=50
)
```

### 2. 灵活的数据类型

响应类使用 `Any` 类型支持各种数据格式：

```python
from schemas.base_schema import ApiResponse

# 支持任意数据类型
response = ApiResponse(
    code="00000",
    data={"name": "John", "age": 25},  # 字典
    message="success"
)

# 也支持模型对象
response2 = ApiResponse(
    code="00000",
    data=my_pydantic_model,  # Pydantic模型
    message="success"
)
```

## 📁 文件结构

```
schemas/
├── base_schema.py      # 统一响应格式
├── error_codes.py      # 统一错误码规范
├── user_schema.py      # 用户相关模型
├── course_schema.py    # 课程相关模型
├── knowledge_content_schema.py
├── programming_exercise_schema.py
├── knowledge_graph_schema.py
├── theme_schema.py
└── README.md          # 本文档
```

## 🔍 错误码规范

### 错误码格式

错误码采用以下格式：
- **前缀**: 标识错误类型 (1字母)
- **数字**: 具体错误编号 (4位数字)

```
[A|U|C|D|F][0-9]{4}
│ │     └── 四位数字编号
│ └────── 一字母错误类型前缀
└──────── 错误码总长度为5位
```

### 错误类型前缀

| 前缀 | 含义 | 示例错误码 |
|------|------|------------|
| `A` | 系统级错误 | `A0001` - 系统内部错误 |
| `U` | 用户相关 | `U0001` - 用户不存在 |
| `C` | 验证码相关 | `C0001` - 验证码错误 |
| `D` | 数据相关 | `D0001` - 数据不存在 |
| `F` | 文件相关 | `F0001` - 文件上传错误 |

### 常用错误码和信息

```python
from schemas.error_codes import ErrorCodes, ErrorMessages

# 成功码
ErrorCodes.SUCCESS = "00000"

# 系统级错误
ErrorCodes.SYSTEM_ERROR = "A0001"      # "系统内部错误，请稍后重试"
ErrorCodes.PARAM_ERROR = "A0002"       # "参数错误，请检查输入"
ErrorCodes.UNAUTHORIZED = "A0003"      # "未授权访问，请先登录"
ErrorCodes.FORBIDDEN = "A0004"         # "权限不足，无法访问"

# 用户相关错误
ErrorCodes.USER_NOT_EXIST = "U0001"    # "用户名或密码错误"
ErrorCodes.USER_PASSWORD_ERROR = "U0002" # "用户名或密码错误"

# 验证码相关错误
ErrorCodes.CAPTCHA_ERROR = "C0001"     # "验证码错误"
ErrorCodes.CAPTCHA_EXPIRED = "C0002"   # "验证码已过期，请重新获取"
ErrorCodes.CAPTCHA_REQUIRED = "C0003"  # "请输入验证码"
```

### 使用示例

```python
from schemas.base_schema import ApiResponse
from schemas.error_codes import ErrorCodes, ErrorMessages, get_error_response, get_success_response

# 成功响应
response = get_success_response(data={"result": "ok"})
# 等同于: {"code": "00000", "data": {"result": "ok"}, "message": "操作成功"}

# 错误响应
response = get_error_response(ErrorCodes.USER_NOT_EXIST)
# 等同于: {"code": "U0001", "data": None, "message": "用户名或密码错误"}

# 自定义错误信息
response = get_error_response(ErrorCodes.PARAM_ERROR, "邮箱格式不正确")

# 在API中使用
@app.post("/api/login")
async def login():
    try:
        # 登录逻辑
        return get_success_response(data={"token": "xxx"})
    except ValueError:
        return get_error_response(ErrorCodes.PARAM_ERROR)
    except Exception:
        return get_error_response(ErrorCodes.SYSTEM_ERROR)
```

## 🔄 迁移说明

### 旧代码
```python
# 每个schema文件都重复定义
class ApiResponse(BaseModel):
    code: str = "00000"
    data: Optional[dict] = None
    message: Optional[str] = None
```

### 新代码
```python
# 统一导入
from schemas.base_schema import ApiResponse, PageResponse

# 在API中使用
return ApiResponse(data=my_data, message="success")
```

## ✅ 优势

1. **统一性**: 所有API使用相同的响应格式
2. **类型安全**: 支持泛型，提供更好的类型提示
3. **维护性**: 响应格式修改只需在一处进行
4. **一致性**: 前后端响应格式完全一致
5. **可扩展**: 容易添加新的响应类型

## 🚀 使用指南

### 在Router中使用

```python
from schemas.base_schema import ApiResponse

@router.get("/items", response_model=ApiResponse)
async def get_items():
    return ApiResponse(data=items, message="获取成功")
```

### 在Service中使用

```python
from schemas.base_schema import ApiResponse

def create_success_response(data: Any, message: str = "success") -> ApiResponse:
    return ApiResponse(data=data, message=message)

def create_error_response(message: str, code: str = "A0001") -> ApiResponse:
    return ApiResponse(code=code, data=None, message=message)
```

## 📊 响应状态码

- `00000`: 成功
- `A0001`: 通用错误
- `A0002`: 参数错误
- `A0003`: 未授权
- `A0004`: 权限不足
- `A0005`: 资源不存在