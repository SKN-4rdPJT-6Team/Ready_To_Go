// 채팅 관리
export class ChatManager {
    constructor(state, domManager) {
        this.state = state;
        this.dom = domManager;
    }

    // 새 채팅 생성
    async createNewChat() {
        if (!this.state.country || !this.state.topic || !this.state.model) {
            alert("국가, 토픽, 모델을 모두 선택해주세요.");
            return;
        }

        try {
            this.state.setLoading(true);
            
            const response = await window.api.createConversation(
                this.state.sessionId,
                this.state.country,
                this.state.topic,
                this.state.model
            );

            const modelName = this.getModelName(this.state.model);
            const newChat = {
                id: Date.now(),
                conversationId: response.id || Date.now(),
                title: `${window.api.countryMap[this.state.country] || this.state.country} - ${window.api.topicMap[this.state.topic] || this.state.topic} (${modelName})`,
                messages: [{
                    role: "bot",
                    text: `안녕하세요! ${modelName}을(를) 사용하는 Ready To Go 챗봇입니다. 무엇을 도와드릴까요?`
                }]
            };

            this.state.addChat(newChat);
            this.state.setActiveChat(newChat.id);
            return newChat;

        } catch (error) {
            console.error('Failed to create conversation:', error);
            return this.createOfflineChat();
        } finally {
            this.state.setLoading(false);
        }
    }

    // 오프라인 채팅 생성
    createOfflineChat() {
        const modelName = this.getModelName(this.state.model);
        const newChat = {
            id: Date.now(),
            conversationId: Date.now(),
            title: `${window.api.countryMap[this.state.country] || this.state.country} - ${window.api.topicMap[this.state.topic] || this.state.topic} (${modelName})`,
            messages: [{
                role: "bot",
                text: `안녕하세요! ${modelName}을(를) 사용하는 Ready To Go 챗봇입니다. 현재 오프라인 모드입니다.`
            }]
        };

        this.state.addChat(newChat);
        this.state.setActiveChat(newChat.id);
        return newChat;
    }

    // 메시지 전송
    async sendMessage(text) {
        if (!text.trim() || this.state.activeChat === null || this.state.loading) return;

        const activeChat = this.state.getActiveChat();
        if (!activeChat) return;

        // 사용자 메시지 추가
        const userMessage = { role: "user", text };
        activeChat.messages.push(userMessage);

        try {
            this.state.setLoading(true);
            
            const response = await window.api.sendMessage(
                text,
                activeChat.conversationId,
                this.state.sessionId,
                this.state.country,
                this.state.topic,
                this.state.model,
                false
            );

            const botMessage = {
                role: "bot",
                text: response.message?.content || response.message || "죄송합니다. 응답을 생성할 수 없습니다.",
                references: response.message?.references
            };

            activeChat.messages.push(botMessage);
            return { userMessage, botMessage };

        } catch (error) {
            console.error('Failed to send message:', error);
            
            const errorMessage = {
                role: "bot",
                text: "죄송합니다. 서버와의 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요."
            };
            
            activeChat.messages.push(errorMessage);
            return { userMessage, botMessage: errorMessage };
        } finally {
            this.state.setLoading(false);
        }
    }

    // 채팅 선택
    selectChat(chatId) {
        this.state.setActiveChat(chatId);
        const selectedChat = this.state.getActiveChat();
        if (selectedChat) {
            this.restoreChatSettings(selectedChat);
        }
    }

    // 채팅 설정 복원
    restoreChatSettings(chat) {
        const title = chat.title;
        const parts = title.split(' (');
        if (parts.length >= 2) {
            const [countryTopicPart, modelPart] = parts;
            const modelName = modelPart.replace(')', '').trim();
            
            if (countryTopicPart.includes(' - ')) {
                const [countryKo, topicKo] = countryTopicPart.split(' - ').map(s => s.trim());
                
                // 한글 -> 영어 역변환
                const countryEn = window.api.reverseCountryMap[countryKo] || countryKo;
                const topicEn = window.api.reverseTopicMap[topicKo] || topicKo;
                
                if (countryEn !== this.state.country) {
                    this.state.updateCountry(countryEn);
                    this.dom.elements.countrySelect.value = countryEn;
                }
                
                if (topicEn !== this.state.topic) {
                    this.state.updateTopic(topicEn);
                    this.dom.elements.topicSelect.value = topicEn;
                }
                
                // 모델 복원
                const foundModel = this.state.models.find(m => m.name === modelName);
                if (foundModel && foundModel.id !== this.state.model) {
                    this.state.updateModel(foundModel.id);
                    this.dom.elements.modelSelect.value = foundModel.id;
                }
            }
        }
    }

    // 모델 이름 가져오기
    getModelName(modelId) {
        const model = this.state.models.find(m => m.id === modelId);
        return model ? model.name : modelId;
    }
}
