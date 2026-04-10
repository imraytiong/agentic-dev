---
status: Active
---
# 🏛️ Master Architectural Decision Log (ADL)

**Tags:** #architecture #planning #adr
**Purpose:** This document is the exhaustive snapshot of all our strategic technical decisions, as well as the queue for pending questions we need to deep dive into.

---

## 🌟 Core Architectural Principles
*These principles govern every technical decision we make.*

1. **Open Source & Self-Hosted First:** We strictly rely on open-source products and self-hosted infrastructure. We avoid commercial SaaS offerings and vendor lock-in to maintain full control, reduce costs, and ensure local debuggability.
2. **Lightweight & Modular:** Avoid bloated frameworks when standard Python or a decoupled microservice will do.
3. **Abstracted Plumbing:** Custom agents should contain *only* business logic (prompts, tools). All distributed infrastructure (networking, telemetry, queues) must be abstracted into the reusable `BaseAgentChassis`.
4. **AI-Assisted Velocity & Defense:** We use agentic developer tools (Antigravity CLI, Gemini CLI) to write code extremely fast. Because these tools are prone to causing regressions, we mandate strict Test-Driven Development (TDD) for deterministic code to defend our velocity.
5. **Strict Integration Contracts:** Multi-agent interoperability is our highest risk for breakage. Inter-agent API schemas (Pydantic models) must be heavily locked down and tested, ensuring AI coding tools cannot hallucinate breaking changes to an integration point.

---

## ✅ Approved Decisions

### 1. Core Framework & Language
*   **Decision:** Google Agent Development Kit (ADK) using strictly Python.
*   **Rationale:** Provides idiomatic multi-agent orchestration, model-agnostic execution (LiteLLM), and vertex readiness while allowing us to build custom Pythonic complementary patterns for gaps.

### 2. Fleet Deployment Architecture
*   **Decision:** Distributed-First (Microservices) via the "Microservice Chassis" pattern.
*   **Rationale:** Prevents monolithic blast radius (one agent crashing the fleet), allows asymmetrical resource scaling, and isolates dependencies.

### 3. Infrastructure Target
*   **Decision:** Cloud-Agnostic & Lightweight (Docker Compose for local Mac Mini -> K3s for Linux cluster).
*   **Rationale:** Avoids cloud vendor lock-in, keeps development cheap and local, and ensures zero-code-change portability from local to production.

### 4. Agent Lifecycle Management
*   **Decision:** Rely on FastAPI `asynccontextmanager` for cold starts, ADK native `/health` probes for K8s/Docker readiness, and OpenTelemetry for tracing.

### 5. BaseAgentChassis Configuration
*   **Decision:** Centralized configuration file (`config.yaml` mounted as a volume to all containers).
*   **Rationale:** Ensures consistency across the distributed fleet. Prevents the headache of keeping multiple `.env` files synced across 10+ different agent containers for shared values like database URIs or global model settings.

### 6. Inter-Agent Communication (Synchronous)
*   **Decision:** REST + Pydantic (JSON).
*   **Rationale:** Easiest to read, debug locally, and native to our FastAPI chassis. 
*   **Future Note:** We may transition to gRPC (Protocol Buffers) later if we find payload sizes become an issue and we are highly confident in our observability and debugging architecture.

### 7. Inter-Agent Communication (Asynchronous)
*   **Decision:** Redis (for Task Queues) wrapped in an Abstract Interface.
*   **Rationale:** Redis is extremely lightweight, fast, and easy to run in Docker Compose/K3s alongside our agents. 
*   **Architecture Mandate:** To ensure adaptability, the `BaseAgentChassis` will define an abstract base class (e.g., `BaseMessageBroker`). Agents will interact *only* with this interface. This guarantees that if/when we outgrow Redis and need advanced routing (RabbitMQ), we only change the underlying chassis implementation, and zero agent logic needs to be rewritten.

### 8. Long-Term Memory & State Persistence
*   **Decision:** PostgreSQL + `pgvector` extension (Hybrid Approach).
*   **Rationale:** Gives us the best of both worlds with minimal infrastructure bloat. We maintain a single database container that can handle strict relational state (e.g., user profiles, task statuses) while natively supporting semantic similarity searches (vector embeddings) for agent memory.

