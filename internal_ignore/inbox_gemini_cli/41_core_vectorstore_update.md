# 🛠️ Universal Core Update: VectorStore Interface & Mock Implementation

**Target Skill:** `adk-core-builder`

## Objective
Update the Universal Core (`src/universal_core/`) to provide a robust, dynamic `BaseVectorStore` interface and an ephemeral in-memory mock implementation using ChromaDB. This allows agent developers to populate semantic search indexes dynamically during runtime.

## Requirements

1. **Update Interface (`src/universal_core/interfaces.py`)**
   - Locate the `BaseVectorStore` abstract base class (or create it if it doesn't exist).
   - Add a new abstract method: `add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]) -> None`.
   - Ensure the existing `semantic_search` method signature is maintained.

2. **Update Mock Adapter (`src/universal_core/mock_adapters.py`)**
   - Locate the `MockVectorStore` class.
   - Initialize an ephemeral ChromaDB client in the constructor (`chromadb.EphemeralClient()`) and get/create a collection (e.g., `mock_collection`).
   - Implement the `add_documents` method to insert records into the ChromaDB collection.
   - Implement the `semantic_search` method to query the ChromaDB collection and return the matched documents/metadata.

3. **Update Dependencies**
   - Add `chromadb` to `requirements.txt` (or the relevant dependency file in the monorepo root).

## Execution Instructions
Please activate the `adk-core-builder` skill. Review this specification to ensure it conforms to the Hexagonal Architecture of the Universal Core, and then proceed to implement the updates. Do not touch any agent-specific code (`src/agents/`); only update the core interfaces and mock infrastructure.
