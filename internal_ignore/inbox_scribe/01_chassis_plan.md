# BaseAgentChassis Execution Plan

Following the Hexagonal Architecture and the "Agent-Driven Development" approach defined in `src/universal_core/universal_core_architecture_spec.md`, the implementation is structured into five distinct layers. Each phase focuses on a specific architectural concern, ensuring the core remains environment-agnostic and robust.

## Phase 1: Foundation (Domain Interfaces)
*   **Goal:** Define the contracts for all infrastructure interactions to ensure the core is 100% environment-agnostic.
*   **Action:** Create `src/universal_core/core/interfaces.py`.
*   **Deliverables:** Abstract Base Classes (ABCs) for `BaseStateStore`, `BaseVectorStore`, `BaseFileStorage`, `BaseMessageBroker`, `BaseTelemetry`, and `BaseMCPServer`.

## Phase 2: The Universal Chassis (Dependency Injection & Lifecycle)
*   **Goal:** Implement the primary orchestration engine and dynamic loading logic.
*   **Action:** Create `src/universal_core/core/chassis.py`.
*   **Deliverables:** `BaseAgentChassis` class with initialization logic for configuration merging (`fleet.yaml` + `config.yaml`), dynamic plugin loading via `importlib`, and instantiation of the Google ADK `LlmAgent`.

## Phase 3: Service Layer & Mega-Abstractions
*   **Goal:** Implement the high-level logic that simplifies agent development and ensures robustness.
*   **Action:** Implement `execute_task` and `ask_structured` within the `BaseAgentChassis`.
*   **Deliverables:** Jinja2 template loading and rendering, automatic `AgentContext` injection (`user_id`, `session_id`, `tenant_id`), and robust LLM extraction with a built-in Pydantic retry loop for JSON healing.

## Phase 4: Communication & Event Handling (Decorators & API)
*   **Goal:** Expose the agent via FastAPI and handle asynchronous background tasks securely.
*   **Action:** Implement the `@consume_task` decorator and the FastAPI application framework.
*   **Deliverables:** Message broker polling, state auto-load/save, dead-letter queue (DLQ) routing, automated webhook execution, native `UploadFile` endpoints for multimodal support, and MCP integration endpoints (`/mcp/sse`, `/mcp/messages`).

## Phase 5: Developer Experience & Validation (Mock Engine & Agent Studio)
*   **Goal:** Enable rapid local prototyping without the need for external infrastructure dependencies.
*   **Action:** Implement `run_local(mock_infrastructure=True)`.
*   **Deliverables:** In-memory mock implementations for state and messaging, the embedded HTML/Vue/Tailwind "Agent Studio" UI at `GET /studio`, and verified local MCP SSE connectivity for IDE integration.