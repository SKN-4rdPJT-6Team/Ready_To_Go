import logging
import json
import asyncio
from django.db.models import F
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import Conversation, Message, FAQ, Document
from ai_services.llm import LLM
from ai_services.rag import RAG

logger = logging.getLogger(__name__)

# LLM과 RAG 인스턴스 생성 (싱글톤)
llm_instance = None
rag_instance = None

def get_llm():
    global llm_instance
    if llm_instance is None:
        llm_instance = LLM()
    return llm_instance

def get_rag():
    global rag_instance
    if rag_instance is None:
        rag_instance = RAG()
    return rag_instance

@api_view(['POST'])
@csrf_exempt
def create_conversation(request):
    """새 대화 세션 시작"""
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        session_id = data.get('session_id')
        country_id = data.get('country_id')
        topic_id = data.get('topic_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = Conversation.objects.create(
            session_id=session_id,
            country=country_id,
            topic=topic_id
        )
        
        return Response({
            'id': conversation.id,
            'session_id': conversation.session_id,
            'country': conversation.country,
            'topic': conversation.topic,
            'created_at': conversation.created_at
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return Response(
            {'error': 'Failed to create conversation'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@csrf_exempt
def process_message(request):
    """사용자 메시지 처리"""
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        message_content = data.get('message')
        if not message_content:
            return Response(
                {'error': 'message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 대화 가져오기 또는 생성
        conversation_id = data.get('conversation_id')
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {'error': f'Conversation {conversation_id} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = Conversation.objects.create(
                session_id=data.get('session_id', f'session_{conversation_id}'),
                country=data.get('country'),
                topic=data.get('topic')
            )
        
        # 사용자 메시지 저장
        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=message_content
        )
        
        # 이전 메시지들 가져오기 (현재 메시지 제외)
        previous_messages = conversation.messages.exclude(
            id=user_message.id
        ).order_by('created_at')
        
        history = [
            {"role": m.role, "content": m.content}
            for m in previous_messages
        ]
        
        # 디버그: 히스토리 확인
        logger.info(f"Conversation {conversation.id} history: {len(history)} messages")
        
        country = data.get('country') or conversation.country
        if country:
            country = country.replace(" ", "").lower()
        
        topic = data.get('topic') or conversation.topic
        if topic:
            if topic == "immigration":
                topic = "immigration_regulations_info"
            elif topic == "safety":
                topic = "immigration_safety_info"
            else:
                topic = topic + "_info"
        
        # RAG 인스턴스 가져오기
        rag = get_rag()
        
        # RAG 검색 (번역 포함)
        context, references = rag.search_with_translation(
            query=message_content,
            country=country,
            doc_type=topic
        )
        
        # RAG 검색 결과 로그
        logger.info(f"RAG search country: {country}, topic: {topic}")
        logger.info(f"RAG context length: {len(context) if context else 0}")
        logger.info(f"References found: {len(references) if references else 0}")
        
        # LLM 응답 생성 (번역 포함)
        model_id = data.get('model_id')
        llm = get_llm()
        
        if model_id:
            llm_with_model = LLM(model_name=model_id)
            response_text = asyncio.run(llm_with_model.generate_with_translation(
                query=message_content,
                context=context,
                references=references,
                history=history,
                translate_to_korean=True
            ))
        else:
            response_text = asyncio.run(llm.generate_with_translation(
                query=message_content,
                context=context,
                references=references,
                history=history,
                translate_to_korean=True
            ))
        
        # 응답 길이 로그
        logger.info(f"Generated response length: {len(response_text) if response_text else 0}")
        
        # 응답 저장
        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=response_text,
            references=json.dumps(references) if references else None
        )
        
        return Response({
            'message': {
                'id': assistant_message.id,
                'conversation_id': conversation.id,
                'role': assistant_message.role,
                'content': assistant_message.content,
                'references': references,
                'created_at': assistant_message.created_at
            },
            'conversation_id': conversation.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return Response(
            {'error': 'Failed to process message'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_conversation_history(request, conversation_id):
    """대화 기록 조회"""
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.all().order_by('created_at')
        
        message_data = []
        for message in messages:
            references = None
            if message.references:
                try:
                    references = json.loads(message.references)
                except json.JSONDecodeError:
                    references = None
            
            message_data.append({
                'id': message.id,
                'role': message.role,
                'content': message.content,
                'references': references,
                'created_at': message.created_at
            })
        
        return Response({
            'conversation_id': conversation.id,
            'messages': message_data
        }, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        logger.error(f"Conversation {conversation_id} not found")
        return Response(
            {'error': 'Conversation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}")
        return Response(
            {'error': 'Failed to fetch conversation history'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_available_models(request):
    """사용 가능한 LLM 모델 목록"""
    try:
        models = [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
            {"id": "phi-2", "name": "Phi-2 (Fine-Tuned)"}
        ]
        
        # LLM 인스턴스에서 모델 목록을 가져올 수 있다면 사용
        llm = get_llm()
        if hasattr(llm, "get_model_list"):
            try:
                models = llm.get_model_list()
            except Exception as e:
                logger.warning(f"Failed to get models from LLM instance: {e}")
        
        return Response(models, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching available models: {e}")
        return Response(
            {'error': 'Failed to fetch available models'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_example_questions(request):
    """예시 질문 반환"""
    try:
        country = request.GET.get('country')
        topic = request.GET.get('topic')
        
        # DB에서 예시 질문 가져오기
        queryset = FAQ.objects.all()
        
        # 필터 적용
        if country:
            queryset = queryset.filter(country__iexact=country)
        if topic:
            if topic == "safety":
                topic = "immigration_safety"
            queryset = queryset.filter(topic__iexact=topic)
            
        # 생성일 기준 정렬 및 가져오기
        questions = queryset.order_by('-created_at')[:5]
        
        examples = [q.question for q in questions] if questions else []
        
        # 기본 예시 질문 (DB에 데이터가 없는 경우)
        if not examples:
            default_examples = {
                "america": {
                    "visa": [
                        "미국 관광비자 신청 방법이 궁금해요",
                        "ESTA와 일반 비자의 차이점이 뭔가요?",
                        "미국 비자 면접 준비사항을 알려주세요"
                    ],
                    "insurance": [
                        "미국 여행보험 추천해주세요",
                        "미국 의료비는 얼마나 비싼가요?",
                        "여행보험 없이 미국 갔다가 아프면 어떡하나요?"
                    ]
                },
                "japan": {
                    "visa": [
                        "일본 무비자 입국 조건이 뭔가요?",
                        "일본 단기체류 비자 신청 방법을 알려주세요"
                    ],
                    "insurance": [
                        "일본 여행보험이 필요한가요?",
                        "일본 여행 중 병원 이용법을 알려주세요"
                    ]
                }
            }
            
            if country and topic:
                examples = default_examples.get(country.lower(), {}).get(topic.lower(), [])
        
        return Response({
            'examples': examples
        }, status=status.HTTP_200_OK)
                
    except Exception as e:
        logger.error(f"Error fetching example questions: {e}")
        return Response(
            {'error': 'Failed to fetch example questions'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def get_document_sources(request):
    """선택된 국가/토픽의 문서 출처 URL 반환"""
    try:
        country = request.GET.get('country')
        topic = request.GET.get('topic')
        
        # DB에서 문서 가져오기
        queryset = Document.objects.exclude(url__isnull=True).exclude(url='')
        
        # 필터 적용
        if country:
            queryset = queryset.filter(country__iexact=country)
        if topic:
            queryset = queryset.filter(topic__iexact=topic)
            
        # URL 리스트 반환 (중복 제거)
        urls = list(set(queryset.values_list('url', flat=True)))
        
        return Response({
            'sources': urls
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error fetching document sources: {e}")
        return Response(
            {'error': 'Failed to fetch document sources'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )