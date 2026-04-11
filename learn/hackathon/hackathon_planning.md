# Hackathon Planning & Execution

This document tracks the logistical and technical setup required to ensure the internal AI Agent Hackathon runs smoothly.

## 0. Prerequisites & Environment
Before participants arrive on Day 1, they should ensure the following prerequisites are met:
* **Gemini CLI & Conductor:** These are the mandatory AI coding assistants for the event.
* **Cloud-Based Virtualization Container:** Due to strict corporate network policies and proxy configurations, participants will likely need to set up a cloud-based virtualization container (e.g., Coder, GitHub Codespaces, or an internal devbox) to successfully run the Gemini CLI, Conductor, and the underlying infrastructure.
* **Git Concepts:** A solid understanding of core Git concepts (branching, remotes, committing) is essential, especially given our dual-remote (public/corporate) repository strategy. *(Note: You don't need to memorize commands; you can always ask your LLM for the exact syntax).*
* **Terminal Tools (Recommended):** Familiarity with terminal multiplexers like `tmux` is highly helpful for managing multiple running services (e.g., your agent's FastAPI server, the AI CLI, and infrastructure logs) in a single window.

## 1. Day 1 Developer Onboarding (The "Zero to Hero" Script)
When participants sit down on Day 1, they should not have to guess how to set up their environment. Instead of running 10 different commands to configure Python and the Gemini CLI, they just need to run our automated bootstrap script.

Provide them with this exact copy/paste script in the kickoff presentation:

```bash
# 1. Clone the repository
git clone <internal-repo-url>
cd hackathon-repo

# 2. Run the automated bootstrap script
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh

# 3. Activate the environment
source venv/bin/activate

# 4. Load the Agent Builder skill to establish your guardrails
gemini load skills/adk-agent-builder/SKILL.md
```

### What the Bootstrap Script Does Automatically:
* Creates a local `.env` file from `.env.example`.
* Builds the Python `venv` and installs all `requirements.txt`.
* Runs `gemini init` to create the local workspace.
* Runs `gemini git init` so the AI understands branches and diffs.
* Runs `gemini context add SYSTEM_INSTRUCTIONS.md` to permanently pin the architectural guardrails to the AI's memory.

## 2. AI Context Automation (Gemini CLI Strategy)
Unlike IDEs like Cursor that automatically read proprietary `.cursorrules` files, the **Gemini CLI** relies on explicit context loading. To ensure every hackathon participant has the correct guardrails without manual prompting, we use a **Global System Prompt**.

We have committed a `SYSTEM_INSTRUCTIONS.md` file to the root of the repository.

This file enforces that the AI:
1. Understands the monorepo layout via the README.
2. Follows the `2_agent_builder_playbook.md`.
3. Adheres to our Hexagonal Architecture and never hallucinates infrastructure.
4. Uses the AI Bridge Protocol (inbox files) to communicate with Gemini Scribe.

**How it's enforced:** The `bootstrap.sh` script automatically runs `gemini context add SYSTEM_INSTRUCTIONS.md` (or the equivalent Conductor command), ensuring the AI never forgets the rules of the monorepo.

## 3. Pre-Hackathon Checklist (For the Core Team)
- [ ] **Universal Core Built:** The `BaseAgentChassis` must be fully coded, tested, and sealed in `src/universal_core/`.
- [ ] **Reference Agent Built:** `sparky_spec.md` should be fully implemented in `src/agents/hello_sparky/` so developers have a working example to copy.
- [ ] **Dual-Remote Git Configured:** Ensure the internal corporate Git server is ready to act as `origin` for all hackathon teams, protecting IP.
- [ ] **`.gitignore` Verified:** Ensure `.gemini/`, `.env`, and `__pycache__` are properly ignored.
- [ ] **Infrastructure Adapters Ready:** Ensure at least the "Mock Infrastructure" (Agent Studio Web UI) is working flawlessly so developers can test locally without needing K3s/Docker.

## 4. Judging & Showcase (To To Defined)
* How will teams demo their agents? (e.g., via the Agent Studio Web UI, or via MCP in their IDE?)
* What are the success criteria? (e.g., proper use of tools, clean state management, adherence to Hexagonal Architecture)

## 5. Diary of Ideas
*Use this section as a running scratchpad for hackathon ideas, themes, and logistical improvements.*

* **Idea 1:** Provide a "Pre-flight Check" script that participants can run to verify their `.env` and Gemini CLI are configured correctly before they write their first prompt.
* **Idea 2:** ...
