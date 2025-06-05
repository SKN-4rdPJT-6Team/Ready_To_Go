// 애플리케이션 상태 관리
export class AppState {
    constructor() {
        this.state = {
            country: "America",
            topic: "visa", 
            model: "gpt-3.5-turbo",
            chatList: [],
            activeChat: null,
            sessionId: `session_${Date.now()}`,
            exampleQuestions: [],
            documentSources: [],
            models: [],
            loading: false
        };
    }

    // 상태 업데이트 메서드들
    updateCountry(country) {
        this.state.country = country;
        this.state.topic = ""; // 토픽 초기화
    }

    updateTopic(topic) {
        this.state.topic = topic;
    }

    updateModel(model) {
        this.state.model = model;
    }

    setLoading(loading) {
        this.state.loading = loading;
    }

    addChat(chat) {
        this.state.chatList.push(chat);
    }

    setActiveChat(chatId) {
        this.state.activeChat = chatId;
    }

    getActiveChat() {
        return this.state.chatList.find(c => c.id === this.state.activeChat);
    }

    setExampleQuestions(questions) {
        this.state.exampleQuestions = questions;
    }

    setDocumentSources(sources) {
        this.state.documentSources = sources;
    }

    setModels(models) {
        this.state.models = models;
    }

    // getter 메서드들
    get country() { return this.state.country; }
    get topic() { return this.state.topic; }
    get model() { return this.state.model; }
    get chatList() { return this.state.chatList; }
    get activeChat() { return this.state.activeChat; }
    get sessionId() { return this.state.sessionId; }
    get exampleQuestions() { return this.state.exampleQuestions; }
    get documentSources() { return this.state.documentSources; }
    get models() { return this.state.models; }
    get loading() { return this.state.loading; }
}
