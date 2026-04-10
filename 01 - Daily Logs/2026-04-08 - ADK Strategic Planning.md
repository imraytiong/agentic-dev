# 2026-04-08 - ADK Strategic Planning & Architectural Gaps

**Tags:** #planning #adk #architecture #python
**Status:** Initial Draft

## 1. The ADK Baseline (What we get out of the box)
By committing to the **Google Agent Development Kit (ADK)**, we have a solid, idiomatic foundation for:
- **Multi-agent orchestration** (sub-agents, routing)
- **Model-agnostic execution** (via LiteLLM)
- **Multimodal streaming** natively
- **Human-in-the-Loop (HITL)** flows
- **Vertex AI Agent Engine** deployment readiness

## 2. The "Unprescribed" Zones (Architectural Gaps & Decisions)
ADK is intentionally modular, which means it leaves several critical system components up to the developer. Since our stack is strictly **Python**, we need to define our standard complementary patterns for the following areas:

### A. Long-Term Memory & State Persistence
- **The Gap:** ADK handles immediate session/context memory well, but doesn't prescribe how to persist state across sessions, user profiles, or long-term episodic memory.
- **Pythonic Options:** 
  - *Relational/Metadata:* PostgreSQL + SQLAlchemy (or SQLModel).
  - *Semantic/Vector:* pgvector, Pinecone, or Milvus integration.
- **Decision Needed:** What is our default database stack for persistent agent memory?

### B. Advanced RAG (Retrieval-Augmented Generation)
- **The Gap:** ADK agents can call search tools, but ADK itself isn't a document parsing/chunking/embedding framework.
- **Complementary Pattern:** Wrap **LlamaIndex** (Python) inside an ADK Tool. LlamaIndex handles the heavy lifting of data ingestion, chunking, and semantic search, returning clean text to the ADK agent.
- **Decision Needed:** Do we standardize on LlamaIndex for RAG tools, or build custom lightweight vector retrievers?

### C. Observability, Logging, & Tracing
- **The Gap:** When multi-agent systems fail or hallucinate, standard `logging` isn't enough. We need to trace the exact chain of thought, tool inputs, and sub-agent handoffs.
- **Complementary Pattern:** OpenTelemetry natively, or an LLM-specific observability platform like **Arize Phoenix** or **LangSmith** (which have great Python SDKs).
- **Decision Needed:** Which telemetry stack will we use to trace ADK executions?

### D. Testing & Evaluation
- **The Gap:** How do we assert that an agent behaves correctly before deploying?
- **Complementary Pattern:** 
  - *Unit Testing:* `pytest` for testing individual Python tools (mocking the LLM).
  - *Agent Eval:* Frameworks like **DeepEval** or **Ragas** to score the agent's actual outputs (faithfulness, answer relevance).
- **Decision Needed:** Establish our CI/CD testing baseline.

### E. Prompt & Configuration Management
- **The Gap:** Where do system prompts live? Hardcoded in Python files, or externalized?
- **Best Practice:** Keep prompts as configuration (e.g., YAML or specialized `.txt`/`.jinja` files) loaded at runtime, keeping Python code strictly for logic.

## 3. Python Development Standards
To keep our agents robust, we will enforce:
- **Dependency Management:** `uv` or `Poetry` (fast, reproducible builds).
- **Data Validation:** `Pydantic` v2 for all Tool inputs/outputs and state schemas. This guarantees the LLM adheres to strict typing.
- **Linting/Formatting:** `Ruff` (fastest, modern standard).

---
## Next Steps
- [ ] Review the gaps above and make definitive stack choices.
- [ ] Update the `Agent Architecture Spec` template to include sections for State, Observability, and RAG approach.


### F. Agent Lifecycle & Process Management
- **The Gap:** How do we handle cold starting, graceful shutdowns, health checks, and interrupting runaway agents?
- **Complementary Pattern:** Leverage ADK's built-in FastAPI wrapper (`get_fast_api_app`) and standard Python `asynccontextmanager` for lifespan events. Use ADK's native `before/after` callbacks for state flushing, and OpenTelemetry for lifecycle tracing.
- **Decision:** Documented in `[Agent Lifecycle Management](Agent%20Lifecycle%20Management.md)`. We will rely on FastAPI lifespan hooks for initialization/shutdown and ADK's native `/health` endpoints for probes.

### G. Deployment Strategy: Distributed-First Cluster
- **Strategic Decision:** We are adopting a **Distributed-First (Microservices)** architecture from day one.
- **Rationale:** While a monolith is easier to start with, AI agents suffer from unpredictable "Blast Radiuses" (one agent's memory leak or infinite tool loop crashes the whole fleet), resource asymmetry (a routing agent needs fast CPU, a data agent needs massive RAM), and dependency conflicts.
- **Implementation:** We will build a reusable Python `BaseAgentChassis` component. This shared library will abstract away the distributed plumbing (FastAPI lifecycle, OpenTelemetry, health checks, networking) so the developer only focuses on writing the specific ADK logic (prompts, tools, models). 
- **See full breakdown:** [Agent Fleet Deployment Infrastructure](Agent%20Fleet%20Deployment%20Infrastructure.md)

### H. Infrastructure Target: Lightweight & Cloud-Agnostic
- **Strategic Decision:** We are optimizing for a single developer on a Mac Mini, scaling up to small bare-metal Linux clusters. We will avoid cloud-vendor lock-in (no Vertex AI/Cloud Run dependency).
- **Implementation:** We will use **Docker Compose** for local Mac Mini orchestration, and **K3s** (lightweight Kubernetes) or Docker Swarm for the Linux cluster. The `BaseAgentChassis` will ensure all agents are containerized and expose standard health probes, making them perfectly portable between Compose and K3s without code changes. Message brokering will use lightweight self-hosted solutions like Redis or RabbitMQ instead of cloud-managed queues.