// DOM 요소 관리
export class DOMManager {
    constructor() {
        this.elements = this.initializeElements();
    }

    initializeElements() {
        return {
            countrySelect: document.getElementById('country'),
            topicSelect: document.getElementById('topic'),
            modelSelect: document.getElementById('model'),
            newChatBtn: document.getElementById('newChatBtn'),
            chatList: document.getElementById('chatList'),
            faqSection: document.getElementById('faqSection'),
            faqCards: document.getElementById('faqCards'),
            sourcesInfo: document.getElementById('sourcesInfo'),
            sourcesBtn: document.getElementById('sourcesBtn'),
            sourcesCount: document.getElementById('sourcesCount'),
            chatArea: document.getElementById('chatArea'),
            chatMessages: document.getElementById('chatMessages'),
            emptyState: document.getElementById('emptyState'),
            chatForm: document.getElementById('chatForm'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            sourcesModal: document.getElementById('sourcesModal'),
            closeSourcesModal: document.getElementById('closeSourcesModal'),
            sourcesList: document.getElementById('sourcesList'),
            mainContent: document.getElementById('mainContent'),
            contentContainer: document.getElementById('contentContainer')
        };
    }

    // DOM 조작 헬퍼 메서드들
    populateSelect(selectElement, options, valueKey = null, textKey = null, valueMap = null) {
        selectElement.innerHTML = '<option value="">선택하세요</option>';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = valueKey ? option[valueKey] : option;
            optionElement.textContent = textKey ? option[textKey] : (valueMap && valueMap[option]) || option;
            selectElement.appendChild(optionElement);
        });
    }

    showElement(element) {
        element.classList.remove('hidden');
    }

    hideElement(element) {
        element.classList.add('hidden');
    }

    toggleElement(element, show) {
        if (show) {
            this.showElement(element);
        } else {
            this.hideElement(element);
        }
    }

    scrollToBottom(element) {
        setTimeout(() => {
            element.scrollTop = element.scrollHeight;
        }, 100);
    }

    clearElement(element) {
        element.innerHTML = '';
    }
}
