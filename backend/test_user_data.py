"""
生成测试用户数据
"""
from sqlalchemy.orm import sessionmaker
from db.database import engine
from db.models import User
from datetime import datetime
import uuid
from passlib.context import CryptContext

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

try:
    # 生成测试用户数据
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "nickname": "系统管理员",
            "gender": 1,
            "mobile": "13800138001",
            "email": "admin@example.com",
            "avatar": "/avatar/admin.png",
            "status": 1
        },
        {
            "username": "zhangsan",
            "password": "123456",
            "nickname": "张三",
            "gender": 1,
            "mobile": "13800138002",
            "email": "zhangsan@example.com",
            "avatar": "/avatar/zhangsan.png",
            "status": 1
        },
        {
            "username": "lisi",
            "password": "123456",
            "nickname": "李四",
            "gender": 2,
            "mobile": "13800138003",
            "email": "lisi@example.com",
            "avatar": "/avatar/lisi.png",
            "status": 1
        },
        {
            "username": "wangwu",
            "password": "123456",
            "nickname": "王五",
            "gender": 1,
            "mobile": "13800138004",
            "email": "wangwu@example.com",
            "avatar": "/avatar/wangwu.png",
            "status": 1
        },
        {
            "username": "zhaoliu",
            "password": "123456",
            "nickname": "赵六",
            "gender": 2,
            "mobile": "13800138005",
            "email": "zhaoliu@example.com",
            "avatar": "/avatar/zhaoliu.png",
            "status": 1
        },
        {
            "username": "sunqi",
            "password": "123456",
            "nickname": "孙七",
            "gender": 0,
            "mobile": "13800138006",
            "email": "sunqi@example.com",
            "avatar": "/avatar/sunqi.png",
            "status": 1
        },
        {
            "username": "zhouba",
            "password": "123456",
            "nickname": "周八",
            "gender": 1,
            "mobile": "13800138007",
            "email": "zhouba@example.com",
            "avatar": "/avatar/zhouba.png",
            "status": 1
        },
        {
            "username": "wujiu",
            "password": "123456",
            "nickname": "吴九",
            "gender": 2,
            "mobile": "13800138008",
            "email": "wujiu@example.com",
            "avatar": "/avatar/wujiu.png",
            "status": 1
        },
        {
            "username": "zhengshi",
            "password": "123456",
            "nickname": "郑十",
            "gender": 0,
            "mobile": "13800138009",
            "email": "zhengshi@example.com",
            "avatar": "/avatar/zhengshi.png",
            "status": 1
        },
        {
            "username": "testuser",
            "password": "123456",
            "nickname": "测试用户",
            "gender": 1,
            "mobile": "13800138010",
            "email": "test@example.com",
            "avatar": "/avatar/test.png",
            "status": 0  # 禁用状态的用户
        }
    ]

    inserted_count = 0
    for user_data in test_users:
        try:
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"用户 {user_data['username']} 已存在，跳过")
                continue

            # 创建用户对象
            user = User(
                username=user_data["username"],
                password=hash_password(user_data["password"]),
                nickname=user_data["nickname"],
                gender=user_data["gender"],
                mobile=user_data["mobile"],
                email=user_data["email"],
                avatar=user_data["avatar"],
                status=user_data["status"]
            )

            db.add(user)
            inserted_count += 1
            print(f"准备插入用户: {user_data['username']} - {user_data['nickname']}")

        except Exception as e:
            print(f"处理用户 {user_data['username']} 时出错: {e}")
            continue

    # 提交所有更改
    db.commit()
    print(f"\n成功插入 {inserted_count} 个用户!")

    # 显示插入的用户
    all_users = db.query(User).all()
    print(f"\n数据库中现在共有 {len(all_users)} 个用户:")
    for user in all_users:
        status_text = "正常" if user.status == 1 else "禁用"
        gender_text = {0: "未知", 1: "男", 2: "女"}.get(user.gender, "未知")
        print(f"ID: {user.id}, 用户名: {user.username}, 昵称: {user.nickname}, 性别: {gender_text}, 状态: {status_text}")

except Exception as e:
    print(f"插入测试数据失败: {e}")
    db.rollback()

finally:
    db.close()