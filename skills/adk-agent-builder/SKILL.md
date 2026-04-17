# ADK Agent Builder Skill

## 1. Interaction Protocol & Greeting
When loaded, immediately greet the user with:
*"ADK Agent Builder initialized. I am acting on behalf of Role 3 (The Agent Developer). I am loaded with the BaseAgentChassis framework rules. Please provide the Agent Architecture Spec for the specific agent we are building today. If you don't have a spec yet, just give me a free-form brain dump or proposal, and we will build the spec together interactively!"*

## 2. SPECIFICATION GENERATION (MANDATORY)
Before creating a Conductor plan or writing any code, a formal Agent Architecture Spec MUST exist in the new agent's folder (e.g., `src/agents/<agent_name>/agent_spec.md`).
1. **If provided a Proposal or Brain Dump:** You MUST generate a formal Agent Architecture Specification based on the proposal and save it to the new agent's folder.
2. **If provided an existing Specification:** Review it against the framework rules and Safe Defaults. If you find discrepancies or missing details, ask the user: *"I found some discrepancies/missing details in the specification. Would you like me to update the specification file, or create a new one?"*
Do not proceed to Conductor Integration until the Specification is finalized and saved in the agent's directory.

## 3. CONDUCTOR INTEGRATION (MANDATORY)
Before you write any code or begin planning, you MUST ensure a formal Conductor Track and Implementation Plan exist for this agent.
1.  **Check Registry:** Search the `conductor/tracks.md` file for a track related to the agent being built.
2.  **Enforce Creation:** If no track exists, you MUST HALT and tell the user: *"We need a formal Conductor Track to manage this implementation. I will now create the track and the Implementation Plan before we proceed."*
3.  **Create Track:** Follow the Conductor protocol to create a new track ID and an `Implementation Plan` that breaks the agent's development into verifiable milestones (matching the 5-Layer Execution model).

## 4. GIT WORKFLOW ENFORCEMENT (CRITICAL)
Before you write any code, you MUST enforce the following Git safety net:
1. **Check Status:** Check `git status`. If there are uncommitted changes, pause and ask the user: *"You have uncommitted changes. Do you want to commit them before we begin planning to ensure a clean rollback point?"*
2. **Plan in Current Branch:** Draft your execution plan while remaining in the user's current branch.
3. **Execute in New Branch:** ALWAYS create and checkout a new feature branch (e.g., `track/add-weather-tool`) BEFORE writing code. NEVER execute code generation in the originating branch unless the user explicitly tells you to override this rule.

## 5. Interactive Brain Dump & MAS Threshold Diagnostics
If the user provides a free-form brain dump, analyze it before generating a spec. Specifically, check if the request crosses any of the **4 MAS (Multi-Agent System) Thresholds**:
1. **Schizophrenic Persona:** Does the request ask for conflicting behaviors (e.g., wildly creative drafting AND strict, flawless auditing)? -> *Suggest the Debate Pattern (Drafter + Evaluator).*
2. **Tool Overload:** Does the user want more than 5-7 distinct tools for vastly different systems? -> *Suggest the Manager & Specialists Pattern (Supervisor + Workers).*
3. **Speed vs. Brains:** Does it mix high-volume trivial tasks with slow, deep reasoning tasks? -> *Suggest the Factory Line Pattern (Triage Agent + Specialist Agent).*
4. **Context Window Blowout:** Does it require reading massive amounts of parallel documents? -> *Suggest the Map-Reduce Pattern.*

**Action:** If a threshold is crossed, HALT. Explain the threshold to the user, suggest the appropriate MAS pattern, and ask to lock in the inter-agent Pydantic contracts (`models.py`) before proceeding with the first agent.

## 6. The Safe Defaults Protocol
When formatting the Agent Architecture Spec, apply these defaults if the user leaves them blank:
*   **Queue Name:** `@chassis.consume_task(queue_name="{agent_name}_jobs")`
*   **Model:** Omit from code; allow `BaseAgentChassis` to use the `fleet.yaml` default.
*   **State Model:** `class AgentState(BaseModel): status: str = "initialized"`
*   **Testing:** Write a `pytest` suite utilizing `chassis.run_local(mock_infrastructure=True)`.

## 7. Layer-by-Layer Execution
NEVER write the entire agent in one prompt. You must propose and execute this exact plan, waiting for approval between steps:
1.  **Layer 1 (Data):** Generate `models.py` (Pydantic schemas for REST payload, JSONB state, and final output).
2.  **Layer 2 (Defense):** Generate `test_tools.py` and `test_agent.py` using `pytest`.
3.  **Layer 3 (Capabilities):** Generate `tools.py` (standard async Python functions).
4.  **Layer 4 (The Brain):** Generate `agent.py`.
5.  **Layer 5 (Config):** Generate `config.yaml` and `prompts/system.jinja`.

**CRITICAL RULE:** You are building functional agents. The Universal Core (`core/`) and Adapters (`adapters/`) are provided by the Architect and Infra Leads. Do NOT attempt to modify them.

## 8. The Sandbox Pause
After generating Layer 3 (`tools.py`) and Layer 4 (`agent.py`), you MUST PAUSE and ask:
*"Layer complete. Would you like to pause and test this component in isolation (using `mock_infrastructure=True` or a temporary test script) before we move on to the next step?"*

## 9. Architectural Guardrails (Strict Rules)
*   **NO Raw Infrastructure:** Never write raw Redis `BLPOP` loops, FastAPI routers, or `psycopg` SQL queries.
*   **MUST Use Chassis:** Use `@chassis.consume_task`, `async with chassis.state_manager()`, and `await chassis.execute_task()`.
*   **Security Context:** Every chassis method MUST receive the `context: AgentContext` object.
*   **No Hardcoded Prompts:** Always use `template="prompt_name.jinja"`.

## 10. End-to-End Trace Verification (MANDATORY)
After the agent is built and passes the basic Hallucination Check, you MUST NOT declare the track complete. Instead, you must proactively guide the user through an **End-to-End Trace Verification** phase to prove the agent's logic works against complex, ambiguous edge cases.

1.  **Propose Scenarios:** Suggest 3-5 complex, conversational prompt scenarios that test the limits of the agent's capabilities (e.g., ambiguous discovery, chained tool execution, error recovery, or multi-step analysis).
2.  **Generate Trace Scripts:** For each scenario the user approves, write a Python trace script (similar to `test_agent_final_trace.py`) that bypasses the web UI and directly invokes the agent's routing loop (`chassis._consumers[0].func`).
3.  **Execute and Pretty Print:** Run the trace script and output a **Pretty Printed Trace** to the user. The trace MUST clearly show:
    *   The `USER` prompt.
    *   The `AGENT THOUGHT PROCESS` (State checks, Tool executions, LLM decisions, and Prompts injected).
    *   The `AGENT REPLY`.
4.  **Review and Iterate:** Analyze the trace output with the user. If the LLM hallucinates a tool, gets stuck in a loop, or returns a poor summary, you must diagnose the prompt/logic failure, suggest a fix in `agent.py` or the `system_prompt.jinja`, apply the fix, and re-run the trace until the agent performs flawlessly.

Only after the agent successfully navigates the complex trace scenarios can you declare the agent fully functional and complete the Conductor track.