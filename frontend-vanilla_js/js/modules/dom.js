// DOM 관리
export class DOMManager {
    constructor() {
        this.$ = this.getElements();
    }

    getElements() {
        return {
            // 셀렉트 박스
            country: document.getElementById('country'),
            topic: document.getElementById('topic'),
            model: document.getElementById('model'),
            
            // 버튼
            newChatBtn: document.getElementById('newChatBtn'),
            sendBtn: document.getElementById('sendBtn'),
            
            // 채팅 영역
            chatList: document.getElementById('chatList'),
            chatArea: document.getElementById('chatArea'),
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            chatForm: document.getElementById('chatForm'),
            
            // FAQ 영역
            faqSection: document.getElementById('faqSection'),
            faqCards: document.getElementById('faqCards'),
            sourcesInfo: document.getElementById('sourcesInfo'),
            
            // 소스 모달
            sourcesBtn: document.getElementById('sourcesBtn'),
            sourcesCount: document.getElementById('sourcesCount'),
            sourcesModal: document.getElementById('sourcesModal'),
            sourcesList: document.getElementById('sourcesList'),
            closeSourcesModal: document.getElementById('closeSourcesModal')
        };
    }

    // 유틸리티
    show(element) {
        element?.classList.remove('hidden');
    }

    hide(element) {
        element?.classList.add('hidden');
    }

    clear(element) {
        if (element) element.innerHTML = '';
    }

    scrollToBottom(element) {
        setTimeout(() => {
            if (element) element.scrollTop = element.scrollHeight;
        }, 100);
    }

    populateSelect(select, options, mapping = {}) {
        if (!select) return;
        
        select.innerHTML = '<option value="">선택하세요</option>';
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.textContent = mapping[option] || option;
            select.appendChild(opt);
        });
    }
}