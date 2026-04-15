# Pre-flight Plan: Core VectorStore Update

**Objective:** Implement `add_documents` in `BaseVectorStore` and provide a ChromaDB-backed `MockVectorStore`.

**Track Branch:** `track/core-vectorstore-update`

**Proposed Changes:**
1.  **`src/universal_core/interfaces.py`**:
    *   Add `async def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]) -> None` to `BaseVectorStore`.
2.  **`src/universal_core/mock_adapters.py`**:
    *   Import `chromadb`.
    *   Update `MockVectorStore.__init__` to initialize `chromadb.EphemeralClient()`.
    *   Implement `add_documents` using ChromaDB collection.
    *   Implement `semantic_search` using ChromaDB collection queries.
3.  **`requirements.txt`**:
    *   Add `chromadb`.

**Verification:**
*   Create a test script `tests/test_universal_core/test_vectorstore_mock.py` to verify `add_documents` and `semantic_search` behavior in the mock adapter.
