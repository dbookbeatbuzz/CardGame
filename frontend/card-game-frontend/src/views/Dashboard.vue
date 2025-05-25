<template>
  <div class="dashboard-container">
    <header>
      <h2>欢迎, <strong>{{ username }}</strong></h2>
    </header>

    <section class="buttons">
      <button class="action-btn" @click="goToRecords">积分和游戏记录</button>
      <button class="action-btn" @click="createRoom">创建房间</button>
      <button class="action-btn" @click="joinRoom">加入房间</button>
    </section>

    <footer>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </footer>
  </div>
</template>

<script>
import axios from '@/utils/axios';

export default {
  name: 'DashboardPage',
  data() {
    return {
      username: '',
      errorMessage: ''
    };
  },
  methods: {
    // 只从 localStorage 获取用户名，不调用 /user/info 接口
    loadUserInfo() {
      this.username = localStorage.getItem("username") || "";
      if (!this.username) {
        this.errorMessage = "请先登录";
      }
    },
    goToRecords() {
      this.$router.push({ name: 'GameRecords' });
    },
    async createRoom() {
      if (!this.username) {
        this.errorMessage = "请先登录";
        return;
      }
      try {
        const response = await axios.post('/room/create', {
          username: this.username
        });
        this.$router.push({ name: 'Room', params: { roomId: response.data.room_id } });
      } catch (error) {
        console.error(error);
        this.errorMessage = error.response?.data?.detail || "创建房间失败";
      }
    },
    async joinRoom() {
      if (!this.username) {
        this.errorMessage = "请先登录";
        return;
      }
      const roomId = prompt("请输入房间ID");
      if (!roomId) {
        this.errorMessage = "房间ID不能为空";
        return;
      }
      try {
        const response = await axios.post('/room/join', {
          room_id: roomId,
          username: this.username
        });
        this.$router.push({ name: 'Room', params: { roomId: response.data.room_id } });
      } catch (error) {
        console.error(error);
        this.errorMessage = error.response?.data?.detail || "加入房间失败";
      }
    }
  },
  mounted() {
    this.loadUserInfo();
  }
};
</script>

<style scoped>
.dashboard-container {
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

header h2 strong {
  color: #2b6777;
}

.buttons {
  margin: 20px 0;
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

.error {
  color: red;
  margin-top: 20px;
  font-size: 1.1em;
}
</style>
