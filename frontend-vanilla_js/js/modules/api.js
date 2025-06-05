// API 통신 관리
export class APIManager {
    constructor(state) {
        this.state = state;
    }

    // 초기 데이터 로드
    async loadInitialData() {
        try {
            const [countries, topics, models] = await Promise.all([
                window.api.getCountries(),
                window.api.getTopics(),
                window.api.getModels() // 초기에는 모든 모델 로드
            ]);

            return { countries, topics, models };
        } catch (error) {
            console.error('Failed to load initial data:', error);
            throw error;
        }
    }

    // 국가-토픽에 따른 모델 로드
    async loadModelsForCountryTopic(country, topic) {
        try {
            return await window.api.getModels(country, topic);
        } catch (error) {
            console.error('Failed to load models for country/topic:', error);
            return [];
        }
    }

    // 예시 질문 및 소스 로드
    async loadExamplesAndSources(country, topic) {
        if (!country || !topic) {
            return {
                exampleQuestions: [],
                documentSources: []
            };
        }

        try {
            const [examplesResponse, sourcesResponse] = await Promise.all([
                window.api.getExamples(country, topic),
                window.api.getDocumentSources(country, topic)
            ]);

            const exampleQuestions = (examplesResponse.examples || []).map(q => ({
                q: q,
                a: "이 질문에 대한 답변을 준비해드릴게요!"
            }));

            const documentSources = sourcesResponse || [];

            return { exampleQuestions, documentSources };
        } catch (error) {
            console.error('Failed to load examples and sources:', error);
            return {
                exampleQuestions: [],
                documentSources: []
            };
        }
    }

    // 대화 생성
    async createConversation(sessionId, country, topic, model) {
        try {
            return await window.api.createConversation(sessionId, country, topic, model);
        } catch (error) {
            console.error('Failed to create conversation:', error);
            throw error;
        }
    }

    // 메시지 전송
    async sendMessage(text, conversationId, sessionId, country, topic, model, stream = false) {
        try {
            return await window.api.sendMessage(
                text,
                conversationId,
                sessionId,
                country,
                topic,
                model,
                stream
            );
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    }
}
