<template>
  <div class="admin-dashboard-container">
    <header>
      <h2>管理员面板</h2>
      <p>欢迎管理员：<strong>{{ username }}</strong></p>
    </header>

    <section class="admin-actions">
      <button class="admin-btn" @click="goToUserQuery">用户信息管理</button>
      <button class="admin-btn" @click="goToRoomManagement">房间管理</button>
      <button class="admin-btn" @click="goToGameLogs">游戏记录查询</button>
    </section>

    <footer>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      username: "",
      errorMessage: ""
    };
  },
  mounted() {
    this.username = localStorage.getItem("username") || "未知";
  },
  methods: {
    goToUserQuery() {
      this.$router.push({ name: 'AdminUserQuery' });
    },
    goToRoomManagement() {
      this.$router.push({ name: 'AdminRoomManagement' });
    },
    goToGameLogs() {
      this.$router.push({ name: 'AdminGameLogs' });
    }
  }
};
</script>

<style scoped>
.admin-dashboard-container {
  max-width: 600px;
  margin: 30px auto;
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

header {
  margin-bottom: 20px;
}

header h2 {
  font-size: 2em;
  color: #2b6777;
}

header p strong {
  color: #134e4a;
}

.admin-actions {
  margin: 20px 0;
}

.admin-btn {
  margin: 10px;
  padding: 12px 24px;
  font-size: 1em;
  border-radius: 4px;
  background-color: #2b6777;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.admin-btn:hover {
  background-color: #134e4a;
}

.error {
  color: red;
  margin-top: 20px;
  font-size: 1.1em;
}
</style>
