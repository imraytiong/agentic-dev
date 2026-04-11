# 4. Deep Topics (Advanced Reading)

**Status:** Post-Hackathon / Homework
**Target Audience:** Agent Developers looking to push the boundaries of their agents.

This guide contains deep-in-the-weeds discussions and advanced techniques that are not required for day one of the hackathon. Come back here when you want to level up your agent's capabilities.

## 1. Advanced Tooling Development

While standard tools just read and write basic state, advanced tools require careful handling of asynchronous execution and external systems.

### Injecting External Clients
When your tool needs to talk to a third-party API (like Salesforce or Jira), do not instantiate the client inside the tool execution. Instead, use the `BaseAgentChassis` dependency injection:
*   Define the client requirement in your `config.yaml`.
*   The Chassis will initialize it once.
*   Access it in your tool via `chassis.get_client("jira")`.

### Complex State Mutations
If a tool needs to perform a complex mutation on the `AgentState` (e.g., updating a nested array of objects based on an external response), use Pydantic's `model_copy(update=...)` to ensure immutability and trigger the state history tracker correctly, rather than mutating the dictionary directly.

## 2. Advanced RAG Integration within Tools

Retrieval-Augmented Generation (RAG) doesn't have to be a monolithic step. You can build specific tools that allow the agent to query semantic memory dynamically.
*   **Vector Search Tooling:** Expose a `search_corporate_wiki(query: str, limit: int)` tool.
*   **Self-Correction:** Build the tool to return not just the text, but a confidence score. If the score is low, the agent can autonomously decide to broaden its search.

## 3. Human-in-the-Loop (HITL) Interruptions

For high-stakes actions (like transferring funds or emailing a client), your tool should not execute immediately.
*   Instead of executing, the tool updates the state to `status: PENDING_APPROVAL`.
*   It drops a message into the UI (via the Agent Studio or MCP).
*   The agent suspends execution until the human clicks "Approve", which sends a webhook back to the FastAPI endpoint to resume the workflow.