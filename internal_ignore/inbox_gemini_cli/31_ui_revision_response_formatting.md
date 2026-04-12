# Payload: Fix UI Response Formatting & Polish Chat Interface

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. We are keeping this fix within the current track (`track/fix_studio_ui_20260411`).

The routing is working perfectly, but we have a few UI and formatting issues to clean up in `src/universal_core/chassis.py`.

**Task 1: Fix JSON Response Formatting**
When the consumer function returns its result (which is a Pydantic model or dict), do not just dump the raw JSON string to the frontend (e.g., `**Agent executed successfully:** \`\`\`json ... \`\`\``). 
Add a final synthesis step in the `/chat` endpoint. Pass the JSON result back to `self.llm.generate_content()` with a prompt like: "Synthesize this structured agent payload into a friendly, conversational reply for the user." Return this clean, conversational string to the frontend.

**Task 2: Update Chat Avatars/Names**
In the HTML/Alpine.js frontend, update the chat bubble labels:
- Instead of showing 'u', spell out **"You"** for the user's messages.
- Instead of showing 'S', dynamically inject the Agent's actual name from the chassis configuration (e.g., `self.config.get('agent', {}).get('name', 'Agent')`), or at least spell out the full name instead of a single letter.

**Task 3: System Diagnostic Welcome Message**
Currently, the first message in the chat is a generic greeting placeholder. Update the initial Alpine.js `messages` array so the first message is a **System Note** providing debugging details about the loaded agent. 
Use Jinja templating in the FastAPI HTML response to inject these details dynamically. For example: 
`"**System Note:** Loaded Agent: {agent_name} | Model: {model_name} | Status: Ready for input."`

Execute these fixes, commit the changes, and drop a message in the scribe inbox when complete.