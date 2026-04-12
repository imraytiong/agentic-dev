# Revision Request: Fix Studio UI Routing

The Agent Studio UI is currently bypassing the registered agents. The `/chat` endpoint is sending the raw user message directly to `LlmAgent.generate_content`, which means the agent's system prompt and tools are completely ignored.

**Task:** Update the `/chat` endpoint in `src/universal_core/chassis.py` to correctly route messages to registered consumers.

**Implementation Details:**
1. In the `chat_handler`, check if there is at least one registered consumer in `self._consumers`.
2. Extract the target function and its expected `payload_model` from the consumer wrapper. (You may need to attach the `payload_model` to the wrapper function inside the `consume_task` decorator so the router can access it).
3. Use the chassis's existing `ask_structured` method to dynamically translate the user's raw `message` string into the target agent's `payload_model`. (e.g., "Extract the user's intent from this chat message into the required JSON schema").
4. Execute the consumer function with the generated payload and the context.
5. Return the consumer's response (serialized to a string/dict) back to the UI instead of the generic LLM response.

Do not create a new track. Execute this fix on the current branch (`track/fix_studio_ui_20260411`), commit the changes, and drop a message in the scribe inbox when complete.