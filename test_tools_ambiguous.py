import asyncio
import logging
from src.agents.jetpack_wiz.tools import resolve_module_path
from src.universal_core.mock_adapters import MockVectorStore

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    vector_store = MockVectorStore()
    
    print("🚀 Running ambiguous semantic search tests against the populated index...\n")
    
    queries = [
        "How do I do background work and scheduling?", # Should find WorkManager
        "What library handles camera capture and streams?", # Should find CameraX
        "Is there a library for slicing arrays into pages?", # Should find Paging
        "I need a library to handle material design 3 dynamic colors", # Should find Compose Material3
        "Something for reading preferences asynchronously", # Should find DataStore Preferences
        "Where is the code that handles backward compatibility for old Android versions?", # Should find AppCompat/Core
        "What is the animation framework?", # Should find Compose Animation or Core Animation
    ]
    
    for query in queries:
        print(f"🤔 Ambiguous Query: '{query}'")
        results = await resolve_module_path(query, vector_store)
        for i, res in enumerate(results):
            print(f"   {i+1}. {res['path']}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
