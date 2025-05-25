// src/utils/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:9000', // 后端 API 地址
});

export default instance;
