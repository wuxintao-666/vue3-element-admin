# 环境配置说明

## 数据库配置

### PostgreSQL数据库设置

1. **安装PostgreSQL**（如果还未安装）
   - Windows: 下载安装PostgreSQL
   - Mac: `brew install postgresql`
   - Linux: `apt-get install postgresql postgresql-contrib` 或 `yum install postgresql postgresql-contrib`

2. **启动PostgreSQL服务**
   ```bash
   # Windows (如果设置为服务)
   net start postgresql-x64-15

   # Mac/Linux
   sudo service postgresql start
   # 或
   brew services start postgresql
   ```

3. **创建数据库和表**

   方式一：使用Python脚本
   ```bash
   cd backend
   python init_db.py
   ```

   方式二：手动创建
   ```bash
   # 连接到PostgreSQL
   psql -U postgres

   # 在PostgreSQL命令行中创建数据库
   CREATE DATABASE vue3_admin WITH ENCODING 'UTF8';
   ```

4. **数据库连接配置**

   在 `backend/db/database.py` 中修改 `DATABASE_URL`：
   ```python
   DATABASE_URL = "postgresql://用户名:密码@主机:端口/数据库名"
   ```

   例如：
   - 本地默认用户 postgres，密码 123456：
     ```python
     DATABASE_URL = "postgresql://postgres:123456@localhost:5432/vue3_admin"
     ```

   - 自定义用户和密码：
     ```python
     DATABASE_URL = "postgresql://myuser:mypassword@192.168.1.100:5432/vue3_admin"
     ```

### 验证数据库连接

```bash
# 进入backend目录
cd backend

# 运行初始化脚本验证连接
python init_db.py

# 或启动服务测试
python main.py
```

## 首次启动步骤

1. **安装Python依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **初始化数据库**
   ```bash
   # 使用Python脚本创建数据库和表
   python init_db.py
   ```

3. **启动后端服务**
   ```bash
   python main.py
   ```
   
   服务将在 `http://localhost:8000` 启动

4. **启动前端**
   ```bash
   # 在项目根目录
   npm install
   npm run dev
   ```

## 常见问题

### 连接数据库失败

**错误信息：** `Can't connect to PostgreSQL server` 或连接超时

**解决方案：**
1. 检查PostgreSQL服务是否启动
2. 检查数据库用户名和密码是否正确
3. 检查数据库是否存在
4. 检查防火墙是否阻止了连接（PostgreSQL默认端口5432）
5. 确认PostgreSQL配置允许远程连接（pg_hba.conf文件）

### 找不到数据库驱动

**错误信息：** `No module named 'psycopg2'`

**解决方案：**
```bash
pip install psycopg2-binary
```

### 表不存在

**错误信息：** `relation "vue3_admin.users" does not exist`

**解决方案：**
运行初始化脚本：
```bash
python init_db.py
```

### 权限问题

**错误信息：** `permission denied for database` 或 `role does not exist`

**解决方案：**
1. 使用PostgreSQL管理员账号创建数据库：
   ```sql
   CREATE USER myuser WITH PASSWORD 'mypassword';
   CREATE DATABASE vue3_admin OWNER myuser;
   GRANT ALL PRIVILEGES ON DATABASE vue3_admin TO myuser;
   ```
2. 或修改连接字符串使用有足够权限的用户（如postgres）

## 数据库初始数据

运行 `init_db.sql` 后，数据库中会包含以下初始用户：

| 用户名 | 密码   | 昵称        | 电话号码     | 邮箱               |
|--------|--------|-------------|--------------|-------------------|
| admin  | 123456 | 超级管理员  | 13800000000  | admin@example.com |
| user   | 123456 | 普通用户    | 13800000001  | user@example.com  |

## 生产环境建议

1. **密码加密**
   - 使用bcrypt加密用户密码
   - 修改 `backend/utils/password_utils.py` 中的密码处理

2. **数据库配置**
   - 使用环境变量管理数据库连接信息
   - 在 `.env` 文件中配置敏感信息

3. **权限管理**
   - 实现JWT token认证
   - 为每个API添加权限检查

4. **性能优化**
   - 添加数据库连接池
   - 实现缓存策略
   - 添加API速率限制
