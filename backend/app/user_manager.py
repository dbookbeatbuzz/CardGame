# app/user_manager.py
from sqlalchemy import select, insert
from app.database import database
from app.models import users

async def register_user(username: str, password: str):
    # 检查用户是否已存在
    query = select(users).where(users.c.username == username)
    existing_user = await database.fetch_one(query)
    if existing_user:
        return False, "用户已存在"
    # 插入新用户
    query = insert(users).values(username=username, password=password)
    await database.execute(query)
    return True, "注册成功"

async def login_user(username: str, password: str):
    query = select(users).where(users.c.username == username)
    user = await database.fetch_one(query)
    if not user:
        return False, "用户不存在"
    if user["password"] != password:
        return False, "密码错误"
    return True, "登录成功"
