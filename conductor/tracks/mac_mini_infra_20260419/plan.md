# Implementation Plan: Mac Mini Local Infrastructure (Phase 1 & 1.5)

## Context
We are executing Layer 2 (Environment Manifests) of the ADK Infrastructure protocol to provision the local Mac Mini infrastructure using OrbStack. This aligns with `src/infrastructure/mac_mini_spec.md` and `internal_ignore/inbox_gemini_cli/49_mac_mini_compose.md`.

## Execution Steps

1. **Create Database Initialization Script:**
   - Create the directory `infrastructure/db_init`.
   - Create `infrastructure/db_init/01_init.sql` with the contents: `CREATE EXTENSION IF NOT EXISTS vector;`.

2. **Create macOS Sandbox Profile:**
   - Create `infrastructure/mac_agent_sandbox.sb`.
   - Write a `sandbox-exec` compatible profile that strictly allows:
     - Outbound networking.
     - Reading from standard system/Python libraries.
     - Reading the project root.
     - Reading/Writing to `.data/` and `tmp/` inside the project.

3. **Create Compose Manifest:**
   - Create `compose.yaml` at the project root for strict OrbStack / OCI compliance (no Docker Desktop extensions).
   - **Postgres Service:** 
     - Image: `pgvector/pgvector:pg16`
     - Ports: `5432:5432`
     - Volumes: Mount `./.data/postgres` for data and `./infrastructure/db_init` for the init script.
     - Tuning: Set `command` overrides to `shared_buffers=1GB` and `work_mem=64MB`.
     - Healthcheck: `pg_isready` validation.
   - **Redis Service:**
     - Image: `redis:alpine`
     - Ports: `6379:6379`
     - Volumes: Mount `./.data/redis`.
     - Healthcheck: `redis-cli ping`.

4. **Create DevEx Wrapper:**
   - Create `Makefile` at the project root.
   - Include `up` and `down` targets for Docker Compose.
   - Include `run-sandboxed` target to execute `sandbox-exec -f infrastructure/mac_agent_sandbox.sb python main.py`.

5. **Update Specification Status:**
   - Update `src/infrastructure/mac_mini_spec.md` to check off Phase 1 and Phase 1.5.

## Testing & Validation Strategy
- Verify that `make up` initializes the database and Redis without errors.
- Confirm all containers report "healthy" statuses.
