---
tags:
  - gemini-scribe/project
---
# Specification: Mac Mini Operational Adapters

## 1. Architectural Overview
This specification defines the operational adapters required to transition the `BaseAgentChassis` from Mock Infrastructure to a fully functional local environment on a Mac Mini (Apple Silicon / ARM64). 

**Core Mandates:**
- **Strict Hexagonal Boundaries:** Adapters must implement Universal Core interfaces (Ports) without bleeding infrastructure logic into the business/agent layer.
- **OCI Compliance & Native Virtualization:** All external dependencies must run in standard OCI containers using **OrbStack** (the premier native macOS virtualization engine) instead of Docker Desktop or Podman (which is flaky).
- **macOS Native Agent Sandboxing:** Python agents must not "go hog wild" on the host OS. The agent processes must be executed inside a macOS native sandbox (`sandbox-exec` / Seatbelt) utilizing a strict `.sb` profile to explicitly allow-list file system and network access.
- **Test-Driven Defense:** Integration tests must utilize `testcontainers` to validate adapters against real ephemeral instances of the infrastructure. Mocking is forbidden in adapter integration tests.
- **Zero-Touch DBA Operations:** The developer (a one-man show) should never have to manually run initialization scripts, tune databases, or manually maintain vector indexes. The local environment must self-bootstrap and self-tune perfectly for an Apple Silicon Mac.
- **Seamless Developer Experience (DevEx):** The one-man show must be able to run, test, and deploy with single commands. Complex sandbox execution strings must be abstracted via a Makefile or runner script.

---

## 2. Adapter Specifications

### 2.1. State & Memory Adapter (PostgreSQL + pgvector)
- **Port Implemented:** `IStateStore` / `IVectorStore`
- **Technology:** PostgreSQL 16+ with the `pgvector` extension.
- **Architecture:** 
  - Use `asyncpg` for asynchronous, non-blocking I/O.
  - State/Memory payloads must be stored in `JSONB` columns for flexible schema evolution.
  - Vector embeddings must utilize `pgvector` (`vector` type) with HNSW indexes for efficient similarity search.
- **DBA Mandates (Zero-Touch & Performance):**
  - **Auto-Initialization:** The container must automatically execute a bootstrap script (`init.sql`) on first boot to execute `CREATE EXTENSION IF NOT EXISTS vector;` and establish the base schemas. No manual DBA intervention allowed.
  - **Mac Mini Unified Memory Tuning:** Default Postgres config is garbage for vector workloads. The container must be explicitly tuned to leverage the Mac Mini's unified memory:
    - `shared_buffers` must be increased (e.g., 1GB to 2GB depending on available RAM).
    - `work_mem` must be heavily increased (e.g., 64MB+) to allow in-memory HNSW index building without spilling to disk.
- **Constraints & Testability:**
  - Must implement robust connection pooling.
  - Must include exponential backoff and retry logic for transient connection drops.
  - **Test Mandate:** Must include concurrency tests asserting safe behavior during simultaneous writes (race conditions).

### 2.2. Message Broker & Async Queue Adapter (Redis)
- **Port Implemented:** `IMessageBroker`
- **Technology:** Redis (latest stable).
- **Architecture:**
  - Use `redis.asyncio` (formerly `aioredis`) for asynchronous communication.
  - Utilize Redis Pub/Sub for ephemeral multi-agent broadcasts, and Redis Streams for durable task queues.
- **Constraints & Testability:**
  - Must gracefully handle connection timeouts. If Redis is unavailable, the agent should fail fast or degrade gracefully, but the `BaseAgentChassis` must not hard-crash.
  - **Test Mandate:** Must prove queue durability under load and verify message acknowledgement (ACK) recovery flows.

### 2.3. LLM Gateway Adapter (LiteLLM)
- **Port Implemented:** `ILLMProvider`
- **Technology:** LiteLLM.
- **Architecture:**
  - Explicitly configured to route to cloud providers (e.g., Google Gemini, OpenAI). 
  - *Decision Record:* Local inference (Ollama/MPS) is explicitly **out of scope** for this phase.
- **FinOps & Security Mandates:**
  - **Budget Controls:** The adapter MUST implement LiteLLM's budget manager or strict token tracking/rate-limiting to prevent runaway agent loops from draining API credits.
  - API keys and routing rules must be strictly injected via environment variables (`.env`), never hardcoded.
- **Constraints & Testability:**
  - **Test Mandate:** Integration tests must NOT hit live cloud APIs (to prevent flaky CI and cost overruns). Must use VCR.py, a local API-compatible stub, or strict contract testing to verify routing and payload formatting.

### 2.4. Telemetry & Observability Adapter
- **Port Implemented:** `ILogger` / `ITelemetry`
- **Technology:** Standard library `logging` / `structlog`.
- **Architecture:**
  - Emit structured JSON logs to standard output (stdout).
  - Let the OCI container runtime capture and route logs. Do not implement complex file-rolling or external log aggregation within the adapter.
- **Constraints & Testability:**
  - **Test Mandate:** Test fixtures must capture `stdout` and assert that critical failure paths emit the exact required structured JSON schema.

---

## 3. Quality Assurance & Test Engineering Mandates (The "Ironclad" Rules)
As the Test Lead, I mandate the following testing strategies be integrated into the implementation definition before a single line of production code is written. "Graceful degradation" is just a theory until proven.

- **Network Fault Injection (Chaos Testing):** `testcontainers` setups for Postgres and Redis MUST include Toxiproxy (or similar network simulation) to actively drop connections, introduce latency, and simulate split-brain scenarios during the test run. We will definitively prove the adapters recover.
- **Zero-Mock Database Integration:** Unit tests can mock the adapter, but the Adapter Integration Tests must use real `testcontainers`.
- **Idempotency Verification:** All Redis Stream consumers and Postgres state upserts must be proven idempotent via automated tests.

---

## 4. Deployment & Bootstrapping (Layer 1)

Before adapter code is written, the environment must be defined.
- **Manifest:** A `compose.yaml` file must be created to orchestrate PostgreSQL (with pgvector) and Redis via OrbStack.
- **macOS Sandbox Profile:** A `mac_agent_sandbox.sb` file must be created to lock down the local Python agent execution using macOS's native `sandbox-exec`, explicitly preventing unauthorized file system or network access.
- **DevEx Runner:** A `Makefile` or shell script must be created to abstract the complexity of running the agent through the sandbox.
- **IoC Configuration:** The `BaseAgentChassis` dependency injection container must be updated to load these adapters dynamically when the environment variable `ADK_ENV=mac_local` is set.

---

## 5. Execution Plan
- [x] **Phase 1:** Create `compose.yaml` for Postgres/Redis OCI containers (via OrbStack), including the zero-touch DBA `init.sql` script.
- [x] **Phase 1.5:** Create `mac_agent_sandbox.sb` profile for native macOS process isolation, and the `Makefile` DevEx wrapper.
- [x] **Phase 2:** Implement Test Fixtures (Testcontainers + Toxiproxy + Local LLM Stub).
- [ ] **Phase 3:** Implement and test the Redis Message Broker Adapter (proving idempotency and fault tolerance).
- [ ] **Phase 4:** Implement and test the Postgres State/Vector Adapter (proving concurrency and fault tolerance).
- [ ] **Phase 5:** Update Chassis IoC to load the new operational adapters.