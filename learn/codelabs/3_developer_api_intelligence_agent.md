# Codelab 3: Developer API Intelligence Agent 🤖📱

**Goal:** Build a sophisticated, real-world assistant that can analyze code repos (we'll use AndroidX for this codelab), track recent changes, and map developer shorthand names for repos to actual code modules.

**What You Will Build:** An AI agent that connects to a local clone of a codebase. When a user asks "What changed in Compose UI lately?", the agent will:
1. **Dynamically Clone** the massive repository to your local machine (using state management to check if it already exists).
2. **Handle** the request asynchronously via a background queue so the UI doesn't freeze during the long download.
3. **Translate** human shorthand ("Compose UI") into the exact repository path.
4. **Execute** real `git log` and `git diff` commands against the local code to analyze recent changes without blowing out the LLM context window.
5. **Synthesize** the raw code diffs into a clear, human-readable summary.

**Status:** Advanced / Offline Challenge
**Format:** Individual Challenge with Open Collaboration

### 🎓 What you will learn:
* How to handle long-running tasks (like cloning a 1.3GB repo) asynchronously using messaging queues so the UI doesn't freeze.
* How to implement **State Management** to track if long-running tasks have already been completed.
* How to use **Logging and Tracing** so users can see terminal output while waiting for async jobs.
* How to build "Semantic Mapping" tools that translate human shorthand (e.g., "Compose UI") into exact system paths.
* How to write tools that execute real terminal commands (like `git log` and `git diff`) and manage the resulting massive data payloads to prevent blowing out the LLM's context window.

## Before you start

### 🛑 Stick to the mocked framework for an easier time
Because this hackathon is designed to run locally on your machines without depending on possibly corporate resources or prohibited external services, **you should build this agent to run entirely in the mock environment.**  You are of course welcome to attempt to plug into policy allowed systems if you're curious.  
### ⚠️ Setting Expectations
This codelab is meant to be **very difficult** and mirrors a practical, real-world use case for building agentic flows. One of our primary goals is to show that it still takes thought, planning, and work to create good tooling—not everything is just "a prompt away."

Throughout this challenge, we hope to highlight the reality of agent development:
*   **Where your time is spent:** Learning the domain, ideating the architecture, and planning the tool boundaries.
*   **Where the AI makes things trivial:** Quickly generating the boilerplate, scaffolding the code, and creating the initial "thing."
*   **Where the AI can be frustrating (and needs you!):** Debugging, hallucinating, taking odd liberties with planning or code generation, and missing edge cases or tests. 

Expect to provide strong guidance to your AI CLI. This codelab simulates the very real, sometimes involved workflow of building production agents.
### 💡 Stuck? Use the Checkpoints!
***This is a complex challenge.*** If you get stuck on a specific architectural hurdle, you don't have to stay blocked! We have provided progressive solution branches in the repository. 

You can check out these branches to see how the "Golden Path" solved the problem, or even merge them into your own work to jumpstart your progress:
* `git checkout solution-codelab3-checkpoint1` (Provides the Async Queue skeleton and `sync_repository` tool)
* `git checkout solution-codelab3-checkpoint2` (Adds the Semantic Mapper tool implementation)
* `git checkout solution-codelab3-complete` (The final Developer API Intelligence Agent using real Git commands and mocked data)

*(Note: The complete, enterprise-grade version of this agent with real Redis/Postgres infrastructure will also be available on the `main` branch under `src/agents/developer_api_agent` as a post-hackathon reference).*

---
## 🚀 Let's Get Started
You are about to build the **Developer API Intelligence Agent**. To do this, you'll need to instruct your AI CLI to scaffold the agent, define its state, and build out its tools. 

As you start generating code, you'll immediately run into a few realities of working with massive codebases: how do you prevent the UI from freezing while cloning gigabytes of data? How do you translate what a developer says into what the file system expects? And how do you read the code without completely overwhelming your LLM? 

Keep these constraints in mind as you tackle the challenges below. Fire up your terminal, initialize your AI coding assistant, and let's start building! 
## Challenge 1: Dealing with Long-Running Tasks
Downloading, parsing, or indexing massive repositories takes time. The AndroidX repo is ~1.3GB and takes about 2 minutes to clone.
* **The Problem:** If you trigger a `git clone` synchronously via a standard FastAPI request, the HTTP connection will timeout and the Agent Studio UI will freeze. Furthermore, the user won't know if the system is broken or just thinking.
* **The Goal:** Build a `sync_repository` tool that uses the `BaseAgentChassis`'s native in-memory queue capabilities. 
    1. **State Management:** The tool should first check if `/tmp/androidx-source` already exists. If it does, skip the clone!
    2. **Async Execution:** If it doesn't exist, the agent should immediately return a status (e.g., "Job Started") to the UI, while the `git clone https://android.googlesource.com/platform/frameworks/support /tmp/androidx-source` happens asynchronously in the background.
    3. **Logging:** Use standard Python `logging` or print statements during the clone. The mock infra will pick this up so you can see the progress in your terminal, proving the background job is running!

## Challenge 2: Translating Developer Shorthand
Developers rarely use the exact Gradle paths when asking questions.
* **The Problem:** A user might ask, "What changed in Compose UI lately?" but the code lives in `androidx.compose.ui:ui` and the folder path is `compose/ui/ui`.
* **The Goal:** Build a tool (or a dedicated routing agent) that maintains a semantic map. It must translate developer shorthand ("Navigation", "Paging", "Room") into the exact artifact IDs and directory paths used in the repository.

## Challenge 3: Executing Real Git Commands (and surviving the Context Window)
Your agent needs eyes on the actual code changes.
* **The Goal:** Build a tool that uses Python's `subprocess` module to execute real `git log` and `git diff` commands against the `/tmp/androidx-source` directory. 
* **The Trap:** A raw `git diff` for a major release will easily blow out an LLM's context window. You must build your tools to summarize, truncate, or selectively extract the diffs *before* passing them back to the agent's brain. (Hint: look at `git log -p -1`, `git diff --stat`, or building Python logic to chunk the output).

## The Strategy (How to tackle this)
This codelab is not a step-by-step tutorial. It is a real engineering challenge of a practical use case that could serve as a major innovation unlock. I recommend:
1. **Open Collaboration:** While this is an individual build, you are highly encouraged to use the open hackathon chat to discuss roadblocks, share prompt strategies, and ideate with your peers.
2. **Use the AI Bridge:** Use your Gemini Web App to paste in terminal output or Python errors and ask it to write the exact Python parsing logic.

Good luck, and remember to ***direct*** your AI CLIs rather than writing all the boilerplate yourselves!

---

## Extra Credit Side Quests (Pushing the Boundaries)
If you finish the core challenges early, try tackling one of these advanced missions here. These ideas are classified by whether they make existing workflows faster (**Efficiency Gain**) or create entirely new capabilities (**Innovation**).

### 1. Automated Release Note Synthesis (Efficiency Gain)
* **The Concept:** API maintainers spend hours parsing merged PRs to write human-readable release notes for each library update.
* **The Mission:** Build a tool that takes a module name (e.g., "Navigation") and two Git tags. The agent fetches all merged PRs between the tags, filters out internal refactors, and drafts a public-facing markdown release note highlighting new features and bug fixes.
* **The Add-on:** Learning about all of these changes takes time. Leverage the agent to expedite your human learning by summarizing complex PRs into digestible, topic-specific insights and key areas you may want to dig deeper into. 

### 2. The "Sample Code" Auto-Migrator (Innovation)
* **The Concept:** When an API is deprecated, maintainers have to manually update dozens of sample apps to prevent developers from copying outdated code.
* **The Mission:** Give the agent access to a local sample repository. When an API changes, the agent autonomously scans the sample repo, finds usages of the deprecated API, and uses an LLM coding tool to generate a Git patch or PR updating the sample code to the new standard.
* **The Add-on:** Detect and test for possible behavior changes. Using an understanding of what could have possibly changed with an API where the change isn't apparent (e.g. no public API have changed) and have the agent predictively generate a variety of test sample plans to take best guesses at what might break. This could be autonomously fed into a team of agents that simply generates the samples and executes them and checks if test assertions fail. 

### 3. Issue Tracker Triage & Routing (Efficiency Gain)
* **The Concept:** Triaging incoming GitHub issues or Issue Tracker bugs is a manual, tedious process.
* **The Mission:** Build a tool that reads the latest open issues. The agent uses the "Semantic Mapper" to determine which module the issue belongs to, tags it appropriately via the API, and drafts a preliminary response if it recognizes a known API misuse based on the docs.
* **The Add-on:** Identify where gaps in samples, documentation, or skills might exist and have the agent automatically propose key improvements across all three (as a plan) for you to review and approve. 

### 4. API "Blast Radius" Analyzer (Innovation)
* **The Concept:** API maintainers need to know *before* a release if a change will break thousands of developers.
* **The Mission:** Build a tool that analyzes an open PR in the repository. The agent determines if the change breaks public API compatibility and generates a "Maintainer Warning Score" predicting how much documentation or community outreach will be required if the PR merges.

---





## Solutions Overview
To ensure everyone walks away with a deep understanding of the architecture, we will provide a **Solutions Overview** at the end of the codelab. We will walk through the real explanations of the code, discuss how the async queues communicate with the frontend, and review the architectural decisions made in the "Golden Path" solution branches.