import os
import json
import logging
from typing import Type, TypeVar, List, Optional
from pydantic import BaseModel
import asyncpg
from asyncpg.pool import Pool

from universal_core.interfaces import BaseStateStore, BaseVectorStore

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class PostgresAdapterError(Exception):
    """Base exception for Postgres adapter to avoid leaking asyncpg errors."""
    pass

class PostgresAdapter(BaseStateStore, BaseVectorStore):
    def __init__(self, connection_string: str = None):
        # CTO Mandate: connection defaults
        self.connection_string = connection_string or f"postgresql://{os.getenv('POSTGRES_USER', 'devuser')}:{os.getenv('POSTGRES_PASSWORD', 'devpassword')}@{os.getenv('DB_HOST', 'localhost')}:5432/{os.getenv('POSTGRES_DB', 'agentic_dev')}"
        self._pool: Optional[Pool] = None

    async def connect(self):
        if not self._pool:
            try:
                # DBA Mandate: robust connection pooling
                self._pool = await asyncpg.create_pool(
                    self.connection_string,
                    min_size=1,
                    max_size=int(os.getenv('MAX_CONNECTIONS', '100'))
                )
            except Exception as e:
                raise PostgresAdapterError(f"Failed to connect to database: {e}")

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    # --- BaseStateStore Implementation ---

    async def save_state(self, key: str, state: BaseModel) -> None:
        await self.connect()
        try:
            async with self._pool.acquire() as conn:
                state_json = state.model_dump_json()
                # Upsert idempotency mandate
                query = """
                    INSERT INTO state_records (key, data, updated_at)
                    VALUES ($1, $2::jsonb, NOW())
                    ON CONFLICT (key) DO UPDATE
                    SET data = EXCLUDED.data, updated_at = NOW();
                """
                await conn.execute(query, key, state_json)
        except asyncpg.PostgresError as e:
            raise PostgresAdapterError(f"Database error saving state: {e}")
        except Exception as e:
            raise PostgresAdapterError(f"Unexpected error saving state: {e}")

    async def load_state(self, key: str, state_model: Type[T]) -> T:
        await self.connect()
        try:
            async with self._pool.acquire() as conn:
                query = "SELECT data FROM state_records WHERE key = $1;"
                row = await conn.fetchrow(query, key)
                if not row:
                    raise KeyError(f"State not found for key: {key}")
                
                # Parse JSONB string back to dict, then to Pydantic model
                data_dict = json.loads(row['data'])
                return state_model.model_validate(data_dict)
        except asyncpg.PostgresError as e:
            raise PostgresAdapterError(f"Database error loading state: {e}")
        except KeyError:
            raise
        except Exception as e:
            raise PostgresAdapterError(f"Unexpected error loading state: {e}")

    # --- BaseVectorStore Implementation ---

    async def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str], embeddings: list[list[float]] = None) -> None:
        """
        Note: The BaseVectorStore interface might not explicitly take embeddings.
        If it doesn't, we'd need an embedding provider. For the sake of the adapter,
        we assume embeddings are provided or we can just store the documents as state
        and use pgvector directly.
        """
        await self.connect()
        if not embeddings or len(embeddings) != len(documents):
            raise PostgresAdapterError("Embeddings must be provided for pgvector.")
            
        try:
            async with self._pool.acquire() as conn:
                # Use execute_many for efficiency
                query = """
                    INSERT INTO state_records (key, data, metadata, embedding, updated_at)
                    VALUES ($1, $2::jsonb, $3::jsonb, $4::vector, NOW())
                    ON CONFLICT (key) DO UPDATE
                    SET data = EXCLUDED.data, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding, updated_at = NOW();
                """
                
                # Format records for execute_many
                records = []
                for i in range(len(documents)):
                    data_json = json.dumps({"document": documents[i]})
                    metadata_json = json.dumps(metadatas[i] if metadatas else {})
                    vector_str = f"[{','.join(map(str, embeddings[i]))}]"
                    records.append((ids[i], data_json, metadata_json, vector_str))
                    
                await conn.executemany(query, records)
        except asyncpg.PostgresError as e:
            raise PostgresAdapterError(f"Database error adding documents: {e}")
        except Exception as e:
            raise PostgresAdapterError(f"Unexpected error adding documents: {e}")

    async def semantic_search(self, query_embedding: list[float], limit: int = 5) -> List[dict]:
        """
        Assuming semantic search takes an embedding directly since we don't have an embedding interface here.
        """
        await self.connect()
        try:
            async with self._pool.acquire() as conn:
                vector_str = f"[{','.join(map(str, query_embedding))}]"
                # HNSW cosine distance operator is <=>
                sql = """
                    SELECT id, key, data, metadata
                    FROM state_records
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2;
                """
                rows = await conn.fetch(sql, vector_str, limit)
                results = []
                for row in rows:
                    results.append({
                        "id": str(row['id']),
                        "key": row['key'],
                        "data": json.loads(row['data']),
                        "metadata": json.loads(row['metadata'])
                    })
                return results
        except asyncpg.PostgresError as e:
            raise PostgresAdapterError(f"Database error during semantic search: {e}")
        except Exception as e:
            raise PostgresAdapterError(f"Unexpected error during semantic search: {e}")
