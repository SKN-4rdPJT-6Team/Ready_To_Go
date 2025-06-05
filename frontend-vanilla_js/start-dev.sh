#!/bin/bash

# Ready To Go 개발 서버 실행 스크립트

echo "🚀 Ready To Go 개발 서버 시작..."
echo ""

# 백엔드 서버 상태 확인
echo "📡 백엔드 서버 상태 확인 중..."
if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo ""
    echo "🌐 프론트엔드 서버 시작..."
    echo "   브라우저에서 http://localhost:8080 으로 접속하세요"
    echo ""
    echo "⏹️  서버를 중지하려면 Ctrl+C 를 누르세요"
    echo ""

    # Python 서버 실행
    python3 -m http.server 8080
else
    echo "❌ Django 백엔드 서버가 실행되지 않았습니다."
    echo "   다음 명령어로 백엔드 서버를 먼저 실행해주세요:"
fi