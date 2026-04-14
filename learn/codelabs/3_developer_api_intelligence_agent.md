# Codelab 3: Developer API Intelligence Agent 🤖📱

**Goal:** Build a sophisticated, real-world assistant that can analyze code repos (we'll use AndroidX for this codelab), track recent changes, and map developer shorthand names for repos to actual code modules.

**What You Will Build:** An AI agent that connects to a local clone of a codebase. When a user asks "What changed in Compose UI lately?", the agent will:
1. **Dynamically Clone** the repository to your local machine (using state management to check if it already exists).
2. **Handle** the request asynchronously via a background queue so the UI doesn't freeze during the long download.
3. **Translate** human shorthand ("Compose UI") into the exact repository path. Ask the user if the found path was what the user meant.  
4. **Execute** real `git log` and `git diff` commands against the local code to analyze recent changes without blowing out the LLM context window.
5. **Synthesize** the raw code diffs into a clear, human-readable summary.

**Status:** Advanced / Offline Challenge
**Format:** Individual Challenge with Open Collaboration

### 🎓 What you will learn:
* How to handle long-running tasks (like cloning a 1.3GB repo) asynchronously using messaging queues so the UI doesn't freeze.
* How to implement **State Management** to track if long-running tasks have already been completed (and so it won't have to do it again)
* How to use **Logging and Tracing** so users can see terminal output while waiting for async jobs.
* How to build "Semantic Mapping" tools that translate human shorthand (e.g., "Compose UI") into exact system paths.
* How to write tools that execute real terminal commands (like `git log` and `git diff`) and manage the resulting massive data payloads to prevent blowing out the LLM's context window.

## Before you start

### 🛑 Stick to the mocked framework for an easier time
Because this hackathon is designed to run locally on your machines without depending on possibly corporate resources or prohibited external services, **you should build this agent to run entirely in the mock environment.**  You are of course welcome to attempt to plug into policy allowed systems if you're curious.  

### ⚠️ This is an intentionally difficult codelab 
This codelab is meant to be **very difficult** and mirrors a practical, real-world use case for building agentic flows. One of our primary goals is to show that it still takes thought, planning, and work to create good tooling—not everything is just "a prompt away."

Throughout this challenge, we hope to highlight the reality of agent development:
*   **Where your time is spent (setting the intention):** Learning the domain, ideating the architecture, and planning the tool boundaries.
*   **Where the AI makes things trivial (and responds to your direction):** Quickly generating the boilerplate, scaffolding the code, and creating the initial "thing."
*   **Where the AI can be frustrating (and needs your help):** Debugging, hallucinating, taking odd liberties with planning or code generation, and missing edge cases or tests. 

Expect to provide strong guidance to your AI CLI. This codelab simulates the very real, sometimes involved workflow of building production agents.

---

## 🚀 Let's Get Started

You are about to build the **Developer API Intelligence Agent**. This agent will act as your personal code historian and repository navigator. 

**Key Features of this Agent:**
* **Asynchronous Repo Management:** Safely clones and updates massive codebases (like AndroidX) in the background without freezing your UI.
* **Semantic Translation:** Understands that when you say "Compose UI", you actually mean the `androidx.compose.ui:ui` artifact and the `compose/ui/ui` directory.
* **Context-Aware Git Execution:** Runs real `git log` and `git diff` commands, intelligently chunking or summarizing the output so it doesn't overwhelm the LLM's context window.

### Example Interactions
By the end of this codelab, your Agent Studio UI should be able to handle complex, multi-step workflows like these:

**Example 1: The Long-Running Task**

- **You:** What's changed recently in Compose UI?
- **Agent:** Hold on, I need to sync the repository first. This might take a minute... *(UI remains responsive)*

*(2 minutes later)*

- **Agent:** Repository synced! I searched the repo for the Compose UI, specifically did you mean `compose/ui/ui`? If so the biggest recent change is a fix to the `Modifier.Node` lifecycle, specifically addressing a memory leak when detaching nodes. Here is a quick summary of the diffs...

**Example 2: Semantic Translation & Ambiguity**

- **You:** What are the latest commits for "Navigation"?
- **Agent:** By "Navigation", do you mean `androidx.navigation:navigation-compose` or `androidx.navigation:navigation-fragment`? 
- **You:** Compose please.
- **Agent:** Got it. Looking at `navigation/navigation-compose`. The last 3 commits involve adding type safety to the NavGraphBuilder. Here are the details...

**Example 3: Context Window Survival**

- **You:** Show me the diff for the latest major refactor in Room.
- **Agent:** The latest commit in `room/room-compiler` is massive (over 4,000 lines changed). Instead of showing you the raw diff, I ran a diff stat. It looks like they completely rewrote the `QueryProcessor.kt` and added 15 new test files. Would you like me to summarize just the changes in `QueryProcessor.kt`?

---

## 🧠 The Agent Builder Workflow: Observe, Think, Act, Verify

Rather than treating this as a standard coding tutorial, we want you to practice **Agent-Driven Development**. In this paradigm, you act as the Technical Director. You spend your time observing constraints and planning the architecture upfront, and then you direct your AI CLI to act on those plans:

- Phase 1: Observe (consider your intentions and outcomes you are seeking)
- Phase 2: Think (define your specifications and review AI's projected plan)
- Phase 3: Act (direct AI to execute the plan and help it along as necessary)
- Phase 4: Verify (validate the solution, iterate and revise as needed)

### Phase 1: Observe (The Domain & Constraints)
Before writing a single prompt, take a step back and look at the reality of the systems you are integrating with.
* **The Long-Running Task:** The AndroidX repo is ~1.3GB. A `git clone` will take about 2 minutes. A synchronous HTTP request will timeout and freeze the UI. 
* **The Translation Gap:** Developers say "Compose UI", but the file system expects `compose/ui/ui`. The agent cannot guess this; it needs deterministic mapping.
* **The Context Window Nuke:** A raw `git diff` for a major framework release will easily output 10,000+ lines of text. Feeding this directly into an LLM will crash the agent or cause severe hallucinations.

*💡 Stuck? Check out the solution for this phase in the [Solutions Overview](#solutions-overview).*

### Phase 2: Think (The Specification & Plan)
Now that you know the constraints, plan the architecture. *This is where you earn your paycheck as an Agent Architect.*
* **State Management:** The agent needs a `DeveloperAPIState` to remember if the repo is `not_cloned`, `cloning`, or `ready`. 
* **Async Queues:** The `sync_repository` tool must be offloaded to a background task using the `BaseAgentChassis`'s native async capabilities. It should log to the terminal so developers know it isn't broken.
* **Tool Boundaries:** We need a semantic mapping dictionary to translate shorthand. We also need a `local_git_executor` tool that uses Python's `subprocess` module. Crucially, this Git tool must be constrained—it should run `git diff --stat` first, forcing the agent to request specific files rather than dumping the whole diff.

*💡 Stuck? Check out the solution for this phase in the [Solutions Overview](#solutions-overview).*

### Phase 3: Act (Direct the CLI Execution)
With your plan in place, instruct your AI CLI to build the agent layer-by-layer. Do not write the boilerplate yourself!
* Open your terminal and use your AI CLI (e.g., Gemini CLI, Cursor).
* Feed it your architectural decisions. (See the *Solution Kickoff Prompts* below for examples of how to direct the CLI).
* If the CLI gets confused, use the **AI Bridge**—paste terminal output or Python errors back into your Gemini Web App to have it write the exact Python parsing logic or refactoring steps for you.

*💡 Stuck? Check out the solution for this phase in the [Solutions Overview](#solutions-overview).*

### Phase 4: Verify (Test & Refine Outcome)
Test the agent in the Agent Studio UI to ensure the architecture holds up.
* Ask the agent to sync the repo. Does the UI respond instantly with "Job Started" while the terminal shows Git progress?
* Ask for "Navigation". Does it pause to clarify which module you meant?
* Ask for a massive diff. Does it successfully summarize it without crashing?

*💡 Stuck? Check out the solution for this phase in the [Solutions Overview](#solutions-overview).*

---

## Extra Credit Side Quests (Pushing the Boundaries)
If you finish the core workflow early, try tackling one of these advanced missions using the same Observe, Think, Act, Verify process.

### 1. Automated Release Note Synthesis (Efficiency Gain)
* **The Problem:** API maintainers spend hours parsing merged PRs to write human-readable release notes for each library update.
* **The Plan:** Build a tool that takes a module name and two Git tags, extracts the relevant commit histories, filters out internal refactors, and drafts a public-facing markdown release note.

### 2. The "Sample Code" Auto-Migrator (Innovation)
* **The Problem:** When an API is deprecated, maintainers manually update dozens of sample apps to prevent developers from copying outdated code.
* **The Plan:** Give the agent access to a local sample repository. Instruct it to find usages of a deprecated API and generate a Git patch or PR updating the code to the new standard.

### 3. Issue Tracker Triage & Routing (Efficiency Gain)
* **The Problem:** Triaging incoming GitHub issues or Issue Tracker bugs is a manual, tedious process.
* **The Plan:** Build a tool that reads open issues, uses the semantic mapper to determine which module they belong to, and drafts a preliminary response proposing relevant tags.

---
<a id="solutions-overview"></a>
## Reference Solution
Your solution may be different. This reference solution provides one possible outcome of the project. You can use this to aid and guide your understanding of how to move from stage to stage.

### Solution: Phase 1 (Observe)
**Reference Checkpoint Branch:** [`solution-codelab3-phase1`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase1)

**Reference Approach:** Before writing any code, Agent Developers should use tools like Gemini Web, NotebookLM, or their preferred LLM to explore the domain constraints. You can paste the AndroidX repository URL and ask, "What are the common submodules here? How large is the repo?" to gather facts and validate your understanding of the constraints.

**Expected Output:** A brief research document or checklist (e.g., `domain_research.md`) that explicitly lists the system constraints: repo size, context window risks, and shorthand mapping requirements. The most vital technical details would be:
* **Repo Size:** A synchronous `git clone` of 1.3GB will trigger a timeout in any standard HTTP server (like FastAPI). You absolutely must use an asynchronous background queue.
* **Context Limits:** You cannot run `git diff` on a major framework and pipe the raw stdout to the LLM. It will exceed the token limit. You must engineer a tool that runs `git diff --stat` first to see the size, or chunks the output.
* **Shorthand:** The LLM cannot magically guess that "Navigation" maps to `navigation/navigation-compose`. It needs a hardcoded dictionary or a semantic search tool to bridge the human-to-system gap.

### Solution: Phase 2 (Think)
**Reference Checkpoint Branch:** [`solution-codelab3-phase2`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase2)

**Reference Approach:** Agent Developers should draft an architectural specification document (e.g., `developer_api_spec.md`) mapping out the state requirements, tool boundaries, and error handling. You can use an architecture-focused prompt in Gemini Web to brainstorm the best way to chunk Git diffs before committing to a design.

**Example Spec Generation Prompts:**
If you aren't sure how to turn your research into an architectural spec, try feeding these prompts into an LLM (like Gemini Web or NotebookLM) to have it draft the document for you:
* *"I am building an AI agent using the BaseAgentChassis framework. Here are my research notes on the domain constraints: [paste notes]. Draft a formal architectural spec including the Pydantic State definition, required Tools, and the async Queue strategy."*
* *"Let's refine the State section of the spec. We need to track the repository clone status (not_cloned, cloning, ready) so the UI can show progress without freezing. Update the draft."*
* *"For the Git diff tool, a raw diff will blow out the LLM context limits. Propose a tool design in the spec that handles this safely (e.g., using `git diff --stat` or chunking) and update the document."*

> 💡 **Iterative Planning:** Keep in mind that building this spec is an iterative process! You will likely go back and forth with the LLM several times—tweaking edge cases and refining the architecture—before you are satisfied that the plan is solid enough to start generating code.

**Expected Output:** A formal architectural specification document (e.g., `developer_api_spec.md`) that defines the required `DeveloperAPIState` properties, the async Queue strategy, and the exact Tool boundaries.

**What your architecture should look like:**
* **State (`DeveloperAPIState`):** Needs `repo_status` (string) to prevent the agent from cloning multiple times, and `current_module` (string) to remember what the user is asking about.
* **Tools:**
  * `sync_repository`: An async tool that runs the clone and updates the state.
  * `translate_shorthand`: A simple sync tool that looks up user terms in a predefined dictionary.
  * `execute_git_command`: A sync tool that uses `subprocess.run` but enforces strict limits (e.g., truncating output over 2000 characters or enforcing `--stat` for diffs).

### Solution: Phase 3 (Act)
**Reference Checkpoint Branch:** [`solution-codelab3-phase3`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase3)

**Reference Approach:** Agent Developers should rely heavily on their AI CLI (Cursor, Windsurf, Gemini CLI) loaded with the `adk-agent-builder` skill. Rather than manually wiring up files, your job is to act as the Technical Director. You will provide the spec document from Phase 2 to the AI CLI, kick off a Conductor track, and let the `adk-agent-builder` skill drive the Specification-Driven Development process. 

The skill will automatically pause at each "layer" of the architecture and ask if you would like to proceed. You should review the code generated at each stop, ask for revisions if needed, and then confirm to move on.

**Expected Output:** The actual functioning Python code generated layer-by-layer by your AI tool, including `agent.py`, `tools.py`, and the `prompts/` directory, properly registered in the system configuration.

**Kickoff Prompt:**
If you are stuck on how to begin Phase 3, try feeding this exact prompt to your AI CLI. The skill will take it from here:

*"I have finalized the architecture in `src/agents/developer_api_agent/developer_api_spec.md`. Please activate the `adk-agent-builder` skill and begin a conductor track to build this agent."*

**The Layer-by-Layer Review Process:**
When you kick off the prompt above, expect to review the following layers:

1. **Layer 1: State & Models (`models.py`)** 
   * *What to do:* Review the Pydantic models. Ensure the `repo_status` field exists and is correctly typed. If it missed a field from your spec, tell the CLI to add it before proceeding.
2. **Layer 2: Prompts (`prompts/`)** 
   * *What to do:* Read the generated system instructions. Ensure the tone is correct and that it explicitly tells the LLM to use the async tool for cloning.
3. **Layer 3: Tools (`tools.py`)** 
   * *What to do:* This is the most critical review. Check the `subprocess` logic for the Git commands. Are they handling context limits (e.g., using `--stat` or truncating)? Are they using async `asyncio.sleep` or background tasks correctly? Ask for revisions if the Git tool looks like it will blow out the context window.
4. **Layer 4: Agent Logic (`agent.py`)** 
   * *What to do:* Check the routing and queue consumption. Ensure the `@chassis.consume_task` decorator is used for the async clone job.
5. **Layer 5: Wiring (`config.yaml`)** 
   * *What to do:* Confirm the agent is registered correctly so it appears in the Agent Studio UI.

### Solution: Phase 4 (Verify)
**Reference Checkpoint Branch:** [`solution-codelab3-phase4`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase4)

**Reference Approach:** Agent Developers should use the local Agent Studio UI to interact with the agent as a real user would. When errors occur (like context window overflows), developers should copy the terminal stack trace and paste it back into their AI CLI or Gemini Web to ask for a fix. 

> 💡 **The Iterative Loop:** Remember, building agents is rarely a one-shot process! It is highly likely that during verification, you will discover a flaw in your design (e.g., the diff stat is still too large, or the semantic mapper missed an edge case). When this happens, you must kick off successive **Observe → Think → Act → Verify** loops. Go back to your spec, update your plan, have the CLI revise the code, and verify again until you arrive at the robust solution you were hoping for.

> 🎬 **The Director's Mindset:** Keep in mind that your AI CLI might get details wrong, hallucinate, and possibly introduce bugs—just like any human software engineer! As the Director, it is your job to validate the work and explicitly ask the AI builder to go through revisions. What you choose to revise is entirely up to you. You might want to get down into the nitty-gritty details of how the code is organized, or you might only care about the user interaction, or you might focus heavily on how state is managed and how the agent responds. Using successively tighter OTAV loops gets you closer to your "ideal" solution.

**Expected Output:** A robust, working agent validated in the Agent Studio UI that successfully handles long-running clones, clarifies shorthand, and summarizes diffs without crashing.

**How to test your implementation:**
1. **The Clone Test:** Type "Sync the repo" in the UI. The UI should instantly reply "Started syncing" (or similar), and your terminal should start showing Git clone progress.
2. **The Clarification Test:** Type "What changed in Navigation?" The agent should pause, use the `translate_shorthand` tool, and ask you to clarify which specific navigation module you meant.
3. **The Nuke Test:** Ask "Show me the full diff for the last 10 commits in Compose UI." If your agent crashes or throws a token limit error, your `execute_git_command` tool is not properly constrained! It should reply with a summary or a truncated diff stat instead.