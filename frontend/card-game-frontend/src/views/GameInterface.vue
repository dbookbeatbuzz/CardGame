<template>
  <div class="game-interface">
    <header>
      <h1>游戏正式开始！</h1>
      <p>房间ID：<strong>{{ roomId }}</strong></p>
    </header>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- 游戏未结束时显示实时游戏界面 -->
    <div v-if="!gameState.finished" class="game-content">
      <section class="deck-info">
        <p>剩余牌数：{{ gameState.deck.length }}</p>
      </section>

      <section class="table">
        <h3>桌面出牌：</h3>
        <ul>
          <li v-for="(card, player) in gameState.table" :key="player">
            <span class="player-name">{{ player }}</span>:
            <span v-if="card">
              <!-- 如果游戏未结束，则显示牌背；游戏结束则显示实际牌面 -->
              <img :src="gameState.finished ? getCardImage(card) : getCardBackImage()" alt="Card" class="card-image" />
            </span>
            <span v-else class="not-played">未出牌</span>
          </li>
        </ul>
      </section>

      <section class="hand">
        <h3>你的手牌：</h3>
        <div class="hand-cards">
          <img
            v-for="(card, index) in gameState.hands[username]"
            :key="index"
            :src="getCardImage(card)"
            alt="Card"
            class="card-image"
            :class="{ selected: selectedCard === card }"
            @click="selectCard(card)"
          />
        </div>
      </section>

      <section class="actions">
        <button class="action-btn" @click="drawCard" :disabled="!canDraw">摸牌</button>
        <button class="action-btn" v-if="selectedCard !== null" @click="confirmPlayCard">
          出牌 ({{ selectedCard.rank }}{{ selectedCard.suit }})
        </button>
        <button class="action-btn" @click="finishGame">结束游戏</button>
      </section>
    </div>

    <!-- 游戏结束时显示最终结果 -->
    <div v-else class="final-result">
      <h3>游戏结束！</h3>
      <section class="final-results">
        <ul>
          <li v-for="(result, player) in finalResults.results" :key="player">
            <span class="player-name">{{ player }}</span>:
            <span class="result-text">
              {{ result > 0 ? '胜' : (result < 0 ? '负' : '平') }}
            </span>
          </li>
        </ul>
      </section>
      <section class="final-table">
        <h3>最终出牌：</h3>
        <ul>
          <li v-for="(card, player) in finalResults.table" :key="player">
            <span class="player-name">{{ player }}</span>:
            <span v-if="card">
              <img :src="getCardImage(card)" alt="Card" class="card-image" />
            </span>
            <span v-else class="not-played">未出牌</span>
          </li>
        </ul>
      </section>
      <button class="action-btn" @click="restartGame">再玩一局</button>
    </div>

    <footer>
      <button class="back-btn" @click="backToLobby">返回大厅</button>
    </footer>
  </div>
</template>

<script>
import axios from '@/utils/axios';

// 预加载所有卡牌图片
const cardImages = {};
const requireCard = require.context('@/assets/cards', false, /\.png$/);
requireCard.keys().forEach((fileName) => {
  const key = fileName.replace('./', '');
  cardImages[key] = requireCard(fileName);
});

