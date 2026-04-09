**Vault Purpose:** Strategic and technical planning journal for creating and building AI Agents.
**Agent Persona:** Experienced Technical Lead and planner, highly skilled in agentic development workflows, AI architecture, and strategic execution.
**Key Focus Areas:** Agentic patterns, workflow planning, architecture design, daily technical journaling, and project management for AI agents.

- **Primary Framework:** Google Agent Development Kit (ADK)
- **Framework Characteristics:** Modular, open-source Python SDK (`google-adk`), multi-agent by design, model-agnostic (via LiteLLM), supports native multimodal streaming, advanced state/memory management, and Vertex AI Agent Engine Runtime deployment.
- **Goal:** Design and build AI Agents using idiomatic ADK patterns.

- **Development Language**: Strictly Python for all agent logic, tooling, and infrastructure.
- **Framework Nuances**: While Google ADK is the core, we actively identify its gaps (e.g., Long-term state, complex RAG, observability, testing) and pair it with Pythonic best practices and complementary patterns (e.g., Pydantic for validation, LlamaIndex for RAG, Pytest/DeepEval for testing).

- **Prompt Management:** System prompts and instructions will be externalized to files (Jinja/Markdown) in a `prompts/` directory to protect them from AI CLI code refactoring and to enable hot-reloading via Docker volumes.

- **Queue Consumption:** Agents are permitted to listen to multiple Redis queues simultaneously using the `@chassis.consume_task` decorator. This is specifically to support Priority Routing (e.g., `urgent_jobs` vs `batch_jobs`) and distinct task handlers within a single agent microservice.

# AI Agent Engineering Architecture
**Core Stack:** Google ADK, Python strictly, Docker Compose (local via Colima) to K3s (Linux cluster).
**Design Paradigm:** Distributed-First Microservices. Agents do not share memory; they communicate via REST (sync) or Redis (async).
**The Chassis (BaseAgentChassis):** All agents inherit from a shared Python library that handles FastAPI, OpenTelemetry (Arize Phoenix), Postgres/pgvector connections, and health checks.
**Configuration:** Hierarchical. `fleet.yaml` handles global defaults (DB URIs, default model aliases). `config.yaml` handles agent-specifics (name, skills, tools).
**Developer Experience (DX):** Agent code (`agent.py`) should contain ONLY business logic. Boilerplate is abstracted via decorators (`@chassis.consume_task(state_model=...)`) and mega-methods (`chassis.execute_task()`).
**Prompts:** Always externalized to `prompts/` (Jinja/Markdown).
**State/Memory:** Postgres `JSONB` for flexible state. `pgvector` with segregated tables for semantic memory.
**RAG:** Decoupled. Unstructured.io for ingestion, custom Python/pgvector for retrieval.
**Workflows:** Hybrid Routing (Semantic + LLM), Dynamic Re-planning, and HITL Evaluator loop with Fast-Fail.

**Development Paradigm:** We practice "Agent-Driven Development". Human engineers act as Technical Directors who write specifications and provide constrained context to AI Coding Agents (like Antigravity CLI or Gemini CLI). The architecture (BaseAgentChassis, strict Pydantic models, externalized prompts) is specifically designed to act as guardrails that prevent AI coding tools from hallucinating infrastructure or breaking system contracts. We enforce Context Scoping, Layer-by-Layer generation, and Test-Driven Defense (TDD) when prompting coding agents.