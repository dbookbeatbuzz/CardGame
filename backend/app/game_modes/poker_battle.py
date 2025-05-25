import random
import json
from datetime import datetime
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, APIRouter
from sqlalchemy import select, update, insert
from app.database import database
from app.models import users, game_records,game_sessions
from app.room_manager import get_room_info
from pathlib import Path

router = APIRouter()


# 加载配置文件
def load_config():
    config_path = Path(__file__).parent / "config" / "poker_battle.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail="无法加载游戏模式配置: " + str(e))


CONFIG = load_config()

# 全局字典存储每个房间的游戏状态
# 状态中新增 playerActions 字段，用于记录每个玩家是否已摸牌和出牌
game_states = {}  # 格式: { room_id: { "deck": [...], "hands": { username: [cards] }, "table": { username: card or None }, "playerActions": { username: { drawn: bool, played: bool } }, "game_time": datetime, "finished": bool } }
# 全局字典存储 WebSocket 连接，用于广播消息
ws_connections = {}  # 格式: { room_id: [WebSocket, ...] }


def card_weight(card, config):
    """根据配置计算牌面权重：权重 = (牌值 * 10) + 花色权重"""
    card_value_order = config.get("card_value_order", {})
    suit_order = config.get("suit_order", {})
    rank_weight = card_value_order.get(card["rank"], 0)
    suit_weight = suit_order.get(card["suit"].lower(), 0)
    return rank_weight * 10 + suit_weight


