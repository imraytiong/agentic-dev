# Codelab Dry Run Notes

This document captures notes, friction points, and required revisions discovered during the roleplay dry run of the 4 hackathon codelabs.

## Codelab 1: Hello Sparky
* **Status:** Completed
* **Notes:**
  * **Friction Point Discovered:** The UI allows file uploads (paperclip icon), but Sparky currently ignores them. This is because Sparky's `HelloRequest` schema and `get_affirmation` tool are strictly text/mood-based and don't process file bytes. 
  * **Revision Made:** Updated Codelab 1 Step 4.2 to frame this as a "Teachable Moment" (limitation of the current schema) rather than an expected feature, to prevent participant confusion.
  * **Enhancement Idea (Verbose Logging):** Terminal output during `--mock` mode is too quiet. We need to increase verbosity by default so developers can see the internal agent loops (tool calls, state mutations). We should add a `--quiet` flag to suppress this.
  * **Enhancement Idea (Agent Studio UI Debugger):** The UI needs to be a true debugging harness. It should display the internal guts of the agent (active prompts, registered tools, loaded skills) and a live running system log showing execution steps, side-by-side with the chat.

## Codelab 2: Upgrading Sparky
* **Status:** In Progress
* **Notes:**
  * *(Placeholder for notes during dry run)*

## Codelab 3: AndroidX Intelligence Agent
* **Status:** Pending
* **Notes:**
  * *(Placeholder for notes during dry run)*

## Codelab 4: Capstone
* **Status:** Pending
* **Notes:**
  * *(Placeholder for notes during dry run)*
## Codelab 2: Upgrading Sparky
* **Observation:** The previous "Git Safety Net" relied on manual `git commit` commands, which developers often forget to run before rapid AI generation.
* **Update:** We modified the `adk-agent-builder` skill (and the codelab instructions) to automate this. The AI CLI is now strictly instructed to:
    1. Check for uncommitted work and ask the user to commit it before planning.
    2. Plan in the current branch.
    3. *Always* create and checkout a new feature branch before executing code generation.
* **Result:** The safety net is now enforced by the AI, preventing accidental overwrites on the `main` branch.