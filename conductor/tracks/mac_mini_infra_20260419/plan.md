# Implementation Plan: Mac Mini Local Infrastructure (Phase 1 & 1.5 & 2)

## Context
We are executing Layer 2 (Environment Manifests) of the ADK Infrastructure protocol to provision the local Mac Mini infrastructure using OrbStack. This aligns with `src/infrastructure/mac_mini_spec.md` and incorporates strict mandates from the Architect, Test Lead, DBA, Container Expert, and CTO.

## Execution Steps

1. **Create Database Initialization Script (DBA Mandate):**
   - Create the directory `infrastructure/db_init`.
   - Create `infrastructure/db_init/01_init.sql`.
   - Contents MUST include: `CREATE EXTENSION IF NOT EXISTS vector;` AND the base schema definition for the `IStateStore` (e.g., a `state_records` table with a `JSONB` column and a `vector` column for embeddings).

2. **Create macOS Sandbox Profile (Container Expert Mandate):**
   - Create `infrastructure/mac_agent_sandbox.sb`.
   - Write a `sandbox-exec` compatible profile that strictly allows:
     - **Explicit Network Allowances:** `(allow network-outbound (literal "/private/var/run/mDNSResponder"))`, `(allow network-bind)`, and explicit TCP outbound to ports 5432 (Postgres), 6379 (Redis), and 443 (LiteLLM Cloud APIs).
     - Reading from standard system/Python libraries `(allow file-read* (subpath "/System") (subpath "/Library") (subpath "/usr"))`.
     - Reading the project root.
     - Reading/Writing to `.data/` and `tmp/` inside the project.

3. **Create Compose Manifest (DBA & Container Expert Mandate):**
   - Create `compose.yaml` at the project root for strict OrbStack / OCI compliance.
   - **Postgres Service:** 
     - Image: `pgvector/pgvector:pg16`
     - Ports: `5432:5432`
     - Environment: Explicitly define `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
     - Volumes: Mount `./.data/postgres:/var/lib/postgresql/data` and `./infrastructure/db_init:/docker-entrypoint-initdb.d`.
     - Tuning: **MUST use exact syntax:** `command: ["postgres", "-c", "shared_buffers=1GB", "-c", "work_mem=64MB", "-c", "max_connections=100"]`
     - Healthcheck: `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}`.
   - **Redis Service:**
     - Image: `redis:alpine`
     - Ports: `6379:6379`
     - Volumes: Mount `./.data/redis:/data`.
     - Healthcheck: `redis-cli ping`.

4. **Create DevEx Wrapper (Architect & CTO Mandate):**
   - Create `Makefile` at the project root.
   - Include `up` and `down` targets for Docker Compose.
   - Include `run-sandboxed` target to execute `sandbox-exec -f infrastructure/mac_agent_sandbox.sb python main.py`.
   - **Critical Fix:** The `run-sandboxed` target MUST inject `ADK_ENV=mac_local` (matching the spec exactly), along with `DB_HOST=localhost`, `REDIS_HOST=localhost`, and `LITELLM_BUDGET=1.00`.

5. **Create Test Fixtures (Test Lead Mandate):**
   - Create `tests/infrastructure/test_mac_mini_adapters.py`.
   - Set up tests utilizing `testcontainers` and `toxiproxy` for Postgres and Redis.
   - **Critical Fix:** Must include `VCR.py` setup for stubbing LiteLLM cloud API calls.
   - **Critical Fix:** Must include test stubs for proving Idempotency in Redis stream consumers and Postgres upserts.

6. **Create Sandbox Validation Script (CTO Mandate):**
   - Create `infrastructure/verify_sandbox.py`.
   - A lightweight script that simply attempts to connect to Postgres (5432), Redis (6379), and ping an external HTTPS endpoint to prove the Seatbelt profile allows the required traffic and blocks the rest.

7. **Update Specification Status:**
   - Update `src/infrastructure/mac_mini_spec.md` to check off Phase 1, Phase 1.5, and Phase 2.

## Testing & Validation Strategy
- Verify that `make up` initializes the database (including the schema) and Redis without errors.
- Confirm all containers report "healthy" statuses.
- Run `make run-sandboxed ARGS="infrastructure/verify_sandbox.py"` to prove the sandbox functions correctly.
- Run `pytest tests/infrastructure/test_mac_mini_adapters.py` to prove automated fixture setup, chaos recovery, and VCR.py integration.
- Prove that the agent cleanly blocks LLM requests once the local `LITELLM_BUDGET` threshold is hit.
## Sandbox Fixes
- Added pyenv paths for Python executable
