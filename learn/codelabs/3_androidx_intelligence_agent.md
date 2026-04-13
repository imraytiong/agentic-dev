# Codelab 3: AndroidX Intelligence Agent 🤖📱

**Goal:** Build a sophisticated, real-world assistant that can analyze the massive AndroidX monorepo, track recent changes, and map developer shorthand to actual code modules.
**Status:** Advanced / Offline Challenge
**Format:** Individual Challenge with Open Collaboration

### 🎓 What you will learn:
* How to handle long-running tasks asynchronously using messaging queues so the UI doesn't freeze.
* How to build "Semantic Mapping" tools that translate human shorthand (e.g., "Compose UI") into exact system paths.
* How to manage and truncate massive data payloads (like Git diffs) to prevent blowing out the LLM's context window.
* How to orchestrate multiple tools (GitHub APIs + Web Scraping) to synthesize a single answer.

---

## The Mission
As an API maintainer or developer, you need an agent that understands the AndroidX monorepo. Instead of simple API calls, this agent must handle long-running tasks, parse massive codebases, and map human intent to complex Git structures.

## Challenge 1: Dealing with Long-Running Tasks
Downloading, parsing, or indexing parts of the AndroidX monorepo takes time.
* **The Problem:** If you do this synchronously via a standard FastAPI request, the HTTP connection will timeout and the Agent Studio UI will freeze.
* **The Goal:** Use the `BaseAgentChassis`'s native Redis queue capabilities. When the user asks to "Index the Room library," the agent should immediately return a status (e.g., "Job Started") to the UI, while the heavy lifting happens asynchronously in the background.

## Challenge 2: Translating Developer Shorthand
Developers rarely use the exact Gradle paths when asking questions.
* **The Problem:** A user might ask, "What changed in Compose UI lately?" but the code lives in `androidx.compose.ui:ui`.
* **The Goal:** Build a tool (or a dedicated routing agent) that maintains a semantic map. It must translate developer shorthand ("Navigation", "Paging", "Room") into the exact artifact IDs and directory paths used in the AndroidX GitHub repository.

## Challenge 3: Reading Massive Code and Docs
Your agent needs eyes on both the code and the public-facing docs.
* **The Goal:** Build specific tools for:
    1. **Git Intelligence:** Querying the GitHub API to read recent commits, PRs, and release tags for specific modules.
    2. **Doc Parsing:** Fetching and parsing recent updates from `developer.android.com` to see if the public documentation matches the recent code changes.
* **The Trap:** A raw Git diff for a major release will easily blow out an LLM's context window. You must build your tools to summarize, truncate, or selectively extract the diffs *before* passing them back to the agent's brain.

## The Strategy (How to tackle this)
This codelab is not a step-by-step tutorial. It is a real engineering challenge of a practical use case that could serve as a major innovation unlock. I recommend:
1. **Open Collaboration:** While this is an individual build, you are highly encouraged to use the open hackathon chat to discuss roadblocks, share prompt strategies, and ideate with your peers.
2. **Use the AI Bridge:** Use your Gemini Web App to paste in AndroidX GitHub API payloads and ask it to write the exact Python parsing logic.
3. **The "Mock First" Tactic:** Create and generate Mock interfaces and mock data for the tools you are building. Don't try to connect to the real GitHub API or download massive payloads on day one. Have your AI CLI generate mock tool interfaces and static JSON responses (e.g., a fake Git diff or mock PR list) to ensure your agent's reasoning loop and UI work flawlessly. **Make sure your mock tools include realistic async delays (e.g., `await asyncio.sleep(1.5)`) to accurately simulate the latency of real Google and GitHub APIs!** Once you feel you've landed a great agent showcase, you can start replacing those mocked tools with real API calls for added effect!

Good luck, and remember to ***direct*** your AI CLIs rather than writing all the boilerplate yourselves!

---

## 🛠️ Provided Mock Services
To help you focus purely on agent logic rather than scraping data or hitting GitHub API limits, we have provided a set of pre-built mock data files focused specifically on **Media (Media3)**, **Camera (CameraX)**, and **System UI (WindowInsets)** modules. These files contain *real* data pulled from actual AndroidX releases and PRs to make your demos authentic.

You can find these in the `src/agents/androidx_agent/mocks/` directory:

1. **`mock_semantic_map.json`**: Maps shorthand like "ExoPlayer" or "WindowInsets" to their exact `androidx` artifact IDs and paths.
2. **`mock_github_prs.json`**: Simulates a GitHub API response returning recently merged PRs for these specific modules (e.g., real fixes for VBR MP3 seeking and CameraPipe migrations).
3. **`mock_git_diff.txt`**: A safe, truncated Git diff showing a real bug fix in ExoPlayer. Use this to practice handling code snippets without blowing out context windows!
4. **`mock_release_notes.json`**: Simulates scraped release notes from `developer.android.com` detailing recent features like Ultra HDR and Compose Pager fixes.

