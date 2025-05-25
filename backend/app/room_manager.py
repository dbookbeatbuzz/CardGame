# app/room_manager.py
import random
import string

# 改为字典形式存储房间信息，其中 users 为 { username: ready } 的形式
rooms = {}

def generate_random_room_id(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_room(username: str):
    room_id = generate_random_room_id()
    while room_id in rooms:
        room_id = generate_random_room_id()
    # 初始化房间，将创建者加入，初始状态为未就绪
    rooms[room_id] = {"room_id": room_id, "users": {}}
    join_room(room_id, username)
    return True, room_id

def join_room(room_id: str, username: str):
    if room_id not in rooms:
        return False, "房间不存在"
    # 如果玩家还未加入，则加入并标记未就绪
    if username not in rooms[room_id]["users"]:
        rooms[room_id]["users"][username] = False
    return True, "加入房间成功"

def set_ready(room_id: str, username: str):
    if room_id not in rooms:
        return False, "房间不存在"
    if username not in rooms[room_id]["users"]:
        return False, "用户未在房间内"
    rooms[room_id]["users"][username] = True
    return True, "已准备就绪"

def all_ready(room_id: str):
    if room_id not in rooms:
        return False
    # 检查所有用户是否都为 True
    return all(rooms[room_id]["users"].values())

def get_room_info(room_id: str):
    return rooms.get(room_id)

def leave_room(room_id: str, username: str):
    """
    从指定房间中移除某个用户。
    """
    if room_id not in rooms:
        return False, "房间不存在"
    if username in rooms[room_id]["users"]:
        del rooms[room_id]["users"][username]
    return True, "退出房间成功"
