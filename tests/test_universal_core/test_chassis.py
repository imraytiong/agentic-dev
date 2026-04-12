import pytest
import json
from typing import List, Any
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import BaseStateStore, AgentContext, BaseMessageBroker
from pydantic import BaseModel, ValidationError

class DummyStateStore(BaseStateStore):
    def __init__(self, config=None):
        self.config = config

    async def save_state(self, key: str, state: BaseModel) -> None:
        pass

    async def load_state(self, key: str, state_model: type) -> BaseModel:
        return state_model()

class DummyWrongAdapter:
    pass

def test_chassis_initialization_no_adapters(monkeypatch):
    monkeypatch.delenv("MOCK_INFRASTRUCTURE", raising=False)
    config = {
        "infrastructure": {}
    }
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    
    assert chassis.state_store is None
    assert chassis.vector_store is None

def test_chassis_loads_valid_adapter(monkeypatch):
    import os
    os.environ.pop("MOCK_INFRASTRUCTURE", None)
    import importlib
    
    def mock_import_module(name):
        class MockModule:
            DummyStateStore = globals()['DummyStateStore']
        return MockModule()
        
    monkeypatch.setattr(importlib, 'import_module', mock_import_module)
    
    config = {
        "infrastructure": {
            "state_store": "mock_module.DummyStateStore"
        }
    }
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    assert isinstance(chassis.state_store, DummyStateStore)

def test_chassis_rejects_invalid_adapter(monkeypatch):
    monkeypatch.delenv("MOCK_INFRASTRUCTURE", raising=False)
    import importlib
    
    def mock_import_module(name):
        class MockModule:
            DummyWrongAdapter = globals()['DummyWrongAdapter']
        return MockModule()
        
    monkeypatch.setattr(importlib, 'import_module', mock_import_module)
    
    config = {
        "infrastructure": {
            "state_store": "mock_module.DummyWrongAdapter"
        }
    }
    
    with pytest.raises(TypeError) as exc_info:
        BaseAgentChassis(config, mock_infrastructure=False)
    
    assert "does not implement the expected interface" in str(exc_info.value)

class SampleResponse(BaseModel):
    message: str
    count: int

@pytest.mark.asyncio
async def test_ask_structured_success():
    chassis = BaseAgentChassis({"infrastructure": {}})
    
    class MockLlmAgent:
        async def generate_content(self, prompt: str) -> str:
            return '```json\n{"message": "hello", "count": 42}\n```'
            
    chassis.llm_agent = MockLlmAgent()
    
    result = await chassis.ask_structured("Test prompt", SampleResponse)
    assert isinstance(result, SampleResponse)
    assert result.message == "hello"
    assert result.count == 42

@pytest.mark.asyncio
async def test_ask_structured_retry_healing():
    chassis = BaseAgentChassis({"infrastructure": {}})
    
    class MockLlmAgent:
        def __init__(self):
            self.attempts = 0
            
        async def generate_content(self, prompt: str) -> str:
            self.attempts += 1
            if self.attempts == 1:
                return 'Invalid JSON format'
            return '{"message": "healed", "count": 1}'
            
    chassis.llm_agent = MockLlmAgent()
    
    result = await chassis.ask_structured("Test prompt", SampleResponse)
    assert result.message == "healed"
    assert result.count == 1
    assert chassis.llm_agent.attempts == 2

@pytest.mark.asyncio
async def test_execute_task():
    chassis = BaseAgentChassis({"infrastructure": {}})
    
    class MockLlmAgent:
        async def generate_content(self, prompt: str) -> str:
            assert "Context User: u123" in prompt
            return '{"message": "success", "count": 10}'
            
    chassis.llm_agent = MockLlmAgent()
    
    context = AgentContext(user_id="u123", session_id="s123", tenant_id="t123")
    
    template = "Context User: {{ user_id }}"
    result = await chassis.execute_task(template, {}, SampleResponse, context)
    
class DummyMessageBroker(BaseMessageBroker):
    def __init__(self, config=None):
        self.config = config
        self.messages = []
        
    async def publish(self, queue_name: str, payload: BaseModel, context: AgentContext) -> None:
        self.messages.append({
            "payload": payload.model_dump(),
            "context": context.model_dump()
        })
        
    async def listen(self, queue_name: str) -> Any:
        if self.messages:
            return self.messages.pop(0)
        # Throw an exception to break the while loop in the test
        import asyncio
        raise asyncio.CancelledError("No more messages")

@pytest.mark.asyncio
async def test_consume_task():
    chassis = BaseAgentChassis({"infrastructure": {}})
    chassis.message_broker = DummyMessageBroker()
    
    # Pre-load a message into the dummy broker
    context = AgentContext(user_id="u1", session_id="s1", tenant_id="t1")
    payload = SampleResponse(message="task_data", count=5)
    await chassis.message_broker.publish("test_queue", payload, context)
    
    # We will use this to verify the function was called
    executed_payload = None
    executed_context = None
    
    @chassis.consume_task(queue_name="test_queue", payload_model=SampleResponse)
    async def my_agent_function(payload: SampleResponse, ctx: AgentContext):
        nonlocal executed_payload, executed_context
        executed_payload = payload
        executed_context = ctx
        
    # The decorator registers the wrapper in chassis._consumers
    assert len(chassis._consumers) == 1
    consumer_coroutine = chassis._consumers[0]
    
    # Run the consumer. It will process the one message and then raise CancelledError
    await consumer_coroutine()
        
    assert executed_payload is not None
    assert executed_payload.message == "task_data"
    assert executed_payload.count == 5
    assert executed_context.user_id == "u1"
id == "u1"
