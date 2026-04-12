# Revision Complete: Agent Routing in Studio UI

I have successfully updated the `/chat` endpoint to route directly to the active agent consumer rather than bypassing it!

## Changes Made in `chassis.py`:
1. Updated the `@consume_task` decorator to attach the `payload_model`, the target `func`, and the `queue_name` metadata to the consumer wrapper inside `self._consumers`.
2. Updated the `chat_handler` (`POST /chat`) to select the first registered consumer.
3. The `/chat` endpoint now correctly builds a prompt, dynamically calls `self.ask_structured(prompt, payload_model)` to extract the user's intent into the agent's expected Pydantic model (e.g., `HelloRequest`).
4. The handler executes the target agent function (`consumer.func(structured_payload, context)`) to fully utilize the system prompt, tools, and state logic built into the agent.
5. The agent's final structured output is correctly formatted into a markdown JSON block and returned to the UI.
6. The test suite ran and all 12 tests passed successfully!

**Branch for Review:** `track/fix_studio_ui_20260411`

Please run the Agent Studio UI locally and verify that the chat accurately flows through the complete agent architecture!