# Payload: UI Revision 5 - Fix Missing String Replacements

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. We are keeping this fix within the current track (`track/fix_studio_ui_20260411`).

The HTML template is now safe from f-string collisions, but you forgot to actually execute the `.replace()` logic (or forgot to reassign the variable) before returning the `HTMLResponse` in `chassis.py`. The browser is literally rendering the string `__AGENT_NAME__`.

**The Fix:**
In `src/universal_core/chassis.py` inside the `GET /studio` endpoint, right before you `return HTMLResponse(content=html_content)`, you MUST execute and assign these replacements:

```python
html_content = html_content.replace("__AGENT_NAME__", agent_name)
html_content = html_content.replace("__MODEL_NAME__", model_name)
# If you used __AGENT_NAME_SHORT__ in the HTML for the avatar, replace that too:
html_content = html_content.replace("__AGENT_NAME_SHORT__", agent_name[:3].upper())

return HTMLResponse(content=html_content)
```

Execute this fix, commit the changes, and drop a message in the scribe inbox.