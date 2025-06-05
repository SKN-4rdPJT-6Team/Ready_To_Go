import logging
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI
import google.generativeai as genai
from langchain_openai import ChatOpenAI
from deep_translator import GoogleTranslator
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

class LLM:
    """번역 기능이 추가된 LLM 모듈 - GPU AI 서버 연동"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or getattr(settings, 'DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
        
        # 클라이언트 초기화
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3
        ) if getattr(settings, 'OPENAI_API_KEY', None) else None
        
        if getattr(settings, 'GOOGLE_API_KEY', None):
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        self.ko_to_en = GoogleTranslator(source='ko', target='en')
        
        self.translator = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0, 
            openai_api_key=settings.OPENAI_API_KEY
        ) if getattr(settings, 'OPENAI_API_KEY', None) else None
        
        # GPU AI 서버 설정
        self.AI_SERVER_URL = getattr(settings, 'GPU_AI_SERVER_URL', "https://9c6b-34-168-217-150.ngrok-free.app")
        self.ai_timeout = httpx.Timeout(60.0, connect=10.0)
        
        logger.info(f"LLM initialized with model: {self.model_name}")
    
    async def _generate_gemini_response(self, query: str, context: str, system_prompt: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Gemini 모델을 사용한 응답 생성"""
        if not getattr(settings, 'GOOGLE_API_KEY', None):
            raise Exception("Google API key not configured")
        
        model_name = self.model_name if self.model_name.startswith("gemini-") else "gemini-1.5-flash"
        
        # System prompt와 context를 결합한 초기 메시지 준비
        system_message = system_prompt
        
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_message
        )
        # Context를 query에 추가 (context가 있는 경우에만)
        
        if context and context.strip():
            enhanced_query = f"""Please answer the following question using the provided context information:

                Context:
                {context}

                Question: {query}"""
        else :
            enhanced_query = query
            
        # 히스토리가 있는 경우 채팅 세션으로 시작
        if history and len(history) > 0:
            # Gemini의 chat history 형식으로 변환
            gemini_history = []
            
            for message in history:
                role = message.get("role", "")
                content = message.get("content", "")
                
                if role == "user":
                    gemini_history.append({
                        "role": "user",
                        "parts": [content]
                    })
                elif role == "assistant":
                    gemini_history.append({
                        "role": "model",
                        "parts": [content]
                    })
            
            # 히스토리와 함께 채팅 시작
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(enhanced_query)
        else:
            # 히스토리가 없는 경우 새 채팅 시작
            chat = model.start_chat()
            response = chat.send_message(enhanced_query)
        
        return response.text
            

    async def _generate_phi_response(self, query: str, context: str) -> str:
        """Phi 모델(GPU 서버)을 사용한 응답 생성"""
        # 서버 상태 확인
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            health_response = await client.get(f"{self.AI_SERVER_URL}/api/health")
            if health_response.json().get("status") != "healthy":
                raise Exception("GPU server not healthy")
        
        # API 호출
        async with httpx.AsyncClient(timeout=self.ai_timeout) as client:
            payload = {"question": query, "context": context}
            response = await client.post(f"{self.AI_SERVER_URL}/api/ask", json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"GPU server response time: {result.get('inference_time', 0):.2f}s")
            
            if result.get("success") and result.get("answer"):
                return result["answer"]
            raise Exception("GPU server returned no answer")

    async def _generate_openai_response(self, query: str, context: str, system_prompt: str, history: Optional[List[Dict[str, str]]]) -> str:
        """OpenAI 모델을 사용한 응답 생성"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        # 사용자 질문 추가
        user_content = f"Query: {query}\n\n"
        if context and context.strip():
            user_content += f"Relevant Information:\n{context}\n\n"
        user_content += "Please provide a direct and natural answer."
        
        messages.append({"role": "user", "content": user_content})
        
        response = await self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0,
            max_tokens=1000
        )
        return response.choices[0].message.content

    async def _generate_response(self, query: str, context: str, history: Optional[List[Dict[str, str]]], system_prompt: str) -> str:
        """모델별 응답 생성"""
        try:
            if self.model_name.startswith("gemini-"):
                try:
                    return await self._generate_gemini_response(query, context, system_prompt, history)
                except Exception as e:
                    logger.warning(f"Gemini failed, falling back to OpenAI: {e}")
                    return await self._generate_openai_response(query, context, system_prompt, history)
            elif "phi" in self.model_name.lower():
                try:
                    return await self._generate_phi_response(query, context)
                except Exception as e:
                    logger.warning(f"Phi failed, falling back to Gemini: {e}")
                    return await self._generate_gemini_response(query, context, system_prompt, history)
            else:
                try:
                    return await self._generate_openai_response(query, context, system_prompt, history)
                except Exception as e:
                    logger.warning(f"OpenAI failed, falling back to Gemini: {e}")
                    return await self._generate_gemini_response(query, context, system_prompt, history)
        except Exception as e:
            logger.error(f"All models failed: {e}")
            raise Exception(f"Failed to generate response: {e}")

    def translate_with_gemini(self, text: str) -> Optional[str]:
            """Gemini로 번역 (1차)"""
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"다음 영어 텍스트를 자연스러운 한국어로 번역해주세요. 단순 번역이 아니라 문맥을 고려해서 의역해주세요:\n\n{text}"
                        }]
                    }]
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(f"Gemini 실패: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"Gemini 에러: {e}")
                return None
    
    def translate_with_chatgpt(self, text: str) -> Optional[str]:
        """ChatGPT로 번역 (3차)"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",  # 저렴한 모델 사용
                "messages": [{
                    "role": "user",
                    "content": f"다음 영어 텍스트를 자연스러운 한국어로 번역해주세요. 문맥을 고려해서 의역해주세요:\n\n{text}"
                }],
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"ChatGPT 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"ChatGPT 에러: {e}")
            return None
    
    def translate(self, english_text: str) -> str:
        """폴백 체인으로 번역 실행"""
        print("번역 시작...")
        
        # 1차: Gemini
        print("Gemini 시도 중...")
        result = self.translate_with_gemini(english_text)
        if result:
            print("✓ Gemini 번역 성공")
            return result

        # 3차: ChatGPT
        print("ChatGPT 시도 중...")
        time.sleep(1)
        result = self.translate_with_chatgpt(english_text)
        if result:
            print("✓ ChatGPT 번역 성공")
            return result
        
        # 모든 번역 실패시
        print("❌ 모든 번역 서비스 실패")
        return f"번역 실패: {english_text}"            
    async def _translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역"""
        try:
            # 이미 한국어인지 확인
            if any(0xAC00 <= ord(char) <= 0xD7A3 for char in text[:50]):
                return text
            
            if not self.translator:
                return text
            
            translate_prompt = f"Translate to Korean naturally: {text}"
            translated = self.translator.invoke(translate_prompt)
            return translated.content
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
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
            system_prompt = """You are Ready To Go, a friendly travel, immigration information assistant.
You specialize in providing accurate information about visa requirements, insurance, and immigration regulations.

IMPORTANT GUIDELINES:
1. NEVER mention "based on the context" or "according to the provided context"
2. Answer directly and naturally as if you know the information
3. Be conversational and helpful
4. If you have specific information, share it confidently
5. If you don't have specific information, provide general helpful advice

Remember: You are having a natural conversation with a traveler who needs help."""
        
        try:
            translated_query = self.ko_to_en.translate(query)
            # 응답 생성
            answer = await self._generate_response(translated_query, context, history, system_prompt)
            
            # 빈 응답 처리
            if not answer or answer.strip() == "":
                answer = "죄송합니다. 해당 질문에 대한 답변을 생성할 수 없습니다. 다시 질문해주세요."
            
            # 한국어 번역
            if translate_to_korean:
                answer = await self._translate_to_korean(answer)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in generate_with_translation: {e}")
            return "죄송합니다. 현재 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요."
