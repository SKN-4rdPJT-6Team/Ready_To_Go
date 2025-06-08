// API 통신 관리자 - Django 백엔드와 통신
export class APIManager {
    constructor() {
        // Django 개발 서버 기본 URL
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

    // HTTP 요청 헬퍼 (기존 call 메서드를 확장)
    async call(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API 호출 실패 ${endpoint}:`, error);
            throw error;
        }
    }

    // 별칭 메서드 (기존 코드 호환성을 위해)
    async request(url, options = {}) {
        return this.call(url, options);
    }

    // 메타데이터 API
    async getCountries() {
        try {
            return await this.call('/countries/');
        } catch (error) {
            console.warn('서버에서 국가 목록을 가져오는데 실패했습니다. 기본값을 사용합니다.');
            return ["America", "Australia", "Austria", "Canada", "China", "France", "Germany", "Italy", "Japan", "New Zealand", "Philippines", "Singapore", "UK"];
        }
    }

    async getTopics() {
        try {
            return await this.call('/topics/');
        } catch (error) {
            console.warn('서버에서 토픽 목록을 가져오는데 실패했습니다. 기본값을 사용합니다.');
            return ["visa", "insurance", "safety", "immigration"];
        }
    }

    async getModels(country = null, topic = null) {
        try {
            const models = await this.call('/chat/settings/models/');
            return this.filterModelsForCountryTopic(models.available_models || models, country, topic);
        } catch (error) {
            console.warn('서버에서 모델 목록을 가져오는데 실패했습니다. 기본값을 사용합니다.');
            const defaultModels = [
                { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
                { id: "gpt-4", name: "GPT-4" },
                { id: "gemini-1.5-flash", name: "Gemini 1.5 Flash" },
                { id: "phi-2", name: "Phi-2 (Fine-Tuned)" }
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
            '안전': ['중국', '영국', '필리핀', '일본', '호주']
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

    // 채팅 API
    async createConversation(sessionId, country, topic, model) {
        return await this.call('/chat/conversation/', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                country_id: country,
                topic_id: topic,
                model_id: model
            })
        });
    }

    async sendMessage(message, conversationId, sessionId, country, topic, model, stream = false) {
        return await this.call('/chat/message/', {
            method: 'POST',
            body: JSON.stringify({
                message,
                conversation_id: conversationId,
                session_id: sessionId,
                country,
                topic,
                model_id: model,
                stream
            })
        });
    }

    async getHistory(conversationId) {
        return await this.call(`/chat/history/${conversationId}/`);
    }

    // FAQ & 소스 API
    async getExamples(country, topic) {
        try {
            const params = new URLSearchParams();
            if (country) params.append('country', country);
            if (topic) params.append('topic', topic);
            
            return await this.call(`/chat/examples/?${params}`);
        } catch (error) {
            console.warn('서버에서 예시를 가져오는데 실패했습니다.');
            return { examples: [] };
        }
    }

    async getSources(country, topic) {
        try {
            const params = new URLSearchParams();
            if (country) params.append('country', country);
            if (topic) params.append('topic', topic);
            
            const response = await this.call(`/chat/sources/?${params}`);
            return { sources: response.sources || [] };
        } catch (error) {
            console.warn('서버에서 소스를 가져오는데 실패했습니다.');
            return { sources: [] };
        }
    }

    // 별칭 메서드 (기존 코드 호환성)
    async getDocumentSources(country, topic) {
        const result = await this.getSources(country, topic);
        return result.sources;
    }

    // 문서 API
    async getDocuments(countryId, topicId, sourceId, limit = 20, offset = 0) {
        let url = `/documents/?country_id=${countryId}&topic_id=${topicId}&limit=${limit}&offset=${offset}`;
        if (sourceId) {
            url += `&source_id=${sourceId}`;
        }
        return await this.call(url);
    }

    async getDocument(documentId) {
        return await this.call(`/documents/${documentId}/`);
    }

    async searchDocuments(query, limit = 20) {
        return await this.call(`/documents/search/?q=${encodeURIComponent(query)}&limit=${limit}`);
    }
}
