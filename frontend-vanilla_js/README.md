# 프론트엔드 아키텍쳐

## 프로젝트 구조

```
frontend-vanilla_js/
├── index.html                 # 메인 HTML (UI 레이아웃)
├── css/
│   └── style.css             # 커스텀 스타일 & 애니메이션
├── js/
│   ├── app.js                # 메인 애플리케이션 (진입점)
│   └── modules/              # 기능별 모듈
│       ├── state.js          # 상태 관리
│       ├── dom.js            # DOM 조작
│       ├── api.js            # API 통신
│       ├── chat.js           # 채팅 관리
│       └── ui.js             # UI 렌더링
├── assets/
│   └── mascot.png            # 마스코트 이미지
└── package.json              # 프로젝트 설정
```

### **1. index.html - 화면 뼈대**

- 전체 화면 구조를 정함 (사이드바 + 메인 대화 화면)
- ui/ux 스타일을 위한 **TailwindCSS** 설정
- 사용자가 선택할 수 있는 **드롭다운 메뉴**와 **입력창**
- **채팅창**, **FAQ 카드**, **출처 모달 창** 자리 배치

### **2. js/app.js - 앱의 시작점 & 중심**

- 웹앱을 처음 실행할 때 필요한 것들을 준비
- 각각의 기능(모듈)을 불러와서 함께 작동하도록 연결
- 버튼 클릭, 폼 제출, 드롭다운 선택 같은 **사용자 행동을 감지하고 처리**

### **3. js/modules/state.js - 상태 저장소**

- 전체 앱에서 공유하는 중요한 정보(상태)를 저장
    
    예: 지금까지의 채팅 내용, 선택한 국가/토픽/모델
    
- 값을 쉽게 가져오고 바꿀 수 있도록 `get`, `set` 함수 제공

### **4. js/modules/dom.js - 화면 요소 조작**

- HTML에서 버튼, 입력창 등 **요소를 쉽게 찾고 저장**
- 자주 쓰는 화면 조작 함수 모음
    
    예:
    
    - `show()` / `hide()` → 보이게 하거나 숨기기
    - `clear()` → 내용을 지우기
    - `scrollToBottom()` → 채팅창을 맨 아래로 내리기
    - `populateSelect()` → 드롭다운 메뉴 채우기

### **5. js/modules/api.js - 백엔드와 통신**

- Django 서버에 요청을 보내고, 데이터를 받아옴
    
    예:
    
    - 국가, 주제, 모델 목록 불러오기
    - 메시지 보내고, 답변 받기
    - FAQ 예시와 참고 자료 가져오기
- 각각의 API 요청을 **간단한 함수로 정리**해둠

### **6. js/modules/chat.js - 채팅 기능**

- 새 채팅을 생성, 기존 채팅을 기록
- 서버로 메시지를 보내고, 응답을 받아서 처리

### **7. js/modules/ui.js - 실제 화면에 보여주기(**UI 렌더링**)**

- 채팅 메시지나 FAQ 카드처럼 **동적으로 생기는 요소들을 화면에 표시**

---

## 워크 플로우

1. 사용자가 "새 대화" 버튼 클릭
2. 국가/토픽/모델 선택
3. 백엔드에 대화 세션 생성 요청
4. 새 채팅 객체 생성 및 상태 저장
5. UI 업데이트 (채팅 리스트, 활성화)
6. 입력 인터페이스 활성화
7. UI에 사용자 메시지 입력 및 전송
8. 백엔드로 메시지 전송
9. AI 응답 수신 및 응답 UI 보여주기

### 1. **초기화**

```jsx
// 1. DOM 로드 완료 시 앱 시작
document.addEventListener('DOMContentLoaded', () => {
    window.travelBotApp = new TravelBotApp();
});

// 2. 모듈들 인스턴스화
constructor() {
    this.state = new AppState();// 상태 관리
    this.dom = new DOMManager();// DOM 조작
    this.api = new APIManager();// API 통신
    this.chat = new ChatManager();// 채팅 관리
    this.ui = new UIRenderer();// UI 렌더링
    this.init();// 초기화 실행
}

// 3. 초기 데이터 로딩
async init() {
    this.bindEvents();// 이벤트 바인딩
    await this.loadInitialData();// API 데이터 로드
    this.ui.updateInterface();// UI 초기 상태 설정
}
```

### 2. **채팅 플로우**

```jsx
// 1. 새 대화 시작
newChatBtn.click() → chat.createNew() → api.createConversation() → state.addChat()

// 2. 메시지 전송
sendBtn.click() → chat.sendMessage() → api.sendMessage() → ui.renderChat()

// 3. FAQ 클릭
faqCard.click() → messageInput.value = question → sendMessage()
```

### 3. **상태 동기화**

```
// 상태 변경 시 UI 자동 업데이트
state.set('activeChat', chatId);
ui.renderChatList();// 채팅 목록 업데이트
ui.renderChat();// 채팅 내용 업데이트
ui.updateInterface();// 버튼 상태 등 업데이트
```

---

## 실행
```bash
python -m http.server 8080
```
