# Payload: UI Revision 4 - Fix HTML Template Rendering

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. We are keeping this fix within the current track (`track/fix_studio_ui_20260411`).

The previous update mangled the HTML output. The browser is rendering literal strings like `me[:1].upper()}` and `{agent_name}`. 

**The Bug:** You likely used a Python f-string (`f"""..."""`) for the HTML content, which collided with the curly braces `{ }` used by Alpine.js and Tailwind, causing format parsing errors and mangled text.

**The Fix:**
In `src/universal_core/chassis.py` inside the `GET /studio` endpoint:
1. Change the HTML content back to a standard, non-f-string (just `"""..."""`).
2. Inside the HTML string, use explicit placeholder tokens like `__AGENT_NAME__` and `__MODEL_NAME__`.
3. Before returning the `HTMLResponse`, manually perform string replacements to inject the data safely. 
   *Example:*
   ```python
   html_content = html_content.replace("__AGENT_NAME__", agent_name)
   html_content = html_content.replace("__MODEL_NAME__", model_name)
   ```
4. **Fix the Avatars:** Do not try to do inline Python slicing (like `me[:1]`) inside the HTML. Just strictly hardcode the word **"You"** for the user's avatar label, and use the `__AGENT_NAME__` placeholder for the agent's avatar label.
5. **Fix the System Note:** Ensure the initial Alpine.js message array looks exactly like this, using the placeholders:
   ```javascript
   messages: [{ role: "system", content: "**System Note:** Loaded Agent: __AGENT_NAME__ | Model: __MODEL_NAME__ | Status: Ready for input." }]
   ```

Execute these fixes, ensure the HTML string is perfectly clean without syntax leaks, commit the changes, and drop a message in the scribe inbox.