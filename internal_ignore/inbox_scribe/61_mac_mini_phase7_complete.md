# Scribe Note: Phase 7 Configuration Cleanup & Ops Consolidation Complete

**Track:** `mac_mini_infra_20260419`
**Branch:** `feat/mac-mini-infra-rev1`
**Status:** Validated

## Summary of Completed Actions
We executed a complete cleanup of scattered configuration state and established proper architectural and Ops directory structures.

### Artifacts Delivered:
1. **Tier 1 Configuration (The Physical Realm):**
   - Created `.env.example` consolidating all infrastructure variables (`ADK_ENV`, `ENABLE_STUDIO`, `LITELLM_BUDGET`, `DB_HOST`, `REDIS_HOST`, etc.).
2. **"Dumb" Makefile:**
   - Now automatically sources `.env` via `-include .env`.
   - Replaced hardcoded paths with dynamic `PROJECT_ROOT`, `PYENV_ROOT`, and `VENV_PATH` calculation using `shell pwd`.
   - Replaced hardcoded sparky execution with an `AGENT` parameter (`AGENT ?= src.agents.hello_sparky.agent`).
3. **Portable Sandbox:**
   - Ensured `ops/mac_local/mac_agent_sandbox.sb` strictly relies on parameterized variables injected from the `Makefile` instead of hardcoded paths.
4. **Tier 2 Configuration (The Agent Identity):**
   - Extracted Sparky's configuration into `src/agents/hello_sparky/agent.yaml`.
   - Updated `src/agents/hello_sparky/agent.py` to dynamically load its config block from this YAML.
5. **Ops Consolidation:**
   - Renamed the root `infrastructure/` directory to `ops/mac_local/`.
   - Updated `compose.yaml` to point Postgres to `ops/mac_local/db_init`.
   - This cleanly separates the OS-level operational artifacts (`ops/`) from the Python adapter code (`src/infrastructure/`).
6. **Mock Adapter Relocation (Architectural Purity):**
   - Evicted all `Mock*` concrete classes out of the Universal Core (`src/universal_core/`).
   - Placed them appropriately in `src/infrastructure/adapters/mock_adapters.py`.
   - Updated `BaseAgentChassis` switchboard to import these conditionally.

**Conclusion:** The Mac Mini Infrastructure Track is thoroughly polished and aligned with all ADK architectural principles.
