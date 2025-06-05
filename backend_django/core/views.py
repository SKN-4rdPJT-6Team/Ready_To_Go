from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def health_check(request):
    """헬스 체크"""
    return Response({"status": "healthy"})

@api_view(['GET'])
def app_info(request):
    """앱 정보"""
    return Response({
        "name": "Ready-To-Go Travel Assistant",
        "version": "1.0.0",
        "status": "running"
    })

@api_view(['GET'])
def countries(request):
    """지원 국가 목록"""
    try:
        from .models import COUNTRIES, Document
        
        # DB에서 실제 등록된 국가들 가져오기
        db_countries = Document.objects.values_list('country', flat=True).distinct()
        
        # 기본 국가 목록 (DB에 데이터가 없는 경우)
        default_countries = [
            "America", "Australia", "Austria", "Canada", "China", 
            "France", "Germany", "Italy", "Japan", "New Zealand", 
            "Philippines", "Singapore", "UK"
        ]
        
        # DB에 데이터가 있으면 그것을 사용, 없으면 기본값 사용
        if db_countries:
            # COUNTRIES 상수에서 일치하는 국가들만 필터링
            available_countries = []
            for country in COUNTRIES:
                if country['name_en'] in db_countries:
                    available_countries.append(country['name_en'])
            
            # 만약 매칭되는 것이 없다면 DB의 모든 국가 반환
            if not available_countries:
                available_countries = list(db_countries)
        else:
            available_countries = default_countries
        
        return Response(available_countries, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        # 오류 발생 시 기본 국가 목록 반환
        return Response([
            "America", "Australia", "Canada", "Japan", "France", 
            "Germany", "Italy", "UK", "China", "Singapore"
        ], status=status.HTTP_200_OK)

@api_view(['GET'])
def topics(request):
    """지원 주제 목록"""
    try:
        from .models import TOPICS, Document
        
        # DB에서 실제 등록된 토픽들 가져오기
        db_topics = Document.objects.values_list('topic', flat=True).distinct()
        
        # 기본 토픽 목록
        default_topics = ["visa", "insurance", "safety", "immigration"]
        
        # DB에 데이터가 있으면 그것을 사용, 없으면 기본값 사용
        if db_topics:
            # _info 접미사 제거 및 정규화
            normalized_topics = []
            for topic in db_topics:
                if topic.endswith('_info'):
                    normalized_topic = topic.replace('_info', '')
                    if normalized_topic == 'immigration_regulations':
                        normalized_topics.append('immigration')
                    elif normalized_topic == 'immigration_safety':
                        normalized_topics.append('safety')
                    else:
                        normalized_topics.append(normalized_topic)
                else:
                    normalized_topics.append(topic)
            
            available_topics = list(set(normalized_topics))
        else:
            available_topics = default_topics
        
        return Response(available_topics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching topics: {e}")
        # 오류 발생 시 기본 토픽 목록 반환
        return Response(["visa", "insurance", "safety", "immigration"], status=status.HTTP_200_OK)

@api_view(['GET'])
def sources(request):
    """문서 출처 목록"""
    try:
        from .models import Document
        
        db_sources = Document.objects.exclude(
            source__isnull=True
        ).exclude(
            source=''
        ).values_list('source', flat=True).distinct()
        
        # 기본 출처 목록 (DB에 데이터가 없는 경우)
        default_sources = ["Government", "Embassy", "Immigration Department"]
        
        sources = list(db_sources) if db_sources else default_sources
        
        return Response(sources, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        return Response(["Government", "Embassy", "Immigration Department"], status=status.HTTP_200_OK)