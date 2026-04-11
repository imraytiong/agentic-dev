# Agent Developer Workspace: Start Here

Welcome to the Agent Developer track (Role 3)! If you are tasked with building the "Brains" and "Hands" of our agents (e.g., The Supervisor, The Deep Researcher, The Data Analyst), you are in the right place. 

Our platform is designed so that you **never have to write infrastructure code**. You will focus 100% of your time on business logic, prompts, and Python tools. The Universal Core is provided by the Architect (Role 1), and the operational environment is mapped by the Infrastructure Leads (Role 2).

## The "Mock First" Paradigm (Why you aren't blocked)
You do **not** need to wait for the Infrastructure Leads to finish setting up Docker, Postgres, or Redis. You can start generating brains immediately!
By using `chassis.run_local(mock_infrastructure=True)`, your agent will use in-memory dictionaries and queues. Once the Infra team is ready, you simply turn off the mock and your agent connects to the real databases without rewriting a single line of business logic.

## Your Progressive Learning Path

To get up to speed quickly without being overwhelmed, please read these documents in the following exact order:

### 1. The Theory
*   **[Conceptual Guide - What is an Agent](Conceptual%20Guide%20-%20What%20is%20an%20Agent.md)**: Read this first. It explains the paradigm shift from traditional software to autonomous agents in simple, non-jargon terms. It covers what you are responsible for vs. what the platform handles for you.

### 2. The Code
*   **[Developer Guide](Developer%20Guide.md)**: This is your daily blueprint. It shows you the exact developer experience (DX), directory structures, and the incredibly clean `agent.py` code you will be generating.

### 3. The Workflow
*   **[Agentic Coding Playbook](Agentic%20Coding%20Playbook.md)**: Understand our "Agent-Driven Development" philosophy. We are Directors, not Typists.
*   **[Agent Directing Guide](Agent%20Directing%20Guide.md)**: Learn the explicit *Observe -> Think -> Act -> Verify* loop for managing your AI CLI (Gemini/Antigravity) so it writes compliant code without hallucinating.

### 4. The Action
*   **Load the Skill**: Fire up your CLI and type `load adk-agent-builder` (view the skill instructions here: **[adk-agent-builder](../../../07%20-%20AI%20CLI%20Skills/adk-agent-builder.md)**).
*   **Grab a Spec**: Go to the **[05 - Templates](../../../05%20-%20Templates)** folder, grab the **[Agent Architecture Spec](../../../05%20-%20Templates/Agent%20Architecture%20Spec.md)**, fill out your business logic, and hand it to the CLI to start building!

---
*Note: If you are ever curious about how the underlying databases, queues, and API wrappers actually work, you can peek over at the **[Platform Engineers](../Platform%20Engineers)** folder (or specifically the **[BaseAgentChassis Internals](../Platform%20Engineers/BaseAgentChassis%20Internals.md)**), but it is strictly optional for your day-to-day work!*