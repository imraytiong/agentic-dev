# AI Bridge Protocol: Phase 5 - Dynamic IoC Switchboard

**To:** AI CLI Agent
**Context:** We are executing the final phase (Phase 5) of the Mac Mini infrastructure track. The team has decided to retain the mock infrastructure for fast, in-memory prototyping while utilizing the new Mac Mini adapters for the actual execution environment.

**Objective:** Update the dependency injection logic in `BaseAgentChassis` (`src/universal_core/chassis.py`) to act as a dynamic switchboard based on the `ADK_ENV` environment variable.

*Note: `ADK_ENV` is injected at runtime via our `Makefile` (e.g., `make run-sandboxed` sets `ADK_ENV=mac_local`).*

### Mandates:

1. **Mock by Default (Fast Coding):** 
   - If `ADK_ENV` is unset or set to `mock`, the chassis MUST load the `MockStateStore`, `MockMessageQueue`, and `MockLLMProvider` exactly as it did before. This preserves our sub-millisecond local testing feedback loop.

2. **Mac Local Routing (Deployment):** 
   - If `ADK_ENV=mac_local`, the chassis MUST:
     - Read the required connection strings and credentials from the environment variables (`DB_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `REDIS_HOST`, etc.).
     - Instantiate the new `PostgresAdapter`, `RedisAdapter`, and `LiteLLMAdapter` using those strings.
     - Inject them into `self.state_store`, `self.vector_store`, `self.message_broker`, and `self.llm_provider`.

3. **Graceful Fallback & Strict Validation:** 
   - If `ADK_ENV=mac_local` but the required environment variables are missing, the chassis MUST NOT fall back to mocks. It must immediately raise a `ValueError` or `ConfigurationError` so the developer knows their environment is misconfigured.

Execute this update to finalize the Mac Mini infrastructure track!