from typing import List, Dict, Any
import httpx
from core.config import settings

class LLMProvider:
    """Unified adapter for calling different LLM APIs."""
    
    def __init__(self, provider: str = None):
        from core.context import request_api_keys
        user_keys = request_api_keys.get({})
        self.provider = provider or user_keys.get("PREFERRED_PROVIDER") or settings.DEFAULT_LLM_PROVIDER
        
    def _is_zh(self, messages: List[Dict[str, str]]) -> bool:
        """Detects if the conversation is in Traditional Chinese."""
        for msg in messages:
            content = msg.get("content", "")
            if any('\u4e00' <= char <= '\u9fff' for char in content):
                return True
        return False

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

    async def generate_title(self, query: str, **kwargs) -> str:
        """Generates a short title for a conversation based on the first query."""
        # Optimization: Do NOT call the LLM to generate a title.
        # This saves 1 API request per conversation and helps avoid 429 Rate Limit errors.
        title = query.strip().split("\n")[0]
        if len(title) > 20:
            title = title[:17] + "..."
        return title

    async def _call_gemini(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        is_zh = self._is_zh(messages)
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 Gemini API Key！" if is_zh else "⚠️ **System Error**: Please configure your Gemini API Key in Settings!"
            
        model = kwargs.get("model") or user_keys.get("PREFERRED_MODEL_GEMINI") or "gemini-3.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Convert standard messages to Gemini format
        gemini_contents = []
        for msg in messages:
            # Gemini roles are usually 'user' or 'model'
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
        payload = {"contents": gemini_contents}
        
        import asyncio
        async with httpx.AsyncClient() as client:
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, timeout=30.0)
                    response.raise_for_status()
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in [429, 500, 502, 503, 504]:
                        if attempt < max_retries - 1:
                            if e.response.status_code == 429:
                                sleep_time = 15 * (attempt + 1)  # 15s, 30s, 45s (total 90s)
                            else:
                                sleep_time = (2 ** attempt) * 3
                            print(f"[Gemini API] Hit {e.response.status_code}, retrying in {sleep_time}s...")
                            await asyncio.sleep(sleep_time)
                            continue
                        if e.response.status_code == 429:
                            return "⚠️ **系統提示**：您的 Gemini API 免費額度已經耗盡 (Rate Limit / Quota Exceeded)。請稍後再試，或是更換一組新的 API Key。" if is_zh else "⚠️ **System Error**: Gemini API Rate Limit / Quota Exceeded. Please try again later or use a different API Key."
                        return f"⚠️ **Gemini API 發生錯誤**：伺服器目前過載或暫時無法回應 (HTTP {e.response.status_code})。請稍後再試。" if is_zh else f"⚠️ **Gemini API Error**: Server overloaded or temporarily unavailable (HTTP {e.response.status_code}). Please try again later."
                    return f"⚠️ **Gemini API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。" if is_zh else f"⚠️ **Gemini API Error**: Failed to get response (HTTP {e.response.status_code})."
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return f"⚠️ **Gemini 連線錯誤**：{str(e)}" if is_zh else f"⚠️ **Gemini Connection Error**: {str(e)}"

    async def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        is_zh = self._is_zh(messages)
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 OpenAI API Key！" if is_zh else "⚠️ **System Error**: Please configure your OpenAI API Key in Settings!"
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": kwargs.get("model") or user_keys.get("PREFERRED_MODEL_OPENAI") or "gpt-4-turbo",
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
                    return "⚠️ **系統提示**：您的 OpenAI API 額度已經耗盡。請檢查您的帳單資訊。" if is_zh else "⚠️ **System Error**: Your OpenAI API quota has been exhausted. Please check your billing information."
                return f"⚠️ **OpenAI API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。" if is_zh else f"⚠️ **OpenAI API Error**: Failed to get response (HTTP {e.response.status_code})."
            except Exception as e:
                return f"⚠️ **OpenAI 連線錯誤**：{str(e)}" if is_zh else f"⚠️ **OpenAI Connection Error**: {str(e)}"

    async def _call_anthropic(self, messages: List[Dict[str, str]], **kwargs) -> str:
        from core.context import request_api_keys
        is_zh = self._is_zh(messages)
        user_keys = request_api_keys.get({})
        api_key = kwargs.get("api_key") or user_keys.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "⚠️ **系統提示**：請先前往 Settings 設定您的 Anthropic API Key！" if is_zh else "⚠️ **System Error**: Please configure your Anthropic API Key in Settings!"
            
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
            "model": kwargs.get("model") or user_keys.get("PREFERRED_MODEL_ANTHROPIC") or "claude-3-5-sonnet-20241022",
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
                    return "⚠️ **系統提示**：您的 Anthropic API 額度已經耗盡。請稍候再試。" if is_zh else "⚠️ **System Error**: Your Anthropic API quota has been exhausted. Please try again later."
                return f"⚠️ **Anthropic API 發生錯誤**：無法取得回應 (HTTP {e.response.status_code})。" if is_zh else f"⚠️ **Anthropic API Error**: Failed to get response (HTTP {e.response.status_code})."
            except Exception as e:
                return f"⚠️ **Anthropic 連線錯誤**：{str(e)}" if is_zh else f"⚠️ **Anthropic Connection Error**: {str(e)}"
