---
status: Active
---
# 🏛️ Master Architectural Decision Log (ADL)

**Tags:** #architecture #planning #adr
**Purpose:** Exhaustive snapshot of all strategic technical decisions, and the queue for pending questions.

---

## 🌟 Core Architectural Principles
1. **Open Source & Self-Hosted First:** Avoid commercial SaaS.
2. **Lightweight & Modular:** Avoid bloated frameworks.
3. **Abstracted Plumbing:** Custom agents contain only business logic. Infrastructure belongs in `BaseAgentChassis`.
4. **AI-Assisted Velocity & Defense:** Use AI CLIs (Antigravity/Gemini). Defend against regressions with strict TDD.
5. **Strict Integration Contracts:** Pydantic models for inter-agent API schemas must be heavily locked down.

---

## ✅ Approved Decisions

### Framework & Deployment
1. **Google ADK & Python:** Core framework.
2. **Distributed-First (Microservices):** Prevents monolithic blast radius.
3. **Cloud-Agnostic (Docker Compose -> K3s):** Portability and local testing.
4. **FastAPI & ADK Native Probes:** For lifecycle management and health checks.
5. **Apple Native Virtualization (Colima):** Default container engine, strictly OCI-compliant for Podman portability. (Decision #21)

### Communication & Infrastructure
6. **REST + Pydantic (JSON):** Synchronous inter-agent communication.
7. **Abstracted Message Broker (e.g., Redis):** Asynchronous task queues.
8. **Hierarchical Configuration (Fleet vs. Agent):** Deep merge of global `fleet.yaml` and local `config.yaml`. (Decision #34)
9. **True Inversion of Control (Dynamic Adapter Loading):** `core/` is sealed. Adapters loaded dynamically via config. (Decision #36)

### Data & Memory
10. **PostgreSQL + `pgvector`:** Hybrid approach for state and memory. (Decision #8)
11. **Database Interface Segregation (Repository Pattern):** Universal Core only handles Python/Pydantic objects. (Decision #35)
12. **JSONB Payload:** NoSQL style agent state storage for maximum flexibility. (Decision #17)
13. **Segregated Vector Tables:** Distinct tables for conversations, documents, and instructions. (Decision #18)
14. **Decoupled RAG Architecture:** Unstructured.io for ingestion, custom Python for retrieval. (Decision #9)

### Observability & Testing
15. **Arize Phoenix:** OpenTelemetry observability backend. (Decision #10)
16. **Hybrid Testing (TDD + Golden Evals):** Pytest for deterministic code, LLM-as-a-Judge for prompts. (Decision #11)
17. **Local Testing & Mocking:** `run_local(mock_infrastructure=True)` for terminal testing without databases. (Decision #14)

### Agent Logic & Workflows
18. **Externalized Prompts:** Jinja/Markdown files to protect from AI code refactoring. (Decision #12)
19. **Configuration-Driven Loading:** Skills and Tools dynamically loaded via `config.yaml`. (Decisions #27 & #28)
20. **Dynamic Model Selection:** Models defined as aliases in `config.yaml` and swappable mid-flight. (Decision #26)
21. **Hybrid Supervisor Routing:** Semantic `pgvector` routing with LLM fallback. (Decision #16)
22. **Dynamic Re-Planner Workflow:** Step-by-step planning and evaluation for complex tasks. (Decision #19)
23. **HITL Evaluator-Optimizer:** Escalation to human with Fast-Fail abort. (Decision #20)

### Chassis API Guardrails
24. **Boilerplate Abstractions:** `async with state_manager()`, `execute_task()`, and Auto-Reply Webhooks. (Decision #31)
25. **Decorator-Injected State:** State automatically loaded and saved by `@consume_task`. (Decision #32)
26. **Zero-Boilerplate Init:** Context auto-injection and one-line initialization. (Decision #33)
27. **Strict API Extensions:** `@consume_task`, `@with_retry`, `ask_structured()`, and `connect_mcp_server()`. (Decision #22)
28. **Multi-Queue Consumption:** For priority routing. (Decision #29)
29. **User Context Propagation:** `AgentContext` wrapper for all communication. (Decision #23)
30. **Async DLQs:** Automated Dead Letter Queue routing for poison pills. (Decision #24)
31. **Tool Sandboxing:** Ephemeral execution via isolated MCP servers. (Decision #25)

---

## ⏳ Pending Decisions & Open Questions

*The queue is currently empty. The architectural baseline is fully defined.*