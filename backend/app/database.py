# app/database.py
from databases import Database
from sqlalchemy import create_engine, MetaData

# 使用 SQLite 数据库（测试环境），数据库文件 test.db 会在 backend 目录下创建
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = MetaData()

# 创建同步的 engine 用于创建数据表
engine = create_engine(
    DATABASE_URL.replace("+aiosqlite", ""),  # 替换为同步驱动
    connect_args={"check_same_thread": False}
)
