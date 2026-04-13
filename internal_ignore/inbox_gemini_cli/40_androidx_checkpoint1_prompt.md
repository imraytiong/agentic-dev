# Checkpoint 1: AndroidX Agent Skeleton (Async Queues)

Hello Gemini CLI! We are beginning Codelab 3: The AndroidX Intelligence Agent. 

Our first goal (Checkpoint 1) is to build the skeleton of the agent and prove that our `BaseAgentChassis` can handle asynchronous tasks without freezing the UI.

Please review the specification at `src/agents/androidx_agent/androidx_spec.md`.

**Task:**
1. Create the `androidx_agent` directory structure under `src/agents/`.
2. Implement the `agent.py` file with the `AndroidXState` Pydantic model.
3. Implement a mock `index_repository` tool. Instead of a hardcoded 10-second sleep, it should read the provided JSON mock files from `src/agents/androidx_agent/mocks/` (like `mock_github_prs.json` or `mock_semantic_map.json`) and include a realistic `await asyncio.sleep(1.5)` to accurately simulate the latency of pulling from real Google/GitHub APIs. It must update the agent state before and after the sleep.
4. Create the `prompts/system.md` file with instructions for the agent.
5. Update any necessary configuration files (like `config.yaml` or `fleet.yaml` if applicable) to register the new agent.

**Constraints:**
- Strictly follow the `BaseAgentChassis` patterns.
- Ensure the tool uses the appropriate asynchronous decorators/patterns so it runs in the background queue and doesn't block the FastAPI thread.
- Do NOT implement real GitHub API calls or Redis/Postgres infrastructure yet. We are using mock infrastructure for this checkpoint.

Once you have generated the code, please write a summary of what you built into `internal_ignore/inbox_scribe/40_cli_response.md` so I can review it.