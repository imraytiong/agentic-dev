# Universal Core Architecture Spec

*Note: This specification is used by the Architect to direct the AI CLI to build the pristine `core/` directory.*

## 1. The Prime Directive
- The `core/` directory must be 100% environment-agnostic.
- **Forbidden Imports:** `asyncpg`, `redis`, `sqlalchemy`, `psycopg2`, or any specific infrastructure client.
- All infrastructure must be loaded dynamically via `importlib` using the plugin strings defined in `fleet.yaml`.

## 2. The Interfaces (`core/interfaces.py`)
Define the following Abstract Base Classes (ABCs):
*   `BaseStateStore`: Must have `async def save_state(key: str, state: BaseModel)` and `async def load_state(key: str, state_model: Type[BaseModel]) -> BaseModel`.
*   `BaseVectorStore`: Must have `async def semantic_search(query: str, limit: int = 5) -> List[BaseModel]`.
*   `BaseMessageBroker`: Must have `async def publish(queue_name: str, payload: BaseModel, context: AgentContext)` and `async def listen(queue_name: str)`.
*   `BaseTelemetry`: Must have `def record_metric(name: str, value: float, tags: dict)`.

## 3. The Core Object (`core/chassis.py`)
*   **Initialization:** The `__init__` method must load `fleet.yaml`, deep merge it with the local `config.yaml`, and instantiate the ADK `LlmAgent`.
*   **Dynamic Loading:** It must read the `infrastructure` block from the merged config and use `importlib` to instantiate the classes that implement the interfaces above.

## 4. The Mega-Abstractions
*   `execute_task(template: str, template_vars: dict, response_model: Type[BaseModel], context: AgentContext)`: 
    *   Must load the Jinja template.
    *   Must automatically inject `context.user_id`, `context.session_id`, and `context.tenant_id` into the `template_vars` before rendering.
    *   Must call `ask_structured`.
*   `ask_structured`: Must catch Pydantic `ValidationError`s and execute a hidden LLM retry loop to fix bad JSON.

## 5. The Decorators
*   `@consume_task(queue_name: str, state_model: Type[BaseModel], max_retries: int = 3)`:
    *   Must pull from `self.message_broker`.
    *   Must use `self.state_store` to load the state and inject it into the wrapped function.
    *   Must catch exceptions, increment retries, and route to `{queue_name}_dlq` if retries are exhausted.
    *   Must auto-save the state when the function exits.
    *   Must automatically send a webhook to `context.reply_to` if the wrapped function returns a Pydantic model.

## 6. The Mock Engine
*   `def run_local(self, mock_infrastructure: bool = False)`:
    *   If True, overrides the dynamically loaded adapters.
    *   Replaces `self.message_broker` with an `asyncio.Queue` implementation.
    *   Replaces `self.state_store` with an in-memory Python dictionary implementation.
    *   Bypasses FastAPI and drops the user into a terminal-based REPL loop.