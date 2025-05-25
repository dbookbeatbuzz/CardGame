<template>
  <div class="admin-page">
    <h2>用户信息查询</h2>
    <div class="form">
      <input v-model="queryId" type="text" placeholder="请输入用户ID" />
      <button @click="searchUser">查询</button>
    </div>
    <div v-if="userInfo" class="result">
      <p>用户名：{{ userInfo.username }}</p>
      <p>当前积分：{{ userInfo.points }}</p>
    </div>
    <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    <button @click="back" class="back-btn">返回</button>
  </div>
</template>

<script>
import axios from '@/utils/axios';
export default {
  name: "UserQuery",
  data() {
    return {
      queryId: '',
      userInfo: null,
      errorMessage: ''
    };
  },
  methods: {
    async searchUser() {
      if (!this.queryId) {
        this.errorMessage = "请输入用户ID";
        return;
      }
      try {
        const res = await axios.get(`/admin/user?id=${this.queryId}`);
        this.userInfo = res.data;
        this.errorMessage = "";
      } catch (err) {
        this.userInfo = null;
        this.errorMessage = err.response?.data?.detail || "查询失败";
      }
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
