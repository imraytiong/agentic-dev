# AI Bridge Protocol: Mac Mini Adapters Implementation (Phase 2)

**To:** AI CLI Agent
**Context:** We are executing Phase 2 of the `mac_mini_infra_20260419` track. Phase 1 (Environment Manifests and Sandboxing) is complete and verified.

**Objective:** Implement the Python operational adapters that adhere to the Universal Core interfaces (Ports) and fulfill the Chaos Testing requirements.

**Instructions:**
Please write the Python adapter code and finalize the test fixtures based on `src/infrastructure/mac_mini_spec.md`.

**Critical Constraints (Enforced by Leadership Team Deep Review):**

1. **Architect Lead (Strict Hexagonal Boundaries):**
   - Create the Python adapters in `src/infrastructure/adapters/`.
   - They MUST strictly implement the Universal Core interfaces: `IStateStore`, `IVectorStore`, `IMessageBroker`, and `ILLMProvider`.
   - Do NOT leak infrastructure-specific exceptions (e.g., `asyncpg.PostgresError`) into the business logic. Wrap them in standard chassis exceptions.

2. **DBA (Zero-Touch & Performance):**
   - For Postgres State/Vector: Use `asyncpg` (NOT SQLAlchemy).
   - Implement robust connection pooling utilizing the `max_connections=100` we set up in Phase 1.
   - Use raw SQL and `JSONB` for state payloads, and `pgvector` for embeddings.

3. **Test Lead (Chaos & Idempotency):**
   - You MUST fill out the test stubs in `tests/infrastructure/test_mac_mini_adapters.py`.
   - Implement Toxiproxy to actively drop the connection to Postgres and Redis during the test run to prove your retry logic works.
   - Implement `VCR.py` (or a local stub) for the LiteLLM tests. NO LIVE API CALLS IN CI.
   - Prove idempotency for the Redis Stream consumer (ensure duplicate messages are ignored/handled).

4. **CTO (FinOps):**
   - The LiteLLM adapter MUST read and respect the `LITELLM_BUDGET` environment variable passed by the Makefile. Fail gracefully if the budget is exceeded.

**Output:** 
Write the adapter implementations and finalize the test suite. Report back when `pytest tests/infrastructure/test_mac_mini_adapters.py` passes successfully.