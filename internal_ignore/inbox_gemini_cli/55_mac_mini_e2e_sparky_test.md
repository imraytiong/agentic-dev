# AI Bridge Protocol: Phase 6 - End-to-End Sparky Validation

**To:** AI CLI Agent
**Context:** We have completed the Mac Mini infrastructure track (Phase 1-5). The `BaseAgentChassis` is now a dynamic IoC switchboard. 

**CRITICAL CTO DIRECTIVE regarding Git Operations:**
Because we have critical demos this week, you are **EXPLICITLY FORBIDDEN** from merging the `feat/mac-mini-infra` branch into `main`. The code must remain on this feature branch indefinitely until the user (Ray) explicitly commands a merge.

**Objective:**
Before we consider this track fully validated, we must run a manual, end-to-end test using our existing `hello_sparky` agent running strictly on the new Mac Mini infrastructure.

**Execution Instructions:**
1. **Spin up Infrastructure:** Execute `make up` to start the Postgres and Redis OrbStack containers. Verify they are healthy.
2. **Execute Sparky:** Run the `hello_sparky` agent using the sandboxed environment (e.g., via `make run-sandboxed` or the specific Sparky runner script), ensuring `ADK_ENV=mac_local` is correctly injected.
3. **Verify Observability:**
   - Confirm Sparky successfully connects to Postgres and performs state/vector operations without throwing `DataError` or connection exhaustion.
   - Confirm Sparky successfully publishes and consumes events from the Redis broker.
   - Confirm Sparky successfully routes a call through the LiteLLM adapter without exceeding the budget limit.
   - Confirm the macOS Seatbelt sandbox (`sandbox-exec`) does not block any required network traffic.

Report back with the exact terminal output and logs from the Sparky execution. Do not merge any code.