### 9. Advanced RAG Implementation
*   **Decision:** Decoupled Architecture (Unstructured.io for Ingestion + Custom Python for Retrieval).
*   **Rationale:** We need high-quality parsing for complex documents (PDFs, etc.), which simple chunkers fail at. By running a dedicated open-source `unstructured-api` container, we offload the heavy ETL work. Our `BaseAgentChassis` remains incredibly lean, using custom Python (SQLAlchemy/psycopg) to query `pgvector` without the bloat or "magic" of frameworks like LlamaIndex or Haystack.

### 10. Observability & Tracing Backend
*   **Decision:** Arize Phoenix (Open Source, Self-Hosted Container).
*   **Rationale:** We are using ADK's native OpenTelemetry support. Arize Phoenix speaks OTel natively and is explicitly built for AI/LLM observability. It allows us to see prompts, tool calls, and RAG retrievals in a single, lightweight Docker container without relying on commercial SaaS platforms (like LangSmith or Datadog).

### 11. Testing & Evaluation
*   **Decision:** The Hybrid Approach (Strict TDD + Golden Evals) with locked-down Integration Contracts.
*   **Rationale:** Because we are using AI-assisted coding tools (Antigravity/Gemini CLI) to build rapidly, the risk of hallucinated regressions is high. 
    *   **Deterministic Code (TDD):** We strictly use `pytest` to test the `BaseAgentChassis`, database queries, and tool logic.
    *   **Interoperability:** We strictly test the Pydantic schemas that define agent-to-agent REST APIs. If an AI coding tool alters a schema, the build fails immediately.
    *   **Non-Deterministic Code (Evals):** We maintain a "Golden Dataset" of perfect inputs/outputs. Before major merges, we run an LLM-as-a-Judge against this dataset to ensure prompt quality hasn't degraded.

### 12. Prompt Management
*   **Decision:** Externalized to Files (Jinja/Markdown).
*   **Rationale:** This establishes a physical boundary that protects our carefully engineered prompts from being accidentally truncated or altered by AI coding assistants (like Antigravity CLI) during code refactors. Furthermore, by volume-mounting the `prompts/` directory into our Docker containers, we can hot-reload prompt tweaks without rebuilding or restarting the Python server, vastly increasing our iteration speed.

### 13. BaseAgentChassis Skeleton
*   **Decision:** Created a standardized Python Skeleton for the chassis.
*   **Rationale:** Defines the contract between the custom agent logic and the underlying distributed K3s infrastructure.

### 14. Local Testing & Mocking (Developer Experience)
*   **Decision:** The `BaseAgentChassis` will include a `run_local()` mode and mock infrastructure toggles.
*   **Rationale:** Developers must be able to test core agent logic (prompts, tool routing) locally via REPL or simple scripts without needing to spin up the full distributed infrastructure (Docker, Postgres, Redis). The chassis will gracefully degrade DB/Redis calls to in-memory dictionaries and bypass OpenTelemetry to ensure local velocity.

### 15. Skill & Context Bundling
*   **Decision:** Implement an `equip_skill()` mechanism in the `BaseAgentChassis`.
*   **Rationale:** We need a standardized way to package and share capabilities across different agents without copy-pasting code. A "Skill" is a folder containing instructions (Jinja) and capabilities (Python tools). The chassis handles dynamically appending the instructions to the agent's system prompt and registering the tools, ensuring DRY (Don't Repeat Yourself) principles.

### 16. Supervisor Routing Strategy
*   **Decision:** The Hybrid Approach (Semantic Routing + LLM Fallback).
*   **Rationale:** For the Front Door Supervisor agent, we first use deterministic semantic routing (embedding the prompt and querying `pgvector` for capability matches). If confidence is high, we route instantly (saving tokens and latency). If confidence is low, we fall back to a fast LLM (Gemini 1.5 Flash) to dynamically reason about the route using tool calls.

### 17. Agent State Storage
*   **Decision:** JSONB Payload (NoSQL style in Postgres).
*   **Rationale:** Provides ultimate flexibility for agent states without requiring SQL migrations. Pydantic handles validation in the Python chassis, and Postgres stores it as a flexible JSONB column, allowing rapid iteration on agent variables and loop tracking.

### 18. Semantic Memory Structure
*   **Decision:** Segregated Vector Tables.
*   **Rationale:** By separating `conversational_memory`, `document_knowledge`, and `core_instructions` into distinct tables, we drastically improve query performance and prevent agents from searching through massive RAG documents when they only need to recall a recent chat message.

