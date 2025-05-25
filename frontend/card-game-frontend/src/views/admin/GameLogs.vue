<template>
  <div class="admin-page">
    <h2>游戏记录查询</h2>
    <div v-if="roomId">查看房间 <strong>{{ roomId }}</strong> 的记录</div>
    <ul>
      <li v-for="record in records" :key="record.id">
        用户：{{ record.username }} | 时间：{{ record.game_time }} |
        结果：{{ record.result }} | 得分：{{ record.score_change }}
      </li>
    </ul>
    <button @click="back" class="back-btn">返回</button>
  </div>
</template>

<script>
import axios from '@/utils/axios';
export default {
  name: "GameLogs",
  data() {
    return {
      records: [],
      roomId: this.$route.query.roomId || null
    };
  },
  async mounted() {
    try {
      const url = this.roomId
        ? `/admin/records?room_id=${this.roomId}`
        : '/admin/records';
      const res = await axios.get(url);
      this.records = res.data.records;
    } catch (err) {
      console.error("加载记录失败", err);
    }
  },
  methods: {
    back() {
      this.$router.push({ name: "AdminDashboard" });
    }
  }
};
</script>

<style scoped>
@import "@/assets/admin-style.css";
</style>
.admin-page {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #2b6777;
  margin-bottom: 20px;
}

.form input {
  padding: 8px;
  margin-right: 10px;
}

button {
  margin: 10px;
  padding: 10px 20px;
  background-color: #2b6777;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #134e4a;
}

.error {
  color: red;
  margin-top: 15px;
}

ul {
  list-style: none;
  padding: 0;
}

.room-list li {
  margin: 10px 0;
}
