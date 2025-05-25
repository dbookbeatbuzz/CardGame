# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.room_manager import create_room, join_room, get_room_info
from app.database import database, engine, metadata
from app.models import users, game_records
from sqlalchemy import select, update
from pathlib import Path
from app.user_manager import register_user, login_user
from app.game_manager import game_manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {}

@app.on_event("startup")
async def startup():
    await database.connect()
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# 用户注册接口
@app.post("/register")
async def register(payload: dict):
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="请输入账号和密码")
    success, msg = await register_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# 用户登录接口
@app.post("/login")
async def login(payload: dict):
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="请输入账号和密码")
    success, msg = await login_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# 房间创建接口
@app.post("/room/create")
async def room_create(payload: dict):
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="缺少用户名")
    success, room_id = create_room(username)
    if not success:
        raise HTTPException(status_code=400, detail="创建房间失败")
    return {"message": "房间创建成功", "room_id": room_id}

# 房间加入接口
@app.post("/room/join")
async def room_join(payload: dict):
    room_id = payload.get("room_id")
    username = payload.get("username")
    if not room_id or not username:
        raise HTTPException(status_code=400, detail="缺少房间ID或用户名")
    success, msg = join_room(room_id, username)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "room_id": room_id}

# 获取房间信息接口（返回所有玩家信息，以数组形式）
@app.get("/room/info")
async def room_info(room_id: str):
    room = get_room_info(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    users_info = []
    for uname, ready in room["users"].items():
        query = select(users).where(users.c.username == uname)
        user_data = await database.fetch_one(query)
        if user_data:
            users_info.append({"username": uname, "points": user_data["points"], "ready": ready})
        else:
            users_info.append({"username": uname, "points": 0, "ready": ready})
    return {"room_id": room["room_id"], "users": users_info}

# 离开房间接口
@app.post("/room/leave")
async def room_leave(payload: dict):
    room_id = payload.get("room_id")
    username = payload.get("username")
    if not room_id or not username:
        raise HTTPException(status_code=400, detail="缺少房间ID或用户名")
    from app.room_manager import leave_room  # 动态导入leave_room
    success, msg = leave_room(room_id, username)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "room_id": room_id}

# 游戏开始接口（调用封装的 game_manager）
@app.post("/game/start")
async def start_game(payload: dict):
    room_id = payload.get("room_id")
    mode = payload.get("mode", "poker_battle")  # 默认使用 poker_battle 模式
    if not room_id:
        raise HTTPException(status_code=400, detail="缺少房间ID")
    room = get_room_info(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    return await game_manager.start_game(mode, room)

# 获取游戏记录接口（返回用户id、用户名、当前积分及所有对局记录）
@app.get("/user/records")
async def get_user_records(username: str):
    query_user = select(users).where(users.c.username == username)
    user = await database.fetch_one(query_user)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    query_records = game_records.select().where(game_records.c.user_id == user["id"]).order_by(game_records.c.game_time.desc())
    records = await database.fetch_all(query_records)
    return {
        "id": user["id"],
        "username": user["username"],
        "points": user["points"],
        "game_records": [dict(record) for record in records]
    }

# 挂载 WebSocket 路由处理房间内就绪状态和游戏开始通知
from app.room_ws import router as room_ws_router
app.include_router(room_ws_router)

#挂载游戏界面的websocket
from app.game_modes.poker_battle import router as poker_battle_router
app.include_router(poker_battle_router)
