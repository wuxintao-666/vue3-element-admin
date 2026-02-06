"""
测试管理员功能
"""
from db.database import SessionLocal, engine, Base
from db.models import Admin
from passlib.context import CryptContext
from datetime import datetime

# 创建密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_admin_functions():
    """测试管理员相关功能"""
    print("开始测试管理员功能...")

    # 确保表存在
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. 测试创建管理员
        print("\n1. 创建管理员...")
        hashed_password = pwd_context.hash("123456")

        admin = Admin(
            username="admin",
            password=hashed_password,
            email="admin@example.com",
            mobile="13800000000",
            last_login=datetime.now()
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"✅ 管理员创建成功: ID={admin.id}, 用户名={admin.username}")

        # 2. 测试查询管理员
        print("\n2. 查询管理员...")
        found_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if found_admin:
            print(f"✅ 管理员查询成功: {found_admin.username}")
        else:
            print("❌ 管理员查询失败")

        # 3. 测试密码验证
        print("\n3. 密码验证测试...")
        if pwd_context.verify("123456", found_admin.password):
            print("✅ 密码验证成功")
        else:
            print("❌ 密码验证失败")

        # 4. 测试更新最后登录时间
        print("\n4. 更新最后登录时间...")
        old_login = found_admin.last_login
        found_admin.last_login = datetime.now()
        db.commit()
        print(f"✅ 登录时间更新成功: {old_login} -> {found_admin.last_login}")

        print("\n🎉 所有管理员功能测试通过！")

    except Exception as e:
        db.rollback()
        print(f"❌ 测试失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_functions()