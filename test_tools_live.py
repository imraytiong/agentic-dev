import asyncio
import logging
from src.agents.jetpack_wiz.tools import ensure_repo_and_index, resolve_module_path
from src.universal_core.mock_adapters import MockVectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def main():
    repo_path = "/tmp/androidx-live-test"
    vector_store = MockVectorStore()
    
    print("🚀 Starting LIVE test of ensure_repo_and_index...")
    
    # 1. Run the clone and index
    status = await ensure_repo_and_index(repo_path, vector_store)
    print("\n--- Status Output ---")
    print(status)
    print("---------------------\n")
    
    # 2. Test semantic search against the index
    queries = [
        "Compose UI", 
        "Room compiler", 
        "DataStore", 
        "Navigation compose",
        "SQLite compilation"
    ]
    
    for query in queries:
        print(f"🔍 Searching for: '{query}'")
        results = await resolve_module_path(query, vector_store)
        for i, res in enumerate(results):
            print(f"   {i+1}. {res['path']} (Score: {res['score']:.2f})")
        print()
        
    print("✅ Live test complete.")

if __name__ == "__main__":
    asyncio.run(main())
