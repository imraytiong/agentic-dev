# Scribe Note: Mac Mini Adapters (Phase 2 Revisions)

**Track:** `mac_mini_infra_20260419`
**Branch:** `feat/mac-mini-infra`
**Status:** Revisions Complete (Architect, DBA, Container, Test Lead, CTO Mandates)

## Summary of Completed Actions
We have refactored the Python operational adapters and test suite to address the critical violations identified during the deep review.

### Artifacts Updated:
1. **Universal Core (`src/universal_core/interfaces.py`):**
   - Moved the `ILLMProvider` interface to the Universal Core to correct the leaked port definition.
2. **Postgres Adapter (`src/infrastructure/adapters/postgres_adapter.py`):**
   - Implemented strict IoC injection for the connection string (removed `os.getenv`).
   - Integrated `pgvector.asyncpg` and successfully registered the vector type.
   - Enforced strict DBA connection limits (`min_size=1`, `max_size=20`).
3. **Redis Adapter (`src/infrastructure/adapters/redis_adapter.py`):**
   - Implemented strict IoC injection for the connection string (removed `os.getenv`).
4. **LiteLLM Adapter (`src/infrastructure/adapters/litellm_adapter.py`):**
   - Implemented strict IoC injection for the budget limit while preserving FinOps tracking logic.
   - Refactored to inherit from the newly moved `ILLMProvider` interface.
5. **DevEx Wrapper (`Makefile`):**
   - Separated execution contexts to run `make test` outside the `sandbox-exec` wrapper, allowing `testcontainers` socket access without compromising production security.
6. **Test Suite (`tests/infrastructure/test_mac_mini_adapters.py`):**
   - Refactored to inject dynamic container URIs into adapter constructors.
   - Added concrete `pgvector` similarity search integration tests.
   - Verified chaos recovery and budget enforcement logic.

**Verification:** `make test` executed successfully with 4/4 passing tests.

**Pending Action:** Awaiting final sign-off before proceeding to Phase 5 (IoC Integration) or merging.