### 19. Plan-and-Execute Workflow Pattern
*   **Decision:** Dynamic Re-Planner Approach.
*   **Rationale:** Instead of a static array of steps that breaks if one step fails, the Planner writes Step 1, the Executor completes it, and the Planner evaluates the result before dynamically writing Step 2. This is slower but highly resilient to errors and unexpected tool outputs.

### 20. Evaluator-Optimizer Workflow Pattern
*   **Decision:** Escalation to Human (HITL) with Fast-Fail Abort.
*   **Rationale:** To prevent infinite token-burning loops, we implement a strict retry limit. If the Drafter fails N times, it escalates to a Human-in-the-Loop via the ADK. Additionally, the Evaluator is given the ability to "Fast-Fail" immediately if it determines the task is fundamentally impossible or the first draft is catastrophically off-base.

### 21. Containerization Engine (Mac Native)
*   **Decision:** Apple Native Virtualization / LIMA (e.g., `colima`) as the default, with strict architectural portability to Podman and OrbStack.
*   **Rationale:** We prioritize open-source and lightweight overhead for the Mac Mini. `colima` leverages Apple's native hypervisor perfectly. However, because corporate environments often mandate Podman, our `docker-compose.yml` and container configurations must remain strictly OCI-compliant. We will not use any engine-specific features or proprietary extensions that would break portability to Podman Desktop.

### 22. Chassis API Extensions (Strict Guardrails)
*   **Decision:** We added four strict API surfaces to the `BaseAgentChassis` to prevent AI coding tools from hallucinating bad infrastructure code:
    1. **`@consume_task`** (Decorator): Abstracts raw Redis listening loops.
    2. **`@with_retry`** (Decorator): Standardizes transient failure resiliency.
    3. **`ask_structured()`** (Method): Enforces strict Pydantic JSON outputs with automatic retry/correction loops.
    4. **`register_tool()` / `connect_mcp_server()`** (Methods): Standardizes OpenTelemetry tracing and ADK ingestion for all python tools and external MCP servers.

### 23. User Context Propagation (Security & Auth)
*   **Decision:** Standardized `AgentContext` Payload Wrapper.
*   **Rationale:** To safely pass user identity, tenant IDs, and session IDs across the distributed agent fleet, the Chassis requires all inter-agent communication (both REST and Redis) to be wrapped in an `AgentContext` Pydantic model. The Chassis automatically extracts this context on incoming requests and injects it into all outbound requests, ensuring agents never execute actions on behalf of the wrong user.

### 24. Async Dead Letter Queues (DLQs)
*   **Decision:** Automated DLQ Routing in the Consumer Decorator.
*   **Rationale:** To prevent "Poison Pill" tasks (e.g., a corrupted PDF that consistently crashes the parsing agent) from blocking the Redis queue indefinitely, the `@consume_task` decorator has a built-in retry counter. If a task fails `X` times, the Chassis automatically moves the payload to a `<queue_name>_dlq` and emits a critical OpenTelemetry alert for human review.

### 25. Tool Sandboxing (Safe Code Execution)
*   **Decision:** Ephemeral Execution via Isolated MCP Servers.
*   **Rationale:** Agents that execute generated code (like the Evaluator) will **never** run code natively within their own Docker container. We mandate the use of strictly isolated sandboxes (e.g., a dedicated, heavily restricted Docker-in-Docker container running an MCP server). The Agent simply connects to this sandbox via the Chassis `connect_mcp_server()` method to execute code safely.

### 26. Externalized Model Configuration & Dynamic Selection
*   **Decision:** Model names (e.g., `gemini-1.5-pro`) are never hardcoded in Python. They are defined as aliases in the `config.yaml` and initialized via the Chassis.
*   **Rationale:** Allows the entire distributed fleet to upgrade to a new model version (e.g., 1.5 to 2.0) by updating a single configuration file without redeploying code. It also allows agents to dynamically swap between "Pro" and "Flash" aliases mid-flight based on the specific speed/reasoning requirements of an incoming task.

### 27. Configuration-Driven Skill Loading
*   **Decision:** We will define the required skills for an agent as a YAML array in `config.yaml`. The `BaseAgentChassis.build_adk_agent()` method will automatically read this array and equip the skills during initialization.
*   **Rationale:** Promotes 12-factor app principles. Allows us to deploy the exact same compiled Python container but give it entirely different capabilities just by changing the volume-mounted configuration file.

