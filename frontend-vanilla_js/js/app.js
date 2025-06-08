// 메인 애플리케이션
import { AppState } from './modules/state.js';
import { DOMManager } from './modules/dom.js';
import { APIManager } from './modules/api.js';
import { ChatManager } from './modules/chat.js';
import { UIRenderer } from './modules/ui.js';

class TravelBotApp {
    constructor() {
        this.state = new AppState();
        this.dom = new DOMManager();
        this.api = new APIManager();
        this.chat = new ChatManager(this.state, this.dom, this.api);
        this.ui = new UIRenderer(this.state, this.dom, this.api);

        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadInitialData();
        this.ui.updateInterface();
    }

    bindEvents() {
        // 셀렉트 박스
        this.dom.$.country?.addEventListener('change', (e) => {
            this.state.set('country', e.target.value);
            this.state.set('topic', '');
            this.dom.$.topic.value = '';
            this.loadExamples();
        });

        this.dom.$.topic?.addEventListener('change', (e) => {
            this.state.set('topic', e.target.value);
            this.loadExamples();
        });

        this.dom.$.model?.addEventListener('change', (e) => {
            this.state.set('model', e.target.value);
        });

        // 버튼
        this.dom.$.newChatBtn?.addEventListener('click', async () => {
            const success = await this.chat.createNew();
            if (success) {
                this.ui.renderChatList();
                this.ui.renderChat();
                this.ui.updateInterface();
            }
        });

        this.dom.$.sendBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.dom.$.chatForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // 채팅 선택
        this.dom.$.chatList?.addEventListener('click', (e) => {
            const chatItem = e.target.closest('[data-chat-id]');
            if (chatItem) {
                this.chat.select(parseInt(chatItem.dataset.chatId));
                this.ui.renderChatList();
                this.ui.renderChat();
                this.ui.updateInterface();
            }
        });

        // FAQ 클릭
        this.dom.$.faqCards?.addEventListener('click', (e) => {
            const faqCard = e.target.closest('.faq-card');
            if (faqCard && this.state.activeChat !== null) {
                const question = faqCard.querySelector('.faq-question').textContent;
                this.dom.$.messageInput.value = question;
                this.sendMessage();
            }
        });

        // 소스 모달
        this.dom.$.sourcesBtn?.addEventListener('click', () => {
            this.ui.showSourcesModal();
        });

        this.dom.$.closeSourcesModal?.addEventListener('click', () => {
            this.ui.hideSourcesModal();
        });

        this.dom.$.sourcesModal?.addEventListener('click', (e) => {
            if (e.target === this.dom.$.sourcesModal) {
                this.ui.hideSourcesModal();
            }
        });

        // 입력 변화 감지
        this.dom.$.messageInput?.addEventListener('input', () => {
            this.ui.updateInterface();
        });
    }

    async loadInitialData() {
        try {
            const [countries, topics, models] = await Promise.all([
                this.api.getCountries(),
                this.api.getTopics(),
                this.api.getModels()
            ]);

            this.ui.renderSelects(countries, topics, models);
            await this.loadExamples();

        } catch (error) {
            console.error('초기 데이터 로드 실패:', error);
        }
    }

    async loadExamples() {
        const { country, topic } = this.state.data;
        if (!country || !topic) {
            this.dom.hide(this.dom.$.faqSection);
            return;
        }

        try {
            const [examples, sources] = await Promise.all([
                this.api.getExamples(country, topic),
                this.api.getSources(country, topic)
            ]);

            this.ui.renderFAQ(examples.examples || [], sources.sources || []);
        } catch (error) {
            console.error('예시 로드 실패:', error);
        }
    }

    async sendMessage() {
        const text = this.dom.$.messageInput?.value.trim();
        if (!text) return;

        // 사용자 메시지를 먼저 채팅에 추가
        const activeChat = this.state.getActiveChat();
        if (!activeChat) return;
        
        activeChat.messages.push({ role: "user", text });
        
        this.dom.$.messageInput.value = '';
        this.ui.renderChat(); // 사용자 메시지 즉시 표시
        this.ui.showLoading();
        this.ui.updateInterface();

        const success = await this.chat.sendMessage(text, true); // skipUserMessage 플래그 추가
        if (success) {
            this.ui.hideLoading();
            this.ui.renderChat();
            this.ui.updateInterface();
        }
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.travelBotApp = new TravelBotApp();
});
