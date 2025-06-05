from django.db import models

class BaseModel(models.Model):
    """기본 모델 클래스"""
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class Document(BaseModel):
    """문서 정보 및 벡터 메타데이터"""
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=500, null=True, blank=True)
    
    country = models.CharField(max_length=100, db_index=True)  # Australia, Canada, France
    topic = models.CharField(max_length=100, db_index=True)    # visa, insurance, immigration
    source = models.CharField(max_length=200, null=True, blank=True)  # 출처 정보
    
    class Meta:
        db_table = 'documents'
        
    def __str__(self):
        return f"{self.country} - {self.topic}: {self.title}"

class Conversation(BaseModel):
    """대화 세션"""
    session_id = models.CharField(max_length=100, db_index=True)
    
    # 선택적 필터
    country = models.CharField(max_length=100, null=True, blank=True)
    topic = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'conversations'
        
    def __str__(self):
        return f"Session {self.session_id} - {self.country}/{self.topic}"

class Message(BaseModel):
    """채팅 메시지"""
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20)  # user, assistant
    content = models.TextField()
    
    # RAG 참조 (JSON 형태로 저장)
    references = models.TextField(null=True, blank=True)  # JSON string
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

class FAQ(BaseModel):
    """FAQ"""
    question = models.TextField()  # 질문 내용
    country = models.CharField(max_length=100, db_index=True)  # 국가 (영문명)
    topic = models.CharField(max_length=100, db_index=True)    # 토픽 (visa, insurance 등)
    
    class Meta:
        db_table = 'faqs'
        
    def __str__(self):
        return f"{self.country} - {self.topic}: {self.question[:50]}..."

# 자주 사용하는 값들
COUNTRIES = [
    {"emoji": "🇺🇸", "name_kr": "미국", "name_en": "America"},
    {"emoji": "🇨🇳", "name_kr": "중국", "name_en": "China"},
    {"emoji": "🇯🇵", "name_kr": "일본", "name_en": "Japan"},
    {"emoji": "🇨🇦", "name_kr": "캐나다", "name_en": "Canada"},
    {"emoji": "🇦🇺", "name_kr": "호주", "name_en": "Australia"},
    {"emoji": "🇩🇪", "name_kr": "독일", "name_en": "Germany"},
    {"emoji": "🇻🇳", "name_kr": "베트남", "name_en": "Vietnam"},
    {"emoji": "🇵🇭", "name_kr": "필리핀", "name_en": "Philippines"},
    {"emoji": "🇮🇩", "name_kr": "인도네시아", "name_en": "Indonesia"},
    {"emoji": "🇹🇭", "name_kr": "태국", "name_en": "Thailand"},
    {"emoji": "🇬🇧", "name_kr": "영국", "name_en": "UK"},
    {"emoji": "🇸🇬", "name_kr": "싱가포르", "name_en": "Singapore"},
    {"emoji": "🇲🇾", "name_kr": "말레이시아", "name_en": "Malaysia"},
    {"emoji": "🇪🇸", "name_kr": "스페인", "name_en": "Spain"},
    {"emoji": "🇳🇿", "name_kr": "뉴질랜드", "name_en": "New Zealand"},
    {"emoji": "🇷🇺", "name_kr": "러시아", "name_en": "Russia"},
    {"emoji": "🇫🇷", "name_kr": "프랑스", "name_en": "France"},
    {"emoji": "🇮🇹", "name_kr": "이탈리아", "name_en": "Italy"},
    {"emoji": "🇦🇹", "name_kr": "오스트리아", "name_en": "Austria"},
    {"emoji": "🇭🇰", "name_kr": "홍콩", "name_en": "Hong Kong"}
]

TOPICS = ["visa", "insurance", "immigration_safety", "immigration_regulations"]
SOURCES = ["Government", "Embassy", "Immigration Department"]
