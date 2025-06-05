# Ready To Go - 여행 정보 챗봇 (바닐라 JavaScript 버전)

여행 정보를 제공하는 AI 챗봇 웹 애플리케이션입니다. Django 백엔드와 연동하여 다양한 국가의 비자, 보험, 안전, 입국규정 정보를 제공합니다.

## 🚀 기능

- **다국가 여행 정보**: 미국, 일본, 호주 등 주요 여행 국가 정보
- **다양한 토픽**: 비자, 보험, 안전, 입국규정 관련 정보
- **AI 모델 선택**: GPT-4, Claude, Gemini 등 다양한 LLM 모델 지원
- **실시간 채팅**: 자연스러운 대화형 인터페이스
- **FAQ 시스템**: 자주 묻는 질문 카드로 빠른 정보 접근
- **문서 참조**: 신뢰할 수 있는 출처 정보 제공
- **반응형 디자인**: 모바일과 데스크톱 모두 최적화

## 🛠 기술 스택

- **Frontend**: 바닐라 JavaScript (ES6+)
- **스타일링**: Tailwind CSS
- **백엔드**: Django (별도 저장소)
- **API 통신**: Fetch API
- **빌드 도구**: 없음 (순수 HTML/CSS/JS)

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
cd /Users/comet39/SKN_PJT/3rd_project_v2/frontend/travel-bot-vanilla
```

### 2. 백엔드 서버 실행
Django 백엔드 서버가 실행되어 있어야 합니다:
```bash
cd /Users/comet39/SKN_PJT/SKN11-4rd-6Team/Ready_To_Go/backend_django
python manage.py runserver
```

### 3. 프론트엔드 실행
로컬 서버를 실행합니다:

#### Python 서버 사용
```bash
python -m http.server 8080
```

#### Node.js serve 사용
```bash
npx serve . -p 8080
```

#### Live Server (VS Code Extension) 사용
VS Code에서 `index.html`을 열고 Live Server 실행

### 4. 브라우저에서 접속
```
http://localhost:8080
```

## 🔧 설정

### API 엔드포인트 변경
`js/api.js` 파일에서 백엔드 서버 URL을 변경할 수 있습니다:

```javascript
constructor() {
    this.baseURL = 'http://localhost:8000/api';  // Django 서버 주소
}
```

### CORS 설정
Django 백엔드에서 CORS 설정이 필요합니다:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

## 📁 프로젝트 구조

```
travel-bot-vanilla/
├── index.html              # 메인 HTML 파일
├── css/
│   └── style.css           # 커스텀 스타일
├── js/
│   ├── api.js              # API 통신 모듈
│   └── app.js              # 메인 애플리케이션 로직
├── assets/
│   └── mascot.png          # 마스코트 이미지
└── README.md               # 프로젝트 문서
```

## 🎮 사용법

1. **국가 선택**: 사이드바에서 여행하고자 하는 국가를 선택
2. **토픽 선택**: 관심 있는 정보 카테고리 선택 (비자, 보험, 안전, 입국규정)
3. **모델 선택**: 사용할 AI 모델 선택
4. **새 대화 시작**: "새 대화" 버튼을 클릭하여 채팅 시작
5. **질문하기**: 텍스트 입력 또는 FAQ 카드 클릭으로 질문
6. **참고 문서**: 답변 하단의 "참고 문서" 링크로 출처 확인

## 🔌 API 엔드포인트

### 메타데이터
- `GET /api/countries/` - 지원 국가 목록
- `GET /api/topics/` - 지원 토픽 목록
- `GET /api/sources/` - 문서 출처 목록

### 채팅
- `POST /api/chat/conversation/` - 새 대화 생성
- `POST /api/chat/message/` - 메시지 전송
- `GET /api/chat/history/{id}/` - 대화 히스토리
- `GET /api/chat/examples/` - 예시 질문
- `GET /api/chat/settings/models/` - 사용 가능한 모델
- `GET /api/chat/sources/` - 문서 출처

### 문서
- `GET /api/documents/` - 문서 목록
- `GET /api/documents/{id}/` - 특정 문서
- `GET /api/documents/search/` - 문서 검색

## 🎨 커스터마이징

### 색상 테마 변경
`css/style.css`에서 CSS 변수를 수정하여 색상 테마를 변경할 수 있습니다:

```css
:root {
    --primary: hsl(199, 89%, 48%);    /* 메인 색상 */
    --secondary: hsl(12, 60%, 65%);   /* 보조 색상 */
    --accent: hsl(165, 60%, 50%);     /* 강조 색상 */
}
```

### 기본 FAQ 수정
`js/api.js`의 `getDefaultFAQs()` 메서드에서 기본 FAQ를 수정할 수 있습니다.

### 애니메이션 효과
`css/style.css`에서 다양한 애니메이션 효과를 커스터마이징할 수 있습니다.

## 🔍 주요 기능 설명

### 1. 상태 관리
바닐라 JavaScript로 구현된 간단한 상태 관리 시스템:
```javascript
this.state = {
    country: "America",
    topic: "visa",
    model: "gpt-3.5-turbo",
    chatList: [],
    activeChat: null,
    // ...
};
```

### 2. API 통신
Fetch API를 사용한 RESTful API 통신:
```javascript
async request(url, options = {}) {
    const response = await fetch(`${this.baseURL}${url}`, config);
    return await response.json();
}
```

### 3. 반응형 UI
Tailwind CSS를 활용한 반응형 디자인과 인터랙티브 요소들

### 4. 오프라인 모드
서버 연결 실패 시 기본 FAQ와 오프라인 모드로 동작

## 🚨 문제 해결

### CORS 오류
```javascript
// Django settings.py에 추가
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

### 이미지가 표시되지 않는 경우
`assets/` 폴더에 `mascot.png` 파일이 있는지 확인하세요.

### API 연결 실패
1. Django 서버가 실행 중인지 확인
2. `js/api.js`의 `baseURL`이 올바른지 확인
3. 브라우저 개발자 도구에서 네트워크 탭 확인

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해 주세요.

---

**Ready To Go** - 스마트한 여행 정보를 위한 AI 챗봇 🌍✈️