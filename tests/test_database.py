import asyncio
import json
from database.connection import init_db, AsyncSessionLocal
from database.models import QueryLog

async def main():
    print("--- Testing Database Layer ---")
    
    print("1. Initializing Database (Creating tables)...")
    await init_db()
    
    print("2. Inserting a mock query log...")
    async with AsyncSessionLocal() as session:
        mock_log = QueryLog(
            user_query="TP53 肺癌",
            language="zh-TW",
            plan=json.dumps([{"agent": "LiteratureAgent", "query": "TP53 lung cancer"}]),
            evidence=json.dumps([{"agent": "LiteratureAgent", "result": "Mock data from PubMed"}]),
            final_answer="TP53 是常見的抑癌基因..."
        )
        session.add(mock_log)
        await session.commit()
        await session.refresh(mock_log)
        
        print(f"-> Successfully inserted log! Database assigned ID: {mock_log.id}")
        print(f"-> Saved Answer: {mock_log.final_answer}")

if __name__ == "__main__":
    asyncio.run(main())
