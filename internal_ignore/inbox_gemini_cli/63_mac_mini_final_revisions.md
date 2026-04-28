# AI Bridge Protocol: Final Polish & Architectural Revisions

**To:** AI CLI Agent
**Context:** We are doing a final, role-by-role architectural review of the `feat/mac-mini-infra-rev1` branch. Please execute the following mandates.

### 🏛️ Architect Lead Mandates
1. **Update YAML Paths:** Update all `infrastructure` paths in `src/agents/hello_sparky/agent.yaml` to point to `src.infrastructure.adapters.mock_adapters...` instead of the old `universal_core` paths.
2. **Refactor Chassis Mock Loading:** Modify the `adk_env == "mock"` logic in `src/universal_core/chassis.py`. The chassis should temporarily inject the mock paths into `self.infrastructure_config` and then call `self._load_adapter()` to instantiate them, removing the static `import` statements from the core engine.

### 🐳 Container Expert Mandates
1. **Ruthless Cleanup:** Recursively delete the legacy `infrastructure/` directory at the root of the repository.
2. **Ops Path Verification:** Update the `Makefile` and `verify_sandbox.py` (if applicable) to strictly reference `ops/mac_local/mac_agent_sandbox.sb` and `ops/mac_local/db_init/`.

### 🗄️ DBA Mandates
1. **Compose Mount Verification:** The CLI MUST update the `compose.yaml` file. The Postgres service volume mount must be changed from `./infrastructure/db_init:/docker-entrypoint-initdb.d` to `./ops/mac_local/db_init:/docker-entrypoint-initdb.d` to ensure the database initializes the vector extension correctly.

### 🧪 Test Lead Mandates
1. **Test Suite Import Refactor:** The CLI MUST perform a global search and replace across the `tests/` directory. All imports of mock adapters must be updated to point to the new location: `from src.infrastructure.adapters.mock_adapters import ...`.
2. **Test Execution Verification:** The CLI must run `make test` (or `pytest`) to explicitly prove that moving the mock adapters did not break the existing unit tests.
### 👔 CTO Mandates
1. **Git Security Check:** The CLI MUST verify that `.env` is explicitly listed in the root `.gitignore` file to prevent leaking database credentials or API keys.
2. **Onboarding Template Verification:** The CLI MUST ensure that `.env.template` contains all the keys required by the `Makefile` and `compose.yaml` (e.g., `ADK_ENV`, `LITELLM_BUDGET`, `DB_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ENABLE_STUDIO`) with safe default values or blank placeholders.