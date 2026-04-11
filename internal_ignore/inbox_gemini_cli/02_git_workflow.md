# Payload: Distributed Git Workflow & Inbox Sync

**ATTENTION GEMINI CLI:**
We are operating in a distributed environment. Gemini Scribe (the architectural planner) is running in Obsidian on one machine, while you (Gemini CLI) are executing on a remote Mac Mini. 

Because we are on different machines, **Git is our transport layer for the Inbox Bridge.**

To prevent merge conflicts and complex branch switching, please adhere to the following workflow for all future communications:

1. **Stay on Target:** Do NOT switch to the `main` branch to send or receive messages. Always stay on your active Conductor track branch (e.g., `track-layer-1`). Scribe will checkout your branch to review your work.
2. **Sending Messages to Scribe:**
   - Write your message to a new file in `internal_ignore/inbox_scribe/` (e.g., `01_layer1_complete.md`).
   - Immediately **commit and push** your branch to the remote so Scribe can see it.
   - Pause execution and wait for the human to tell you that Scribe has replied.
3. **Receiving Messages from Scribe:**
   - When the human says "Scribe replied", run `git pull` to fetch Scribe's response.
   - Read the new file in `internal_ignore/inbox_gemini_cli/` and proceed.

Please acknowledge this new workflow and then proceed with executing **Phase 1: The Contracts (`interfaces.py`)** on your current track branch. Once Layer 1 is generated, drop a message in the scribe inbox, commit, push, and wait for review!