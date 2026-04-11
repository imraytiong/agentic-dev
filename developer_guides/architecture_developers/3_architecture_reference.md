# 3. Architecture Reference (Code & Specs)

**Target Audience:** The Architect (Role 1)
**Goal:** A quick reference for the expected outputs of the Universal Core generation.

---

## 1. The Core Specification
The ultimate source of truth for the Universal Core is located at:
`src/universal_core/universal_core_architecture_spec.md`

This file dictates exactly what the AI CLI should build. If you ever need to add a new core capability (e.g., a new interface for a Vector Database), you must update the spec *first*, and then prompt the AI CLI to update the code.

## 2. Expected Output: `interfaces.py`
The AI should generate abstract base classes that look structurally similar to this:

```python
from typing import Optional, Type
from pydantic import BaseModel

class BaseStateStore:
    async def save_state(self, key: str, value: BaseModel):
        raise NotImplementedError

    async def load_state(self, key: str, target_model: Type[BaseModel]) -> Optional[BaseModel]:
        raise NotImplementedError

class BaseMessageBroker:
    async def publish(self, queue_name: str, payload: BaseModel):
        raise NotImplementedError

    async def consume(self, queue_name: str):
        raise NotImplementedError

class BaseMCPServer:
    async def start_sse_stream(self):
        raise NotImplementedError

class BaseFileStorage:
    async def save_file(self, data: bytes) -> str:
        raise NotImplementedError
```

## 3. The Sandbox Test Script (`test_core.py`)
When you perform the "Sandbox Pause" during generation, the AI should generate a test script that looks something like this. You will run this to verify the core before handing it off.

```python
import asyncio
from src.universal_core.chassis import BaseAgentChassis
from pydantic import BaseModel

# 1. Initialize the chassis in Mock Mode
chassis = BaseAgentChassis(mock_infrastructure=True)

# 2. Define a dummy state model
class DummyState(BaseModel):
    visits: int = 0

# 3. Define a dummy payload
class DummyJob(BaseModel):
    user_id: str
    action: str

# 4. Use the core decorator
@chassis.consume_task(queue_name="test_jobs", state_model=DummyState)
async def handle_job(payload: DummyJob, context, state: DummyState):
    print(f"Processing job for {payload.user_id}...")
    state.visits += 1
    return {"status": "success", "visits": state.visits}

# 5. Run the mock engine
if __name__ == "__main__":
    print("Starting Mock Engine. Access Studio at http://localhost:8000/studio")
    asyncio.run(chassis.run_local())
```