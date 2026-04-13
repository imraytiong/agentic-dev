import asyncio
import pytest
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from pydantic import BaseModel

class TaskPayload(BaseModel):
    data: str

@pytest.mark.asyncio
async def test_mock_background_processing():
    # 1. Initialize chassis with mock infrastructure
    config = {
        "agent": {"name": "TestAgent"},
        "infrastructure": {}
    }
    chassis = BaseAgentChassis(config, mock_infrastructure=True)
    
    processed_data = []
    
    # 2. Register a background consumer
    @chassis.consume_task(queue_name="test_queue", payload_model=TaskPayload)
    async def process_task(payload: TaskPayload, context: AgentContext):
        processed_data.append(payload.data)
        
    # 3. Start the chassis (boots background consumers)
    # We need to run this in a way that we can stop it or just wait a bit
    start_task = asyncio.create_task(chassis.start())
    
    # Give consumers a moment to start (though start() is fast)
    await asyncio.sleep(0.1)
    
    # 4. Publish a message to the mock queue
    context = AgentContext(user_id="u1", session_id="s1", tenant_id="t1")
    payload = TaskPayload(data="hello_mock")
    await chassis.message_broker.publish("test_queue", payload, context)
    
    # 5. Wait for the consumer to process the message
    # We use a loop with a timeout
    for _ in range(10):
        if len(processed_data) > 0:
            break
        await asyncio.sleep(0.1)
        
    assert "hello_mock" in processed_data
    
    # Cleanup: cancel background tasks
    for task in chassis._background_tasks:
        task.cancel()
    await start_task
