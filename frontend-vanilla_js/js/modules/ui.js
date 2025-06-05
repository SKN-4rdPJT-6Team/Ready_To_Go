// UI 렌더링 관리
export class UIRenderer {
    constructor(state, domManager) {
        this.state = state;
        this.dom = domManager;
    }

    // 국가 목록 렌더링
    renderCountries(countries) {
        this.dom.populateSelect(
            this.dom.elements.countrySelect, 
            countries, 
            null, 
            null, 
            window.api.countryMap
        );
        this.dom.elements.countrySelect.value = this.state.country;
    }

    // 토픽 목록 렌더링
    renderTopics(topics) {
        this.dom.populateSelect(
            this.dom.elements.topicSelect, 
            topics, 
            null, 
            null, 
            window.api.topicMap
        );
        this.dom.elements.topicSelect.value = this.state.topic;
    }

    // 모델 목록 렌더링
    renderModels(models) {
        this.dom.clearElement(this.dom.elements.modelSelect);
        
        let modelList = models;
        if (models.available_models) {
            modelList = models.available_models;
        }
        
        modelList.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            this.dom.elements.modelSelect.appendChild(option);
        });
        
        if (modelList.length > 0 && !this.state.model) {
            this.state.updateModel(modelList[0].id);
        }
        this.dom.elements.modelSelect.value = this.state.model;
    }

    // FAQ 섹션 렌더링
    renderFAQSection() {
        if (this.state.exampleQuestions.length === 0) {
            this.dom.hideElement(this.dom.elements.faqSection);
            return;
        }

        this.dom.showElement(this.dom.elements.faqSection);
        this.dom.clearElement(this.dom.elements.faqCards);

        this.state.exampleQuestions.forEach((faq, index) => {
            const card = this.createFAQCard(faq, index);
            this.dom.elements.faqCards.appendChild(card);
        });

        // 소스 정보 업데이트
        if (this.state.documentSources.length > 0) {
            this.dom.showElement(this.dom.elements.sourcesInfo);
            this.dom.elements.sourcesCount.textContent = this.state.documentSources.length;
        } else {
            this.dom.hideElement(this.dom.elements.sourcesInfo);
        }
    }

    // FAQ 카드 생성
    createFAQCard(faq, index) {
        const card = document.createElement('button');
        card.className = 'faq-card min-w-[220px] max-w-[260px] bg-white border border-gray-200 rounded-xl px-5 py-4 text-left flex-shrink-0 hover:ring-4 hover:ring-primary/30 focus:outline-none transition-all duration-300 transform hover:scale-105 shadow-md hover:shadow-lg card-travel';
        
        card.innerHTML = `
            <div class="faq-question text-primary font-bold mb-2 truncate transition-all duration-300">
                ${faq.q}
            </div>
            <div class="faq-answer text-gray-600 text-xs mt-1 h-0 opacity-0 transition-all duration-300 overflow-hidden">
                ${faq.a}
            </div>
        `;

        return card;
    }

    // 채팅 리스트 렌더링
    renderChatList() {
        this.dom.clearElement(this.dom.elements.chatList);
        
        if (this.state.chatList.length === 0) {
            this.dom.elements.chatList.innerHTML = '<span class="text-gray-400 text-sm">대화가 없습니다</span>';
            return;
        }

        this.state.chatList.forEach(chat => {
            const chatItem = document.createElement('button');
            chatItem.className = `chat-list-item text-left px-3 py-2 rounded-lg hover:bg-primary/10 text-gray-800 w-full truncate transition-all ${
                chat.id === this.state.activeChat ? 'active' : ''
            }`;
            chatItem.innerHTML = `💬 ${chat.title}`;
            chatItem.dataset.chatId = chat.id;
            
            this.dom.elements.chatList.appendChild(chatItem);
        });
    }

    // 채팅 영역 렌더링
    renderChatArea() {
        const activeChat = this.state.getActiveChat();
        
        if (!activeChat) {
            this.disableChatInterface();
            return;
        }

        this.dom.clearElement(this.dom.elements.chatMessages);
        
        if (activeChat.messages.length === 0) {
            this.dom.elements.chatMessages.innerHTML = '<div class="text-center text-gray-500 py-16">대화를 시작해 보세요.</div>';
        } else {
            activeChat.messages.forEach(message => {
                this.addMessageToChat(message);
            });
        }

        this.dom.scrollToBottom(this.dom.elements.chatArea);
    }

    // 메시지를 채팅에 추가
    addMessageToChat(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message flex ${message.role === "user" ? "justify-end" : "justify-start"}`;
        
        if (message.role === "bot") {
            messageDiv.innerHTML = `
                <div class="flex items-end gap-2">
                    <img src="assets/mascot.png" class="w-7 h-7 mr-2" alt="bot" onerror="this.style.display='none'">
                    <span class="bg-primary/90 text-white px-4 py-2 rounded-2xl rounded-bl-sm max-w-[70%] shadow-sm text-left whitespace-pre-wrap">${message.text}</span>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="flex items-end gap-2">
                    <span class="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl rounded-br-sm max-w-[70%] shadow-sm whitespace-pre-wrap">${message.text}</span>
                    <div class="w-7 h-7 rounded-full bg-gray-600 flex items-center justify-center text-xs font-bold text-white">나</div>
                </div>
            `;
        }

        this.dom.elements.chatMessages.appendChild(messageDiv);
    }

    // 로딩 메시지 추가
    addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingMessage';
        loadingDiv.className = 'flex justify-start';
        loadingDiv.innerHTML = `
            <div class="flex items-end gap-2">
                <img src="assets/mascot.png" class="w-7 h-7 mr-2" alt="bot" onerror="this.style.display='none'">
                <span class="bg-primary/90 text-white px-4 py-2 rounded-2xl rounded-bl-sm min-w-[140px] shadow-sm text-left">
                    <span class="loading-dots">답변 생성 중</span>
                </span>
            </div>
        `;
        this.dom.elements.chatMessages.appendChild(loadingDiv);
        this.dom.scrollToBottom(this.dom.elements.chatArea);
    }

    // 로딩 메시지 제거
    removeLoadingMessage() {
        const loadingMessage = document.getElementById('loadingMessage');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    // 채팅 인터페이스 활성화
    enableChatInterface() {
        this.dom.elements.chatArea.classList.remove('opacity-50');
        this.dom.elements.chatArea.classList.add('min-h-[240px]', 'max-h-[50vh]');
        this.dom.elements.chatArea.classList.remove('min-h-[300px]', 'max-h-[350px]');
        
        this.dom.elements.chatForm.classList.remove('opacity-50');
        this.dom.elements.messageInput.disabled = false;
        this.dom.elements.messageInput.placeholder = "질문을 입력하세요";
        this.dom.elements.sendBtn.disabled = false;
        this.dom.elements.sendBtn.classList.remove('opacity-60', 'cursor-not-allowed');
        
        // 메인 컨텐츠 레이아웃 조정
        this.dom.elements.mainContent.classList.remove('justify-center');
        this.dom.elements.contentContainer.classList.add('flex-1');
        
        // FAQ 섹션 표시
        if (this.state.exampleQuestions.length > 0) {
            this.dom.showElement(this.dom.elements.faqSection);
        }
    }

    // 채팅 인터페이스 비활성화
    disableChatInterface() {
        this.dom.elements.chatArea.classList.add('opacity-50');
        this.dom.elements.chatArea.classList.remove('min-h-[240px]', 'max-h-[50vh]');
        this.dom.elements.chatArea.classList.add('min-h-[300px]', 'max-h-[350px]');
        
        this.dom.elements.chatForm.classList.add('opacity-50');
        this.dom.elements.messageInput.disabled = true;
        this.dom.elements.messageInput.placeholder = "새 대화 시작 버튼을 눌러주세요";
        this.dom.elements.sendBtn.disabled = true;
        this.dom.elements.sendBtn.classList.add('opacity-60', 'cursor-not-allowed');
        
        // 메인 컨텐츠 레이아웃 조정
        this.dom.elements.mainContent.classList.add('justify-center');
        this.dom.elements.contentContainer.classList.remove('flex-1');
        
        // FAQ 섹션 숨기기
        this.dom.hideElement(this.dom.elements.faqSection);
        
        // 빈 상태 표시
        this.dom.clearElement(this.dom.elements.chatMessages);
        this.dom.elements.chatMessages.appendChild(this.dom.elements.emptyState);
    }

    // 버튼 상태 업데이트
    updateSendButton() {
        if (this.state.loading) {
            this.dom.elements.sendBtn.textContent = "전송 중...";
            this.dom.elements.sendBtn.disabled = true;
            this.dom.elements.sendBtn.classList.add('opacity-60', 'cursor-not-allowed');
        } else {
            this.dom.elements.sendBtn.textContent = "전송";
            this.dom.elements.sendBtn.disabled = this.state.activeChat === null || !this.dom.elements.messageInput.value.trim();
            if (!this.dom.elements.sendBtn.disabled) {
                this.dom.elements.sendBtn.classList.remove('opacity-60', 'cursor-not-allowed');
            }
        }
    }

    // 소스 모달 렌더링
    renderSourcesModal() {
        this.dom.clearElement(this.dom.elements.sourcesList);
        
        this.state.documentSources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'flex items-start py-2 border-b border-gray-100 last:border-0';
            
            let domain = '사이트';
            let path = source;
            try {
                const url = new URL(source);
                domain = url.hostname.replace('www.', '');
                path = url.pathname + url.search;
            } catch (e) {
                domain = source.split('/')[2] || '사이트';
            }
            
            sourceItem.innerHTML = `
                <span class="text-gray-400 mr-2">${index + 1}.</span>
                <a href="${source}" target="_blank" rel="noopener noreferrer" class="text-sm text-blue-600 hover:underline break-all">
                    <span class="font-medium">${domain}</span>
                    <span class="text-gray-500">${path}</span>
                </a>
            `;
            
            this.dom.elements.sourcesList.appendChild(sourceItem);
        });
    }

    // 소스 모달 표시
    showSourcesModal() {
        this.renderSourcesModal();
        this.dom.elements.sourcesModal.classList.remove('hidden');
        this.dom.elements.sourcesModal.classList.add('modal-enter');
    }

    // 소스 모달 숨기기
    hideSourcesModal() {
        this.dom.elements.sourcesModal.classList.add('hidden');
        this.dom.elements.sourcesModal.classList.remove('modal-enter');
    }
}