**How to use them:**
Instead of writing complex network requests in your tools, simply read these files! **Remember to add your forced delays to simulate the network request!**
```python
import json
import os
import asyncio

async def read_mock_prs() -> str:
    # Simulate the latency of hitting the real GitHub API
    await asyncio.sleep(1.5) 
    
    mock_path = os.path.join(os.path.dirname(__file__), "mocks", "mock_github_prs.json")
    with open(mock_path, "r") as f:
        return json.dumps(json.load(f), indent=2)
```

---

## Extra Credit Side Quests (Pushing the Boundaries)
If you finish the core challenges early, try tackling one of these advanced missions here. These ideas are classified by whether they make existing workflows faster (**Efficiency Gain**) or create entirely new capabilities (**Innovation**).

### 1. Automated Release Note Synthesis (Efficiency Gain)
* **The Concept:** API maintainers spend hours parsing merged PRs to write human-readable release notes for each library update.
* **The Mission:** Build a tool that takes a module name (e.g., "Navigation") and two Git tags. The agent fetches all merged PRs between the tags, filters out internal refactors, and drafts a public-facing markdown release note highlighting new features and bug fixes.
* **The Add-on:** Learning about all of these changes takes time. Leverage the agent to expedite your human learning by summarizing complex PRs into digestible, topic-specific insights and key areas you may want to dig deeper into. 

### 2. The "Sample Code" Auto-Migrator (Innovation)
* **The Concept:** When AndroidX deprecates an API, maintainers have to manually update dozens of sample apps (like the `architecture-samples` repo) to prevent developers from copying outdated code.
* **The Mission:** Give the agent access to a local sample repository. When an AndroidX API changes, the agent autonomously scans the sample repo, finds usages of the deprecated API, and uses an LLM coding tool to generate a Git patch or PR updating the sample code to the new standard.
* **The Add-on:** Detect and test for possible behavior changes. Using an understanding of what could have possibly changed with an API where the change isn't apparent (e.g. no public API have changed) and have the agent predictively generate a variety of test sample plans to take best guesses at what might break. This could be autonomously fed into a team of agents that simply generates the samples and executes them and checks if test assertions fail. 

### 3. Issue Tracker Triage & Routing (Efficiency Gain)
* **The Concept:** Triaging incoming GitHub issues or Google Issue Tracker bugs is a manual, tedious process.
* **The Mission:** Build a tool that reads the latest open issues. The agent uses the "Semantic Mapper" to determine which AndroidX module the issue belongs to, tags it appropriately via the API, and drafts a preliminary response if it recognizes a known API misuse based on the docs.
* **The Add-on:** Identify where gaps in samples, documentation, or skills might exist and have the agent automatically propose key improvements across all three (as a plan) for you to review and approve. 

### 4. API "Blast Radius" Analyzer (Innovation)
* **The Concept:** API maintainers need to know *before* a release if a change will break thousands of developers.
* **The Mission:** Build a tool that analyzes an open PR in the AndroidX repo. The agent determines if the change breaks public API compatibility and generates a "Maintainer Warning Score" predicting how much documentation or community outreach will be required if the PR merges.

---

## 🛑 Important: Strict Mock Environment
Because this hackathon is designed to run locally on your laptops without requiring heavy Docker containers, **you must build this agent to run entirely in the mock environment.** 
You do not need to build any infrastructure adapters for Codelab 3. Continue to assume you are working purely in the mock environment provided by the `BaseAgentChassis`.

## 💡 Stuck? Use the Checkpoints!
***This is a complex challenge.*** If you get stuck on a specific architectural hurdle, you don't have to stay blocked! We have provided progressive solution branches in the repository. 

You can check out these branches to see how the "Golden Path" solved the problem, or even merge them into your own work to jumpstart your progress:
* `git checkout solution-codelab3-checkpoint1` (Provides the Async Queue skeleton and Mock Tools)
* `git checkout solution-codelab3-checkpoint2` (Adds the Semantic Mapper tool implementation)
* `git checkout solution-codelab3-complete` (The final AndroidX Agent using mocked data)

*(Note: The complete, enterprise-grade version of this agent with real Redis/Postgres infrastructure will also be available on the `main` branch under `src/agents/androidx_agent` as a post-hackathon reference).*

## Solutions Overview
To ensure everyone walks away with a deep understanding of the architecture, we will provide a **Solutions Overview** at the end of the codelab. We will walk through the real explanations of the code, discuss how the async queues communicate with the frontend, and review the architectural decisions made in the "Golden Path" solution branches.