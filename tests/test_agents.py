import asyncio
from agents.coordinator import CoordinatorAgent
from agents.literature_agent import LiteratureAgent

async def main():
    print("--- Testing Agent Framework ---")
    
    coordinator = CoordinatorAgent()
    lit_agent = LiteratureAgent()
    
    coordinator.register_agent(lit_agent)
    
    user_query = "TP53 在肺癌的最新研究進展是什麼？請提供參考文獻。"
    print(f"User Query: {user_query}\n")
    
    result = await coordinator.execute_workflow(user_query)
    
    print("\n" + "="*50)
    print("FINAL ANSWER")
    print("="*50)
    print(result["final_answer"])

if __name__ == "__main__":
    asyncio.run(main())
