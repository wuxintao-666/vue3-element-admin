# 环境配置说明

## 数据库配置

### MySQL数据库设置

1. **安装MySQL**（如果还未安装）
   - Windows: 下载安装MySQL Community Server
   - Mac: `brew install mysql`
   - Linux: `apt-get install mysql-server` 或 `yum install mysql-server`

2. **启动MySQL服务**
   ```bash
   # Windows (如果设置为服务)
   net start MySQL80
   
   # Mac/Linux
   sudo service mysql start
   # 或
   brew services start mysql
   ```

3. **创建数据库和表**
   
   方式一：使用SQL文件
   ```bash
   mysql -u root -p < init_db.sql
   ```
   
   方式二：手动创建
   ```bash
   mysql -u root -p
   ```
   然后在MySQL命令行中执行 `init_db.sql` 文件中的SQL语句

4. **数据库连接配置**
   
   在 `backend/db/database.py` 中修改 `DATABASE_URL`：
   ```python
   DATABASE_URL = "mysql+pymysql://用户名:密码@主机:端口/数据库名"
   ```
   
   例如：
   - 本地默认用户 root，密码 root：
     ```python
     DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/vue3_admin"
     ```
   
   - 自定义用户和密码：
     ```python
     DATABASE_URL = "mysql+pymysql://myuser:mypassword@192.168.1.100:3306/vue3_admin"
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
   # 创建数据库和表
   mysql -u root -p < init_db.sql
   
   # 或使用Python脚本
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

**错误信息：** `Can't connect to MySQL server`

**解决方案：**
1. 检查MySQL服务是否启动
2. 检查数据库用户名和密码是否正确
3. 检查数据库是否存在
4. 检查防火墙是否阻止了连接

### 找不到数据库驱动

**错误信息：** `No module named 'pymysql'`

**解决方案：**
```bash
pip install pymysql
```

### 表不存在

**错误信息：** `Table 'vue3_admin.users' doesn't exist`

**解决方案：**
运行初始化脚本：
```bash
python init_db.py
```

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
