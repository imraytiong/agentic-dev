---
tags:
  - architecture
  - core
  - specification
status: Active
---
# Universal Core Architecture Spec

**Target:** `core/interfaces.py` and `core/chassis.py`
**Owner:** The Architect (Role 1)
**Purpose:** Provide the sealed, environment-agnostic foundation for the `BaseAgentChassis`. This code must run 100% locally in RAM using `mock_infrastructure=True` to unblock Agent Developers on Day 1.

## 1. Strict Constraints
*   **No Operational Dependencies:** You may NOT import `asyncpg`, `redis`, `sqlalchemy`, or any specific database/broker libraries. 
*   **Allowed Libraries:** `google-adk`, `fastapi`, `pydantic`, `jinja2`, `pyyaml`, `asyncio`, `importlib`, and standard Python libraries.
*   **Strict Typing:** Everything must be heavily typed. Use Pydantic for all data models.

## 2. `core/interfaces.py` (The Contracts)
Define the Abstract Base Classes (ABCs) that Track A (Infra) will later implement:
*   `BaseStateStore`: `save_state(key: str, value: BaseModel)`, `load_state(key: str, target_model: Type[BaseModel]) -> Optional[BaseModel]`
*   `BaseVectorStore`: `semantic_search(query: str, limit: int = 5) -> List[BaseModel]`
*   `BaseMessageBroker`: `publish(queue_name: str, payload: BaseModel)`, `consume(queue_name: str)` (Note: `consume` logic is mostly handled by the decorator, but the interface needs definition).

## 3. `core/chassis.py` (The Logic)

### A. Core Models
*   Define `AgentContext(BaseModel)`: `user_id`, `session_id`, `tenant_id` (optional), `trace_id`, `reply_to` (optional).

### B. Initialization (`__init__`)
*   Parameters: `agent_name` (optional, defaults to config), `config_path`, `fleet_config_path`.
*   Logic:
    *   Deep merge `fleet.yaml` and `config.yaml`.
    *   Extract `agent_name` from config.
    *   Initialize Jinja2 environment.
    *   **Dynamic Loading (IoC):** Use `importlib` to load `state_store`, `vector_store`, `message_broker`, and `telemetry` adapters from the `infrastructure` config block. *If `mock_infrastructure=True`, instantiate in-memory mock versions instead.*
    *   Call `self.build_adk_agent()`.

### C. The Mega-Abstractions (Methods)
*   `build_adk_agent()`: Reads config, sets the model alias, loads tools dynamically via `importlib`, and equips skills (appends Jinja files to system prompt).
*   `execute_task(template: str, template_vars: dict, response_model: Type[BaseModel], context: AgentContext)`: Merges context into vars, renders Jinja, calls ADK agent, and forces strict Pydantic JSON output.
*   `call_agent_sync(target_agent: str, endpoint: str, payload: BaseModel, context: AgentContext)`: Wrapper for synchronous REST calls. Includes retry logic.
*   `publish_async_task(queue_name: str, payload: BaseModel, context: AgentContext)`: Wraps the message broker publish.

### D. The Decorators
*   `@with_retry(max_retries=3)`: Standard exponential backoff decorator.
*   `@consume_task(queue_name: str, state_model: Type[BaseModel], max_retries: int = 3)`: 
    *   Abstracts the queue listener.
    *   Extracts `AgentContext`.
    *   Loads state via `state_store_client`.
    *   Injects state into the wrapped function.
    *   Saves state on exit.
    *   Routes to `{queue_name}_dlq` if exceptions exceed `max_retries`.
    *   Triggers auto-reply webhook if the function returns a Pydantic model and `context.reply_to` exists.

### E. The Mock Engine (`run_local`)
*   `run_local(func, payload, context, mock_infrastructure=True)`: Bypasses FastAPI. Uses a Python dictionary for state and standard `asyncio` queues. This is critical for Track C developers to test logic locally.