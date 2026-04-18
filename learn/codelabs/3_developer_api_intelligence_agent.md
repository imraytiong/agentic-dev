# Codelab 3: Developer API Intelligence Agent 🤖📱

**Goal:** Build a sophisticated, real-world assistant that can analyze code repos (we'll use AndroidX for this codelab), track recent changes, and map developer shorthand names for repos to actual code modules.

**What You Will Build:** An AI agent that connects to a local clone of a codebase. When a user asks "What changed in Compose UI lately?", the agent will:
1. **Dynamically Clone** the repository to your local machine (using state management to check if it already exists).
2. **Handle** the request asynchronously via a background queue so the UI doesn't freeze during the long download.
3. **Index** the downloaded repository by storing module paths and descriptions into a vector database.
4. **Translate** human shorthand ("Compose UI") into the exact modules using semantic search against the indexed vector database. Ask the user if the found path was what the user meant.  
5. **Execute** real `git log` and `git diff` commands against the local code to analyze recent changes without blowing out the LLM context window.
6. **Synthesize** the raw code diffs into a clear, human-readable summary.

**Status:** Advanced / Offline Challenge
**Format:** Individual Challenge with Open Collaboration

### 🎓 What you will learn:
* How to handle long-running tasks (like cloning a repo) asynchronously using messaging queues so the UI doesn't freeze.
* How to implement **State Management** to track if long-running tasks have already been completed (and so it won't have to do it again)
* How to use **Logging and Tracing** so users can see terminal output while waiting for async jobs.
* How to build "Semantic Mapping" tools that translate human shorthand (e.g., "Compose UI") into exact system paths using vector databases populated during runtime.
* How to write tools that execute real terminal commands (like `git log` and `git diff`) and manage the resulting massive data payloads to prevent blowing out the LLM's context window.

## Before you start

### 🛑 Stick to the mocked framework for an easier time
Because this codelab is designed to run locally on your machines without depending on possibly corporate resources or prohibited external services, **you should build this agent to run entirely in the mock environment.**  You are of course welcome to attempt to plug into policy allowed systems if you're curious.  

### 🛠️ Prerequisite: Git CLI
Since your agent will be executing real terminal commands against a cloned repository, **you must have `git` installed and accessible in your system PATH.** 

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
* **Dynamic Indexing:** Parses the repository after cloning and populates a vector store with module names and paths.
* **Semantic Translation:** Understands that when you say "Compose UI", you actually mean the `androidx.compose.ui:ui` artifact and the `compose/ui/ui` directory by querying a vector store.
* **Context-Aware Git Execution:** Runs real `git log` and `git diff` commands, intelligently chunking or summarizing the output so it doesn't overwhelm the LLM's context window.

### Example Interactions
By the end of this codelab, your Agent Studio UI should be able to handle complex, multi-step workflows like these:

**Example 1: The Long-Running Task**

- **You:** What's changed recently in Compose UI?
- **Agent:** Hold on, I need to sync the repository first. This might take a minute... *(UI remains responsive)*

*(2 minutes later)*

- **Agent:** Repository synced and indexed! I searched the repo for the Compose UI, specifically did you mean `compose/ui/ui`? If so the biggest recent change is a fix to the `Modifier.Node` lifecycle, specifically addressing a memory leak when detaching nodes. Here is a quick summary of the diffs...

**Example 2: Semantic Translation & Ambiguity**

- **You:** What are the latest commits for "Navigation"?
- **Agent:** By "Navigation", do you mean `androidx.navigation:navigation-compose` or `androidx.navigation:navigation-fragment`? 
- **You:** Compose please.
- **Agent:** Got it. Looking at `navigation/navigation-compose`. The last 3 commits involve adding type safety to the NavGraphBuilder. Here are the details...

**Example 3: Context Window Survival**

- **You:** Show me the diff for the latest major refactor in Room.
- **Agent:** The latest commit in `room/room-compiler` is massive (over 4,000 lines changed). Instead of showing you the raw diff, I ran a diff stat. It looks like they completely rewrote the `QueryProcessor.kt` and added 15 new test files. Would you like me to summarize just the changes in `QueryProcessor.kt`?

### Useful Hints Before You Start

**AndroidX is big**: so you may want to have the tooling be intelligent enough to sparsely download only what you need at the beginning.  Cloning the repo will likely take a significant amount of time and can possibly be inherently flaky.  You'll want to ensure that the agent generating  robust enough code to handle partial failures or network interruptions gracefully during the process. 
- **asynchronous** logic is going to be necessary to prevent UI freezing
- **retries** and backoff lostic is also something worth investing in 
- **statefulness** operations against the repo (such as downloading and indexing) are costly.  Consider leveraging 'memory' to ensure you don't repeat unnecessary logic
 
**AndroidX stores relevant API information** in the following ways:

- **README.md** at the root of each submodule directory has human constructed write-up about the module.  That said it's not always accurate, sometimes outdated, and subject to the whim of the author
- **api/current.txt**: lists the public API surface area and method signatures for a given module.
- **gradle build files are rich content** for indexing and analytics.  Gradle details like the module name and description may be use ful 'indexing content' 

**Vector Databases allow for semantic searches:** AI agents typically rely on using a 'vector database' which allows for 'meaning rich' searches.  The details of such is beyond this codelab but as a 'Technical Director' all you need to know is that you can give the vector database useful files that allows the agent to perform weighted searches on 'likeness of content' without depending on exact matches or custom fuzzy matching.  The mock infrastructure leverages ChromaDB. 


---

## 🧠 The Agent Builder Workflow: Observe, Think, Act, Verify

Rather than treating this as a standard coding tutorial, we want you to practice **Agent-Driven Development**. In this paradigm, you act as the Technical Director. You spend your time observing constraints and planning the architecture upfront, and then you direct your AI CLI to act on those plans:

- Phase 1: Observe (consider your intentions and outcomes you are seeking)
- Phase 2: Think (define your specifications and review AI's projected plan)
- Phase 3: Act (direct AI to execute the plan and help it along as necessary)
- Phase 4: Verify (validate the solution, iterate and revise as needed)

### Phase 1: Observe (The Domain & Constraints)
Before writing a single prompt, take a step back and look at the reality of the systems you are integrating with. Consider the physical and technical constraints of the environment.
* **The Long-Running Task:** How large is the repository you are downloading? How long will a standard clone operation take, and what happens to a synchronous web request if it waits that long?
* **The Translation Gap:** How do humans talk about the code vs. how the file system organizes it? How can the agent dynamically build a map of this codebase so it knows the difference?
* **The Context Window:** What happens when an agent tries to read a massive code change? How much text can your LLM actually process before it crashes or hallucinates?

*Hint: If you aren't sure what to consider, try asking your AI LLM (like Gemini Web or NotebookLM): "Based on what I'm trying to build (an AI agent that clones a massive repo and reads git diffs), what do you think I should consider? Give me 5-10 technical things to work through."*

*💡 Stuck? See the [reference solution for Phase 1](#solution-phase-1-observe).*

### Phase 2: Think (The Specification & Plan)
Now that you know the constraints, plan the architecture. *This is where you earn your paycheck as an Agent Architect.*

* **State Management:** What data does the agent need to remember between interactions? How will it know if a long-running task is already finished or still in progress?
* **Async Queues:** How will you design the agent to handle tasks that take minutes to complete without freezing the user interface? How will you keep the user informed of the progress?
* **Tool Boundaries:** What specific tools does the agent need to bridge the translation gap? How will you design the sync tool to not only download the code, but also parse the directory structure and populate the vector store? How will the semantic search tool query it?

*Hint: Take your research from Phase 1 and draft a technical specification. If you need help, ask your AI: "I need to build an architecture spec for an agent that handles long-running tasks and massive data payloads. What state fields, async queues, and tool boundaries should I define?"*

*💡 Stuck? See the [reference solution for Phase 2](#solution-phase-2-think).*

### Phase 3: Act (Direct the CLI Execution)
With your plan in place, instruct your AI CLI to build the agent layer-by-layer. Do not write the boilerplate yourself!
* **The Hand-off:** Provide your specification to your AI coding assistant and instruct it to begin building. 
* **The Layered Review:** As the AI generates the state, prompts, tools, and logic, review its work. Does the generated code actually address the constraints you planned for?
* **The Course Correction:** If the CLI hallucinates or gets confused, how will you guide it back on track? 

*Hints:* 
- **Use the `adk-agent-builder`** skill to guide your CLI through a structured generation process. Tell it: "Here is my architectural spec. Please activate the adk-agent-builder skill and walk me through building this agent layer-by-layer."
- **The process is NOT rigid.** Consider the agent a 'junior engineer with lots of smarts but possibly not great decision or architectural making'.  When it's working through each phase you can ask for explanations of it logic, challenge it's decisions, and ask it to revise decisions.
- **Progressively ask it to update the specification and plan as needed:** any time you see that it's done something incorrect you find that the implementation is drifting from your initial architectural requirements. It will make adjustments to the plan and continue generating code based on your refined requirements.
	- "how does the github download work? "
	- "what are we indexing? why? Should we index the gradle builds, readme.md, and api/current.txt to make it a more rich search experience?"
- **DO NOT allow the agent to write code without producing a plan:**  as the agent progresses it has skills guardrails, however sometimes it can get too eager to make code changes. You can ask it to revert and instead make a plan, create coverage tests, and then do the code.
	- "you made code changes without explaining the plan, revert, and create a plan. you also forgot to use test coverage"
- **Ask the agent to perform expensive MANUAL tests:**  mocked unit tests catches many regressions but it doesn't by nature test actual interactions with real external systems where many of the more difficult bugs can occur. Ask it to run a manual tests especially during the tool construction where possible complex deterministic logic needs to be correctly crafted.
	- "run the tools against real jetpack repo. test that it correctly downloads the repo and that the indexing with chromadb actually works."


*💡 Stuck? See the [reference solution for Phase 3](#solution-phase-3-act).*

### Phase 4: Verify (Test & Refine Outcome)
Test the agent in the Agent Studio UI to ensure the architecture holds up against edge cases.
* **The Async Test:** Trigger your long-running task. Does the UI freeze, or does it remain responsive while the work happens in the background?
* **The Ambiguity Test:** Ask the agent a vague question using developer shorthand. Does it guess blindly, or does it stop to clarify what you meant?
* **The Stress Test:** Ask the agent for an enormous amount of data (like a massive code change). Does it crash, or does it protect its context window?

*Hint: If a test fails, copy the terminal errors or unexpected outputs and start a new Observe -> Think -> Act loop with your AI to refine the solution..  Or, if the agent is not behaving as you thought it might, prompt in the terminal what you're seeing and also what you were expecting instead. 

*💡 Stuck? See the [reference solution for Phase 4](#solution-phase-4-verify).*

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
**Reference Output:** A brief research document or checklist (e.g., `domain_research.md`) that explicitly lists the system constraints: repo size, context window risks, and shorthand mapping requirements. The most vital technical details would be:
* **Repo Size:** A synchronous `git clone` of 1.3GB will trigger a timeout in any standard HTTP server (like FastAPI). You absolutely must use an asynchronous background queue.
* **Context Limits:** You cannot run `git diff` on a major framework and pipe the raw stdout to the LLM. It will exceed the token limit. You must engineer a tool that runs `git diff --stat` first to see the size, or chunks the output.
* **Shorthand:** The LLM cannot magically guess that "Navigation" maps to `navigation/navigation-compose`. It needs a semantic search tool to bridge the human-to-system gap, which means the repository must be indexed into a vector store after cloning.

**Reference Approach:** Before writing any code, Agent Developers should use tools like Gemini Web, NotebookLM, or their preferred LLM to explore the domain constraints. You can paste the AndroidX repository URL and ask, "What are the common submodules here? How large is the repo?" to gather facts and validate your understanding of the constraints.

Reference [Gemini Web discussion](https://gemini.google.com/share/866045485d31) and final output: 

```
# Agent Specification: Android-Dissect Proposal (v1.1)

## 1.0 System Overview
* **1.1 System Objective:** Build an interactive AI agent capable of cloning, navigating, and summarizing the AndroidX/Jetpack monolithic repository. The agent must handle long-running I/O tasks asynchronously, translate human-readable framework concepts into exact repository paths, and strictly manage its context window when analyzing massive code diffs.
* **1.2 Architectural Framework:** The agent must be built upon the `agentic-dev` Hexagonal Architecture framework utilizing Python.

## 2.0 Environment & Storage Strategy
* **2.1 Execution Environment:** The agent will operate uncontainerized, as the deployment environment itself is already a containerized execution space.
* **2.2 Configurable Storage:** The root storage locations for both the target repository clones and the agent's state files MUST be dynamically configurable via the agent's `.yaml` configuration file (no hardcoded absolute paths).
* **2.3 Repository Clone Strategy:** The agent must utilize `git clone --filter=blob:none` combined with `git sparse-checkout` to manage the repository footprint and download times.

## 3.0 State Management Schema
* **3.1 State Storage Mechanism:** The agent must utilize the native memory storage mechanism provided by the `agentic-dev` framework to maintain state, allowing for asynchronous pausing, resuming, and follow-up queries without losing context across sessions.
* **3.2 Active Focus State Object:** The state must track `active_focus`, a JSON object containing the `module_path`, `current_files_in_context`, and `head_sha`.
* **3.3 Command History Array:** The state must track `command_history`, an array of the last 5 executed tool calls to prevent the agent from entering infinite execution loops.
* **3.4 Cached Summaries Ledger:** The state must track `cached_summaries`, a key-value store mapping commit hashes or file paths to LLM-generated summaries. This prevents raw diffs from re-entering the prompt on subsequent conversational turns.
* **3.5 Pending Interrupt State Object:** The state must track `pending_interrupt`, a JSON object storing the agent's mental state and intent when it yields execution to the user for disambiguation.

## 4.0 Tool Specifications
* **4.1 Tool: `resolve_module_path`**
    * **4.1.1 Purpose:** Translates lazy human references (e.g., "Room DB", "Compose UI") into concrete AndroidX directory paths.
    * **4.1.2 Execution Constraint:** The agent MUST call this tool before executing any Git commands if the exact repository path is unknown.
    * **4.1.3 Implementation Directive:** Utilize the `agentic-dev` framework's built-in vector capabilities to embed and perform semantic searches against the parsed `settings.gradle` or directory tree map.
    * **4.1.4 Expected Output:** The tool must return an array of the top 3 to 5 path candidates alongside their confidence scores.
* **4.2 Tool: `run_git_command`**
    * **4.2.1 Purpose:** Safely executes Git commands against the local sparse checkout.
    * **4.2.2 Security and Execution Boundaries:** Raw bash execution is explicitly forbidden. The tool must accept an array of parameterized arguments (e.g., `["log", "-n", "3", "--stat", "--", "path/to/module"]`).
    * **4.2.3 Directory Scoping Guardrail:** The Python function executing the subprocess must force a `cwd` (current working directory) targeted specifically to the configured repository volume.
    * **4.2.4 History Alteration Guardrail:** The tool must block any Git commands that alter remote or local history (e.g., `push`, `reset --hard`).
    * **4.2.5 Auto-Truncation Mechanism:** If the `stdout` of the Git subprocess exceeds 8,000 characters, the tool must automatically truncate the output and return a system warning instructing the agent to use narrower constraints.

## 5.0 Architectural Execution Flows
* **5.1 The Triage Loop**
    * **5.1.1 Prohibited Actions:** The agent is explicitly forbidden from requesting raw unified diffs (`-p`) on large modules without first triaging the blast radius.
    * **5.1.2 Step 1 Initial Discovery:** The agent must run `run_git_command` utilizing the `--stat` or `--name-only` flags.
    * **5.1.3 Step 2 File Review:** The agent reviews the list of changed files from Step 1.
    * **5.1.4 Step 3 Targeted Extraction:** The agent targets a specific, single file to request the raw diff.
* **5.2 The Disambiguation Interrupt**
    * **5.2.1 Trigger Condition:** If the `resolve_module_path` tool returns multiple low-confidence candidates, the agent must trigger an interrupt.
    * **5.2.2 Step 1 State Preservation:** The agent saves its current intent and the list of options to the `pending_interrupt` state.
    * **5.2.3 Step 2 User Prompting:** The agent outputs the options to the user and completely yields execution.
    * **5.2.4 Step 3 State Rehydration:** Upon receiving the user's reply, the framework rehydrates the agent's state, injects the selected path, and resumes execution.

## 6.0 Implementation Tasks for the AI Assistant
* **6.1 Interrupt Hooking Task:** Review the `BaseAgentChassis` in the `agentic-dev` core. Determine how to implement the `YieldToUser` interrupt pattern within the existing event loop.
* **6.2 Mock Injection Task:** Structure the `run_git_command` tool so it can seamlessly read from local mock fixtures during unit testing instead of invoking the actual `subprocess.run`.
* **6.3 Post-Clone Indexing Task:** Write a post-clone hook script that extracts the AndroidX directory map and loads it into the framework's vector store to power the `resolve_module_path` tool.
```

### Solution: Phase 2 (Think)

**Expected Output:** The CLI should propose a plan similar to:

 I've created and checked out the track/android-dissect-agent branch to ensure we have a
  clean environment for development.

  Based on the Android-Dissect Proposal and the ADK Agent Builder guidelines, here is the
  execution plan. We will build this layer by layer:

  Execution Plan: Android-Dissect Agent
   1. `Layer 1 (Data - models.py):`
       * `Create AndroidDissectState (tracking active_focus, command_history,`
         `cached_summaries, pending_interrupt).`
       * `Create standard Pydantic models for Input/Output payloads.`
   2. `Layer 2 (Defense - test_tools.py & test_agent.py):`
       * `Create a pytest suite.`
       * `Use patch or mock fixtures for run_git_command to ensure we don't execute raw git`
         `commands against the host during unit tests.`
   3. `Layer 3 (Capabilities - tools.py):`
       * `Implement resolve_module_path utilizing the framework's mock vector capabilities.`
       * `Implement run_git_command using subprocess with directory scoping and the 8,000`
         `character output truncation guardrail.`
   4. `Layer 4 (The Brain - agent.py):`
       * `Implement the agent using @chassis.consume_task.`
       * `Implement the Triage Loop and the Disambiguation Interrupt (checking state, saving`
         `pending_interrupt, and returning early if disambiguation is needed).`
   5. `Layer 5 (Config - config.yaml & prompts/system_prompt.jinja):`
       * `Set up the dynamic volume/storage configurations.`

  `If you approve this plan, I will immediately begin executing Layer 1 (Data) by creating`
  `src/agents/android_dissect/models.py.`

  `Do you approve this plan?`

**What your architecture should look like:**
* **State (`DeveloperAPIState`):** Needs `repo_status` (string) to prevent the agent from cloning multiple times, and `current_module` (string) to remember what the user is asking about.
* **Tools:**
  * `sync_repository`: An async tool that runs the clone, parses the directory structure to find key modules, populates `chassis.vector_store.add_documents()`, and updates the state.
  * `translate_shorthand`: A sync tool that uses the framework's `chassis.vector_store.semantic_search()` to look up user terms and map them to physical repository paths.
  * `execute_git_command`: A sync tool that uses `subprocess.run` but enforces strict limits (e.g., truncating output over 2000 characters or enforcing `--stat` for diffs).

**Reference Approach:** Agent Developers should draft an architectural specification document (e.g., `developer_api_spec.md`) mapping out the state requirements, tool boundaries, and error handling. You can use an architecture-focused prompt in Gemini Web to brainstorm the best way to chunk Git diffs before committing to a design.

**Example Spec Generation Prompts:**
If you aren't sure how to turn your research into an architectural spec, try feeding these prompts into an LLM (like Gemini Web or NotebookLM) to have it draft the document for you:
* *"I am building an AI agent using the BaseAgentChassis framework. Here are my research notes on the domain constraints: [paste notes]. Draft a formal architectural spec including the Pydantic State definition, required Tools, and the async Queue strategy."*
* *"Let's refine the State section of the spec. We need to track the repository clone status (not_cloned, cloning, ready) so the UI can show progress without freezing. Update the draft."*
* *"For the Git diff tool, a raw diff will blow out the LLM context limits. Propose a tool design in the spec that handles this safely (e.g., using `git diff --stat` or chunking) and update the document."*

> 💡 **Iterative Planning:** Keep in mind that building this spec is an iterative process! You will likely go back and forth with the LLM several times—tweaking edge cases and refining the architecture—before you are satisfied that the plan is solid enough to start generating code.
### Solution: Phase 3 (Act)
**Reference Checkpoint Branch:** [`solution-codelab3-phase3`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase3)

**Expected Output:** The actual functioning Python code generated layer-by-layer by your AI tool, including `agent.py`, `tools.py`, and the `prompts/` directory, properly registered in the system configuration.

**Reference Approach:** Agent Developers should rely heavily on their AI CLI (Cursor, Windsurf, Gemini CLI) loaded with the `adk-agent-builder` skill. Rather than manually wiring up files, your job is to act as the Technical Director. You will provide the spec document from Phase 2 to the AI CLI, kick off a Conductor track, and let the `adk-agent-builder` skill drive the Specification-Driven Development process.  You run a prompt similar to:

*"I have finalized the architecture in `src/agents/developer_api_agent/developer_api_spec.md`. Please activate the `adk-agent-builder` skill and begin a conductor track to build this agent."*

The skill will automatically pause at each "layer" of the architecture and ask if you would like to proceed. You should review the code generated at each stop, ask for revisions if needed, and then confirm to move on.

**The Layer-by-Layer Review Process:**
When you kick off the prompt above, expect to review the following layers:

1. **Layer 1: State & Models (`models.py`)** 
   * *What to do:* Review the Pydantic models. Ensure the `repo_status` field exists and is correctly typed. If it missed a field from your spec, tell the CLI to add it before proceeding.
2. **Layer 2: Prompts (`prompts/`)** 
   * *What to do:* Read the generated system instructions. Ensure the tone is correct and that it explicitly tells the LLM to use the async tool for cloning.
3. **Layer 3: Tools (`tools.py`)** 
   * *What to do:* This is the most critical review. Check the `subprocess` logic for the Git commands. Are they handling context limits? Check the `sync_repository` tool - is it properly calling `chassis.vector_store.add_documents()` to index the repo? Check the `translate_shorthand` tool - is it calling `chassis.vector_store.semantic_search()`?
4. **Layer 4: Agent Logic (`agent.py`)** 
   * *What to do:* Check the routing and queue consumption. Ensure the `@chassis.consume_task` decorator is used for the async clone job.
5. **Layer 5: Wiring (`config.yaml`)** 
   * *What to do:* Confirm the agent is registered correctly so it appears in the Agent Studio UI.
### Solution: Phase 4 (Verify)
**Reference Checkpoint Branch:** [`solution-codelab3-phase4`](https://github.com/your-org/hackathon-monorepo/tree/solution-codelab3-phase4)

**Expected Output:** A robust, working agent validated in the Agent Studio UI that successfully handles long-running clones, clarifies shorthand, and summarizes diffs without crashing.

**How to test your implementation:**
1. **The Clone Test:** Type "Sync the repo" in the UI. The UI should instantly reply "Started syncing" (or similar), and your terminal should start showing Git clone progress.
2. **The Clarification Test:** Type "What changed in Navigation?" The agent should pause, use the `translate_shorthand` tool, and ask you to clarify which specific navigation module you meant.
3. **The Nuke Test:** Ask "Show me the full diff for the last 10 commits in Compose UI." If your agent crashes or throws a token limit error, your `execute_git_command` tool is not properly constrained! It should reply with a summary or a truncated diff stat instead.

**Reference Approach:** Agent Developers should use the local Agent Studio UI to interact with the agent as a real user would. When errors occur (like context window overflows), developers should copy the terminal stack trace and paste it back into their AI CLI or Gemini Web to ask for a fix. 

> 💡 **The Iterative Loop:** Remember, building agents is rarely a one-shot process! It is highly likely that during verification, you will discover a flaw in your design (e.g., the diff stat is still too large, or the semantic mapper missed an edge case). When this happens, you must kick off successive **Observe → Think → Act → Verify** loops. Go back to your spec, update your plan, have the CLI revise the code, and verify again until you arrive at the robust solution you were hoping for.

> 🎬 **The Director's Mindset:** Keep in mind that your AI CLI might get details wrong, hallucinate, and possibly introduce bugs—just like any human software engineer! As the Director, it is your job to validate the work and explicitly ask the AI builder to go through revisions. What you choose to revise is entirely up to you. You might want to get down into the nitty-gritty details of how the code is organized, or you might only care about the user interaction, or you might focus heavily on how state is managed and how the agent responds. Using successively tighter OTAV loops gets you closer to your "ideal" solution.