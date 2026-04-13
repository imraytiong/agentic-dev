# Checkpoint 1: Developer API Agent Skeleton (Async Queues)

Hello Gemini CLI! We are beginning Codelab 3: The Developer API Intelligence Agent. 

Our first goal (Checkpoint 1) is to build the skeleton of the agent and prove that our `BaseAgentChassis` can handle asynchronous tasks without freezing the UI. To do this, we are going to build a tool that downloads a massive 1.3GB git repository in the background.

Please review the specification at `src/agents/developer_api_agent/developer_api_spec.md`.

**Task:**
1. Create the `developer_api_agent` directory structure under `src/agents/`.
2. Implement the `agent.py` file with the `DeveloperAPIState` Pydantic model (ensure it tracks `repo_status`).
3. Implement the `sync_repository` tool. It must:
    - Run asynchronously in the background queue.
    - Check if the `/tmp/androidx-source` directory exists.
    - If it does not exist, update state to "cloning", use `subprocess.run` to execute the `git clone https://android.googlesource.com/platform/frameworks/support /tmp/androidx-source` command.
    - If it does exist, skip the clone.
    - Update state to "ready" when finished.
    - Include explicit Python `logging` or `print()` statements before and after the clone so the user can see terminal activity during the ~2 minute download.
4. Create the `prompts/system.md` file with instructions telling the agent to always ensure the repository is synced before answering questions about code.
5. Update any necessary configuration files (like `config.yaml` or `fleet.yaml` if applicable) to register the new agent.

**Constraints:**
- Strictly follow the `BaseAgentChassis` patterns.
- Ensure the tool uses the appropriate asynchronous decorators/patterns so it runs in the background queue and doesn't block the FastAPI thread.
- Do NOT implement real Redis/Postgres infrastructure yet. We are using mock infrastructure for this checkpoint.

Once you have generated the code, please write a summary of what you built into `internal_ignore/inbox_scribe/40_cli_response.md` so I can review it.