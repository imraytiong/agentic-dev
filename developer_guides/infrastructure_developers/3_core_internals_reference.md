# 3. Core Internals Reference

**Target Audience:** Platform Engineers, Architects, and curious Agent Developers
**Goal:** Understand exactly what happens *under the hood* of the `BaseAgentChassis`. 

If you need to debug the chassis, extend its capabilities, or understand how it abstracts away infrastructure, read on.

---

## 1. Hierarchical Configuration (Deep Merging)

To prevent repeating the exact same database URIs and model definitions across 50 different agents, the chassis uses a **Hierarchical Configuration Pattern**. When `chassis = BaseAgentChassis()` is called, it reads two YAML files and performs a "Deep Merge".

### A. The Global Fleet Config (`fleet.yaml`)
This file is mounted to *every* container in the cluster. It contains the universal defaults.
```yaml
models:
  default: "gemini-1.5-pro"

infrastructure:
  state_store: "src.infrastructure.public_adapters.postgres.PostgresStateStore"
```

### B. The Local Agent Config (`config.yaml`)
This file is specific to the agent. If this agent *needs* a specific override (e.g., pointing to a highly secure, isolated Postgres database), it simply defines `database: uri: "..."` locally, and the Chassis will prioritize the local setting.

---

## 2. Auto-Initialization & Dynamic Loading

The `BaseAgentChassis.__init__()` method does a massive amount of heavy lifting so the developer's `agent.py` file remains clean.

**What happens during initialization:**
1. **Config Merge:** Merges `fleet.yaml` and `config.yaml`.
2. **Dynamic Adapter Loading (IoC):** Reads the `infrastructure` block from `fleet.yaml` and uses `importlib` to dynamically load the operational adapters. The Core remains completely sealed and agnostic.
3. **ADK Bootstrapping:** Automatically initializes the underlying Google ADK Agent.
4. **Skill Equipping:** Iterates over `config.get("skills", [])` and appends them to the core System Prompt.
5. **Tool Registration:** Uses Python's `importlib` to dynamically load the agent's `tools.py` file, wraps each function in OpenTelemetry tracing spans, and registers it.

---

## 3. The `@consume_task` Decorator State Management

The `@chassis.consume_task(queue_name="jobs", state_model=MyState)` decorator is the most powerful abstraction in the chassis. 

**When a message arrives on the configured message broker, the decorator executes this exact lifecycle:**
1. **Deserialization:** Parses the JSON payload into the expected Pydantic model.
2. **Context Extraction:** Extracts the `AgentContext` (trace IDs, user IDs) from the message headers.
3. **State Loading:** Calls the dynamically loaded `state_store_client` to fetch the raw data and parse it into the developer's requested `state_model`.
4. **Execution:** Calls the developer's Python function, injecting the `payload`, `context`, and `state`.
5. **State Saving (On Exit):** When the function finishes, passes the modified `state` object back to the `state_store_client` for serialization and upsert.
6. **Auto-Reply (Webhooks):** If the function `return`s a Pydantic model, it automatically serializes it and fires an HTTP POST request to the `context.reply_to` webhook URL.
7. **Dead Letter Queue (DLQ):** If the function throws an unhandled exception, it increments the retry counter or routes the payload to `{queue_name}_dlq`.

---

## 4. The Interfaces (`src/universal_core/interfaces.py`)

```python
from typing import Optional, List, Type
from pydantic import BaseModel

class BaseStateStore:
    async def save_state(self, key: str, value: BaseModel): pass
    async def load_state(self, key: str, target_model: Type[BaseModel]) -> Optional[BaseModel]: pass

class BaseMessageBroker:
    async def publish(self, queue_name: str, payload: BaseModel): pass
    async def consume(self, queue_name: str): pass
    
class BaseMCPServer:
    async def start_sse_stream(self): pass
    
class BaseFileStorage:
    async def save_file(self, data: bytes) -> str: pass
```

## 5. The Operational Adapters (`src/infrastructure/`)

These implement the base classes and handle all serialization/deserialization, ensuring the Core only ever sees Pydantic models.

```python
# src/infrastructure/public_adapters/postgres.py
from src.universal_core.interfaces import BaseStateStore
from pydantic import BaseModel
from typing import Type, Optional

class PostgresStateStore(BaseStateStore):
    def __init__(self, config: dict):
        self.uri = config.get("database", {}).get("uri")

    async def save_state(self, key: str, value: BaseModel):
        # Serialize Pydantic model to JSONB and upsert
        pass
```