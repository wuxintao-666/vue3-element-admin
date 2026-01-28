from db.database import SessionLocal
from db.models import User
from datetime import datetime

db = SessionLocal()

user = User(
    username="user_1",
    password="123456",   # 真实项目要 hash，这里是模拟
    nickname="user_nickname_1",
    gender="0",
    mobile="13800138001",
    email="user@test.com",
    avatar="https://example.com/avatar1.png",
    status=1,
    recentsignin=datetime.now()
)

db.add(user)
db.commit()
db.refresh(user)

print("插入成功，ID =", user.id)
