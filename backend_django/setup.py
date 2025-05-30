#!/usr/bin/env python
"""
Django 프로젝트 초기 설정 스크립트
"""

import os
import sys
import django
from pathlib import Path

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from core.models import Document, FAQ, COUNTRIES

def run_migrations():
    """마이그레이션 실행"""
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("Migrations completed!")

def create_superuser():
    """슈퍼유저 생성"""
    print("Creating superuser...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
    except KeyboardInterrupt:
        print("Superuser creation cancelled.")

def load_sample_data():
    """샘플 데이터 로드"""
    print("Loading sample data...")
    
    # 샘플 문서 추가
    sample_documents = [
        {
            'title': 'Australia Visa Information',
            'country': 'australia',
            'topic': 'visa',
            'url': 'https://www.homeaffairs.gov.au/trav/visa',
            'source': 'Government'
        },
        {
            'title': 'Canada Immigration Guide',
            'country': 'canada', 
            'topic': 'immigration_regulations',
            'url': 'https://www.canada.ca/en/immigration-refugees-citizenship.html',
            'source': 'Government'
        },
        {
            'title': 'Japan Travel Insurance',
            'country': 'japan',
            'topic': 'insurance',
            'url': 'https://www.jnto.go.jp/eng/',
            'source': 'Embassy'
        }
    ]
    
    for doc_data in sample_documents:
        doc, created = Document.objects.get_or_create(
            title=doc_data['title'],
            defaults=doc_data
        )
        if created:
            print(f"Created document: {doc.title}")
    
    # 샘플 FAQ 추가
    sample_faqs = [
        {
            'question': 'How do I apply for an Australian tourist visa?',
            'country': 'australia',
            'topic': 'visa'
        },
        {
            'question': 'What documents do I need for Canadian immigration?',
            'country': 'canada',
            'topic': 'immigration_regulations'
        },
        {
            'question': 'Is travel insurance mandatory for Japan?',
            'country': 'japan',
            'topic': 'insurance'
        }
    ]
    
    for faq_data in sample_faqs:
        faq, created = FAQ.objects.get_or_create(
            question=faq_data['question'],
            defaults=faq_data
        )
        if created:
            print(f"Created FAQ: {faq.question[:50]}...")
    
    print("Sample data loaded!")

def main():
    """메인 설정 함수"""
    print("Django 프로젝트 초기 설정을 시작합니다...")
    
    # 1. 마이그레이션 실행
    run_migrations()
    
    # 2. 샘플 데이터 로드
    load_sample_data()
    
    # 3. 슈퍼유저 생성 (선택사항)
    create_superuser_choice = input("슈퍼유저를 생성하시겠습니까? (y/n): ")
    if create_superuser_choice.lower() == 'y':
        create_superuser()
    
    print("\n" + "="*50)
    print("Django 프로젝트 설정이 완료되었습니다!")
    print("다음 명령어로 서버를 시작할 수 있습니다:")
    print("python manage.py runserver")
    print("="*50)

if __name__ == '__main__':
    main()
