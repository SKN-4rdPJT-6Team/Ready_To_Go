from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

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
    from .models import COUNTRIES, Document
    
    # DB에서 실제 등록된 국가들만 가져오기
    db_countries = Document.objects.values_list('country', flat=True).distinct()
    
    # 상수에서 일치하는 국가들만 필터링
    available_countries = [
        country for country in COUNTRIES 
        if country['name_en'].lower() in [c.lower() for c in db_countries]
    ]
    
    return Response(available_countries)

@api_view(['GET'])
def topics(request):
    """지원 주제 목록"""
    from .models import TOPICS, Document
    
    # DB에서 실제 등록된 토픽들만 가져오기
    db_topics = Document.objects.values_list('topic', flat=True).distinct()
    
    return Response(list(db_topics))

@api_view(['GET'])
def sources(request):
    """문서 출처 목록"""
    from .models import Document
    
    db_sources = Document.objects.values_list('source', flat=True).distinct()
    return Response([source for source in db_sources if source])

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', app_info, name='app_info'),
    path('countries/', countries, name='countries'),
    path('topics/', topics, name='topics'),
    path('sources/', sources, name='sources'),
]
