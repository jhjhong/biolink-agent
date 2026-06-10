from typing import List, Dict, Any
import httpx
from core.config import settings

class LLMProvider:
    """Unified adapter for calling different LLM APIs."""
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        messages format: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        if self.provider == "gemini":
            return await self._call_gemini(messages, **kwargs)
        elif self.provider == "openai":
            return await self._call_openai(messages, **kwargs)
        elif self.provider == "anthropic":
            return await self._call_anthropic(messages, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _call_gemini(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 Gemini API Key！"
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
        
        # Convert standard messages to Gemini format
        gemini_contents = []
        for msg in messages:
            # Gemini roles are usually 'user' or 'model'
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
        payload = {"contents": gemini_contents}
        
        import asyncio
        async with httpx.AsyncClient() as client:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, timeout=30.0)
                    response.raise_for_status()
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in [500, 502, 503, 504]:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        return f"⚠️ **Gemini API 發生錯誤**：伺服器目前過載或暫時無法回應 (HTTP {e.response.status_code})。請稍後再試。"
                    if e.response.status_code == 429:
                        return "⚠️ **系統提示**：您的 Gemini API 免費額度已經耗盡 (Rate Limit / Quota Exceeded)。請稍後再試，或是更換一組新的 API Key。"
                    return f"⚠️ **Gemini API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。"
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return f"⚠️ **Gemini 連線錯誤**：{str(e)}"

    async def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 OpenAI API Key！"
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": kwargs.get("model", "gpt-4-turbo"),
            "messages": messages
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    return "⚠️ **系統提示**：您的 OpenAI API 額度已經耗盡。請檢查您的帳單資訊。"
                return f"⚠️ **OpenAI API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。"
            except Exception as e:
                return f"⚠️ **OpenAI 連線錯誤**：{str(e)}"

    async def _call_anthropic(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 Anthropic API Key！"
            
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_prompt = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
                
        payload = {
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": anthropic_messages
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    return "⚠️ **系統提示**：您的 Anthropic API 額度已經耗盡。請稍候再試。"
                return f"⚠️ **Anthropic API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。"
            except Exception as e:
                return f"⚠️ **Anthropic 連線錯誤**：{str(e)}"
