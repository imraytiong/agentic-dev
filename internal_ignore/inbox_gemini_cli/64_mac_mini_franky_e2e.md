# Franky E2E Diagnostic Implementation Request

**To: AI CLI**
**From: Architect Lead**

We are implementing a new Synthetic Diagnostic Agent named "Franky" (`src/agents/franky/agent.py`) and a seamless DevEx upgrade for the `Makefile`. 

Please review the following architectural mandates before implementing Phase 1.

### Architect Lead Mandates:
1. **Infrastructure-Agnostic Design:** Franky must be completely ignorant of the underlying infrastructure. He must NOT import `asyncpg`, `redis`, or any specific adapter classes.
2. **Interface-Only Interaction:** Franky's 4-step diagnostic routine must interact exclusively with the Universal Core ports via `self.chassis.state_store`, `self.chassis.vector_store`, `self.chassis.message_broker`, and `self.chassis.llm_provider`. 
3. **Dynamic E2E Target:** The new `make test-e2e` target must support dynamic environment injection. It must work flawlessly whether `ADK_ENV=mock` or `ADK_ENV=mac_local` is passed.

Please acknowledge these constraints and proceed to implement Franky's `agent.yaml` and `agent.py` skeleton.
***

**To: AI CLI**
**From: Test Lead**

### Test Lead Mandates:
1. **The 4-Step Diagnostic Routine:** Franky must execute these exact steps sequentially:
   - **Step 1 (LLM/FinOps):** Send a cheap, low-token prompt (e.g., "You are a diagnostic tool. Reply with exactly two words: 'Franky Online'"). Assert the response matches.
   - **Step 2 (State JSONB):** Generate a random UUID, save a diagnostic JSON payload to `state_store`, immediately read it back, and assert the data matches.
   - **Step 3 (Vector):** Insert a mock embedding array, perform a similarity search, and assert the correct record is returned.
   - **Step 4 (Message Broker):** Publish a diagnostic payload to `message_broker`, consume it, and assert the payload matches.
2. **Loud Failures:** Franky is an automated test. If any assertion fails, or if a component times out, Franky MUST log the exact failure and exit with a non-zero code (e.g., `sys.exit(1)`).
3. **Clean Teardown:** After a successful run, Franky must cleanly disconnect and exit with `sys.exit(0)` so the `Makefile` knows the test passed.
***

**To: AI CLI**
**From: Container Expert**

### Container Expert Mandates:
1. **Auto-Venv Activation:** The developer should not have to manually run `source venv/bin/activate`. Update the `Makefile` so that the `run-sandboxed` and new `test-e2e` targets automatically detect if `$VIRTUAL_ENV` is set. If it is not, the Makefile must automatically locate and use the Python binary inside the local `.venv` or `.pyenv` directory.
2. **True Sandbox Validation:** When `make test-e2e ADK_ENV=mac_local` is executed, Franky MUST be run through the `sandbox-exec` utility using our `mac_agent_sandbox.sb` profile. This proves definitively that the OS kernel is not blocking any of our 4 critical infrastructure components.

***

**To: AI CLI**
**From: CTO**

### CTO Mandates:
1. **FinOps Protection (Cheap Inference):** Franky's health check will run often. Ensure the `agent.yaml` for Franky forces a fast, extremely cheap model (e.g., `gemini-1.5-flash` or `gpt-4o-mini`) and strictly caps the `max_tokens` parameter to 10 or fewer. We do not want to burn API credits on a health check.
2. **DevEx (Make test-e2e):** The new `make test-e2e` target must default to `ADK_ENV=mock` if omitted, ensuring the fastest possible feedback loop. It should also safely pass the `PROJECT_ROOT` and `PYENV_ROOT` variables to the sandbox just like `run-sandboxed` does.

**CLI Execution Directive:**
You now have the complete set of mandates from the Architect, Test Lead, Container Expert, and CTO. 
Please implement Franky (`src/agents/franky/agent.yaml` & `agent.py`) and upgrade the `Makefile` accordingly.