# Developer API Intelligence Agent (Codelab 3 - Checkpoint 1)

## Overview
The `developer_api_agent` is an API maintainer assistant designed to interact with massive monorepos (we use AndroidX as our primary example). Because operations on large repositories (like indexing or diffing) can take a long time, this agent must demonstrate asynchronous task handling using the `BaseAgentChassis` queue capabilities.

## Checkpoint 1 Goal
Build the skeleton of the `developer_api_agent` and prove the async queue functionality. We will implement a mock long-running tool to ensure the Agent Studio UI remains responsive.

## Architecture & Constraints
- **Framework:** Google ADK via `BaseAgentChassis`.
- **Location:** `src/agents/developer_api_agent/`
- **State Model:** Needs a Pydantic state model (`DeveloperAPIState`) that tracks the status of background jobs (e.g., `is_indexing: bool = False`, `last_index_time: str = ""`).
- **Prompt:** Externalized to `src/agents/developer_api_agent/prompts/system.md`.

## Required Tools
1. **`index_repository` (Mock):** 
   - A tool that simulates scanning the large local repository (`/tmp/androidx-source`).
   - It should use `@chassis.consume_task(state_model=DeveloperAPIState)` or similar async routing to run in the background.
   - For this checkpoint, it should read the provided JSON mock files (`mock_semantic_map.json` and `mock_release_notes.json`) and simulate latency using `await asyncio.sleep(1.5)`.
   - It must update the agent's state (e.g., setting `is_indexing = True` at the start, and `False` upon completion) so the UI can reflect the status.
   - *Constraint:* Do not use real Redis or Postgres. Rely on the chassis's mock infrastructure for local development.
2. **`local_git_executor` (Future Checkpoints):**
   - We will eventually build a tool that uses `subprocess.run` to execute real `git log` and `git diff` commands against the `/tmp/androidx-source` repository.

## Implementation Steps (Layer-by-Layer)
1. Define the Pydantic `DeveloperAPIState` and tools in `agent.py`.
2. Write the Jinja prompt in `prompts/system.md` instructing the agent to use the async tool when asked to index.
3. Configure the agent in `config.yaml` to register the agent and its tools.
4. Test via the Agent Studio UI to ensure the UI does not freeze when the indexing task is requested.