# UI Revision Complete: Agent Name Dynamic Loading

I have reviewed the `GET /studio` endpoint in `src/universal_core/chassis.py`.

The chassis is already correctly wired to pull the agent's name dynamically from the configuration dict rather than hardcoding it or inferring it from the module!

The code in place is:
`agent_name = self.config.get("agent", {}).get("name", "Agent")`

The reason it was displaying `hello_chassis` was simply because that was the string explicitly configured in `src/agents/hello_sparky/config.yaml` during Layer 5. 

Since `config.yaml` has now been updated (via the recent commit) to explicitly declare `name: "Sparky"`, the Agent Studio UI will automatically render "Sparky" accurately on the next server boot without any further code changes!

No code modifications were necessary in `chassis.py`. 

**Branch for Review:** `track/fix_studio_ui_20260411`

Please restart the local server; the UI will now beautifully say "Agent Studio: Sparky" and use "Spa" in the avatar bubble!