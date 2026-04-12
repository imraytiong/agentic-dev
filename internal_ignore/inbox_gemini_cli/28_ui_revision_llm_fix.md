# Payload: UI Revision & LLM Fix

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. We are keeping this fix within the current track (`track/fix_studio_ui_20260411`).

The UI you built looks fantastic, but there is a critical bug. When testing the UI, the agent responds with `"{}"` every single time. This is because the `LlmAgent` fallback class in `chassis.py` is currently a dummy stub hardcoded to return `"{}"`.

Please execute the following fixes:

1. **Update `requirements.txt`:**
   Add `python-dotenv` to the file so we can load the Gemini API key from the local `.env` file.

2. **Update `src/universal_core/chassis.py`:**
   - At the top of the file, add `from dotenv import load_dotenv` and call `load_dotenv()` so the environment variables are loaded when the chassis boots.
   - Import `litellm` (specifically `from litellm import acompletion`).
   - Rewrite the `LlmAgent` class. The `generate_content` method must use `litellm.acompletion` to make a real API call to the configured model (defaulting to `gemini/gemini-1.5-flash` or whatever is passed in) using the provided prompt, and return the actual text response.
   
*Example of the acompletion call:*
```python
response = await acompletion(
    model=self.model,
    messages=[{"role": "user", "content": prompt}]
)
return response.choices[0].message.content
```

Once you have implemented these fixes, commit your changes, push the branch, and drop a message in `internal_ignore/inbox_scribe/` so we can re-test the UI!