# 60: Mac Mini Configuration Cleanup & Ops Consolidation

**Priority:** HIGH
**Context:** We need to clean up the scattered configuration state and establish a proper Ops directory structure.

## 1. Implement Tier 1 Configuration (The Physical Realm)
Consolidate all infrastructure variables into `.env` and `.env.template`.
- Ensure `.env` contains: `ADK_ENV`, `ENABLE_STUDIO`, `LITELLM_BUDGET`, `DB_HOST`, `REDIS_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and API keys.

## 2. Implement the "Dumb" Makefile
Update the `Makefile` to:
- `include .env` and `export` its variables.
- Dynamically resolve `PROJECT_ROOT` and `PYENV_ROOT`.
- Accept the `AGENT` variable (defaulting to `src.agents.hello_sparky.agent`) so any agent can be run.

## 3. Implement the Portable Sandbox
Update the `.sb` file:
- Strip out hardcoded username and project paths.
- Replace them with dynamic `(param "PROJECT_ROOT")` and `(param "PYENV_ROOT")` injections from the Makefile.
- Use `string-append` for dynamic write paths.

## 4. Implement Tier 2 Configuration (The Agent Identity)
- Extract Sparky's hardcoded Python configuration into a new `src/agents/hello_sparky/agent.yaml` file.
- Update `src/agents/hello_sparky/agent.py` to load its identity from that YAML file.

## 5. Consolidate Deployment Artifacts (The Ops Pattern)
We currently have a root `infrastructure/` folder for manifests and a `src/infrastructure/` folder for Python code. This is confusing. 
- Rename the root `infrastructure/` folder to `ops/mac_local/`.
- Move `mac_agent_sandbox.sb`, `db_init/01_init.sql`, and `verify_sandbox.py` into `ops/mac_local/`.
- Update the `Makefile` and `compose.yaml` to point to these new paths (e.g., `sandbox-exec -f ops/mac_local/mac_agent_sandbox.sb`).
- This cleanly separates Python adapter code (`src/infrastructure`) from OS/deployment manifests (`ops/`).
## 6. Relocate Mock Adapters (Architectural Purity)
The Universal Core must not contain concrete implementations.
- Move all mock adapter classes (e.g., `MockStateStore`, `MockMessageQueue`, `MockLLMProvider`) out of `src/universal_core/`.
- Relocate them to `src/infrastructure/adapters/mock_adapters.py` (or equivalent).
- Update `src/universal_core/chassis.py` to import these mocks from the `infrastructure/adapters` boundary when `ADK_ENV=mock`.