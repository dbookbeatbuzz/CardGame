<template>
  <div class="game-records">
    <header>
      <h2>用户信息</h2>
    </header>
    <section class="user-info">
      <p>用户名：<strong>{{ username }}</strong></p>
      <p>用户ID：<strong>{{ userId }}</strong></p>
      <p>当前积分：<strong>{{ points }}</strong></p>
    </section>
    <section class="records-list" v-if="records.length">
      <h3>历史对局记录</h3>
      <ul>
        <li v-for="record in records" :key="record.id">
          <span class="record-room">房间号：{{ record.room_id }}</span> |
          <span class="record-time">时间：{{ record.game_time }}</span> |
          <span class="record-opponents">对局对手：{{ record.opponents }}</span> |
          <span class="record-result">结果：{{ record.result }}</span> |
          <span class="record-score">得分：{{ record.score_change }}</span>
        </li>
      </ul>
    </section>
    <section class="no-records" v-else>
      <p>暂无游戏记录</p>
    </section>
    <footer>
      <button class="back-btn" @click="goBack">返回大厅</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </footer>
  </div>
</template>

<script>
import axios from '@/utils/axios';
export default {
  name: "GameRecords",
  data() {
    return {
      username: "",
      userId: "",
      points: 0,
      records: [],
      errorMessage: ""
    };
  },
  methods: {
    async fetchRecords() {
      this.username = localStorage.getItem("username") || "";
      if (!this.username) {
        this.errorMessage = "请先登录";
        return;
      }
      try {
        const response = await axios.get('/user/records', {
          params: { username: this.username, t: Date.now() }
        });
        this.userId = response.data.id;
        this.points = response.data.points;
        this.records = response.data.game_records;
      } catch (error) {
        console.error("获取游戏记录失败", error);
        this.errorMessage = error.response?.data?.detail || "获取游戏记录失败";
      }
    },
    goBack() {
      this.$router.push({ name: "Dashboard" });
    }
  },
  mounted() {
    this.fetchRecords();
  }
};
</script>

<style scoped>
.game-records {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: left;
}
header {
  text-align: center;
  margin-bottom: 20px;
}
header h2 {
  font-size: 2em;
  color: #333;
  margin-bottom: 10px;
}
.user-info {
  font-size: 1.2em;
  color: #2b6777;
  margin-bottom: 20px;
  text-align: center;
}
.user-info p {
  margin: 5px 0;
}
.records-list h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
  text-align: center;
}
.records-list ul {
  list-style: none;
  padding: 0;
}
.records-list li {
  font-size: 1.1em;
  margin: 10px 0;
  padding: 5px;
  border-bottom: 1px solid #ccc;
}
.records-list li:last-child {
  border-bottom: none;
}
.record-room,
.record-time,
.record-opponents,
.record-result,
.record-score {
  margin-right: 5px;
}
.no-records {
  text-align: center;
  font-size: 1.1em;
  color: #555;
  margin-bottom: 20px;
}
footer {
  text-align: center;
  margin-top: 20px;
}
.back-btn {
  padding: 10px 20px;
  background-color: #2b6777;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.2s;
}
.back-btn:hover {
  background-color: #134e4a;
}
.error {
  color: red;
  margin-top: 20px;
  font-size: 1.1em;
}
</style>
