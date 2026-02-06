"""
初始化管理员用户脚本
"""
from db.database import SessionLocal, engine, Base
from db.models import Admin
from passlib.context import CryptContext
from datetime import datetime

# 创建密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """创建管理员用户"""
    # 创建数据库表（如果不存在）
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 检查管理员用户是否已存在
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if existing_admin:
            print("管理员用户已存在，跳过创建")
            return existing_admin

        # 创建管理员用户
        hashed_password = pwd_context.hash("123456")

        admin_user = Admin(
            username="admin",
            password=hashed_password,
            email="admin@example.com",
            mobile="13800000000",
            last_login=datetime.now()
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("🎉 管理员用户创建成功！")
        print(f"ID: {admin_user.id}")
        print(f"用户名: admin")
        print(f"密码: 123456")
        print(f"邮箱: {admin_user.email}")
        print(f"手机号: {admin_user.mobile}")

        return admin_user

    except Exception as e:
        db.rollback()
        print(f"❌ 创建管理员用户失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()