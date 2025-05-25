<template>
  <div class="admin-page">
    <h2>房间管理</h2>
    <ul class="room-list">
      <li v-for="room in rooms" :key="room.room_id">
        <strong>房间号：</strong>{{ room.room_id }}
        <span> | 玩家数：{{ room.user_count }}</span>
        <button @click="viewRecords(room.room_id)">查看记录</button>
        <button @click="deleteRoom(room.room_id)">删除</button>
      </li>
    </ul>
    <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    <button @click="back" class="back-btn">返回</button>
  </div>
</template>

<script>
import axios from '@/utils/axios';
export default {
  name: "RoomManagement",
  data() {
    return {
      rooms: [],
      errorMessage: ''
    };
  },
  async mounted() {
    try {
      const res = await axios.get("/admin/rooms");
      this.rooms = res.data.rooms;
    } catch (err) {
      this.errorMessage = err.response?.data?.detail || "加载房间信息失败";
    }
  },
  methods: {
    async deleteRoom(roomId) {
      try {
        await axios.post('/admin/room/delete', { room_id: roomId });
        this.rooms = this.rooms.filter(r => r.room_id !== roomId);
      } catch (err) {
        this.errorMessage = err.response?.data?.detail || "无法删除房间";
      }
    },
    viewRecords(roomId) {
      this.$router.push({ name: "AdminGameLogs", query: { roomId } });
    },
    back() {
      this.$router.push({ name: "AdminDashboard" });
    }
  }
};
</script>

<style scoped>
@import "@/assets/admin-style.css";
</style>
