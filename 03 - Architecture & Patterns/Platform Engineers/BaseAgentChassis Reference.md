---
Status: Approved
status: Approved
---
# BaseAgentChassis Reference Skeleton

**Tags:** #architecture #python #chassis #adk
**Status:** Active Reference

This document outlines the Python skeleton for the `BaseAgentChassis`. To enforce True Inversion of Control (IoC), the codebase is split into two directories: `core/` (which is sealed and pre-built) and `adapters/` (which the Infrastructure Team builds). Adapters are dynamically loaded at runtime via `fleet.yaml`.

## Directory Structure
```text
adk_chassis_lib/
├── core/
│   ├── chassis.py       # SEALED: The Universal Core logic only
│   ├── interfaces.py    # SEALED: Abstract Base Classes (e.g., BaseStateStore)
├── adapters/
│   ├── postgres.py      # INFRA: Implements BaseStateStore
│   ├── redis.py         # INFRA: Implements BaseMessageBroker
│   └── telemetry.py     # INFRA: Arize Phoenix OTel setup
```

## 1. The Universal Core (`core/chassis.py`)

```python
import os
import yaml
import importlib
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Type, List, Callable

from fastapi import FastAPI
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader

from google_adk.agent import LlmAgent
from core.interfaces import BaseStateStore, BaseVectorStore, BaseMessageBroker

class AgentContext(BaseModel):
    user_id: str
    session_id: str
    tenant_id: Optional[str] = None
    trace_id: str
    reply_to: Optional[str] = None 

class BaseAgentChassis:
    def __init__(
        self, 
        config_path: str = "/app/config.yaml",
        fleet_config_path: str = "/app/fleet.yaml",
        prompts_dir: str = "/app/prompts",
        skills_dir: str = "/app/skills"
    ):
        self.config = self._deep_merge_config(fleet_config_path, config_path)
        self.agent_name = self.config.get("agent", {}).get("name", "unnamed_agent")
        self.jinja_env = Environment(loader=FileSystemLoader(prompts_dir))
        self.skills_dir = skills_dir
        
        # === DYNAMIC ADAPTER LOADING (PLUGIN PATTERN) ===
        infra_config = self.config.get("infrastructure", {})
        self.state_store_client: BaseStateStore = self._load_adapter(infra_config.get("state_store"))
        self.vector_store_client: BaseVectorStore = self._load_adapter(infra_config.get("vector_store"))
        self.message_broker_client: BaseMessageBroker = self._load_adapter(infra_config.get("message_broker"))
        
        self.build_adk_agent()

    def _load_adapter(self, module_path: str) -> Any:
        """Dynamically imports and instantiates an adapter class from a string."""
        if not module_path:
            return None
        module_name, class_name = module_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, class_name)
        return adapter_class(self.config)

    # ... [Rest of Universal Core methods: execute_task, ask_structured, consume_task] ...
```

## 2. The Interfaces (`core/interfaces.py`)

```python
from typing import Optional, List, Type
from pydantic import BaseModel

class BaseStateStore:
    async def save_state(self, key: str, value: BaseModel): pass
    async def load_state(self, key: str, target_model: Type[BaseModel]) -> Optional[BaseModel]: pass

class BaseVectorStore:
    async def semantic_search(self, query: str, limit: int = 5) -> List[BaseModel]: pass

class BaseMessageBroker:
    async def publish(self, queue_name: str, payload: BaseModel): pass
    async def consume(self, queue_name: str): pass
```

## 3. The Operational Adapters (`adapters/`)

These are built by the Infrastructure Team (Track A). They implement the base classes and handle all serialization/deserialization, ensuring the Core only ever sees Pydantic models.

```python
# adapters/postgres.py
from core.interfaces import BaseStateStore
from pydantic import BaseModel
from typing import Type, Optional

class PostgresStateStore(BaseStateStore):
    def __init__(self, config: dict):
        self.uri = config.get("database", {}).get("uri")
        # Initialize asyncpg pool logic here

    async def save_state(self, key: str, value: BaseModel):
        # Serialize Pydantic model to JSONB and upsert
        pass

    async def load_state(self, key: str, target_model: Type[BaseModel]) -> Optional[BaseModel]:
        # Fetch JSONB, parse into target_model
        pass
```