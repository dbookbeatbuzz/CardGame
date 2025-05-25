# app/game_manager.py
import importlib
import json
from pathlib import Path
from fastapi import HTTPException

# 定义存放游戏模式配置的目录
GAME_MODES_DIR = Path(__file__).parent / "game_modes"
CONFIG_DIR = GAME_MODES_DIR / "config"

class GameManager:
    def __init__(self):
        self.modes_config = self._load_modes_config()

    def _load_modes_config(self):
        """
        加载游戏模式配置：
        1. 如果存在统一配置文件 'game_modes.json' 在 CONFIG_DIR 下，则加载该文件，并返回一个字典。
        2. 否则，遍历 CONFIG_DIR 中的每个 JSON 文件，以文件名（不含扩展名）为键，文件内容为值。
        """
        unified_config_path = CONFIG_DIR / "game_modes.json"
        if unified_config_path.exists():
            try:
                with open(unified_config_path, "r", encoding="utf-8") as f:
                    modes_config = json.load(f)
                    if not isinstance(modes_config, dict):
                        raise ValueError("统一配置文件格式不正确，应为 JSON 对象")
                    return modes_config
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"加载统一游戏模式配置失败: {str(e)}")
        else:
            # 遍历 CONFIG_DIR 中的单个 JSON 文件
            modes_config = {}
            for config_file in CONFIG_DIR.glob("*.json"):
                mode_name = config_file.stem
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        modes_config[mode_name] = json.load(f)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"加载游戏模式配置 {mode_name} 失败: {str(e)}")
            return modes_config

    def get_mode_config(self, mode_name: str):
        """读取指定游戏模式的配置"""
        if mode_name not in self.modes_config:
            raise HTTPException(status_code=400, detail=f"游戏模式 {mode_name} 不存在")
        return self.modes_config[mode_name]

    async def start_game(self, mode_name: str, room):
        """根据模式名启动游戏（异步版本）"""
        config = self.get_mode_config(mode_name)
        try:
            # 动态加载游戏模式处理代码模块，例如 app/game_modes/poker_battle.py
            module = importlib.import_module(f"app.game_modes.{mode_name}")
            # 调用模块中的异步函数 start_game(room, config) 并等待结果
            return await module.start_game(room, config)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"加载游戏模式 {mode_name} 失败: {str(e)}")

# 创建全局 GameManager 实例
game_manager = GameManager()
