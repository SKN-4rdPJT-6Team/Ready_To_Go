import logging
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI
import google.generativeai as genai
from langchain_openai import ChatOpenAI
from deep_translator import GoogleTranslator
import asyncio
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class LLM:
    """번역 기능이 추가된 LLM 모듈 - GPU AI 서버 연동"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL
        
        # OpenAI 클라이언트 초기화
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3
        ) if settings.OPENAI_API_KEY else None
        
        # Gemini 초기화
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # 번역기 초기화
        self.translator = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0, 
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # GPU AI 서버 설정
        self.AI_SERVER_URL = getattr(settings, 'GPU_AI_SERVER_URL', "http://localhost:8001")
        self.ai_timeout = httpx.Timeout(60.0, connect=10.0)
        
        logger.info(f"LLM initialized with model: {self.model_name}")
    
    async def _call_gpu_server(self, question: str, context: str = None, max_tokens: int = 150) -> Dict[str, Any]:
        """GPU AI 서버 호출"""

    
    async def _fallback_to_gpt35(self, messages: List[Dict[str, str]]) -> str:
        """GPT-3.5로 폴백"""
        logger.warning("Falling back to gpt-3.5-turbo")
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT-3.5 fallback failed: {e}")
            return "죄송합니다. 현재 AI 서비스에 문제가 발생했습니다."
    
    async def _generate_openai_response(self, messages: List[Dict[str, str]]) -> str:
        """OpenAI 모델 응답 생성"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0,
                max_tokens=1000
            )
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            logger.warning("Rate limit reached, retrying after delay")
            await asyncio.sleep(5)
            return await self._fallback_to_gpt35(messages)
            
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API error: {e}")
            return await self._fallback_to_gpt35(messages)
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            return await self._fallback_to_gpt35(messages)
    
    async def _generate_gemini_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Gemini 모델 응답 생성"""
        try:
            # 히스토리 텍스트 구성
            history_text = ""
            for msg in messages[1:-1]:  # system과 마지막 user 메시지 제외
                role = "User:" if msg['role'] == 'user' else "Assistant:"
                history_text += f"{role} {msg['content']}\n"
            
            full_prompt = f"{system_prompt}\n\n{history_text}User: {messages[-1]['content']}\nAssistant:"
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return await self._fallback_to_gpt35(messages)
    
    async def _generate_finetuned_model_response(self, query: str, context: str) -> str:
        """파인튜닝 모델 응답 생성"""
        try:
            # 서버 상태 확인
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                health_response = await client.get(f"{self.AI_SERVER_URL}/api/health")
                if health_response.json().get("status") != "healthy":
                    raise Exception("GPU server not healthy")
    
            # 서버의 응답 요청
            async with httpx.AsyncClient(timeout=self.ai_timeout) as client:
                payload = {
                    "question": query,
                    "context": context,
                    "max_tokens": max_tokens
                }
                
                response = await client.post(f"{self.AI_SERVER_URL}/api/ask", json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"GPU server response time: {result.get('inference_time', 0):.2f}s")
                    
            if result.get("success") and result.get("answer"):
                return result["answer"]
            else:
                raise Exception("GPU server returned no answer")
                
        except Exception as e:
            logger.error(f"GPU server failed: {e}")
            # GPT-3.5로 폴백
            messages = [
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": f"Query: {query}\nContext: {context}"}
            ]
            return await self._fallback_to_gpt35(messages)
    
    async def _translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역"""
        try:
            # 이미 한국어인지 확인
            if any(0xAC00 <= ord(char) <= 0xD7A3 for char in text[:50]):
                return text
            
            translate_prompt = f"Translate to Korean naturally: {text}"
            translated = self.translator.invoke(translate_prompt)
            return translated.content
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def _build_messages(self, query: str, context: str, history: Optional[List[Dict[str, str]]], system_prompt: str) -> List[Dict[str, str]]:
        """메시지 리스트 구성"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # 히스토리 추가
        if history:
            messages.extend(history)
        
        # 사용자 질문 추가
        if context and context.strip():
            user_content = f"Query: {query}\n\nRelevant Information:\n{context}\n\nPlease provide a direct and natural answer."
        else:
            user_content = f"Query: {query}\n\nPlease provide a helpful answer."
            
        messages.append({"role": "user", "content": user_content})
        return messages
    
    async def generate_with_translation(
        self,
        query: str,
        context: str,
        references: List[Dict[str, Any]],
        translate_to_korean: bool = True,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """응답 생성 후 한국어로 번역"""
        
        # 기본 시스템 프롬프트
        if not system_prompt:
            system_prompt = """You are Ready To Go, a friendly travel information assistant.
You specialize in providing accurate information about visa requirements, insurance, and immigration procedures.

IMPORTANT GUIDELINES:
1. NEVER mention "based on the context" or "according to the provided context"
2. Answer directly and naturally as if you know the information
3. Be conversational and helpful
4. If you have specific information, share it confidently
5. If you don't have specific information, provide general helpful advice

Remember: You are having a natural conversation with a traveler who needs help."""
        
        # 메시지 구성
        messages = self._build_messages(query, context, history, system_prompt)
        
        # 모델별 응답 생성
        if self.model_name.startswith("gpt-"):
            answer = await self._generate_openai_response(messages)
        elif self.model_name.startswith("gemini-"):
            answer = await self._generate_gemini_response(messages, system_prompt)
        elif "phi" in self.model_name.lower():
            answer = await self._generate_finetuned_model_response(query, context)
        else:
            logger.warning(f"Unknown model: {self.model_name}, falling back to GPT-3.5")
            answer = await self._fallback_to_gpt35(messages)
        
        # 한국어 번역
        if translate_to_korean and answer:
            answer = await self._translate_to_korean(answer)
        
        return answer
