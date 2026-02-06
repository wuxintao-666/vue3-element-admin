# 管理员系统说明

## 📋 概述

系统现在分离了普通用户和管理员，提供了独立的管理员表(`admins`)用于管理系统后台登录。

## 🗄️ 数据库结构

### Admin 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键ID |
| username | VARCHAR(50) | 管理员用户名（唯一） |
| password | VARCHAR(255) | 密码哈希（bcrypt） |
| email | VARCHAR(100) | 邮箱 |
| mobile | VARCHAR(20) | 手机号 |
| last_login | DATETIME | 最后登录时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 🔧 初始化管理员

### 1. 重置数据库（首次运行或结构变更时）

```bash
cd backend
python reset_database.py
```

### 2. 初始化管理员账户

```bash
python init_admin.py
```

**默认管理员账户：**
- 用户名: `admin`
- 密码: `123456`
- 邮箱: `admin@example.com`
- 手机号: `13800000000`

## 🧪 测试功能

运行管理员功能测试：

```bash
python test_admin.py
```

## 🔐 登录验证流程

1. **前端提交**: 用户名 + 密码
2. **后端验证**:
   - 从 `admins` 表查询用户
   - 验证密码哈希（bcrypt）
   - 更新最后登录时间
3. **返回Token**: 生成访问令牌和刷新令牌

## 🚀 API 接口

### 登录接口
```
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "username": "admin",
  "password": "123456",
  "captchaKey": "xxx",
  "captchaCode": "ABCD"
}
```

**响应:**
```json
{
  "code": "00000",
  "data": {
    "access_token": "admin_token_1_1234567890",
    "refresh_token": "refresh_token_1_1234567890"
  },
  "msg": "登录成功"
}
```

### 注册接口
```
POST /api/v1/auth/register
```

**请求体:**
```json
{
  "username": "newadmin",
  "password": "123456",
  "email": "admin@example.com",
  "mobile": "13800000000"
}
```

## ⚠️ 注意事项

1. **密码安全**: 密码使用bcrypt哈希存储
2. **日志记录**: 每次登录会更新最后登录时间

## 🛠️ 开发说明

- 管理员模型: `db/models.py` - `Admin` 类
- 管理员Schema: `schemas/admin_schema.py`
- 登录逻辑: `api/admin_router.py`
- 初始化脚本: `init_admin.py`
- 测试脚本: `test_admin.py`