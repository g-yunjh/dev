<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from './stores/chat'

const store = useChatStore()

// --- 상태 변수들 ---
const isLoggedIn = ref(false) // 로그인 했는지 여부
const myName = ref('')        // 입력받을 내 닉네임
const inputMsg = ref('')      // 채팅 입력값
const messageContainer = ref(null) 

// --- 로그인(입장) 함수 ---
const login = async () => {
  if (!myName.value.trim()) {
    alert("닉네임을 입력해주세요!")
    return
  }
  
  // 로그인 처리 (화면 전환)
  isLoggedIn.value = true
  
  // 방 목록 가져오기 & 첫번째 방 입장
  await store.fetchRooms()
  if (store.rooms.length > 0) {
    store.joinRoom(store.rooms[0].id)
  }
}

// --- 채팅 관련 로직 ---
// 메시지가 오면 스크롤을 맨 아래로 내림
watch(() => store.messages.length, () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
})

const send = async () => {
  if (!inputMsg.value.trim()) return
  await store.sendMessage(inputMsg.value, myName.value)
  inputMsg.value = ''
}
</script>

<template>
  <div v-if="!isLoggedIn" class="login-container">
    <div class="login-card">
      <h1>SimChat 입장 🚪</h1>
      <p>사용할 닉네임을 입력하세요</p>
      <input 
        v-model="myName" 
        @keyup.enter="login"
        type="text" 
        placeholder="예: 홍길동" 
        autofocus
      />
      <button @click="login">입장하기</button>
    </div>
  </div>

  <div v-else class="app-container">
    
    <aside class="sidebar">
      <div class="sidebar-header">SimChat 💬</div>
      <ul class="room-list">
        <li v-for="room in store.rooms" :key="room.id">
          <button 
            @click="store.joinRoom(room.id)"
            :class="{ active: store.currentRoom === room.id }"
          >
            # {{ room.name }}
          </button>
        </li>
      </ul>
      <div class="my-profile">
        내 닉네임: <strong>{{ myName }}</strong>
      </div>
    </aside>

    <main class="chat-area">
      <header class="chat-header">
        <h2>{{ store.rooms.find(r => r.id === store.currentRoom)?.name || '채팅방 선택' }}</h2>
      </header>

      <div class="messages-container" ref="messageContainer">
        <div v-if="store.messages.length === 0" class="empty-state">
          대화 내용이 없습니다. 첫 메시지를 보내보세요!
        </div>

        <div 
          v-for="msg in store.messages" 
          :key="msg.id" 
          class="message-wrapper"
          :class="{ 'my-message': msg.username === myName, 'other-message': msg.username !== myName }"
        >
          <span class="sender-name" v-if="msg.username !== myName">{{ msg.username }}</span>
          <div class="bubble">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <div class="input-area">
        <input 
          v-model="inputMsg" 
          @keyup.enter="send" 
          type="text" 
          placeholder="메시지를 입력하세요..." 
        />
        <button @click="send" :disabled="!inputMsg.trim()">전송</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* --- 로그인 화면 스타일 --- */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  font-family: 'Apple SD Gothic Neo', sans-serif;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-align: center;
  width: 300px;
}

.login-card h1 {
  margin-top: 0;
  color: #2c3e50;
}

.login-card input {
  width: 100%;
  padding: 12px;
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box; /* 패딩 포함 크기 계산 */
}

.login-card button {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
}

.login-card button:hover {
  background-color: #2980b9;
}

/* --- 기존 채팅 스타일 (동일) --- */
.app-container {
  display: flex;
  height: 100vh;
  font-family: 'Apple SD Gothic Neo', sans-serif;
  color: #333;
}

.sidebar {
  width: 240px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  font-size: 1.2rem;
  font-weight: bold;
  background-color: #1a252f;
}

.room-list {
  flex: 1;
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
}

.room-list button {
  width: 100%;
  text-align: left;
  padding: 15px 20px;
  background: none;
  border: none;
  color: #bdc3c7;
  cursor: pointer;
  transition: 0.2s;
  font-size: 1rem;
}

.room-list button:hover {
  background-color: #34495e;
  color: white;
}

.room-list button.active {
  background-color: #3498db;
  color: white;
  font-weight: bold;
}

.my-profile {
  padding: 15px;
  background-color: #1a252f;
  font-size: 0.9rem;
  color: #95a5a6;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}

.chat-header {
  padding: 15px 20px;
  background-color: white;
  border-bottom: 1px solid #ddd;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  text-align: center;
  color: #888;
  margin-top: 50px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.bubble {
  padding: 10px 15px;
  border-radius: 15px;
  font-size: 0.95rem;
  line-height: 1.4;
  word-break: break-all;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.sender-name {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
  margin-left: 5px;
}

.my-message {
  align-self: flex-end;
}

.my-message .bubble {
  background-color: #3498db;
  color: white;
  border-bottom-right-radius: 0;
}

.other-message {
  align-self: flex-start;
}

.other-message .bubble {
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-bottom-left-radius: 0;
}

.input-area {
  padding: 20px;
  background-color: white;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 10px;
}

.input-area input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 1rem;
}

.input-area input:focus {
  border-color: #3498db;
}

.input-area button {
  padding: 0 25px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.2s;
}

.input-area button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}
</style>