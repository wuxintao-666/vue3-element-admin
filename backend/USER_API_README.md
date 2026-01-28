# 用户管理API使用说明

## 数据库配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 创建数据库
使用MySQL客户端执行 `init_db.sql` 文件：
```bash
mysql -u root -p < init_db.sql
```

或者在MySQL中手动执行文件内容。

**默认数据库配置：**
- 主机：localhost
- 用户名：root
- 密码：root
- 数据库：vue3_admin

如需修改，请在 `db/database.py` 中修改 `DATABASE_URL`

### 3. 初始化数据库表（Python方式）
```bash
python init_db.py
```

## 提供的API端点

### 1. 获取用户列表（分页）
**请求：**
```
GET /api/v1/users/page?pageNum=1&pageSize=10&keywords=&status=
```

**参数说明：**
- `pageNum`: 页码，默认1
- `pageSize`: 每页数量，默认10
- `keywords`: 搜索关键词（用户名/昵称/手机号），可选
- `status`: 状态过滤（1:正常 0:禁用），可选

**响应示例：**
```json
{
    "code": "00000",
    "data": {
        "list": [
            {
                "id": 1,
                "username": "admin",
                "nickname": "超级管理员",
                "gender": "1",
                "mobile": "13800000000",
                "email": "admin@example.com",
                "avatar": null,
                "status": 1,
                "recentsignin": null,
                "createtime": "2024-01-28T10:00:00"
            }
        ],
        "total": 2
    },
    "message": "获取成功"
}
```

### 2. 获取用户详情
**请求：**
```
GET /api/v1/users/{user_id}/form
```

**响应示例：**
```json
{
    "code": "00000",
    "data": {
        "id": 1,
        "username": "admin",
        "nickname": "超级管理员",
        "gender": "1",
        "mobile": "13800000000",
        "email": "admin@example.com",
        "status": 1,
        "createtime": "2024-01-28T10:00:00"
    },
    "message": "获取成功"
}
```

### 3. 创建用户
**请求：**
```
POST /api/v1/users
Content-Type: application/json

{
    "username": "testuser",
    "password": "123456",
    "nickname": "测试用户",
    "gender": "1",
    "mobile": "13800000002",
    "email": "test@example.com",
    "status": 1
}
```

**响应示例：**
```json
{
    "code": "00000",
    "message": "创建成功"
}
```

### 4. 更新用户
**请求：**
```
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
    "nickname": "更新后的昵称",
    "mobile": "13800000003",
    "status": 1
}
```

**响应示例：**
```json
{
    "code": "00000",
    "message": "更新成功"
}
```

### 5. 删除用户（支持批量）
**请求：**
```
DELETE /api/v1/users/{user_ids}
```

参数说明：
- `user_ids`: 用户ID，多个用逗号分隔（如：1,2,3）

**响应示例：**
```json
{
    "code": "00000",
    "message": "删除成功"
}
```

### 6. 重置用户密码
**请求：**
```
POST /api/v1/users/{user_id}/reset-password
Content-Type: application/json

{
    "password": "newpassword123"
}
```

**响应示例：**
```json
{
    "code": "00000",
    "message": "重置成功"
}
```

## 数据库表结构

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    gender VARCHAR(2) DEFAULT '0',
    mobile VARCHAR(11),
    email VARCHAR(50),
    avatar VARCHAR(255),
    status INT DEFAULT 1,
    recentsignin DATETIME,
    createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 初始数据

创建数据库后，会自动插入以下用户：

| 用户名 | 密码   | 昵称        | 手机号      |
|--------|--------|-------------|------------|
| admin  | 123456 | 超级管理员  | 13800000000|
| user   | 123456 | 普通用户    | 13800000001|

## 注意事项

1. **密码加密**：当前实现中密码未加密，生产环境需要使用bcrypt或其他加密算法
2. **权限验证**：当前未实现权限验证，生产环境需要添加JWT认证
3. **错误处理**：API返回统一格式的错误响应
4. **性能优化**：建议在生产环境添加缓存和数据库连接池优化

## 运行服务

```bash
# 确保MySQL服务正在运行
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 运行服务
python main.py
# 或使用uvicorn
uvicorn main:app --reload
```

服务将在 `http://localhost:8000` 启动

## 前端集成

前端已配置使用这些API，确保：
1. 后端服务启动并运行
2. 数据库已初始化
3. CORS跨域已配置（已在main.py中配置）
