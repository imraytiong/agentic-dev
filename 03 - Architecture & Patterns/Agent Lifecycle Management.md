# Agent Lifecycle Management

**Tags:** #architecture #adk #lifecycle #python #fastapi
**Status:** Approved Pattern

This document outlines our standard approach for managing the lifecycle of AI Agents built with the Google Agent Development Kit (ADK) in Python. It covers cold starting, graceful shutdowns, health checks, and process management.

## 1. Overview of the ADK Execution Layer
ADK applies a clean, 4-layer architecture (Agent, Tool, Execution, Model). Lifecycle management primarily hooks into the **Execution Layer** (managed by the `Runner` or `FastAPI` server) and the **State/Context** systems (`SessionService`, `MemoryService`).

## 2. Cold Starting & Initialization
When an agent instance boots up, we must ensure all dependencies, connections, and external tools are ready before accepting traffic.

**Standard Pattern:**
*   **FastAPI Lifespan Events:** Since ADK agents are often wrapped in its built-in FastAPI server (`get_fast_api_app`), we use standard FastAPI `@asynccontextmanager` lifespan handlers.
*   **Dependency Injection:** Initialize database connection pools (e.g., SQLAlchemy/pgvector), vector store clients (e.g., LlamaIndex), and external API clients during the startup phase.
*   **Tool Registration:** Pre-register all `FunctionTool` and MCP (Model Context Protocol) tools so they are cached and ready for the `Runner`.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from adk.server import get_fast_api_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize persistent memory connections
    await db_pool.connect()
    # 2. Pre-load cached prompts or RAG indices
    await rag_service.load_index()
    yield
    # 3. Graceful shutdown (see below)
    await db_pool.disconnect()

# Inject into ADK's FastAPI wrapper
app = get_fast_api_app(agent_runner, lifespan=lifespan)
```

## 3. Health Checks & Readiness Probes
Robust health inspection is critical, especially when deploying to Vertex AI Agent Engine or Kubernetes.

**Standard Pattern:**
*   **Native ADK Endpoints:** ADK natively exposes `/health` and `/version` endpoints when using the `adk api_server` CLI or `get_fast_api_app`. We rely on these for basic load balancer liveness probes.
*   **Deep Health Checks:** For readiness probes, we extend the FastAPI app to check downstream dependencies (LLM API connectivity, vector DB health).
*   **Agentic Verification (The "Ralph Loop"):** For complex agents (e.g., coding agents), we utilize ADK's `LoopAgent` to force the agent to verify its own output against objective criteria (e.g., running tests) before returning a "healthy" task completion state.

## 4. State Management During Execution (Event Callbacks)
To manage state cleanly mid-flight, we utilize ADK's event-driven architecture rather than hardcoding state saves into tools.

**Standard Pattern:**
*   Use `before_agent_prompt` callbacks to inject dynamic context or recall long-term memory just before the LLM fires.
*   Use `after_agent_callback` to explicitly flush session data to our persistent database (e.g., PostgreSQL).

## 5. Stopping, Cancelling, & Interruptions
Managing runaway agents and handling user cancellations efficiently to save costs and prevent state corruption.

**Standard Pattern:**
*   **Standard HTTP/SSE Cancellation:** If a user cancels a request, the `asyncio.Task` is cancelled. To prevent the agent's memory from being polluted by a half-finished thought, we use ADK's **Rewind** feature to revert session state, or explicitly set `ctx.end_invocation = True`.
*   **Bidirectional (BIDI) Streaming (Gemini Live):** When using `runner.run_live()`, we execute a *true model stop* by calling `live_request_queue.close()`. This sends a WebSocket close frame, immediately terminating token generation on Google's servers.
*   **Streaming Tools:** For agents monitoring continuous data feeds, equip them with a designated `stop_streaming(function_name)` tool so the agent can autonomously halt the feed once it has sufficient data.
*   **Graceful Shutdown:** Handled via the FastAPI lifespan teardown (closing DB pools, flushing OpenTelemetry logs).

## 6. Observability Integration
As of ADK v1.23, custom tracing is replaced with built-in **OpenTelemetry**.
*   **Standard Pattern:** Ensure the OpenTelemetry exporter is initialized during the cold start. Every step (reasoning, tool invocation, errors) is automatically traced, giving us full visibility into the agent's lifecycle without manual `logger.info()` clutter.
## 7. System-Wide Fleet Orchestration (Multi-Agent Management)
Managing the startup, shutdown, and health of *all* agents across the system requires a coordinated approach, especially when dealing with a complex multi-agent architecture.

**Standard Pattern:**
*   **The Agent Registry:** Maintain a centralized Python registry (e.g., a custom `AgentManager` class or a dependency injection container) that tracks all active agent instances, their configurations, and specific dependencies.
*   **Master Lifespan Manager:** If deploying as a unified service, use a "Master" FastAPI application. The master app's lifespan event iterates through the Agent Registry, triggering the cold-start (initialization) and graceful shutdown (teardown) sequences for *all* registered agents concurrently using `asyncio.gather()`.
*   **Microservice / Distributed Approach:** If deploying agents as individual microservices, rely on infrastructure-level orchestration (like Kubernetes or Vertex AI Agent Engine). The system-wide startup/shutdown is handled by K8s Deployments, which use the individual `/health` probes to ensure the entire fleet is ready before routing traffic via an API Gateway or a central ADK `RouterAgent`.
*   **Fleet Health Dashboard:** Aggregate the health checks of all sub-agents. If a critical sub-agent fails its readiness probe, the Master application should reflect a degraded state, preventing the system from accepting overarching tasks that rely on the failed agent.