import asyncio
import os
from core.llm_provider import LLMProvider

async def main():
    print("--- Testing LLM Provider ---")
    
    provider = LLMProvider(provider="gemini")
    
    messages = [
        {"role": "system", "content": "You are a helpful scientific assistant. Please reply concisely."},
        {"role": "user", "content": "What is the main function of the BRCA1 gene in one sentence?"}
    ]
    
    print(f"Using Provider: {provider.provider}")
    print(f"Prompt: {messages[1]['content']}")
    
    print("\nWaiting for response...")
    response = await provider.chat(messages)
    
    print("\nResponse:")
    print("-" * 30)
    print(response)
    print("-" * 30)
    
    if "Error" in response:
        print("\nNote: Please create a .env file and set GEMINI_API_KEY or OPENAI_API_KEY to see a real response.")

if __name__ == "__main__":
    asyncio.run(main())
