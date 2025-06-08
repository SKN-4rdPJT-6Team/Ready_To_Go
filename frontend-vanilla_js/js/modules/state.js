// 상태 관리
export class AppState {
    constructor() {
        this.data = {
            country: "America",
            topic: "visa", 
            model: "gpt-3.5-turbo",
            chats: [],
            activeChat: null,
            sessionId: `session_${Date.now()}`,
            loading: false
        };
    }

    // 상태 업데이트
    set(key, value) {
        this.data[key] = value;
    }

    get(key) {
        return this.data[key];
    }

    // 채팅 관련
    addChat(chat) {
        this.data.chats.push(chat);
        this.data.activeChat = chat.id;
    }

    getActiveChat() {
        return this.data.chats.find(chat => chat.id === this.data.activeChat);
    }

    // 편의 메서드
    get country() { return this.data.country; }
    get topic() { return this.data.topic; }
    get model() { return this.data.model; }
    get chats() { return this.data.chats; }
    get activeChat() { return this.data.activeChat; }
    get loading() { return this.data.loading; }
}