import asyncio
from tools.literature.pubmed_tool import PubMedTool

async def main():
    print("--- Testing Tool Framework ---")
    
    # Initialize the tool
    pubmed_tool = PubMedTool()
    
    print(f"Tool Name: {pubmed_tool.name}")
    print(f"Tool Description: {pubmed_tool.description}")
    print("-" * 30)
    
    # Test query
    query = "BRCA1 AND breast cancer"
    print(f"Executing query: '{query}'")
    
    result = await pubmed_tool.execute(query=query, max_results=2)
    
    if result["status"] == "success":
        print(f"\nFound {result['metadata']['count']} articles:")
        for idx, article in enumerate(result["results"], 1):
            print(f"\n[{idx}] {article['title']}")
            print(f"    Authors: {', '.join(article['authors'])}")
            print(f"    Journal: {article['journal']} ({article['pubdate']})")
            print(f"    URL: {article['source_url']}")
    else:
        print(f"\nError: {result['message']}")

if __name__ == "__main__":
    asyncio.run(main())
