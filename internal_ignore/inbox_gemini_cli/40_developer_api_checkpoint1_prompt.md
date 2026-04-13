# Checkpoint 1: Developer API Agent Skeleton (Async Queues)

Hello Gemini CLI! We are beginning Codelab 3: The Developer API Intelligence Agent. 

Our first goal (Checkpoint 1) is to build the skeleton of the agent and prove that our `BaseAgentChassis` can handle asynchronous tasks without freezing the UI.

Please review the specification at `src/agents/developer_api_agent/developer_api_spec.md`.

**Task:**
1. Create the `developer_api_agent` directory structure under `src/agents/`. (*Note: The mocks directory may already exist here*).
2. Implement the `agent.py` file with the `DeveloperAPIState` Pydantic model.
3. Implement a mock `index_repository` tool. It should read the provided JSON mock files from `src/agents/developer_api_agent/mocks/` (like `mock_semantic_map.json` or `mock_release_notes.json`) and include a realistic `await asyncio.sleep(1.5)` to accurately simulate the latency of long-running tasks. It must update the agent state before and after the sleep.
4. Create the `prompts/system.md` file with instructions for the agent.
5. Update any necessary configuration files (like `config.yaml` or `fleet.yaml` if applicable) to register the new agent.

**Constraints:**
- Strictly follow the `BaseAgentChassis` patterns.
- Ensure the tool uses the appropriate asynchronous decorators/patterns so it runs in the background queue and doesn't block the FastAPI thread.
- Do NOT implement real Git commands or Redis/Postgres infrastructure yet. We are using mock infrastructure for this checkpoint.

Once you have generated the code, please write a summary of what you built into `internal_ignore/inbox_scribe/40_cli_response.md` so I can review it.