import json
import logging
from django.http import StreamingResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Conversation, Message, FAQ, Document
from core.serializers import (
    ConversationCreateSerializer, 
    ChatRequestSerializer
)
from ai_services.rag import RAG
from ai_services.llm import LLM

logger = logging.getLogger(__name__)

# AI 서비스 인스턴스 (전역으로 한 번만 생성)
rag = RAG()
llm = LLM()

@api_view(['POST'])
def create_conversation(request):
    """새 대화 세션 시작"""

@api_view(['POST'])
def process_message(request):
    """사용자 메시지 처리"""
    # 1. 대화 가져오기 또는 생성
    # 2. 사용자 메시지 저장
    # 3. 이전 메시지 히스토리 가져오기
    # 4. 국가/토픽 지정
    # 5. RAG 검색
    # 6. LLM 응답 생성
    # 7. 응답 저장
    # 8. 최종 return

@api_view(['GET'])
def get_conversation_history(request, conversation_id):
    """대화 기록 조회"""

@api_view(['GET'])
def get_available_models(request):
    """사용 가능한 LLM 모델 목록 반환"""

@api_view(['GET'])
def get_example_questions(request):
    """예시 질문(자주하는 질문) 반환"""

@api_view(['GET'])
def get_document_sources(request):
    """선택된 국가/토픽의 문서 출처 URL 반환"""