export default {
  name: "GameInterface",
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      username: "",
      gameState: {
        deck: [],
        hands: {},
        table: {},
        finished: false
      },
      finalResults: {},
      errorMessage: "",
      ws: null,
      selectedCard: null,
      hasDrawn: false
    };
  },
  computed: {
    // 允许摸牌的条件：当前玩家手牌为空且未摸牌
    canDraw() {
      return !this.hasDrawn && (!this.gameState.hands[this.username] || this.gameState.hands[this.username].length === 0);
    }
  },
  methods: {
    getCardImage(card) {
      const key = `${card.suit.toLowerCase()}_${card.rank}.png`;
      console.log("Loading card image:", key);
      if (cardImages[key]) {
        return cardImages[key];
      } else {
        console.error("图片未找到：", key);
        return "";
      }
    },
    getCardBackImage() {
      // 牌背图片命名为 "card_back.png"
      const key = "card_back.png";
      if (cardImages[key]) {
        return cardImages[key];
      } else {
        console.error("牌背图片未找到：", key);
        return "";
      }
    },
    async startGame() {
      try {
        const response = await axios.post('/game/start', {
          room_id: this.roomId,
          mode: "poker_battle"
        });
        console.log("初始化游戏状态返回：", response.data);
        this.gameState = response.data.game_state;
        this.hasDrawn = false;
      } catch (error) {
        console.error("游戏初始化失败", error);
        this.errorMessage = error.response?.data?.detail || "游戏初始化失败";
      }
    },
    connectWebSocket() {
      this.ws = new WebSocket(`ws://localhost:9000/ws/game/${this.roomId}`);
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
        if (data.action === "game_init") {
          this.gameState = data.game_state;
          this.hasDrawn = false;
        } else if (data.action === "draw_card") {
          this.gameState = data.state;
        } else if (data.action === "play_card") {
          this.gameState = data.state;
          this.selectedCard = null;
        } else if (data.action === "update_game") {
          this.gameState = data.game_state;
        } else if (data.action === "finish_game") {
          this.finalResults = data.result;
          this.gameState.finished = true;
          alert("游戏结束！");
        } else if (data.action === "game_restart") {
          this.gameState = data.game_state;
          this.gameState.finished = false;
          this.finalResults = {};
          this.hasDrawn = false;
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
    drawCard() {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this.errorMessage = "WebSocket 未连接";
        return;
      }
      if (!this.canDraw) {
        this.errorMessage = "您已经摸过牌，无法重复摸牌";
        return;
      }
      const msg = { action: "draw_card", username: this.username };
      this.ws.send(JSON.stringify(msg));
      this.hasDrawn = true;
    },
    selectCard(card) {
      this.selectedCard = card;
    },
    confirmPlayCard() {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this.errorMessage = "WebSocket 未连接";
        return;
      }
      if (this.selectedCard === null) {
        this.errorMessage = "请先选中一张牌";
        return;
      }
      const msg = { action: "play_card", username: this.username, card: this.selectedCard };
      this.ws.send(JSON.stringify(msg));
    },
    finishGame() {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this.errorMessage = "WebSocket 未连接";
        return;
      }
      const msg = { action: "finish_game", username: this.username };
      this.ws.send(JSON.stringify(msg));
    },
    restartGame() {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this.errorMessage = "WebSocket 未连接";
        return;
      }
      const msg = { action: "restart_game", username: this.username };
      this.ws.send(JSON.stringify(msg));
    },
    backToLobby() {
      if (this.ws) {
        this.ws.close();
      }
      this.$router.push({ name: "Dashboard" });
    }
  },
  mounted() {
    this.username = localStorage.getItem("username") || "";
    this.startGame();
    this.connectWebSocket();
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  }
};
</script>

<style scoped>
.game-interface {
  max-width: 900px;
  margin: 20px auto;
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

header {
  margin-bottom: 20px;
}

header h1 {
  font-size: 2em;
  color: #333;
  margin-bottom: 5px;
}

header p {
  font-size: 1.2em;
  color: #555;
}

.deck-info {
  margin: 10px 0;
  font-weight: bold;
  font-size: 1.1em;
}

.table, .final-table, .hand, .actions {
  margin: 20px 0;
}

.table ul, .final-results ul, .final-table ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.table li, .final-results li, .final-table li {
  font-size: 1.1em;
  margin: 5px 0;
}

.player-name {
  font-weight: bold;
  color: #2b6777;
}

.not-played {
  color: #888;
}

.hand-cards {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.card-image {
  width: 80px;
  height: auto;
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 4px;
  transition: transform 0.2s, border 0.2s;
}

.card-image:hover {
  transform: scale(1.05);
}

.card-image.selected {
  border-color: red;
}

.actions button, .back-btn, .action-btn {
  margin: 10px;
  padding: 10px 20px;
  background-color: #2b6777;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.actions button:hover, .back-btn:hover {
  background-color: #134e4a;
}

.error {
  color: red;
  margin-top: 20px;
  font-size: 1.1em;
  white-space: pre-wrap;
}

.final-result {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
}

.final-result h3 {
  margin-bottom: 10px;
  font-size: 1.5em;
  color: #333;
}

.final-results li {
  font-size: 1.1em;
  margin: 5px 0;
}
</style>
