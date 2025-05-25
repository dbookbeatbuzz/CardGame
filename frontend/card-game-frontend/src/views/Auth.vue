<template>
  <div class="auth-container">
    <h2>{{ isRegister ? "注册新用户" : "用户登录" }}</h2>
    <form @submit.prevent="handleSubmit" class="auth-form">
      <div class="form-group">
        <label for="username">账号：</label>
        <input type="text" id="username" v-model="username" placeholder="请输入账号" required />
      </div>
      <div class="form-group">
        <label for="password">密码：</label>
        <input type="password" id="password" v-model="password" placeholder="请输入密码" required />
      </div>
      <button type="submit" class="action-btn">
        {{ isRegister ? "注册" : "登录" }}
      </button>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </form>
    <p @click="toggleMode" class="toggle-link">
      {{ isRegister ? "已有账号？点击登录" : "没有账号？点击注册" }}
    </p>
  </div>
</template>

<script>
import axios from '@/utils/axios';

export default {
  name: 'AuthPage',
  data() {
    return {
      isRegister: false,  // false 显示登录，true 显示注册
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister;
      this.errorMessage = '';
    },
    async handleSubmit() {
      if (!this.username || !this.password) {
        this.errorMessage = '请输入账号和密码';
        return;
      }
      try {
        if (this.isRegister) {
          // 调用注册接口
          await axios.post('/register', {
            username: this.username,
            password: this.password
          });
          this.errorMessage = '注册成功，请登录';
          this.isRegister = false;
        } else {
          // 调用登录接口
          await axios.post('/login', {
            username: this.username,
            password: this.password
          });
          // 登录成功后保存用户名并跳转到 dashboard 页面
          localStorage.setItem("username", this.username);
          this.$router.push('/dashboard');
        }
      } catch (error) {
        this.errorMessage =
          error.response && error.response.data && error.response.data.detail
            ? error.response.data.detail
            : (this.isRegister ? '注册失败' : '登录失败');
      }
    }
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.auth-container h2 {
  font-size: 1.8em;
  color: #333;
  margin-bottom: 20px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.form-group {
  width: 100%;
  margin-bottom: 15px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #2b6777;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.action-btn {
  margin-top: 10px;
  width: 100%;
  padding: 10px;
  background-color: #2b6777;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #134e4a;
}

.error {
  color: red;
  margin-top: 10px;
  font-size: 1.1em;
}

.toggle-link {
  margin-top: 15px;
  color: #2b6777;
  cursor: pointer;
  text-decoration: underline;
  font-weight: bold;
}
</style>
