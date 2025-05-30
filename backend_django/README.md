# Django Backend - Ready To Go Travel Assistant

Django REST Framework 기반의 여행 정보 AI 어시스턴트 백엔드입니다.

## 주요 기능

- **AI 채팅**: OpenAI GPT, Google Gemini, Fine-tuned Flan-T5 모델 지원
- **RAG 시스템**: ChromaDB 기반 벡터 검색 및 문서 참조
- **다국어 지원**: 한국어-영어 자동 번역
- **문서 관리**: PDF 문서 처리 및 벡터화
- **국가별 정보**: 비자, 보험, 이민 정보 제공

## 프로젝트 구조 (간결화됨)

```
backend_django/
├── config/                 # Django 설정
├── core/                   # 핵심 모델 및 공통 기능
│   ├── models.py          # Document, Conversation, Message, FAQ
│   ├── admin.py           # Django Admin 설정
│   └── management/commands/  # 커스텀 관리 명령어
├── chat/                   # 채팅 기능 (통합형)
│   ├── views.py           # 모든 채팅 로직 (API + 비즈니스 로직)
│   └── urls.py            # URL 라우팅
├── documents/              # 문서 관리
├── ai_services/            # AI 서비스 (LLM, RAG)
└── data/                  # PDF 파일 & 벡터 DB
```

## 설치 및 실행

### 1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키와 데이터베이스 정보 입력
```

### 4. 데이터베이스 설정
```bash
# MySQL 데이터베이스 생성
mysql -u root -p
CREATE DATABASE RTG_V2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 빠른 시작
```bash
python quickstart.py
```

또는 수동으로:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## API 엔드포인트

### 기본 정보
- `GET /api/` - 앱 정보
- `GET /api/health/` - 헬스 체크
- `GET /api/countries/` - 지원 국가 목록
- `GET /api/topics/` - 지원 주제 목록

### 채팅
- `POST /api/chat/conversation/` - 새 대화 세션 생성
- `POST /api/chat/message/` - 메시지 전송
- `GET /api/chat/history/<conversation_id>/` - 대화 기록 조회
- `GET /api/chat/examples/` - 예시 질문
- `GET /api/chat/sources/` - 문서 출처
- `GET /api/chat/settings/models/` - 사용 가능한 모델

### 문서
- `GET /api/documents/` - 문서 목록
- `GET /api/documents/<document_id>/` - 문서 상세
- `POST /api/documents/upload/` - 문서 업로드
- `DELETE /api/documents/<document_id>/delete/` - 문서 삭제

## 환경 변수

```env
# Django 설정
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

# 데이터베이스
DB_NAME=RTG_V2
DB_USER=root
DB_PASSWORD=mysql
DB_HOST=localhost
DB_PORT=3306

# AI 서비스
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key

# 벡터 DB
VECTOR_DB_PATH=data/vectors
```

## 데이터베이스 모델

### Document
- 문서 정보 및 메타데이터
- 국가, 주제별 분류

### Conversation
- 채팅 세션 관리
- 사용자별 대화 기록

### Message
- 개별 채팅 메시지
- RAG 참조 정보 포함

### FAQ
- 자주 묻는 질문
- 국가/주제별 분류

## 기존 FastAPI에서 마이그레이션

기존 FastAPI 프로젝트의 데이터를 Django로 마이그레이션하려면:

```bash
# 데이터 복사
python copy_data.py

# FastAPI DB에서 마이그레이션 (선택사항)
python manage.py migrate_from_fastapi --source-db mysql://user:pass@host/db

# PDF 인덱싱
python manage.py index_pdfs --pdf-dir data/pdfs
```

## 개발 도구

### Django Admin
```bash
# 관리자 계정 생성
python manage.py createsuperuser

# 관리 페이지 접속: http://localhost:8000/admin/
```

### 테스트
```bash
python manage.py test
```

### 데이터베이스 관리
```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 데이터베이스 초기화
python manage.py flush
```

## 배포

### 프로덕션 설정
```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Static files
STATIC_ROOT = '/path/to/static/'
```

### Gunicorn으로 실행
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 주요 개선사항 (FastAPI 대비)

1. **더 간단한 구조**: 
   - Services와 Views 분리 없이 통합된 구조
   - 파일 수 감소로 더 직관적
2. **관리 인터페이스**: Django Admin으로 데이터 관리
3. **ORM**: Django ORM으로 더 직관적인 데이터베이스 조작
4. **미들웨어**: CORS, 보안 등 기본 제공
5. **테스트**: Django 테스트 프레임워크 활용
6. **배포**: 더 성숙한 배포 생태계

## 아키텍처 원칙

- **단순성**: 복잡한 레이어 분리 없이 필요한 기능만 구현
- **직관성**: Django의 관례를 따라 이해하기 쉬운 구조
- **유지보수성**: 적은 파일 수로 관리 부담 감소

## 라이센스

MIT License
