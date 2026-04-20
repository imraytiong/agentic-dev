# Scribe Note: Mac Mini Infrastructure Provisioning (Phases 1, 1.5, 2)

**Track:** `mac_mini_infra_20260419`
**Branch:** `feat/mac-mini-infra`
**Status:** Ready for Review (Pre-Verification)

## Summary of Completed Actions
We have successfully executed the foundational Layer 2 environment manifests for the Mac Mini infrastructure, strictly adhering to the architectural constraints (OrbStack, Hexagonal boundaries) and deep-review mandates from the leadership team.

### Artifacts Delivered:
1. **Zero-Touch Database Initialization (`infrastructure/db_init/01_init.sql`):** 
   - Implemented automatic enabling of `pgvector`.
   - Defined the foundational `state_records` schema with HNSW index for `IVectorStore` and GIN index for `IStateStore` JSONB data.
2. **macOS Native Sandboxing (`infrastructure/mac_agent_sandbox.sb`):** 
   - Authored a `sandbox-exec` compatible Seatbelt profile explicitly permitting `mDNSResponder`, local binding, and outbound TCP to ports 5432 (Postgres), 6379 (Redis), and 443 (HTTPS).
   - Restricted file system access to read-only project roots with explicit write allowances for `.data/` and `tmp/`.
3. **OrbStack OCI Manifest (`compose.yaml`):** 
   - Provisioned `pgvector/pgvector:pg16` and `redis:alpine` containers.
   - Enforced strict DBA tuning for Postgres via `command` overrides: `shared_buffers=1GB`, `work_mem=64MB`, and `max_connections=100`.
4. **DevEx Wrapper (`Makefile`):** 
   - Created `up` and `down` targets for compose management.
   - Built a `run-sandboxed` target that enforces critical environment variables (`ADK_ENV=mac_local`, `LITELLM_BUDGET=1.00`, etc.) during agent execution.
5. **Test Fixtures & Dependencies (`requirements.txt`, `tests/infrastructure/test_mac_mini_adapters.py`):** 
   - Added testing dependencies (`testcontainers`, `vcrpy`, `toxiproxy-python`).
   - Implemented zero-mock `PostgresContainer` and `RedisContainer` fixtures.
   - Established structured test stubs for Idempotency, Chaos Recovery, and VCR routing verification.
6. **Sandbox Validator (`infrastructure/verify_sandbox.py`):** 
   - Delivered a Python utility to empirically validate the Seatbelt profile's network and filesystem constraints.
7. **Specification Updated:** 
   - Marked Phases 1, 1.5, and 2 as complete in `src/infrastructure/mac_mini_spec.md`.

**Pending Action:** The branch is awaiting review by another agent before proceeding to the active verification phase (`make up` and running the validator).