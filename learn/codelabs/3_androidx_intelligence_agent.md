# Codelab 3: AndroidX Intelligence Agent 🤖📱

**Goal:** Build a sophisticated, real-world DevRel assistant that can analyze the massive AndroidX monorepo, track recent changes, and map developer shorthand to actual code modules.
**Status:** Advanced / Offline Challenge
**Format:** Team Collaboration & Problem Solving

### 🎓 What you will learn:
* How to handle long-running tasks asynchronously using Redis queues so the UI doesn't freeze.
* How to build "Semantic Mapping" tools that translate human shorthand (e.g., "Compose UI") into exact system paths.
* How to manage and truncate massive data payloads (like Git diffs) to prevent blowing out the LLM's context window.
* How to orchestrate multiple tools (GitHub APIs + Web Scraping) to synthesize a single answer.

---

## The Mission
Your team (Android Developer Relations) needs an agent that understands the AndroidX monorepo. Instead of simple API calls, this agent must handle long-running tasks, parse massive codebases, and map human intent to complex Git structures.

## Challenge 1: Asynchronous Execution (Long-Running Tasks)
Downloading, parsing, or indexing parts of the AndroidX monorepo takes time.
* **The Problem:** If you do this synchronously via a standard FastAPI request, the HTTP connection will timeout and the Agent Studio UI will freeze.
* **The Goal:** Use the `BaseAgentChassis`'s native Redis queue capabilities. When the user asks to "Index the Room library," the agent should immediately return a status (e.g., "Job Started") to the UI, while the heavy lifting happens asynchronously in the background.

## Challenge 2: Semantic Mapping (Shorthand to Modules)
Developers rarely use the exact Gradle paths when asking questions.
* **The Problem:** A user might ask, "What changed in Compose UI lately?" but the code lives in `androidx.compose.ui:ui`.
* **The Goal:** Build a tool (or a dedicated routing agent) that maintains a semantic map. It must translate DevRel shorthand ("Navigation", "Paging", "Room") into the exact artifact IDs and directory paths used in the AndroidX GitHub repository.

## Challenge 3: Git & Documentation Intelligence
Your agent needs eyes on both the code and the public-facing docs.
* **The Goal:** Build specific tools for:
    1. **Git Intelligence:** Querying the GitHub API to read recent commits, PRs, and release tags for specific modules.
    2. **Doc Parsing:** Fetching and parsing recent updates from `developer.android.com` to see if the public documentation matches the recent code changes.
* **The Trap:** A raw Git diff for a major release will easily blow out an LLM's context window. You must build your tools to summarize, truncate, or selectively extract the diffs *before* passing them back to the agent's brain.

## The Strategy (How to tackle this)
This codelab is not a step-by-step tutorial. It is a real engineering challenge.
1. **Divide and Conquer:** Have one person build the Semantic Mapper, one person figure out the GitHub API truncation, and one person set up the asynchronous Redis state.
2. **Use the AI Bridge:** Use your Gemini Web App to paste in AndroidX GitHub API payloads and ask it to write the exact Python parsing logic.
3. **Mock First:** Don't download the real 10GB AndroidX repo on day one. Mock the GitHub API responses first to ensure your agent's reasoning loop works.

Good luck, and remember to direct your AI CLIs rather than writing all the boilerplate yourselves!

## Extra Credit Missions (Pushing the Boundaries)
If your team finishes the core challenges early, try tackling one of these advanced DevRel missions. These ideas are classified by whether they make existing workflows faster (**Efficiency Gain**) or create entirely new capabilities (**Innovation**).

### 1. Automated Release Note Synthesis (Efficiency Gain)
* **The Concept:** DevRel spends hours parsing merged PRs to write human-readable release notes for each library update.
* **The Mission:** Build a tool that takes a module name (e.g., "Navigation") and two Git tags. The agent fetches all merged PRs between the tags, filters out internal refactors, and drafts a public-facing markdown release note highlighting new features and bug fixes.

### 2. The "Sample Code" Auto-Migrator (Innovation)
* **The Concept:** When AndroidX deprecates an API, DevRel has to manually update dozens of sample apps (like the `architecture-samples` repo) to prevent developers from copying outdated code.
* **The Mission:** Give the agent access to a local sample repository. When an AndroidX API changes, the agent autonomously scans the sample repo, finds usages of the deprecated API, and uses an LLM coding tool to generate a Git patch or PR updating the sample code to the new standard.

### 3. Issue Tracker Triage & Routing (Efficiency Gain)
* **The Concept:** Triaging incoming GitHub issues or Google Issue Tracker bugs is a manual, tedious process.
* **The Mission:** Build a tool that reads the latest open issues. The agent uses the "Semantic Mapper" to determine which AndroidX module the issue belongs to, tags it appropriately via the API, and drafts a preliminary response if it recognizes a known API misuse based on the docs.

### 4. API "Blast Radius" Analyzer (Innovation)
* **The Concept:** DevRel needs to know *before* a release if a change will break thousands of developers.
* **The Mission:** Build a tool that analyzes an open PR in the AndroidX repo. The agent determines if the change breaks public API compatibility and generates a "DevRel Warning Score" predicting how much documentation or community outreach will be required if the PR merges.

---

## 🛑 Important: The Mock Infrastructure Constraint
Because this hackathon is designed to run locally on your laptops without requiring heavy Docker containers, **you must build this agent to run entirely in the mock environment.**
If your agent requires background queues (Challenge 1) or vector search, instruct your AI CLI to build lightweight in-memory (`asyncio.Queue`) or file-based (`json`) adapters rather than spinning up Redis or Postgres. The `BaseAgentChassis` supports this seamlessly!

## 💡 Stuck? Use the Checkpoints!
This is a complex challenge. If your team gets stuck on a specific architectural hurdle, you don't have to stay blocked! We have provided progressive solution branches in the repository. 

You can check out these branches to see how the "Golden Path" solved the problem, or even merge them into your own work to jumpstart your progress:
* `git checkout solution-codelab3-checkpoint1` (Provides the Async Queue skeleton and Mock Adapters)
* `git checkout solution-codelab3-checkpoint2` (Adds the Semantic Mapper tool implementation)
* `git checkout solution-codelab3-complete` (The final, fully mocked AndroidX Agent)

*(Note: The complete, enterprise-grade version of this agent with real Redis/Postgres infrastructure will also be available on the `main` branch under `src/agents/androidx_agent` as a post-hackathon reference).*
