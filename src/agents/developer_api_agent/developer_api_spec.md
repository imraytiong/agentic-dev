# Developer API Intelligence Agent (Codelab 3 - Checkpoint 1)

## Overview
The `developer_api_agent` is an API maintainer assistant designed to interact with massive monorepos (we use AndroidX as our primary example). Because operations on large repositories (like cloning or diffing) can take a long time, this agent must demonstrate asynchronous task handling using the `BaseAgentChassis` queue capabilities.

## Checkpoint 1 Goal
Build the skeleton of the `developer_api_agent` and prove the async queue functionality. We will implement a `sync_repository` tool that actually clones the AndroidX repository to the local disk, tracking its state so the Agent Studio UI remains responsive during the 2-minute download.

## Architecture & Constraints
- **Framework:** Google ADK via `BaseAgentChassis`.
- **Location:** `src/agents/developer_api_agent/`
- **State Model:** Needs a Pydantic state model (`DeveloperAPIState`) that tracks the status of the repository (e.g., `repo_status: str = "not_cloned"` -> `"cloning"` -> `"ready"`).
- **Prompt:** Externalized to `src/agents/developer_api_agent/prompts/system.md`.

## Required Tools
1. **`sync_repository`:** 
   - A tool that ensures the massive local repository (`/tmp/androidx-source`) exists.
   - It should use `@chassis.consume_task(state_model=DeveloperAPIState)` or similar async routing to run in the background.
   - **State Management:** It must first check if the directory `/tmp/androidx-source` exists. If it does, update the state to `"ready"` and return immediately.
   - **Async Execution:** If it doesn't exist, update state to `"cloning"`, run `subprocess.run(['git', 'clone', 'https://android.googlesource.com/platform/frameworks/support', '/tmp/androidx-source'])`, and then update state to `"ready"`.
   - **Logging:** Use Python's `logging` module or `print()` statements to log "Starting clone..." and "Clone complete..." so the user can see progress in the terminal.
   - *Constraint:* Do not use real Redis or Postgres. Rely on the chassis's mock infrastructure for local development.

2. **`local_git_executor` (Future Checkpoints):**
   - We will eventually build a tool that uses `subprocess.run` to execute real `git log` and `git diff` commands against the `/tmp/androidx-source` repository.

## Implementation Steps (Layer-by-Layer)
1. Define the Pydantic `DeveloperAPIState` and tools in `agent.py`.
2. Write the Jinja prompt in `prompts/system.md` instructing the agent to use the async tool when asked to sync or initialize the repo.
3. Configure the agent in `config.yaml` to register the agent and its tools.
4. Test via the Agent Studio UI to ensure the UI does not freeze when the sync task is requested, and watch the terminal logs to verify the clone is happening.