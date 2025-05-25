<template>
  <div class="room-container">
    <header>
      <h2>房间：<strong>{{ roomId }}</strong></h2>
      <h3>房间内玩家</h3>
    </header>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <section class="players-list" v-if="players.length">
      <ul>
        <li v-for="player in players" :key="player.username">
          <span class="player-name">{{ player.username }}</span> - 积分: {{ player.points }} -
          <span class="player-status">{{ player.ready ? "已准备" : "未准备" }}</span>
        </li>
      </ul>
    </section>

    <section class="buttons">
      <button class="action-btn" @click="markReady" :disabled="currentPlayerReady">
        {{ currentPlayerReady ? "已就绪" : "开始游戏（就绪）" }}
      </button>
      <button class="action-btn" @click="refreshRoom">刷新房间信息</button>
      <button class="action-btn" @click="leaveRoom">返回大厅</button>
    </section>

    <footer>
      <p>请等待所有玩家准备完毕，系统将自动进入游戏界面</p>
    </footer>
  </div>
</template>

<script>
import axios from '@/utils/axios';
export default {
  name: "RoomPage",
  props: ["roomId"],
  data() {
    return {
      players: [],         // 房间内所有玩家信息
      errorMessage: "",
      currentPlayerReady: false,
      username: "",
      ws: null
    };
  },
  methods: {
    connectWebSocket() {
      // 建立 WebSocket 连接到后端对应房间接口
      this.ws = new WebSocket(`ws://localhost:9000/ws/room/${this.roomId}`);
      this.ws.onopen = () => {
        console.log("WebSocket 已连接");
      };
      this.ws.onmessage = (event) => {
        let data;
        try {
          data = JSON.parse(event.data);
        } catch (e) {
          console.error("解析消息失败", e);
          return;
        }
        console.log("收到消息：", data);
        if (data.action === "update_room") {
          // 假设后端返回的 room 对象中 users 为数组形式
          if (data.room && data.room.users) {
            this.players = data.room.users;
          }
        } else if (data.action === "game_start") {
          // 所有玩家就绪后跳转到游戏界面
          this.$router.push({ name: "GameInterface", params: { roomId: this.roomId } });
        } else if (data.action === "error") {
          this.errorMessage = data.detail || "未知错误";
        }
      };
      this.ws.onerror = (err) => {
        console.error("WebSocket 错误", err);
        this.errorMessage = "WebSocket 连接失败";
      };
      this.ws.onclose = () => {
        console.log("WebSocket 已关闭");
      };
    },
    markReady() {
      if (!this.username) {
        this.errorMessage = "请先登录";
        return;
      }
      const msg = { action: "ready", username: this.username };
      this.ws.send(JSON.stringify(msg));
      this.currentPlayerReady = true;
    },
    async refreshRoom() {
      try {
        const response = await axios.get('/room/info', { params: { room_id: this.roomId } });
        console.log("刷新房间信息返回:", response.data);
        this.players = response.data.users;
      } catch (error) {
        console.error("刷新房间信息失败", error);
        this.errorMessage = "刷新房间信息失败";
      }
    },
    async leaveRoom() {
      try {
        await axios.post('/room/leave', { room_id: this.roomId, username: this.username });
        if (this.ws) {
          this.ws.close();
        }
        this.$router.push({ name: "Dashboard" });
      } catch (error) {
        console.error("退出房间失败", error);
        this.errorMessage = error.response?.data?.detail || "退出房间失败";
      }
    }
  },
  mounted() {
    this.username = localStorage.getItem("username") || "";
    this.connectWebSocket();
    this.refreshRoom();
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  }
};
</script>

<style scoped>
.room-container {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

header {
  margin-bottom: 20px;
}

header h2 {
  font-size: 2em;
  color: #333;
  margin-bottom: 5px;
}

header h3 {
  font-size: 1.3em;
  color: #555;
}

.players-list {
  margin: 20px 0;
}

.players-list ul {
  list-style: none;
  padding: 0;
}

.players-list li {
  font-size: 1.1em;
  margin: 10px 0;
}

.player-name {
  font-weight: bold;
  color: #2b6777;
}

.player-status {
  color: #888;
}

.buttons {
  margin-top: 20px;
}

.action-btn {
  margin: 10px;
  padding: 10px 20px;
  background-color: #2b6777;
  border: none;
  color: #fff;
  font-size: 1em;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #134e4a;
}

footer {
  margin-top: 20px;
}

.error {
  color: red;
  margin-top: 20px;
  white-space: pre-wrap;
}
</style>
