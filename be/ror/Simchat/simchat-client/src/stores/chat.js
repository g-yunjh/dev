import { defineStore } from 'pinia'
import axios from 'axios'
import { createConsumer } from '@rails/actioncable'

const api = axios.create({ baseURL: 'http://localhost:3000' })
const cable = createConsumer('ws://localhost:3000/cable') // 웹소켓 주소

export const useChatStore = defineStore('chat', {
  state: () => ({
    rooms: [],
    currentRoom: null,
    messages: [],
    subscription: null // 소켓 구독 정보 저장
  }),
  actions: {
    async fetchRooms() {
      const res = await api.get('/rooms')
      this.rooms = res.data
    },
    async joinRoom(roomId) {
        // 1. 기존 방 구독 취소
        if (this.subscription) this.subscription.unsubscribe()

        // ✅ [수정됨] 방을 바꿀 때 가장 먼저 현재 메시지 목록을 초기화!
        this.messages = []
        this.currentRoom = roomId

        // 2. 메시지 목록 불러오기 (로딩되는 동안 위에서 초기화했으므로 빈 화면이 뜸)
        // (주의: Rails 컨트롤러에서 room_id로 필터링이 제대로 구현되어 있어야 합니다)
        const res = await api.get(`/messages?room_id=${roomId}`)
        this.messages = res.data

        // 3. 실시간 구독 시작
        this.subscription = cable.subscriptions.create(
        { channel: 'ChatChannel', room_id: roomId },
        {
            received: (newMessage) => {
            this.messages.push(newMessage)
            // (선택사항) 새 메시지 오면 스크롤 자동으로 내리기 위한 이벤트 발생 시점
            }
        }
        )
    },
    async sendMessage(content, username) {
      // 메시지 전송은 HTTP POST로 (CRUD - Create)
      await api.post('/messages', {
        room_id: this.currentRoom,
        content,
        username
      })
      // 여기서 this.messages.push 하지 않음! (소켓이 받아서 처리할 것이므로)
    }
  }
})