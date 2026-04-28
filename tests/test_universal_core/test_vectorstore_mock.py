import pytest
from src.infrastructure.adapters.mock_adapters import MockVectorStore

@pytest.mark.asyncio
async def test_mock_vectorstore_add_and_search():
    store = MockVectorStore()
    
    # Add documents
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial Intelligence is transforming the world.",
        "Python is a versatile programming language."
    ]
    metadatas = [
        {"category": "animals"},
        {"category": "technology"},
        {"category": "programming"}
    ]
    ids = ["doc1", "doc2", "doc3"]
    
    await store.add_documents(documents, metadatas, ids)
    
    # Search for a technology related query
    results = await store.semantic_search("AI and the future", limit=1)
    
    assert len(results) == 1
    assert results[0].id == "doc2"
    assert "Artificial Intelligence" in results[0].document
    assert results[0].metadata["category"] == "technology"

@pytest.mark.asyncio
async def test_mock_vectorstore_empty_search():
    store = MockVectorStore()
    # Searching an empty collection
    results = await store.semantic_search("nothing", limit=5)
    assert len(results) == 0
