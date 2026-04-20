# AI Bridge Protocol: Mac Mini Infrastructure Execution

**To:** AI CLI Agent
**Context:** We are executing the `mac_mini_infra_20260419` track to build out the local Mac Mini infrastructure.

**Instructions:**
Please execute the implementation plan located at `conductor/tracks/mac_mini_infra_20260419/plan.md`. 

**Critical Constraints (Enforced by Leadership Team Deep Review):**
1. **Container Expert:** The `mac_agent_sandbox.sb` MUST include explicit permissions for `mDNSResponder`, `network-bind`, and explicit TCP outbound rules for ports 5432, 6379, and 443.
2. **DBA:** The `compose.yaml` Postgres tuning MUST use the exact syntax: `command: ["postgres", "-c", "shared_buffers=1GB", "-c", "work_mem=64MB", "-c", "max_connections=100"]`. Do not use a bare string or it will crash. `01_init.sql` must also include the base table schema, not just the extension.
3. **Architect & CTO:** The `Makefile` `run-sandboxed` target MUST pass `ADK_ENV=mac_local` (not `ENV=mac_local`), connection strings, and the `LITELLM_BUDGET=1.00`. You must also create the `verify_sandbox.py` script.
4. **Test Lead:** You must create the `testcontainers` and `toxiproxy` test fixtures, AND include `VCR.py` for LiteLLM, AND include test stubs for Idempotency in `tests/infrastructure/test_mac_mini_adapters.py`.

Execute Steps 1 through 7 in the plan. Report back when complete or if you encounter any issues with the sandbox profile syntax.