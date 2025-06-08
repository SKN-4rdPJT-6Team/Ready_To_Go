// UI 렌더링
export class UIRenderer {
    constructor(state, dom, api) {
        this.state = state;
        this.dom = dom;
        this.api = api;
        this.documentSources = [];
    }

    // 셀렉트 박스 렌더링
    renderSelects(countries, topics, models) {
        // API 매핑이 없을 경우 기본 매핑 사용
        const countryMap = this.api?.countryMap || {};
        const topicMap = this.api?.topicMap || {};
        
        this.dom.populateSelect(this.dom.$.country, countries, countryMap);
        this.dom.populateSelect(this.dom.$.topic, topics, topicMap);
        this.renderModels(models);
        
        // 기본값 설정
        this.dom.$.country.value = this.state.country;
        this.dom.$.topic.value = this.state.topic;
        this.dom.$.model.value = this.state.model;
    }

    renderModels(models) {
        const select = this.dom.$.model;
        if (!select) return;
        
        this.dom.clear(select);
        const modelList = models.available_models || models;
        
        modelList.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            select.appendChild(option);
        });
    }

    // 채팅 리스트 렌더링
    renderChatList() {
        const container = this.dom.$.chatList;
        if (!container) return;

        if (this.state.chats.length === 0) {
            container.innerHTML = '<span class="text-gray-400 text-sm">대화가 없습니다</span>';
            return;
        }

        container.innerHTML = this.state.chats.map(chat => `
            <button class="chat-list-item text-left px-3 py-2 rounded-lg hover:bg-primary/10 text-gray-800 w-full truncate transition-all ${
                chat.id === this.state.activeChat ? 'bg-primary/20' : ''
            }" data-chat-id="${chat.id}">
                💬 ${chat.title}
            </button>
        `).join('');
    }

    // 채팅 메시지 렌더링
    renderChat() {
        const container = this.dom.$.chatMessages;
        if (!container) return;

        const activeChat = this.state.getActiveChat();
        
        if (!activeChat) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-16">
                    <p class="text-lg font-medium mb-2">대화를 시작하려면</p>
                    <p class="text-sm">'새 대화' 버튼을 클릭하세요</p>
                </div>
            `;
            return;
        }

        container.innerHTML = activeChat.messages.map(message => `
            <div class="flex ${message.role === "user" ? "justify-end" : "justify-start"} mb-4">
                ${this.renderMessage(message)}
            </div>
        `).join('');

        this.dom.scrollToBottom(this.dom.$.chatArea);
    }

    renderMessage(message) {
        if (message.role === "bot") {
            return `
                <div class="flex items-end gap-2">
                    <img src="assets/mascot.png" class="w-7 h-7" alt="bot" onerror="this.style.display='none'">
                    <span class="bg-primary/90 text-white px-4 py-2 rounded-2xl rounded-bl-sm max-w-[70%] shadow-sm whitespace-pre-wrap">${message.text}</span>
                </div>
            `;
        } else {
            return `
                <div class="flex items-end gap-2">
                    <span class="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl rounded-br-sm max-w-[70%] shadow-sm whitespace-pre-wrap">${message.text}</span>
                    <div class="w-7 h-7 rounded-full bg-gray-600 flex items-center justify-center text-xs font-bold text-white">나</div>
                </div>
            `;
        }
    }

    // FAQ 렌더링
    renderFAQ(examples, sources = []) {
        if (examples.length === 0) {
            this.dom.hide(this.dom.$.faqSection);
            return;
        }

        this.dom.show(this.dom.$.faqSection);
        
        this.dom.$.faqCards.innerHTML = `
            <div class="faq-cards-wrapper">
                ${examples.map(question => `
                    <button class="faq-card min-w-[220px] max-w-[260px] bg-white border border-gray-200 rounded-xl px-5 py-4 text-left flex-shrink-0 hover:ring-4 hover:ring-primary/30 focus:outline-none transition-all duration-300 transform hover:scale-105 shadow-md hover:shadow-lg">
                        <div class="faq-question text-primary font-bold mb-2">${question}</div>
                    </button>
                `).join('')}
            </div>
        `;

        // 소스 정보 표시
        this.documentSources = sources;
        if (sources.length > 0) {
            if (this.dom.$.sourcesCount) {
                this.dom.$.sourcesCount.textContent = sources.length;
            }
            if (this.dom.$.sourcesInfo) {
                this.dom.show(this.dom.$.sourcesInfo);
            }
        } else {
            if (this.dom.$.sourcesInfo) {
                this.dom.hide(this.dom.$.sourcesInfo);
            }
        }
    }

    // 로딩 표시
    showLoading() {
        if (!this.dom.$.chatMessages) return;
        
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingMessage';
        loadingDiv.innerHTML = `
            <div class="flex justify-start mb-4">
                <div class="flex items-end gap-2">
                    <img src="assets/mascot.png" class="w-7 h-7" alt="bot" onerror="this.style.display='none'">
                    <span class="bg-primary/90 text-white px-4 py-2 rounded-2xl rounded-bl-sm shadow-sm">
                        <span class="loading-dots">답변 생성 중</span>
                    </span>
                </div>
            </div>
        `;
        this.dom.$.chatMessages.appendChild(loadingDiv);
        this.dom.scrollToBottom(this.dom.$.chatArea);
    }

    hideLoading() {
        document.getElementById('loadingMessage')?.remove();
    }

    // 인터페이스 상태 업데이트
    updateInterface() {
        const isActive = this.state.activeChat !== null;
        const isLoading = this.state.loading;

        // 채팅 영역
        this.dom.$.chatArea?.classList.toggle('opacity-50', !isActive);
        
        // 입력 폼
        this.dom.$.chatForm?.classList.toggle('opacity-50', !isActive);
        if (this.dom.$.messageInput) {
            this.dom.$.messageInput.disabled = !isActive || isLoading;
            this.dom.$.messageInput.placeholder = isActive ? "질문을 입력하세요" : "새 대화 시작 버튼을 눌러주세요";
        }
        
        // 전송 버튼
        if (this.dom.$.sendBtn) {
            this.dom.$.sendBtn.disabled = !isActive || isLoading;
            this.dom.$.sendBtn.textContent = isLoading ? "전송 중..." : "전송";
            this.dom.$.sendBtn.classList.toggle('opacity-60', this.dom.$.sendBtn.disabled);
        }
    }

    // 소스 모달
    showSourcesModal() {
        if (!this.documentSources.length || !this.dom.$.sourcesList) return;
        
        this.dom.$.sourcesList.innerHTML = this.documentSources.map((source, index) => `
            <div class="flex items-start py-2 border-b border-gray-100 last:border-0">
                <span class="text-gray-400 mr-2">${index + 1}.</span>
                <a href="${source}" target="_blank" class="text-sm text-blue-600 hover:underline break-all">
                    ${this.getDomain(source)}
                </a>
            </div>
        `).join('');
        
        this.dom.show(this.dom.$.sourcesModal);
    }

    hideSourcesModal() {
        this.dom.hide(this.dom.$.sourcesModal);
    }

    getDomain(url) {
        try {
            return new URL(url).hostname.replace('www.', '');
        } catch {
            return url;
        }
    }
}