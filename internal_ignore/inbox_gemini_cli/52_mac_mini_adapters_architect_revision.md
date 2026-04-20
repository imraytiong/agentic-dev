# AI Bridge Protocol: Mac Mini Adapters (Phase 2 Revisions)

**To:** AI CLI Agent
**Context:** We are reviewing the generated Phase 3 and 4 adapters (`postgres_adapter.py`, `redis_adapter.py`, `litellm_adapter.py`) and the `Makefile`.

**Status:** The Test Lead and CTO have approved your implementations. However, the **Architect Lead**, **Container Expert**, and **DBA** have identified critical violations that must be resolved before we can proceed to Phase 5.

### 🏛️ Architect Lead Mandates

1. **Leaked Port Definition:** The `ILLMProvider` interface is currently defined *inside* `src/infrastructure/adapters/litellm_adapter.py`. 
   - **Mandate:** An adapter cannot define its own contract. You must move the `ILLMProvider` interface definition to the Universal Core (where the other Ports reside) and import it into the adapter.

2. **Hardcoded Infrastructure Configuration:** Both `PostgresAdapter` and `RedisAdapter` contain hardcoded fallback connection strings and `os.getenv` logic in their `__init__` methods.
   - **Mandate:** This violates Inversion of Control. Adapters must be ignorant of the environment. Remove all `os.getenv` and fallback logic from the `__init__` methods. They must strictly accept a `connection_string` parameter. If the string is missing or `None`, raise a `ValueError` immediately. The logic for reading environment variables belongs exclusively in the IoC container bootstrap layer, not the adapter.

### 🐳 Container Expert Mandates

1. **Test Execution Context Collision:** The `testcontainers` library requires access to the OrbStack/Docker daemon socket to spin up test databases. If tests are run through the `sandbox-exec` wrapper, they will crash with a "Permission Denied" error because the sandbox strictly blocks socket access.
   - **Mandate:** Do NOT punch a hole in the sandbox profile (`mac_agent_sandbox.sb`) for the Docker socket. Doing so is a massive container escape vulnerability.
   - **Mandate:** Update the `Makefile` to strictly separate execution contexts. The `make run-sandboxed` target must continue to use the strict `.sb` profile for agent execution. However, you must ensure that `make test` executes `pytest` *outside* of the `sandbox-exec` wrapper so `testcontainers` can communicate with the OrbStack daemon.

### 🗄️ DBA Mandates

1. **Vector Type Registration Failure:** `asyncpg` does not natively understand `pgvector` data types. If not registered, inserts/queries will crash with a `DataError`.
   - **Mandate:** The `PostgresAdapter` MUST `import pgvector.asyncpg`. Immediately after the `asyncpg.create_pool()` initialization, you MUST execute `await pgvector.asyncpg.register_vector(self.pool)`.

2. **Connection Pool Exhaustion:** The adapter must not exhaust the database connection limits we tuned in Phase 1.
   - **Mandate:** The `asyncpg.create_pool()` call must explicitly define connection limits. Enforce `min_size=1` and `max_size=20`.

3. **Strict Parameterization:** 
   - **Mandate:** Ensure the vector similarity search uses properly cast parameterized queries (e.g., `ORDER BY embedding <=> $1::vector`). Absolutely NO string interpolation for the vector arrays.

**Output:**
Please refactor the adapters and the `Makefile` to resolve these violations. Report back when complete.
### 🧪 Test Lead Mandates

1. **Implement True Toxiproxy:** The test suite MUST spin up a `ToxiproxyContainer` alongside the Postgres/Redis containers. The adapter must connect *through* the proxy, and the test must actively sever the proxy connection (`proxy.down()`) during an active read/write operation to assert the adapter's exponential backoff/retry logic successfully recovers the connection. No more fake connection strings.
2. **Vector Integration Assertion:** The Postgres integration test MUST include a concrete assertion that inserts a mock embedding and successfully retrieves it using the `<=>` operator to prove the DBA's `register_vector` fix works.
3. **IoC Test Injection Update:** All tests must be updated to pass the dynamically generated `testcontainers` connection strings directly into the adapter `__init__` methods to comply with the Architect's new IoC mandate.
### 👔 CTO Mandates

1. **Zero-Friction Testing:** The CLI MUST ensure that despite the addition of Toxiproxy and dynamic IoC injection, the developer experience remains exactly one command: `make test`. The `Makefile` must handle all environment variable injection, pathing, and sandbox bypassing automatically. If `make test` requires manual setup steps, the implementation is rejected.
2. **Preserve FinOps Logic:** While refactoring the `LiteLLMAdapter` to fix the Architect's interface leakage, the CLI MUST NOT accidentally strip out or break the `LITELLM_BUDGET` tracking logic.