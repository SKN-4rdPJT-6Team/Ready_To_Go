// 모듈 import
import { AppState } from './modules/state.js';
import { DOMManager } from './modules/dom.js';
import { ChatManager } from './modules/chat.js';
import { UIRenderer } from './modules/ui.js';
import { APIManager } from './modules/api.js';

// 메인 애플리케이션 클래스
class TravelBotApp {
    constructor() {
        // 모듈 초기화
        this.state = new AppState();
        this.dom = new DOMManager();
        this.chat = new ChatManager(this.state, this.dom);
        this.ui = new UIRenderer(this.state, this.dom);
        this.api = new APIManager(this.state);

        this.bindEvents();
        this.loadInitialData();
    }

    // 이벤트 바인딩
    bindEvents() {
        // 셀렉트 박스 이벤트
        this.dom.elements.countrySelect.addEventListener('change', (e) => {
            this.handleCountryChange(e.target.value);
        });

        this.dom.elements.topicSelect.addEventListener('change', (e) => {
            this.handleTopicChange(e.target.value);
        });

        this.dom.elements.modelSelect.addEventListener('change', (e) => {
            this.handleModelChange(e.target.value);
        });

        // 새 대화 버튼
        this.dom.elements.newChatBtn.addEventListener('click', () => {
            this.handleNewChat();
        });

        // 채팅 폼 제출
        this.dom.elements.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSendMessage();
        });

        // 채팅 리스트 클릭 (이벤트 위임)
        this.dom.elements.chatList.addEventListener('click', (e) => {
            const chatItem = e.target.closest('.chat-list-item');
            if (chatItem && chatItem.dataset.chatId) {
                this.handleChatSelect(parseInt(chatItem.dataset.chatId));
            }
        });

        // FAQ 카드 클릭 (이벤트 위임)
        this.dom.elements.faqCards.addEventListener('click', (e) => {
            const faqCard = e.target.closest('.faq-card');
            if (faqCard) {
                const question = faqCard.querySelector('.faq-question').textContent;
                this.handleFAQClick(question);
            }
        });

        // 소스 모달 관련
        this.dom.elements.sourcesBtn.addEventListener('click', () => {
            this.ui.showSourcesModal();
        });

        this.dom.elements.closeSourcesModal.addEventListener('click', () => {
            this.ui.hideSourcesModal();
        });

        this.dom.elements.sourcesModal.addEventListener('click', (e) => {
            if (e.target === this.dom.elements.sourcesModal) {
                this.ui.hideSourcesModal();
            }
        });

        // 메시지 입력 변화 감지
        this.dom.elements.messageInput.addEventListener('input', () => {
            this.ui.updateSendButton();
        });
    }

    // 초기 데이터 로드
    async loadInitialData() {
        try {
            const { countries, topics, models } = await this.api.loadInitialData();

            this.ui.renderCountries(countries);
            this.ui.renderTopics(topics);
            this.ui.renderModels(models);
            this.state.setModels(models.available_models || models);

            // 초기 예시 질문 및 소스 로드
            await this.loadExamplesAndSources();

        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    // 국가 변경 처리
    async handleCountryChange(country) {
        this.state.updateCountry(country);
        this.dom.elements.topicSelect.value = "";
        await this.loadExamplesAndSources();
        await this.updateModelsForCurrentSelection();
    }

    // 토픽 변경 처리
    async handleTopicChange(topic) {
        this.state.updateTopic(topic);
        await this.loadExamplesAndSources();
        await this.updateModelsForCurrentSelection();
    }

    // 현재 선택에 따른 모델 업데이트
    async updateModelsForCurrentSelection() {
        if (this.state.country && this.state.topic) {
            try {
                const models = await this.api.loadModelsForCountryTopic(
                    this.state.country,
                    this.state.topic
                );
                
                this.state.setModels(models);
                this.ui.renderModels(models);
                
                // 현재 선택된 모델이 사용 불가능하면 기본값으로 변경
                const currentModel = this.state.model;
                const isCurrentModelAvailable = models.some(model => model.id === currentModel);
                
                if (!isCurrentModelAvailable && models.length > 0) {
                    this.state.updateModel(models[0].id);
                    this.dom.elements.modelSelect.value = models[0].id;
                }
            } catch (error) {
                console.error('Failed to update models:', error);
            }
        }
    }

    // 모델 변경 처리
    handleModelChange(model) {
        this.state.updateModel(model);
    }

    // 예시 질문 및 소스 로드
    async loadExamplesAndSources() {
        const { exampleQuestions, documentSources } = await this.api.loadExamplesAndSources(
            this.state.country, 
            this.state.topic
        );

        this.state.setExampleQuestions(exampleQuestions);
        this.state.setDocumentSources(documentSources);
        this.ui.renderFAQSection();
    }

    // 새 대화 시작 처리
    async handleNewChat() {
        const newChat = await this.chat.createNewChat();
        if (newChat) {
            this.ui.renderChatList();
            this.ui.renderChatArea();
            this.ui.enableChatInterface();
            this.dom.elements.messageInput.value = "";
            this.ui.updateSendButton();
        }
    }

    // 메시지 전송 처리
    async handleSendMessage() {
        const text = this.dom.elements.messageInput.value.trim();
        if (!text) return;

        // UI에 사용자 메시지 추가
        this.ui.addMessageToChat({ role: "user", text });
        this.dom.elements.messageInput.value = "";
        this.ui.updateSendButton();
        this.dom.scrollToBottom(this.dom.elements.chatArea);

        // 로딩 표시
        this.ui.addLoadingMessage();

        try {
            const { userMessage, botMessage } = await this.chat.sendMessage(text);
            
            this.ui.removeLoadingMessage();
            this.ui.addMessageToChat(botMessage);

        } catch (error) {
            this.ui.removeLoadingMessage();
            console.error('Message send failed:', error);
        } finally {
            this.dom.scrollToBottom(this.dom.elements.chatArea);
            this.ui.updateSendButton();
        }
    }

    // 채팅 선택 처리
    handleChatSelect(chatId) {
        this.chat.selectChat(chatId);
        this.ui.renderChatList();
        this.ui.renderChatArea();
        this.ui.enableChatInterface();
        this.dom.elements.messageInput.value = "";
        this.ui.updateSendButton();
    }

    // FAQ 클릭 처리
    handleFAQClick(question) {
        if (this.state.activeChat === null) return;
        this.dom.elements.messageInput.value = question;
        this.handleSendMessage();
    }
}

// 애플리케이션 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.travelBotApp = new TravelBotApp();
});