### 28. Configuration-Driven Tool Loading
*   **Decision:** Tools will be defined as an array of strings in the `config.yaml` file. The `BaseAgentChassis` will dynamically import and register these functions from the agent's `tools.py` module during initialization.
*   **Rationale:** Further decouples business capabilities from infrastructure wiring. A developer can build a library of 50 tools in `tools.py`, but only expose 3 of them by editing the YAML configuration file, creating massive flexibility for deploying different agent profiles without changing Python code.

### 29. Multi-Queue Consumption (Priority Routing)
*   **Decision:** Agents are permitted to consume from multiple Redis queues simultaneously using the `@chassis.consume_task` decorator.
*   **Rationale:** Enables priority routing (e.g., a `research_urgent` queue vs a `research_batch` queue) and allows a single agent microservice to handle distinct task schemas with different Python handler functions, resolving priority bottlenecks.

### 30. Externalize Agent Name in Configuration
*   **Decision:** The `agent_name` is now externalized and defined strictly inside the `config.yaml` file (`agent: name: "research_agent"`).
*   **Rationale:** Further decouples Python code from environment-specific or deployment-specific identifiers. Allows deploying the exact same Python code as two differently named agents just by swapping the mounted YAML configuration.

### 31. Chassis Boilerplate Abstractions
*   **Decision:** Added three "Mega-Abstractions" to the Chassis to reduce developer boilerplate: `async with chassis.state_manager()`, `await chassis.execute_task()`, and Auto-Reply Webhooks.
*   **Rationale:** Shrinks the `agent.py` code from ~30 lines of boilerplate down to ~5 lines of pure business logic. This creates the ultimate Developer Experience (DX) and drastically reduces the surface area for AI coding assistants (like Antigravity CLI) to hallucinate bad infrastructure code.

### 32. Decorator-Injected State Management
*   **Decision:** We abstracted state management directly into the `@chassis.consume_task` decorator via the `state_model` parameter.
*   **Rationale:** Pushes Developer Experience (DX) to the absolute maximum. The AI CLI now writes literally zero infrastructure or state-lifecycle boilerplate inside the function body, focusing 100% on business logic. The decorator handles loading, injecting, and saving the state automatically.

### 33. Zero-Boilerplate Initialization and Context Auto-Injection
*   **Decision:** Moved `build_adk_agent()` directly into the `BaseAgentChassis.__init__()` and updated `execute_task()` to automatically inject `AgentContext` variables into Jinja prompts.
*   **Rationale:** The developer now instantiates the chassis with a single line (`chassis = BaseAgentChassis()`) and no longer needs to manually pass `user_id` or `session_id` into prompt variables. The mathematical minimum of code is now required to define an agent.

---

## ⏳ Pending Decisions & Open Questions (The Deep Dive Queue)

*The queue is currently empty. The architectural baseline is fully defined.*

## Decision #34: Hierarchical Configuration (Fleet vs. Agent)
**Date:** 2026-04-09
**Context:** Many configuration values (Database URIs, Redis Endpoints, Telemetry URLs, Default Model Aliases) are universal across the entire fleet of agents. Requiring developers to copy-paste these into every single agent's `config.yaml` violates DRY principles and makes rotating credentials difficult.
**Decision:** We will implement a **Hierarchical Configuration Pattern**. The `BaseAgentChassis` will automatically read a global `/app/fleet.yaml` file (mounted to all containers) and deeply merge it with the local `/app/config.yaml` file.
**Rationale:** This allows 99% of agents to have a tiny `config.yaml` containing only their specific name, skills, and tools. If an agent *needs* to override a global default (e.g., pointing to a specific isolated database), they simply define it in their local `config.yaml`, which takes precedence over the fleet config.
## Decision #35: Database Interface Segregation (Repository Pattern)
**Date:** 2026-04-10
**Context:** Tying the `BaseAgentChassis` universal core directly to `asyncpg` or Postgres-specific JSONB features creates a massive blast radius if the infrastructure environment changes (e.g., corporate mandates MongoDB or Pinecone). 
**Decision:** We enforce the Abstract Repository Pattern. We removed `self.db_pool` and replaced it with `self.state_store_client` and `self.vector_store_client`.
**Rationale:** The Universal Core must only speak in Pydantic models and standard Python types. The Operational Adapters handle translating these Python objects into the specific database queries. This guarantees that if Postgres is ripped out, zero agent business logic needs to be rewritten.