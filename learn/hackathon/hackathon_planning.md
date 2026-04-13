# Hackathon Planning & Execution

This document tracks the logistical and technical setup required to ensure the internal AI Agent Hackathon runs smoothly.

## Hackathon Goals
By the end of this hackathon, participants will achieve the following core objectives (derived directly from the 4 Codelabs):

1. **Master Agent-Driven Development (ADD):** Shift from writing code to *directing* AI coding assistants using strict specifications, layer-by-layer generation, and Test-Driven Defense (TDD). 
2. **Understand the BaseAgentChassis Architecture:** Learn to deploy, test, and interact with agents seamlessly using the mock infrastructure, testing multimodal file uploads via the Agent Studio Web UI, and inspecting agent reasoning loops.
3. **Build Stateful, Resilient Agents:** Move beyond simple prompts to create robust agents with persistent memory (Pydantic state), custom tools, and fallback reasoning (General Intelligence) to elegantly handle tool failures.
4. **Tackle Enterprise-Scale Agentic Workflows:** Solve complex architectural challenges like handling long-running asynchronous tasks (Redis queues), managing massive data payloads (Git diffs/Context limits), and mapping human intent to code paths.
5. **End-to-End Custom Agent Creation:** Successfully ideate, specify, and build a fully custom agent from scratch that solves a real-world team workflow problem, while maintaining strict Git version control.