async def initialize_game(room, config):
    """
    初始化游戏状态：
      - 生成52张牌的牌堆（牌以字典形式表示：{ "suit": "spades", "rank": "7" }）
      - 初始化每个玩家的手牌为空
      - 桌面出牌记录初始化为 None（表示未出牌）
      - 为每个玩家设置 playerActions 标志 { drawn: False, played: False }
      - 记录游戏开始时间和标记游戏未结束
    """
    room_id = room["room_id"]
    suits = ["clubs", "diamonds", "hearts", "spades"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    deck = [{"suit": suit, "rank": rank} for suit in suits for rank in ranks]
    random.shuffle(deck)
    players = list(room["users"].keys())
    state = {
        "deck": deck,
        "hands": {player: [] for player in players},
        "table": {player: None for player in players},
        "playerActions": {player: {"drawn": False, "played": False} for player in players},
        "game_time": datetime.utcnow(),
        "finished": False
    }
    game_states[room_id] = state
    return state


async def draw_card(room_id: str, username: str):
    """
    摸牌操作：
      - 如果该玩家已摸牌，则拒绝再次摸牌
      - 否则从牌堆中抽取一张牌，加入玩家手牌，并将 playerActions[username].drawn 置为 True
    """
    if room_id not in game_states:
        raise HTTPException(status_code=400, detail="游戏状态未初始化")
    state = game_states[room_id]
    if state["playerActions"].get(username, {}).get("drawn", False):
        raise HTTPException(status_code=400, detail="已摸牌，无法重复摸牌")
    if not state["deck"]:
        raise HTTPException(status_code=400, detail="牌堆为空")
    card = state["deck"].pop(0)
    state["hands"][username].append(card)
    state["playerActions"][username]["drawn"] = True
    return card, state


async def play_card(room_id: str, username: str, card: dict):
    """
    出牌操作：
      - 如果该玩家已出牌，则拒绝重复出牌
      - 检查玩家手牌中是否存在该牌，若存在则移除，并记录到桌面出牌，同时将 playerActions[username].played 置为 True
    """
    if room_id not in game_states:
        raise HTTPException(status_code=400, detail="游戏状态未初始化")
    state = game_states[room_id]
    if state["playerActions"].get(username, {}).get("played", False):
        raise HTTPException(status_code=400, detail="已出牌，无法重复出牌")
    if username not in state["hands"] or card not in state["hands"][username]:
        raise HTTPException(status_code=400, detail="该玩家没有这张牌")
    state["hands"][username].remove(card)
    state["table"][username] = card
    state["playerActions"][username]["played"] = True
    return state


async def finish_game(room, config):
    room_id = room["room_id"]
    if room_id not in game_states:
        raise HTTPException(status_code=400, detail="游戏状态未初始化")
    state = game_states[room_id]
    if state["finished"]:
        raise HTTPException(status_code=400, detail="该局游戏已结束")
    if any(card is None for card in state["table"].values()):
        raise HTTPException(status_code=400, detail="并非所有玩家都已出牌")

    played = list(state["table"].items())
    played.sort(key=lambda x: card_weight(x[1], config), reverse=True)

    results = {}
    if len(played) == 2:
        results[played[0][0]] = CONFIG["scoring"]["2_players"]["win"]
        results[played[1][0]] = CONFIG["scoring"]["2_players"]["lose"]
    elif len(played) == 3:
        results[played[0][0]] = CONFIG["scoring"]["3_players"]["win"]
        results[played[1][0]] = CONFIG["scoring"]["3_players"]["draw"]
        results[played[2][0]] = CONFIG["scoring"]["3_players"]["lose"]
    else:
        raise HTTPException(status_code=400, detail="不支持该玩家数量")

    # 创建对局 session 并获取 session_id
    players = list(state["table"].keys())
    game_time = state["game_time"]
    session_insert = insert(game_sessions).values(
        room_id=room_id,
        game_time=game_time,
        players=",".join(players)
    )
    session_id = await database.execute(session_insert)

    for player in players:
        query = select(users).where(users.c.username == player)
        user_data = await database.fetch_one(query)
        if not user_data:
            continue
        score_change = results.get(player, 0)
        new_points = user_data["points"] + score_change
        upd = update(users).where(users.c.id == user_data["id"]).values(points=new_points)
        await database.execute(upd)
        opponents = [p for p in players if p != player]
        opponents_str = ",".join(opponents)
        if score_change > 0:
            result_label = "win"
        elif score_change < 0:
            result_label = "loss"
        else:
            result_label = "draw"
        record = {
            "user_id": user_data["id"],
            "session_id": session_id,
            "game_time": game_time,
            "room_id": room_id,
            "opponents": opponents_str,
            "result": result_label,
            "score_change": score_change
        }
        ins = insert(game_records).values(**record)
        await database.execute(ins)

    state["finished"] = True
    return {"results": results, "table": state["table"]}


async def start_game_http(room, config):
    state = await initialize_game(room, config)
    return {"game_state": state, "mode": "poker_battle"}


async def start_game(room, config):
    return await start_game_http(room, config)


##########################
# WebSocket 路由集成
##########################

@router.websocket("/ws/game/{room_id}")
async def game_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    if room_id not in ws_connections:
        ws_connections[room_id] = []
    ws_connections[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except Exception:
                continue
            action = message.get("action")
            username = message.get("username")
            if action == "draw_card":
                try:
                    card, state = await draw_card(room_id, username)
                    response = {"action": "draw_card", "username": username, "card": card, "state": state}
                except HTTPException as e:
                    response = {"action": "error", "detail": e.detail}
                    # 错误只发给当前连接
                    await websocket.send_text(json.dumps(response, default=str))
                    continue
                for conn in ws_connections.get(room_id, []):
                    await conn.send_text(json.dumps(response, default=str))
            elif action == "play_card":
                card = message.get("card")
                try:
                    state = await play_card(room_id, username, card)
                    response = {"action": "play_card", "username": username, "card": card, "state": state}
                except HTTPException as e:
                    response = {"action": "error", "detail": e.detail}
                for conn in ws_connections.get(room_id, []):
                    await conn.send_text(json.dumps(response, default=str))
                # 检查是否所有玩家已出牌
                current_state = game_states.get(room_id)
                if current_state and all(v is not None for v in current_state["table"].values()):
                    try:
                        room = get_room_info(room_id)
                        result = await finish_game(room, CONFIG)
                        finish_msg = {"action": "finish_game", "result": result}
                        for conn in ws_connections.get(room_id, []):
                            await conn.send_text(json.dumps(finish_msg, default=str))
                    except HTTPException as e:
                        err_msg = {"action": "error", "detail": e.detail}
                        for conn in ws_connections.get(room_id, []):
                            await conn.send_text(json.dumps(err_msg, default=str))
            elif action == "restart_game":
                room = get_room_info(room_id)
                try:
                    new_state = await initialize_game(room, CONFIG)
                    restart_msg = {"action": "game_restart", "game_state": new_state}
                    for conn in ws_connections.get(room_id, []):
                        await conn.send_text(json.dumps(restart_msg, default=str))
                except HTTPException as e:
                    restart_msg = {"action": "error", "detail": e.detail}
                    await websocket.send_text(json.dumps(restart_msg, default=str))
            elif action == "finish_game":
                room = get_room_info(room_id)
                try:
                    result = await finish_game(room, CONFIG)
                    response = {"action": "finish_game", "result": result}
                    for conn in ws_connections.get(room_id, []):
                        await conn.send_text(json.dumps(response, default=str))
                except HTTPException as e:
                    response = {"action": "error", "detail": e.detail}
                    await websocket.send_text(json.dumps(response, default=str))
            else:
                response = {"action": "error", "detail": "Unknown action"}
                await websocket.send_text(json.dumps(response, default=str))
    except WebSocketDisconnect:
        ws_connections[room_id].remove(websocket)
