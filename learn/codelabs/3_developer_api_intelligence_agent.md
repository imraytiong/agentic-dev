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

### 💡 Stuck? Use the Checkpoints!
If you get stuck don't stay blocked for too long. Use the branches below to get you moving forward faster. 

You can check out these branches to see how the "Golden Path" solved the problem, or even merge them into your own work to jumpstart your progress:
* `git checkout solution-codelab3-checkpoint1` (Provides the Async Queue skeleton and `sync_repository` tool)
* `git checkout solution-codelab3-checkpoint2` (Adds the Semantic Mapper tool implementation)
* `git checkout solution-codelab3-complete` (The final Developer API Intelligence Agent using real Git commands and mocked data)

*(Note: The complete, enterprise-grade version of this agent with real Redis/Postgres infrastructure will also be available on the `main` branch under `src/agents/developer_api_agent` as a post-hackathon reference).*

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
> **You:** What's changed recently in Compose UI?
> **Agent:** Hold on, I need to sync the repository first. This might take a minute... *(UI remains responsive)*
> *(2 minutes later)*
> **Agent:** Repository synced! I searched the repo for the Compose UI, specifically did you mean `compose/ui/ui`? If so the biggest recent change is a fix to the `Modifier.Node` lifecycle, specifically addressing a memory leak when detaching nodes. Here is a quick summary of the diffs...

**Example 2: Semantic Translation & Ambiguity**
> **You:** What are the latest commits for "Navigation"?
> **Agent:** By "Navigation", do you mean `androidx.navigation:navigation-compose` or `androidx.navigation:navigation-fragment`? 
> **You:** Compose please.
> **Agent:** Got it. Looking at `navigation/navigation-compose`. The last 3 commits involve adding type safety to the NavGraphBuilder. Here are the details...

**Example 3: Context Window Survival**
> **You:** Show me the diff for the latest major refactor in Room.
> **Agent:** The latest commit in `room/room-compiler` is massive (over 4,000 lines changed). Instead of showing you the raw diff, I ran a diff stat. It looks like they completely rewrote the `QueryProcessor.kt` and added 15 new test files. Would you like me to summarize just the changes in `QueryProcessor.kt`?

---

## 🧠 The Agent Builder Workflow: Observe, Think, Act, Verify

Rather than treating this as a standard coding tutorial, we want you to practice **Agent-Driven Development**. In this paradigm, you act as the Technical Director. You spend your time observing constraints and planning the architecture upfront, and then you direct your AI CLI to act on those plans.

Follow this macro-workflow to conquer the codelab:

### Phase 1: Observe (The Domain & Constraints)
Before writing a single prompt, take a step back and look at the reality of the systems you are integrating with.
* **The Long-Running Task:** The AndroidX repo is ~1.3GB. A `git clone` will take about 2 minutes. A synchronous HTTP request will timeout and freeze the UI. 
* **The Translation Gap:** Developers say "Compose UI", but the file system expects `compose/ui/ui`. The agent cannot guess this; it needs deterministic mapping.
* **The Context Window Nuke:** A raw `git diff` for a major framework release will easily output 10,000+ lines of text. Feeding this directly into an LLM will crash the agent or cause severe hallucinations.

### Phase 2: Think (The Architecture & Spec)
Now that you know the constraints, plan the architecture. *This is where you earn your paycheck as an Agent Architect.*
* **State Management:** The agent needs a `DeveloperAPIState` to remember if the repo is `not_cloned`, `cloning`, or `ready`. 
* **Async Queues:** The `sync_repository` tool must be offloaded to a background task using the `BaseAgentChassis`'s native async capabilities. It should log to the terminal so developers know it isn't broken.
* **Tool Boundaries:** We need a semantic mapping dictionary to translate shorthand. We also need a `local_git_executor` tool that uses Python's `subprocess` module. Crucially, this Git tool must be constrained—it should run `git diff --stat` first, forcing the agent to request specific files rather than dumping the whole diff.

### Phase 3: Act (The AI CLI Execution)
With your plan in place, instruct your AI CLI to build the agent layer-by-layer. Do not write the boilerplate yourself!
* Open your terminal and use your AI CLI (e.g., Gemini CLI, Cursor).
* Feed it your architectural decisions. (See the *Solution Kickoff Prompts* below for examples of how to direct the CLI).
* If the CLI gets confused, use the **AI Bridge**—paste terminal output or Python errors back into your Gemini Web App to have it write the exact Python parsing logic or refactoring steps for you.

### Phase 4: Verify (The Testing & HITL)
Test the agent in the Agent Studio UI to ensure the architecture holds up.
* Ask the agent to sync the repo. Does the UI respond instantly with "Job Started" while the terminal shows Git progress?
* Ask for "Navigation". Does it pause to clarify which module you meant?
* Ask for a massive diff. Does it successfully summarize it without crashing?

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

## Solutions Overview
To ensure everyone walks away with a deep understanding of the architecture, we will provide a **Solutions Overview** at the end of the codelab. We will walk through the real explanations of the code, discuss how the async queues communicate with the frontend, and review the architectural decisions made in the "Golden Path" solution branches.

### Solution Kickoff Prompts
If you are stuck on how to begin Phase 3 (Act), try feeding these exact prompts to your AI CLI to get the momentum going:

**1. Scaffold the Agent:**
*"Use the `adk-agent-builder` skill to scaffold a new agent called 'developer_api_agent'. It should be able to track state, specifically whether a local repository is 'not_cloned', 'cloning', or 'ready'."*

**2. Wire it up:**
*"Register this new agent in our system configuration so I can see it and talk to it in the Agent Studio UI."*

**3. Build the Core Tool:**
*"Build a tool for this agent that clones the AndroidX repo to `/tmp/androidx-source`. It needs to run in the background so the UI doesn't freeze, and it should print its progress to the terminal so I know it's working."*