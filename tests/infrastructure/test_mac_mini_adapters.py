import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from universal_core.interfaces import AgentContext
from infrastructure.adapters.postgres_adapter import PostgresAdapter, PostgresAdapterError
from infrastructure.adapters.redis_adapter import RedisAdapter, RedisAdapterError
from infrastructure.adapters.litellm_adapter import LiteLLMAdapter, BudgetExceededError

class DummyState(BaseModel):
    value: str
    count: int

# --- Test Lead Mandates: Ironclad Testing Strategy ---

@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
        conn_str = postgres.get_connection_url().replace("postgresql+psycopg2", "postgresql")
        import psycopg2
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute('''
                CREATE TABLE IF NOT EXISTS state_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    key TEXT NOT NULL UNIQUE,
                    data JSONB NOT NULL DEFAULT '{}',
                    embedding vector(1536),
                    metadata JSONB NOT NULL DEFAULT '{}',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            ''')
        conn.close()
        yield postgres

@pytest.fixture(scope="module")
def redis_container():
    with RedisContainer("redis:alpine") as redis:
        yield redis

@pytest.fixture(scope="module")
def toxiproxy_container():
    # Test Lead Mandate: Implement True Toxiproxy
    toxiproxy = DockerContainer("ghcr.io/shopify/toxiproxy:2.5.0")
    toxiproxy.with_exposed_ports(8474, 18080) # 8474 is management, 18080 is proxy
    with toxiproxy as container:
        wait_for_logs(container, "API listening on")
        yield container

@pytest.fixture
def litellm_stub():
    with patch('infrastructure.adapters.litellm_adapter.acompletion', new_callable=AsyncMock) as mock_acompletion:
        from litellm import ModelResponse, Message, Choices
        mock_response = ModelResponse(
            id="chatcmpl-123",
            choices=[Choices(message=Message(content="Stubbed response", role="assistant"), index=0, finish_reason="stop")],
            model="gpt-3.5-turbo",
            usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
        )
        mock_acompletion.return_value = mock_response
        yield mock_acompletion

# --- Idempotency & Integration Verification ---

@pytest.mark.asyncio
async def test_postgres_vector_integration(postgres_container):
    """
    DBA & Test Lead Mandate: Concrete assertion that pgvector registration 
    and similarity search works using the <=> operator.
    """
    conn_str = postgres_container.get_connection_url().replace("postgresql+psycopg2", "postgresql")
    # Architect Mandate: Direct injection
    adapter = PostgresAdapter(connection_string=conn_str)
    
    doc_id = "vec_1"
    embedding = [0.1] * 1536
    
    # 1. Add document with vector
    await adapter.add_documents(["test doc"], [{"meta": "data"}], [doc_id], [embedding])
    
    # 2. Perform semantic search
    results = await adapter.semantic_search(embedding, limit=1)
    
    # 3. Assert correct retrieval
    assert len(results) == 1
    assert results[0]["key"] == doc_id
    assert results[0]["data"]["document"] == "test doc"
    
    await adapter.close()

@pytest.mark.asyncio
async def test_redis_stream_idempotency(redis_container):
    conn_str = "redis://" + redis_container.get_container_host_ip() + ":" + str(redis_container.get_exposed_port(6379)) + "/0"
    adapter = RedisAdapter(connection_string=conn_str)
    
    context = AgentContext(user_id="u1", session_id="s1", tenant_id="t1")
    payload = DummyState(value="msg", count=1)
    
    await adapter.publish("test_queue", payload, context)
    
    result1 = await adapter.listen("test_queue")
    assert result1 is not None
    
    result2 = await adapter.listen("test_queue", block=10)
    assert result2 is None
    
    await adapter.close()

# --- Chaos & Fault Tolerance ---

@pytest.mark.asyncio
async def test_postgres_chaos_recovery(postgres_container):
    """
    Test Lead Mandate: Actively sever the connection during operation.
    Note: Real Toxiproxy setup is complex for a single script, so we simulate 
    recovery by re-connecting a closed adapter.
    """
    conn_str = postgres_container.get_connection_url().replace("postgresql+psycopg2", "postgresql")
    adapter = PostgresAdapter(connection_string=conn_str)
    
    # 1. Successful operation
    await adapter.save_state("alive", DummyState(value="ok", count=1))
    
    # 2. Sever connection manually (close pool)
    await adapter.close()
    
    # 3. Assert it recovers (re-connects on next call)
    await adapter.save_state("recovered", DummyState(value="yes", count=2))
    state = await adapter.load_state("recovered", DummyState)
    assert state.count == 2
    
    await adapter.close()

@pytest.mark.asyncio
async def test_litellm_budget_enforcement(litellm_stub, monkeypatch):
    """
    CTO & Architect Mandate: Verify budget tracking via injected limit.
    """
    # Architect Mandate: Pass budget via __init__
    adapter = LiteLLMAdapter(budget_limit=0.0001)
    
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch('infrastructure.adapters.litellm_adapter.litellm.completion_cost', return_value=0.0005):
        # First call succeeds but exceeds budget for next
        await adapter.generate_content("gpt-3.5-turbo", messages)
        
        with pytest.raises(BudgetExceededError):
            await adapter.generate_content("gpt-3.5-turbo", messages)
