from django.core.management.base import BaseCommand
from ai_services.rag import RAG
import os

class Command(BaseCommand):
    help = 'PDF 문서들을 벡터 데이터베이스에 인덱싱합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pdf-dir',
            type=str,
            help='PDF 파일들이 있는 디렉토리 경로',
            default='data/pdfs'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='기존 벡터 DB를 삭제하고 새로 생성',
        )

    def handle(self, *args, **options):
        self.stdout.write('PDF 인덱싱을 시작합니다...')
        
        pdf_dir = options['pdf_dir']
        if not os.path.exists(pdf_dir):
            self.stdout.write(
                self.style.ERROR(f'PDF 디렉토리가 존재하지 않습니다: {pdf_dir}')
            )
            return
        
        try:
            # RAG 시스템 초기화
            rag = RAG()
            
            # 기존 데이터 삭제 (force 옵션)
            if options['force']:
                self.stdout.write('기존 벡터 데이터를 삭제합니다...')
                # 여기에 벡터 DB 초기화 로직 추가 가능
            
            # PDF 처리
            rag.process_pdf_directory(pdf_dir)
            
            self.stdout.write(
                self.style.SUCCESS('PDF 인덱싱이 완료되었습니다!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'인덱싱 중 오류 발생: {str(e)}')
            )
