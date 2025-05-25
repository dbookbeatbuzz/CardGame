# app/room_ws.py
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.room_manager import set_ready, all_ready, get_room_info

router = APIRouter()

# 保存各个房间的 WebSocket 连接
room_connections = {}

@router.websocket("/ws/room/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    if room_id not in room_connections:
        room_connections[room_id] = []
    room_connections[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("Received WebSocket data:", data)
            try:
                message = json.loads(data)
            except Exception:
                continue
            action = message.get("action")
            username = message.get("username")
            if action == "ready":
                success, msg = set_ready(room_id, username)
                if not success:
                    await websocket.send_text(json.dumps({"action": "error", "detail": msg}))
                    continue
                # 广播最新房间状态
                room = get_room_info(room_id)
                broadcast_data = json.dumps({"action": "update_room", "room": room})
                for conn in room_connections.get(room_id, []):
                    await conn.send_text(broadcast_data)
                if all_ready(room_id):
                    start_data = json.dumps({"action": "game_start", "room_id": room_id})
                    for conn in room_connections.get(room_id, []):
                        await conn.send_text(start_data)
            else:
                # 处理其他类型消息（例如聊天等）
                await websocket.send_text(json.dumps({"action": "echo", "data": message}))
    except WebSocketDisconnect:
        print("WebSocket disconnected for room:", room_id)
        room_connections[room_id].remove(websocket)
