// 채팅 관리
export class ChatManager {
    constructor(state, dom, api) {
        this.state = state;
        this.dom = dom;
        this.api = api;
    }

    async createNew() {
        const { country, topic, model } = this.state.data;
        
        if (!country || !topic || !model) {
            alert("국가, 토픽, 모델을 모두 선택해주세요.");
            return false;
        }

        try {
            this.state.set('loading', true);
            
            // 백엔드에 대화 생성
            const conversation = await this.api.createConversation(
                this.state.data.sessionId, country, topic, model
            );

            // 새 채팅 생성
            const newChat = {
                id: Date.now(),
                conversationId: conversation?.id || Date.now(),
                title: this.getChatTitle(),
                messages: [{
                    role: "bot",
                    text: "안녕하세요! Ready To Go 챗봇입니다. 무엇을 도와드릴까요?"
                }]
            };

            this.state.addChat(newChat);
            return true;

        } catch (error) {
            console.error('채팅 생성 실패:', error);
            // 오프라인 모드
            this.createOffline();
            return true;
        } finally {
            this.state.set('loading', false);
        }
    }

    createOffline() {
        const newChat = {
            id: Date.now(),
            conversationId: Date.now(),
            title: this.getChatTitle() + " (오프라인)",
            messages: [{
                role: "bot",
                text: "안녕하세요! 현재 오프라인 모드입니다."
            }]
        };
        this.state.addChat(newChat);
    }

    async sendMessage(text, skipUserMessage = false) {
        const activeChat = this.state.getActiveChat();
        if (!activeChat || !text.trim()) return false;

        // 사용자 메시지 추가 (이미 추가되었다면 건너뛰기)
        if (!skipUserMessage) {
            activeChat.messages.push({ role: "user", text });
        }

        try {
            this.state.set('loading', true);
            
            // API 호출
            const response = await this.api.sendMessage(
                text,
                activeChat.conversationId,
                this.state.data.sessionId,
                this.state.country,
                this.state.topic,
                this.state.model
            );

            // 봇 응답 추가
            activeChat.messages.push({
                role: "bot",
                text: response?.message?.content || response?.message || "응답을 생성할 수 없습니다."
            });

            return true;

        } catch (error) {
            console.error('메시지 전송 실패:', error);
            activeChat.messages.push({
                role: "bot",
                text: "죄송합니다. 서버 연결에 문제가 있습니다."
            });
            return true;
        } finally {
            this.state.set('loading', false);
        }
    }

    select(chatId) {
        this.state.set('activeChat', chatId);
    }

    getChatTitle() {
        const countryName = this.api?.countryMap?.[this.state.country] || this.state.country;
        const topicName = this.api?.topicMap?.[this.state.topic] || this.state.topic;
        const modelName = this.dom.$.model.options[this.dom.$.model.selectedIndex]?.text || this.state.model;
        return `${countryName} - ${topicName} (${modelName})`;
    }
}