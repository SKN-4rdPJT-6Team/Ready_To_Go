import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from core.models import Document
from core.serializers import DocumentSerializer

logger = logging.getLogger(__name__)

@api_view(['GET'])
def list_documents(request):
    """문서 목록 조회"""
    try:
        # 쿼리 파라미터
        country = request.GET.get('country')
        topic = request.GET.get('topic')
        source = request.GET.get('source')
        
        # 기본 쿼리셋
        queryset = Document.objects.all()
        
        # 필터 적용
        if country:
            queryset = queryset.filter(country__iexact=country)
        if topic:
            queryset = queryset.filter(topic__iexact=topic)
        if source:
            queryset = queryset.filter(source__iexact=source)
        
        # 페이지네이션 (간단한 구현)
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        documents = queryset.order_by('-created_at')[start:end]
        total_count = queryset.count()
        
        serializer = DocumentSerializer(documents, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_document(request, document_id):
    """문서 상세 조회"""
    try:
        document = Document.objects.get(id=document_id)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Document not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def upload_document(request):
    """문서 업로드"""
    try:
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()
            return Response(
                DocumentSerializer(document).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_document(request, document_id):
    """문서 삭제"""
    try:
        document = Document.objects.get(id=document_id)
        document.delete()
        return Response({'message': 'Document deleted successfully'})
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Document not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
