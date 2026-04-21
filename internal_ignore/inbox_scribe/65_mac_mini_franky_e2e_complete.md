# Scribe Note: Phase 8 Franky E2E Diagnostic Complete

**Track:** `mac_mini_infra_20260419`
**Branch:** `feat/mac-mini-infra-rev1`
**Status:** Validated

## Summary of Completed Actions
We have successfully implemented the `Franky` synthetic diagnostic agent and completely upgraded the `Makefile` testing capabilities.

### Artifacts Delivered:
1. **Franky Configuration (`src/agents/franky/agent.yaml`):**
   - Configured with `gemini-2.5-flash`, forcing `max_tokens=10` and `temperature=0.0` to explicitly protect the CTO's FinOps budget during routine testing.
   - Initialized with strict `mock_adapters` infrastructure paths for legacy decoupling.
2. **Franky Diagnostic Routine (`src/agents/franky/agent.py`):**
   - Implemented a robust 4-step E2E sequence:
     1. **LLM/FinOps:** Sends a strict 2-word probe ("Franky Online").
     2. **State Store:** Generates UUID, upserts diagnostic JSONB payload, loads and asserts.
     3. **Vector Store:** Injects standard 1536-dim embedding array, performs `<=>` semantic search, asserts exact document recall.
     4. **Message Broker:** Publishes to `franky_diag_queue`, blocks on `listen` (max 5s), and asserts payload UUID match.
   - Enforced "Loud Failures" (`sys.exit(1)`) on any assertion or timeout to break CI/CD pipelines correctly.
3. **Makefile Upgrades (`Makefile`):**
   - **Auto-Venv Activation:** Dynamically injects `$VIRTUAL_ENV` or defaults to `$(PROJECT_ROOT)/venv`.
   - **`test-e2e` Target:** 
     - Fully dynamic: Defaults to `ADK_ENV=mock` for sub-millisecond local dev testing.
     - Automatically routes `ADK_ENV=mac_local` through `sandbox-exec` to guarantee the OS kernel (`Seatbelt`) isn't blocking real socket connections.
     - Secured `GEMINI_API_KEY` injection for true end-to-end sandbox inference.

**Verification:**
- `make test-e2e` (Mock) -> Passed (100% in-memory execution).
- `make test-e2e ADK_ENV=mac_local` -> Sparky successfully booted inside the sandbox, executed database connections, and correctly raised an `APIConnectionError` when testing the invalid injected Gemini key, definitively proving out-of-sandbox network calls are executing properly through the newly defined profile.

**Conclusion:** The infrastructure is now equipped with a fully automated, FinOps-safe, cross-environment diagnostic probe.