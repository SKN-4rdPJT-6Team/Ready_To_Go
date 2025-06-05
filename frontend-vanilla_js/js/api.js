// API 모듈 - Django 백엔드와 통신
class API {
    constructor() {
        // Django 개발 서버 기본 URL (필요에 따라 변경)
        this.baseURL = 'http://localhost:8000/api';
        
        // 국가 및 토픽 매핑
        this.countryMap = {
            "America": "미국",
            "Australia": "호주", 
            "Austria": "오스트리아",
            "Canada": "캐나다",
            "China": "중국",
            "France": "프랑스",
            "Germany": "독일",
            "Italy": "이탈리아",
            "Japan": "일본",
            "New Zealand": "뉴질랜드",
            "Philippines": "필리핀",
            "Singapore": "싱가포르",
            "UK": "영국"
        };

        this.topicMap = {
            "visa": "비자",
            "insurance": "보험", 
            "safety": "안전",
            "immigration": "입국규정"
        };

        // 역매핑
        this.reverseCountryMap = Object.fromEntries(
            Object.entries(this.countryMap).map(([key, value]) => [value, key])
        );

        this.reverseTopicMap = Object.fromEntries(
            Object.entries(this.topicMap).map(([key, value]) => [value, key])
        );
    }

    // HTTP 요청 헬퍼
    async request(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(`${this.baseURL}${url}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${url}:`, error);
            throw error;
        }
    }

    // 메타데이터 API
    async getCountries() {
        try {
            return await this.request('/countries/');
        } catch (error) {
            console.warn('Failed to fetch countries from server, using defaults');
            // 기본값 반환
            return ["America", "Australia", "Canada", "Japan", "France", "Germany", "Italy", "UK", "China", "Singapore"];
        }
    }

    async getTopics() {
        try {
            return await this.request('/topics/');
        } catch (error) {
            console.warn('Failed to fetch topics from server, using defaults');
            // 기본값 반환
            return ["visa", "insurance", "safety", "immigration"];
        }
    }

    async getSources() {
        try {
            return await this.request('/sources/');
        } catch (error) {
            console.warn('Failed to fetch sources from server');
            return [];
        }
    }

    // 채팅 API
    async createConversation(sessionId, countryId, topicId, modelId) {
        return await this.request('/chat/conversation/', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                country_id: countryId,
                topic_id: topicId,
                model_id: modelId
            })
        });
    }

    async sendMessage(message, conversationId, sessionId, country, topic, modelId, stream = false) {
        return await this.request('/chat/message/', {
            method: 'POST',
            body: JSON.stringify({
                message,
                conversation_id: conversationId,
                session_id: sessionId,
                country,
                topic,
                model_id: modelId,
                stream
            })
        });
    }

    async getHistory(conversationId) {
        return await this.request(`/chat/history/${conversationId}/`);
    }

    async getExamples(country, topic) {
        try {
            const params = new URLSearchParams();
            if (country) params.append('country', country);
            if (topic) params.append('topic', topic);
            
            return await this.request(`/chat/examples/?${params}`);
        } catch (error) {
            console.warn('Failed to fetch examples from server, using defaults');
        }
    }

    async getModels(country, topic) {
        try {
            const models = await this.request('/chat/settings/models/');
            return this.filterModelsForCountryTopic(models, country, topic);
        } catch (error) {
            console.warn('Failed to fetch models from server, using defaults');
            // 기본 모델 목록 반환
            const defaultModels = [
                { id: "gpt-4", name: "GPT-4" },
                { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
                { id: "phi-2", name: "Phi-2" }
            ];
            return this.filterModelsForCountryTopic(defaultModels, country, topic);
        }
    }

    // Phi-2 모델 사용 가능 여부 확인
    isPhiModelAvailable(country, topic) {
        // 허용된 국가-토픽 조합 정의
        const allowedCombinations = {
            '비자': ['호주', '영국', '캐나다', '미국', '일본'],
            '보험': ['이탈리아', '호주', '미국'],
            '입국규정': ['호주', '오스트리아', '캐나다', '싱가포르', '영국'],
            '안전정보': ['중국', '영국', '필리핀', '일본', '호주']
        };

        // 영어 토픽명을 한국어로 변환
        const koreanTopic = this.topicMap[topic] || topic;
        const koreanCountry = this.countryMap[country] || country;

        // 허용된 조합인지 확인
        return allowedCombinations[koreanTopic]?.includes(koreanCountry) || false;
    }

    // 국가-토픽에 따라 모델 필터링
    filterModelsForCountryTopic(models, country, topic) {
        if (!country || !topic) {
            return models;
        }

        // Phi-2 모델이 허용되지 않는 경우 제외
        if (!this.isPhiModelAvailable(country, topic)) {
            return models.filter(model => 
                !model.id.toLowerCase().includes('phi')
            );
        }

        return models;
    }

    async getDocumentSources(country, topic) {
        try {
            const params = new URLSearchParams();
            if (country) params.append('country', country);
            if (topic) params.append('topic', topic);
            
            const response = await this.request(`/chat/sources/?${params}`);
            return response.sources || [];
        } catch (error) {
            console.warn('Failed to fetch document sources');
            return [];
        }
    }

    // 문서 API
    async getDocuments(countryId, topicId, sourceId, limit = 20, offset = 0) {
        let url = `/documents/?country_id=${countryId}&topic_id=${topicId}&limit=${limit}&offset=${offset}`;
        if (sourceId) {
            url += `&source_id=${sourceId}`;
        }
        return await this.request(url);
    }

    async getDocument(documentId) {
        return await this.request(`/documents/${documentId}/`);
    }

    async searchDocuments(query, limit = 20) {
        return await this.request(`/documents/search/?q=${encodeURIComponent(query)}&limit=${limit}`);
    }
}

// API 인스턴스 생성
window.api = new API();