## 0. Prerequisites & Environment
Before participants arrive on Day 1, they should ensure the following prerequisites are met:
* **Gemini CLI & Conductor:** These are the mandatory AI coding assistants for the event.
* **Cloud-Based Virtualization Container:** Due to strict corporate network policies and proxy configurations, participants will likely need to set up a cloud-based virtualization container (e.g., Coder, GitHub Codespaces, or an internal devbox) to successfully run the Gemini CLI, Conductor, and the underlying infrastructure.
* **Git Concepts:** A solid understanding of core Git concepts (branching, remotes, committing) is essential, especially given our dual-remote (public/corporate) repository strategy. *(Note: You don't need to memorize commands; you can always ask your LLM for the exact syntax).*
* **Terminal Tools (Recommended):** Familiarity with terminal multiplexers like `tmux` is highly helpful for managing multiple running services (e.g., your agent's FastAPI server, the AI CLI, and infrastructure logs) in a single window.

## 1. Day 1 Developer Onboarding (The "Zero to Hero" Script)
When participants sit down on Day 1, they should not have to guess how to set up their environment. Instead of running 10 different commands to configure Python and the Gemini CLI, they just need to run our automated bootstrap script.

Provide them with this exact copy/paste one-liner in the kickoff presentation:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/imraytiong/agentic-dev/main/scripts/start_hackathon.sh)"
```
*(Note: Update the URL above to point to the raw text of the script on your internal Git server).*

**After the script finishes, they simply run:**
```bash
cd agentic-dev
source venv/bin/activate
gemini load skills/adk-agent-builder/SKILL.md
```

### What the Bootstrap Script Does Automatically:
* Clones (or pulls) the repository.
* Creates a local `.env` file from `.env.example`.
* Builds the Python `venv` and installs all `requirements.txt`.
* Runs `gemini init` to create the local workspace.
* Runs `gemini git init` so the AI understands branches and diffs.
* Runs `gemini context add SYSTEM_INSTRUCTIONS.md` to permanently pin the architectural guardrails to the AI's memory.

## 2. The Hackathon Framework (The 4 Codelabs)
The hackathon structure is guided by four progressive codelabs. These take developers from environment setup all the way to building a fully custom enterprise agent.

* **Codelab 1: Hello Sparky (`learn/codelabs/1_hello_sparky.md`)**
  * *Focus:* Environment setup and running a pre-built agent.
  * *Goal:* Run the bootstrap script, boot Sparky with mock infrastructure, interact with it via the Agent Studio Web UI (including multimodal file drops), and manually inspect its reasoning loop.
* **Codelab 2: Upgrading Sparky (`learn/codelabs/2_upgrading_sparky.md`)**
  * *Focus:* Introduction to Agent-Driven Development.
  * *Goal:* Use the AI CLI to add a new tool (weather), update the Pydantic `AgentState` to remember the user's location, modify the Jinja prompt to handle tool failures via general intelligence, and establish Git versioning and TDD practices.
* **Codelab 3: AndroidX Intelligence Agent (`learn/codelabs/3_androidx_intelligence_agent.md`)**
  * *Focus:* Advanced enterprise agent architecture.
  * *Goal:* An individual offline challenge to build a complex DevRel agent. Requires handling long-running tasks (Redis queues), semantic mapping of AndroidX modules, and querying Git/Web APIs while managing context limits.
* **Codelab 4: Capstone - Build Your Own Agent (`learn/codelabs/4_capstone_build_your_own.md`)**
  * *Focus:* End-to-end creation of a custom agent.
  * *Goal:* Use Gemini Web or Scribe for ideation, draft a formal `agent_spec_template.md`, and use the AI CLI to build, test, and deploy a brand new custom agent.

## 3. Hackathon Agenda (Monday - Friday)
To keep the momentum going, the hackathon follows a structured 5-day timeline mapping directly to the codelabs and final capstone.

* **Monday (Day 1): The Kickoff & Fundamentals**
  * *Morning:* Kickoff presentation, environment setup, and running the `start_hackathon.sh` script.
  * *Late Morning:* **Codelab 1 (Hello Sparky)** - Running the mock infrastructure and interacting with the UI.
  * *Afternoon:* **Codelab 2 (Upgrading Sparky)** - Introduction to Agent-Driven Development and modifying an agent via the CLI.
* **Tuesday (Day 2): The Enterprise Challenge**
  * *All Day:* **Codelab 3 (AndroidX Intelligence Agent)** - Developers tackle the offline challenge individually, collaborating in the open chat. Focus on asynchronous Redis queues, semantic mapping, and Git/Doc intelligence.
* **Wednesday (Day 3): Ideation & Capstone Kickoff**
  * *Morning:* Finish Codelab 3 or tackle the Extra Credit missions.
  * *Afternoon:* **Codelab 4 (Capstone) Kickoff** - Ideation phase. Teams use LLMs to brainstorm, scope their custom agent idea, and write their `agent_spec_template.md`.
* **Thursday (Day 4): Heads-Down Building**
  * *All Day:* **Codelab 4 (Execution)** - Teams use the CLI to build their custom agents layer-by-layer. Focus on implementing custom tools, handling state, and testing via the Agent Studio or MCP.
* **Friday (Day 5): Polish, Demo, & Retrospective**
  * *Morning:* Final code polish, bug fixing, and preparing the demo environment.
  * *Afternoon:* Judging & Showcase! Teams demo their custom agents.
  * *Late Afternoon:* Wrap-up, retrospective, and awards.

## 4. AI Context Automation (Gemini CLI Strategy)
Unlike IDEs like Cursor that automatically read proprietary `.cursorrules` files, the **Gemini CLI** relies on explicit context loading. To ensure every hackathon participant has the correct guardrails without manual prompting, we use a **Global System Prompt**.

We have committed a `SYSTEM_INSTRUCTIONS.md` file to the root of the repository.

This file enforces that the AI:
1. Understands the monorepo layout via the README.
2. Follows the `2_agent_builder_playbook.md`.
3. Adheres to our Hexagonal Architecture and never hallucinates infrastructure.
4. Uses the AI Bridge Protocol (inbox files) to communicate with Gemini Scribe.

**How it's enforced:** The `start_hackathon.sh` script automatically runs `gemini context add SYSTEM_INSTRUCTIONS.md` (or the equivalent Conductor command), ensuring the AI never forgets the rules of the monorepo.

## 5. Pre-Hackathon Checklist (For the Core Team)
- [ ] **Universal Core Built:** The `BaseAgentChassis` must be fully coded, tested, and sealed in `src/universal_core/`.
- [ ] **Reference Agent Built:** `sparky_spec.md` should be fully implemented in `src/agents/hello_sparky/` so developers have a working example to copy.
- [ ] **Dual-Remote Git Configured:** Ensure the internal corporate Git server is ready to act as `origin` for all hackathon teams, protecting IP.
- [ ] **`.gitignore` Verified:** Ensure `.gemini/`, `.env`, and `__pycache__` are properly ignored.
- [ ] **Infrastructure Adapters Ready:** Ensure at least the "Mock Infrastructure" (Agent Studio Web UI) is working flawlessly so developers can test locally without needing K3s/Docker.

## 6. Judging & Showcase (To Be Defined)
* How will teams demo their agents? (e.g., via the Agent Studio Web UI, or via MCP in their IDE?)
* What are the success criteria? (e.g., proper use of tools, clean state management, adherence to Hexagonal Architecture)

## 7. Diary of Ideas
*Use this section as a running scratchpad for hackathon ideas, themes, and logistical improvements.*

* **Idea 1:** Provide a "Pre-flight Check" script that participants can run to verify their `.env` and Gemini CLI are configured correctly before they write their first prompt.
* **Idea 2:** ...