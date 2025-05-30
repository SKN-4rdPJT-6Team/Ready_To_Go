from django.core.management.base import BaseCommand
from django.db import connection
import pymysql
from core.models import Document, Conversation, Message, FAQ
import json

class Command(BaseCommand):
    help = 'FastAPI 데이터를 Django로 마이그레이션합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-db',
            type=str,
            help='원본 데이터베이스 연결 문자열 (mysql://user:pass@host/db)',
            required=True
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 마이그레이션 없이 테스트만 실행',
        )

    def handle(self, *args, **options):
        self.stdout.write('FastAPI 데이터 마이그레이션을 시작합니다...')
        
        # 원본 DB 연결
        source_db_url = options['source_db']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN 모드로 실행합니다.'))
        
        try:
            # URL 파싱 (예: mysql://user:pass@host/db)
            if not source_db_url.startswith('mysql://'):
                raise ValueError("MySQL 연결 문자열이 필요합니다: mysql://user:pass@host/db")
            
            # 간단한 URL 파싱
            url_parts = source_db_url.replace('mysql://', '').split('/')
            if len(url_parts) != 2:
                raise ValueError("잘못된 데이터베이스 URL 형식")
            
            auth_host, db_name = url_parts
            if '@' not in auth_host:
                raise ValueError("인증 정보가 없습니다")
            
            auth, host = auth_host.split('@')
            user, password = auth.split(':')
            
            # 원본 DB 연결
            source_conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=db_name,
                charset='utf8mb4'
            )
            
            self.stdout.write('원본 데이터베이스에 연결되었습니다.')
            
            # 마이그레이션 실행
            self.migrate_documents(source_conn, dry_run)
            self.migrate_conversations(source_conn, dry_run)
            self.migrate_messages(source_conn, dry_run)
            self.migrate_faqs(source_conn, dry_run)
            
            source_conn.close()
            
            self.stdout.write(
                self.style.SUCCESS('마이그레이션이 완료되었습니다!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'마이그레이션 중 오류 발생: {str(e)}')
            )

    def migrate_documents(self, source_conn, dry_run):
        """문서 마이그레이션"""
        self.stdout.write('문서 데이터를 마이그레이션합니다...')
        
        with source_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents")
            documents = cursor.fetchall()
            
            # 컬럼 정보 가져오기
            cursor.execute("DESCRIBE documents")
            columns = [col[0] for col in cursor.fetchall()]
            
            count = 0
            for doc_row in documents:
                doc_dict = dict(zip(columns, doc_row))
                
                if not dry_run:
                    Document.objects.get_or_create(
                        title=doc_dict.get('title', ''),
                        defaults={
                            'url': doc_dict.get('url', ''),
                            'country': doc_dict.get('country', ''),
                            'topic': doc_dict.get('topic', ''),
                            'source': doc_dict.get('source', ''),
                        }
                    )
                count += 1
                
        self.stdout.write(f'문서 {count}개 마이그레이션 완료')

    def migrate_conversations(self, source_conn, dry_run):
        """대화 마이그레이션"""
        self.stdout.write('대화 데이터를 마이그레이션합니다...')
        
        with source_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM conversations")
            conversations = cursor.fetchall()
            
            cursor.execute("DESCRIBE conversations")
            columns = [col[0] for col in cursor.fetchall()]
            
            count = 0
            for conv_row in conversations:
                conv_dict = dict(zip(columns, conv_row))
                
                if not dry_run:
                    Conversation.objects.get_or_create(
                        id=conv_dict.get('id'),
                        defaults={
                            'session_id': conv_dict.get('session_id', ''),
                            'country': conv_dict.get('country', ''),
                            'topic': conv_dict.get('topic', ''),
                        }
                    )
                count += 1
                
        self.stdout.write(f'대화 {count}개 마이그레이션 완료')

    def migrate_messages(self, source_conn, dry_run):
        """메시지 마이그레이션"""
        self.stdout.write('메시지 데이터를 마이그레이션합니다...')
        
        with source_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM messages")
            messages = cursor.fetchall()
            
            cursor.execute("DESCRIBE messages")
            columns = [col[0] for col in cursor.fetchall()]
            
            count = 0
            for msg_row in messages:
                msg_dict = dict(zip(columns, msg_row))
                
                if not dry_run:
                    try:
                        conversation = Conversation.objects.get(
                            id=msg_dict.get('conversation_id')
                        )
                        Message.objects.get_or_create(
                            id=msg_dict.get('id'),
                            defaults={
                                'conversation': conversation,
                                'role': msg_dict.get('role', 'user'),
                                'content': msg_dict.get('content', ''),
                                'references': msg_dict.get('references', ''),
                            }
                        )
                    except Conversation.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'대화 ID {msg_dict.get("conversation_id")} 없음, 메시지 건너뜀'
                            )
                        )
                        continue
                count += 1
                
        self.stdout.write(f'메시지 {count}개 마이그레이션 완료')

    def migrate_faqs(self, source_conn, dry_run):
        """FAQ 마이그레이션"""
        self.stdout.write('FAQ 데이터를 마이그레이션합니다...')
        
        with source_conn.cursor() as cursor:
            # FAQ 테이블이 존재하는지 확인
            cursor.execute("SHOW TABLES LIKE 'faqs'")
            if not cursor.fetchone():
                self.stdout.write('FAQ 테이블이 존재하지 않습니다. 건너뜁니다.')
                return
            
            cursor.execute("SELECT * FROM faqs")
            faqs = cursor.fetchall()
            
            cursor.execute("DESCRIBE faqs")
            columns = [col[0] for col in cursor.fetchall()]
            
            count = 0
            for faq_row in faqs:
                faq_dict = dict(zip(columns, faq_row))
                
                if not dry_run:
                    FAQ.objects.get_or_create(
                        question=faq_dict.get('question', ''),
                        defaults={
                            'country': faq_dict.get('country', ''),
                            'topic': faq_dict.get('topic', ''),
                        }
                    )
                count += 1
                
        self.stdout.write(f'FAQ {count}개 마이그레이션 완료')
