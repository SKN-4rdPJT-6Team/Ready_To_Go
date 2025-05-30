#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

def copy_fastapi_data():
    """FastAPI 데이터를 Django 프로젝트로 복사"""
    
    # 경로 설정
    fastapi_dir = Path("/Users/comet39/SKN_PJT/SKN11-3rd-6Team/backend_v1")
    django_dir = Path("/Users/comet39/SKN_PJT/SKN11-3rd-6Team/backend_django")
    
    print("FastAPI 데이터를 Django 프로젝트로 복사합니다...")
    
    # PDF 파일들 복사
    fastapi_pdfs = fastapi_dir / "data" / "pdfs"
    django_pdfs = django_dir / "data" / "pdfs"
    
    if fastapi_pdfs.exists():
        print("PDF 파일들을 복사합니다...")
        try:
            # PDF 파일들을 하나씩 복사
            copied_count = 0
            for pdf_file in fastapi_pdfs.glob("*.pdf"):
                shutil.copy2(pdf_file, django_pdfs / pdf_file.name)
                print(f"  복사됨: {pdf_file.name}")
                copied_count += 1
            print(f"PDF 파일 복사 완료: {copied_count}개 파일")
        except Exception as e:
            print(f"PDF 파일 복사 중 오류: {e}")
    else:
        print(f"경고: PDF 디렉토리를 찾을 수 없습니다: {fastapi_pdfs}")
    
    # 벡터 DB 복사 (선택사항)
    fastapi_vectors = fastapi_dir / "data" / "vectors"
    django_vectors = django_dir / "data" / "vectors"
    
    if fastapi_vectors.exists():
        print("벡터 데이터베이스를 복사합니다...")
        try:
            for item in fastapi_vectors.iterdir():
                if item.is_file():
                    shutil.copy2(item, django_vectors / item.name)
                elif item.is_dir():
                    shutil.copytree(item, django_vectors / item.name, dirs_exist_ok=True)
            print("벡터 DB 복사 완료")
        except Exception as e:
            print(f"벡터 DB 복사 중 오류: {e}")
    else:
        print(f"정보: 벡터 DB 디렉토리를 찾을 수 없습니다: {fastapi_vectors}")
    
    # .env 파일 백업
    fastapi_env = fastapi_dir / ".env"
    if fastapi_env.exists():
        print(".env 파일을 참조용으로 백업합니다...")
        try:
            shutil.copy2(fastapi_env, django_dir / ".env.fastapi_backup")
            print("기존 .env 파일은 .env.fastapi_backup으로 복사되었습니다.")
        except Exception as e:
            print(f".env 파일 복사 중 오류: {e}")
    
    print("\n데이터 복사가 완료되었습니다!")
    print("\n다음 단계:")
    print("1. .env 파일 설정 (cp .env.example .env 후 편집)")
    print("2. pip install -r requirements.txt")
    print("3. python setup.py (초기 설정)")
    print("4. python manage.py runserver")

if __name__ == "__main__":
    copy_fastapi_data()
