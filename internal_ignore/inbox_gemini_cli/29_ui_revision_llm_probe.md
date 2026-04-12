# Payload: UI Revision 2 - LLM Probe & Fix

**ATTENTION GEMINI CLI:**
Do NOT create a new track or switch branches. Continue working on the current UI fix branch.

The previous fix successfully connected `litellm`, but we are hitting a 404 error: `models/gemini-1.5-flash is not found for API version v1beta`. 

Please execute the following fixes in `src/universal_core/chassis.py`:

1. **Fix the Model Prefix and Update to Latest Model:**
   When using LiteLLM with Google AI Studio keys, the model string must be prefixed with `gemini/`. We also need to update to the latest flash model. Update the `LlmAgent` initialization or the overarching config so that the model string evaluates to `gemini/gemini-2.5-flash`.

2. **Add Startup Logging:**
   In the `run_local` or `start` method (where the mock infrastructure boots), add logging statements (using Python's `logging` or `print`) that output:
   - The exact model string being used.
   - The API key it is attempting to use (Please mask the key for security, e.g., print the first 4 and last 4 characters: `AIza...XyZ1`).

3. **Add a Fast-Fail Probe Test:**
   Before the FastAPI server fully boots, execute a tiny "probe" test to the LLM (e.g., send a simple "ping" or "hello" prompt using `litellm.acompletion`). 
   - If it succeeds, log "LLM Probe Successful".
   - If it throws an exception (like the 404 or an auth error), catch the exception, print a highly visible critical error message to the terminal explaining why it failed, and call `sys.exit(1)` to fast-fail the application.

Please implement these changes, commit them to the current branch, and drop a message in `inbox_scribe/` when complete.