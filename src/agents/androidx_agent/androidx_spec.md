# AndroidX Intelligence Agent (Codelab 3 - Checkpoint 1)

## Overview
The `androidx_agent` is a DevRel assistant designed to interact with the AndroidX monorepo. Because operations on large repositories (like indexing) can take a long time, this agent must demonstrate asynchronous task handling using the `BaseAgentChassis` queue capabilities.

## Checkpoint 1 Goal
Build the skeleton of the `androidx_agent` and prove the async queue functionality. We will implement a mock long-running tool to ensure the Agent Studio UI remains responsive.

## Architecture & Constraints
- **Framework:** Google ADK via `BaseAgentChassis`.
- **Location:** `src/agents/androidx_agent/`
- **State Model:** Needs a Pydantic state model (`AndroidXState`) that tracks the status of background jobs (e.g., `is_indexing: bool = False`, `last_index_time: str = ""`).
- **Prompt:** Externalized to `src/agents/androidx_agent/prompts/system.md`.

## Required Tools
1. **`index_repository` (Mock):** 
   - A tool that simulates downloading and indexing a large repository.
   - It should use `@chassis.consume_task(state_model=AndroidXState)` or similar async routing to run in the background.
   - For this checkpoint, it should simply `asyncio.sleep(10)` to simulate a 10-second long-running task.
   - It must update the agent's state (e.g., setting `is_indexing = True` at the start, and `False` upon completion) so the UI can reflect the status.
   - *Constraint:* Do not use real Redis or Postgres. Rely on the chassis's mock infrastructure for local development.

## Implementation Steps (Layer-by-Layer)
1. Define the Pydantic `AndroidXState` and tools in `agent.py`.
2. Write the Jinja prompt in `prompts/system.md` instructing the agent to use the async tool when asked to index.
3. Configure the agent in `config.yaml` to register the agent and its tools.
4. Test via the Agent Studio UI to ensure the UI does not freeze when the indexing task is requested.