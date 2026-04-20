# Task: Create Mac Mini Local Infrastructure Environment Manifest (Phase 1 & 1.5)

**Context:** We are executing Phase 1 and 1.5 of the `src/infrastructure/mac_mini_spec.md`. We need to lay down the local environment contract before writing any Python adapter code. As the Resident Container Expert and CTO, we are enforcing the use of OrbStack, macOS native sandboxing, and a seamless developer experience.

**Objective:** Create a `compose.yaml` file at the root of the project to orchestrate the local infrastructure required for the Mac Mini adapters via OrbStack. Create a macOS Seatbelt profile to sandbox the Python agent, and a DevEx wrapper to make it easy to run.

## Requirements for `compose.yaml`:
1. **PostgreSQL with pgvector (Tuned for Mac Mini):**
   - Image: Use an official or trusted OCI-compliant image that bundles Postgres 16+ with the `pgvector` extension (e.g., `pgvector/pgvector:pg16`).
   - Ports: Expose `5432:5432`.
   - Volumes: 
     - Mount a local directory (e.g., `./.data/postgres:/var/lib/postgresql/data`) for persistence.
     - **DBA Mandate:** Mount an initialization script directory (e.g., `./infrastructure/db_init:/docker-entrypoint-initdb.d`) so the database self-bootstraps.
   - Command Overrides: Tune the database for the Mac Mini unified memory right in the compose file. Add arguments: `command: ["postgres", "-c", "shared_buffers=1GB", "-c", "work_mem=64MB"]`.
   - Environment: Set up default development credentials (e.g., user, password, db name).
   - Healthcheck: Must include a robust `pg_isready` healthcheck.

2. **Redis:**
   - Image: Use the official `redis:alpine` image.
   - Ports: Expose `6379:6379`.
   - Volumes: Mount a local directory (e.g., `./.data/redis:/data`) for persistence.
   - Healthcheck: Must include a `redis-cli ping` healthcheck.

## Requirements for `mac_agent_sandbox.sb`:
- Create a macOS native sandbox profile (`sandbox-exec` compatible).
- **Network:** Allow outbound network connections (for API calls to LLMs and local Postgres/Redis).
- **Filesystem:** 
  - Deny all filesystem writes by default.
  - Explicitly allow read/write access ONLY to the project/vault directory and necessary temporary/cache directories.
  - Allow read-only access to necessary system libraries (Python binaries, etc.).

## Requirements for DevEx Wrapper (`Makefile`):
- Create a simple `Makefile` at the project root to abstract the developer workflows.
- Must include a `run-sandboxed` target that executes the agent using: `sandbox-exec -f infrastructure/mac_agent_sandbox.sb python main.py`
- Must include `up` and `down` targets for the OrbStack compose file.

## Artifacts to Generate:
1. **`compose.yaml`**: The root docker-compose file meeting the constraints above.
2. **`infrastructure/db_init/01_init.sql`**: A bootstrap script that automatically runs `CREATE EXTENSION IF NOT EXISTS vector;`.
3. **`infrastructure/mac_agent_sandbox.sb`**: The Seatbelt profile to lock down the agent process.
4. **`Makefile`**: The developer experience wrapper for seamless execution.

## Architectural Constraints:
- **Strict Native Virtualization:** We are using **OrbStack**. Do not use any Docker Desktop proprietary extensions. Podman is strictly forbidden as it is flaky.
- **No Business Logic:** This file is strictly for infrastructure orchestration and OS-level security.

**Output:** Generate the `compose.yaml`, `01_init.sql`, `mac_agent_sandbox.sb`, and `Makefile`. Once completed, update the execution plan in `src/infrastructure/mac_mini_spec.md` to mark Phase 1 and 1.5 as complete.