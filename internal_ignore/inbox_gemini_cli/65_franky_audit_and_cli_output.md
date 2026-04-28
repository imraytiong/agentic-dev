# AI Bridge Protocol: Franky Audit & CLI Instrumentation

**To: AI CLI**
**Context:** We need to audit Franky (`src/agents/franky/agent.py`) and the Operational Adapters to ensure zero infrastructure leakage, and upgrade Franky's output to be highly parseable for AI CLI tools.

Please execute the following brutal mandates from the leadership team:

### 🏛️ Architect Lead Mandates (Portability & Anti-Leakage)
1. **Audit Franky's Payloads:** Review `src/agents/franky/agent.py`. Franky MUST pass standard Python primitives (e.g., `dict` for state payloads, standard `list` of floats for vectors) to the chassis. Remove any `json.dumps()`, `numpy` casting, or backend-specific formatting from Franky's code.
2. **Push Transformation to Adapters:** Ensure the `PostgresAdapter` handles the `json.dumps()` for JSONB and the specific `pgvector` casting internally. Ensure the `RedisAdapter` handles the string/bytes encoding internally. 
3. **Strict Mock Parity:** Ensure the `MockStateStore` and `MockVectorStore` accept those exact same standard primitives. The Mocks MUST `copy.deepcopy()` dictionaries when storing/retrieving to simulate the serialization boundary of a real database and prevent reference-mutation bugs.

### 🧪 Test Lead Mandates (CLI-Friendly Instrumentation)
1. **Structured Output:** Franky must not use standard conversational `print()` statements. Upgrade Franky's output to emit strictly formatted, machine-readable lines (e.g., `[DIAGNOSTIC] STEP=1 COMPONENT=LLM STATUS=PASS LATENCY=120ms`).
2. **Failure Traceability:** If a step fails, Franky must emit a structured error line containing the exact exception type and message (e.g., `[DIAGNOSTIC_ERROR] STEP=3 COMPONENT=VECTOR EXCEPTION=DataError MESSAGE="..."`) before exiting with `sys.exit(1)`.
3. **Strict Exit Codes:** `sys.exit(0)` on perfect success, `sys.exit(1)` on any failure.

### 👔 CTO Mandates (Loud Failures)
1. **Capability Boundaries:** If an adapter (especially a Mock adapter) cannot fulfill a contract (e.g., the Mock doesn't support complex vector distance thresholds), it MUST raise a loud, explicit `NotImplementedError` or a custom `UnsupportedCapabilityError`. 
2. **Zero Polyfills:** The adapter must NEVER fail silently or force the agent to write conditional logic (`if backend == 'mock':`).

**Output:** Execute this audit and refactor across `franky/agent.py`, the Mac Mini adapters, and the Mock adapters. Report back when `make test-e2e` (in both `mock` and `mac_local` modes) passes with the new structured output.