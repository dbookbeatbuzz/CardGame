import sqlalchemy
from app.database import metadata

# 用户表：使用 id 作为主键，username 唯一，points 默认 0
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True, index=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("points", sqlalchemy.Integer, nullable=False, server_default="0")
)

# 对局记录表：每条记录通过 user_id 关联到用户，对局记录中包含对局时间、房间号、对局对手、胜负结果、得分变化等
game_records = sqlalchemy.Table(
    "game_records",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False, index=True),
    sqlalchemy.Column("session_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("game_sessions.id"), nullable=False, index=True),
    sqlalchemy.Column("game_time", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("room_id", sqlalchemy.String, nullable=False, index=True),
    sqlalchemy.Column("opponents", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("result", sqlalchemy.String, nullable=False),  # "win", "loss", "draw"
    sqlalchemy.Column("score_change", sqlalchemy.Integer, nullable=False)
)

# 游戏对局表：记录每场完整的对局信息
game_sessions = sqlalchemy.Table(
    "game_sessions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True),
    sqlalchemy.Column("room_id", sqlalchemy.String, unique=True, nullable=False, index=True),
    sqlalchemy.Column("game_time", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("players", sqlalchemy.String, nullable=False),  # 以逗号分隔的玩家用户名列表
)