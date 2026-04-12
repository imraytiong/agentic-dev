# Payload: UI Revision 6 - Read Agent Name from Config

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. We are keeping this fix within the current track (`track/fix_studio_ui_20260411`).

The UI is working, but it is currently displaying the agent name as the module/folder name (e.g., `hello_chassis` or `hello_sparky`) instead of the actual human-readable name defined in the YAML configuration.

**The Fix:**
In `src/universal_core/chassis.py` inside the `GET /studio` endpoint (or wherever you are defining `agent_name` for the string replacements):
Ensure that `agent_name` is pulled dynamically from the loaded configuration dictionary, NOT derived from the class name, module name, or folder path.

*Example:*
```python
# Extract it from the merged config
agent_name = self.config.get("agent", {}).get("name", "Unknown Agent")
```

Execute this fix so the UI correctly displays "Sparky" (as defined in `config.yaml`), commit the changes, and drop a message in the scribe inbox.