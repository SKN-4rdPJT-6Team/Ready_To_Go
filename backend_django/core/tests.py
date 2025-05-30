from django.test import TestCase, Client
from django.urls import reverse
from core.models import Document, Conversation, Message
import json

class CoreModelTestCase(TestCase):
    """핵심 모델 테스트"""
    
    def setUp(self):
        self.document = Document.objects.create(
            title="Test Document",
            country="test_country",
            topic="test_topic",
            url="https://example.com"
        )
        
        self.conversation = Conversation.objects.create(
            session_id="test_session",
            country="test_country",
            topic="test_topic"
        )

    def test_document_creation(self):
        """문서 생성 테스트"""
        self.assertEqual(self.document.title, "Test Document")
        self.assertEqual(self.document.country, "test_country")
        
    def test_conversation_creation(self):
        """대화 생성 테스트"""
        self.assertEqual(self.conversation.session_id, "test_session")
        
    def test_message_creation(self):
        """메시지 생성 테스트"""
        message = Message.objects.create(
            conversation=self.conversation,
            role="user",
            content="Test message"
        )
        self.assertEqual(message.content, "Test message")
        self.assertEqual(message.conversation, self.conversation)

class APITestCase(TestCase):
    """API 엔드포인트 테스트"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_app_info(self):
        """앱 정보 엔드포인트 테스트"""
        response = self.client.get(reverse('app_info'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('name', data)
        self.assertIn('version', data)
    
    def test_countries_endpoint(self):
        """국가 목록 엔드포인트 테스트"""
        response = self.client.get(reverse('countries'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

class ChatAPITestCase(TestCase):
    """채팅 API 테스트"""
    
    def setUp(self):
        self.client = Client()
        self.conversation_data = {
            'session_id': 'test_session',
            'country_id': 'test_country',
            'topic_id': 'test_topic'
        }
    
    def test_create_conversation(self):
        """대화 생성 API 테스트"""
        response = self.client.post(
            reverse('create_conversation'),
            data=json.dumps(self.conversation_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('id', data)
        self.assertEqual(data['session_id'], 'test_session')
    
    def test_get_available_models(self):
        """사용 가능한 모델 목록 API 테스트"""
        response = self.client.get(reverse('get_available_models'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        # 기본 모델들이 포함되어 있는지 확인
        model_ids = [model['id'] for model in data]
        self.assertIn('gpt-3.5-turbo', model_ids)
    
    def test_get_conversation_history(self):
        """대화 기록 조회 테스트"""
        # 테스트용 대화 생성
        conversation = Conversation.objects.create(
            session_id="test_session_2",
            country="australia",
            topic="visa"
        )
        
        # 테스트용 메시지 생성
        Message.objects.create(
            conversation=conversation,
            role="user",
            content="Test question"
        )
        
        response = self.client.get(
            reverse('get_conversation_history', args=[conversation.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['content'], "Test question")

class DocumentAPITestCase(TestCase):
    """문서 API 테스트"""
    
    def setUp(self):
        self.client = Client()
        self.document = Document.objects.create(
            title="Test Document",
            country="australia",
            topic="visa",
            url="https://example.com"
        )
    
    def test_list_documents(self):
        """문서 목록 API 테스트"""
        response = self.client.get(reverse('list_documents'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 1)
    
    def test_get_document(self):
        """문서 상세 API 테스트"""
        response = self.client.get(
            reverse('get_document', args=[self.document.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], "Test Document")
    
    def test_upload_document(self):
        """문서 업로드 API 테스트"""
        document_data = {
            'title': 'New Document',
            'country': 'canada',
            'topic': 'insurance',
            'url': 'https://newdoc.com'
        }
        response = self.client.post(
            reverse('upload_document'),
            data=json.dumps(document_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], 'New Document')
