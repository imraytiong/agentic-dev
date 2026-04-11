import pytest
from src.agents.hello_sparky.agent import chassis, process_hello
from src.agents.hello_sparky.models import HelloRequest, HelloResponse, HelloState
from src.universal_core.interfaces import AgentContext
import os

@pytest.mark.asyncio
async def test_agent_execution_loop(monkeypatch):
    # Setup mock infrastructure on chassis
    os.environ["MOCK_INFRASTRUCTURE"] = "true"
    chassis.__init__({}, mock_infrastructure=True)
    
    # Mock the LLM to return a consistent structured response
    class MockLlmAgent:
        async def generate_content(self, prompt: str) -> str:
            return '{"greeting_message": "Hello Ray!", "affirmation": "mocked affirmation", "total_interactions": 1}'
            
    chassis.llm_agent = MockLlmAgent()
    
    # Setup test data
    payload = HelloRequest(developer_name="Ray", current_mood="happy")
    context = AgentContext(user_id="user123", session_id="sesh1", tenant_id="t1")
    
    # Pre-publish a message to the queue to trigger the consumer
    await chassis.message_broker.publish("hello_jobs", payload, context)
    
    # Run the wrapped function manually for the test (bypassing the while True loop)
    # The decorated function is wrapped, so we can call it directly
    # Note: Because the wrapper returns the wrapper function, we need to access the original
    # Wait, the decorator returns the wrapper which contains the loop.
    # It's easier to test the inner logic directly or just call process_hello if we had extracted it.
    # Since process_hello is wrapped in the consume_task loop, we can't easily test it directly 
    # without running the consumer loop.
    
    # Let's extract the inner function from the decorators closures or just test the 
    # message processing by running the consumer loop for one iteration.
    
    consumer_coroutine = chassis._consumers[0]
    
    # Modify the broker to raise CancelledError after processing one message
    import asyncio
    original_listen = chassis.message_broker.listen
    
    async def mock_listen(queue_name):
        try:
            return await original_listen(queue_name)
        except asyncio.QueueEmpty:
            pass # Wait... listen uses .get() which blocks.
            
    # Actually, the dummy mock broker uses asyncio.Queue which blocks on .get().
    # Let's just put an item, and then put a special poison pill, or cancel the task.
    task = asyncio.create_task(consumer_coroutine())
    
    # Give the task a moment to process the message
    await asyncio.sleep(0.1)
    
    # Cancel the loop
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
        
    # Verify state was saved
    state = await chassis.state_store.load_state("sparky_state_user123", HelloState)
    assert state.interaction_count == 1